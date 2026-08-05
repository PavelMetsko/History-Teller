#!/usr/bin/env python3
"""Оптимизация арта под размер установки. Идемпотентно: повторный прогон ничего не портит.

Что делает:
  Персонажи (char_*) — спрайты с мягкой альфой, рисуются максимум ~560px в высоту,
    а лежат в 1024×1536. Уменьшаем до 768px и переквантуем pngquant'ом (PNG-8 + alpha,
    тем же способом, каким они изначально сделаны).
  Сцены (scene_*) — непрозрачные фоны 1024×1024, панель не бывает шире ~1330px,
    так что разрешение оставляем, а меняем кодек: JPEG на iOS, WebP на Android.
  Пропсы (prop_*) не трогаем — их 4 штуки на 0.2 МБ.

Почему форматы разные:
  actool перекодирует всё в Assets.car без потерь (проверено: HEIC-исходник раздувается
    вчетверо), поэтому на iOS выигрыш даёт только уменьшение пикселей + JPEG, который
    каталог кладёт как есть. WebP каталог не принимает.
  Android грузит файлы напрямую (res/drawable по имени без расширения, asset-паки —
    по пути), поэтому там WebP без ограничений.

Usage:
    python3 tools/optimize_art.py [--dry-run] [--platform ios|android|both]
"""
import argparse
import io
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

CHAR_MAX_H = 768      # запас ×1.4 к самому большому рендеру спрайта (~560px на 3x)
JPEG_QUALITY = 82
WEBP_QUALITY = 82
PNGQUANT_QUALITY = "60-92"

IOS_CATALOGS = [
    ROOT / "ios/Modules/GameContent/Resources/Assets.xcassets",
    *sorted((ROOT / "ios/Modules/GameContent/ChapterResources").glob("*.xcassets")),
]
ANDROID_DIRS = [
    ROOT / "android/app/src/main/res/drawable",
    *sorted(p / "src/main/assets" for p in (ROOT / "android").glob("chapter_*")),
]


def kind_of(name: str) -> str:
    """char / scene / other — по префиксу имени ассета."""
    stem = Path(name).stem
    return "char" if stem.startswith("char_") else "scene" if stem.startswith("scene_") else "other"


def downscale_char(im: Image.Image) -> Image.Image:
    if im.height <= CHAR_MAX_H:
        return im
    return im.resize((round(im.width * CHAR_MAX_H / im.height), CHAR_MAX_H), Image.LANCZOS)


def quantize_png(im: Image.Image, dst: Path) -> None:
    """RGBA → PNG-8 с попиксельной альфой. pngquant умеет это, PIL — нет."""
    raw = io.BytesIO()
    im.save(raw, "PNG")
    for args in ([f"--quality={PNGQUANT_QUALITY}"], []):   # без границ качества — если строгие не прошли
        r = subprocess.run(
            ["pngquant", "--force", "--strip", "--speed", "1", *args, "--output", str(dst), "-"],
            input=raw.getvalue(), capture_output=True,
        )
        if r.returncode == 0:
            return
    dst.write_bytes(raw.getvalue())   # pngquant не справился — кладём как есть, не теряем ассет


# --- iOS -------------------------------------------------------------------

def ios_imagesets():
    for cat in IOS_CATALOGS:
        for iset in sorted(cat.glob("*.imageset")):
            meta = iset / "Contents.json"
            if not meta.exists():
                continue
            data = json.loads(meta.read_text())
            images = [i for i in data.get("images", []) if i.get("filename")]
            if len(images) == 1:
                yield iset, meta, data, images[0]


def process_ios(iset: Path, meta: Path, data: dict, entry: dict, dry: bool):
    src = iset / entry["filename"]
    if not src.exists():
        return None
    before = src.stat().st_size
    kind = kind_of(src.name)

    if kind == "char":
        im = Image.open(src)
        if im.height <= CHAR_MAX_H and src.suffix == ".png":
            return None                                    # уже обработан
        im = downscale_char(im.convert("RGBA"))
        if dry:
            with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
                quantize_png(im, Path(tmp.name))
                return before, Path(tmp.name).stat().st_size
        quantize_png(im, src)
        return before, src.stat().st_size

    if kind == "scene":
        if src.suffix == ".jpg":
            return None                                    # уже обработан
        im = Image.open(src)
        if im.mode == "RGBA" or "transparency" in im.info:
            return None                                    # прозрачная «сцена» — JPEG не подходит
        dst = src.with_suffix(".jpg")
        im.convert("RGB").save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        after = dst.stat().st_size
        if dry:
            dst.unlink()
        else:
            src.unlink()
            entry["filename"] = dst.name
            meta.write_text(json.dumps(data, indent=2) + "\n")
        return before, after
    return None


# --- Android ---------------------------------------------------------------

def process_android(src: Path, dry: bool):
    kind = kind_of(src.name)
    if kind == "other" or src.suffix == ".webp":
        return None
    before = src.stat().st_size
    im = Image.open(src)
    if kind == "char":
        im = downscale_char(im.convert("RGBA"))
    else:
        im = im.convert("RGB")
    dst = src.with_suffix(".webp")
    im.save(dst, "WEBP", quality=WEBP_QUALITY, method=6)
    after = dst.stat().st_size
    if dry:
        dst.unlink()
    else:
        src.unlink()
    return before, after


# --- main ------------------------------------------------------------------

def run(platform: str, dry: bool):
    jobs = []
    if platform in ("ios", "both"):
        jobs += [("iOS", lambda a=a: process_ios(*a, dry)) for a in ios_imagesets()]
    if platform in ("android", "both"):
        for d in ANDROID_DIRS:
            if d.exists():
                jobs += [("Android", lambda p=p: process_android(p, dry))
                         for p in sorted(d.iterdir()) if p.suffix in (".png", ".jpg")]

    totals = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for (tag, _), res in zip(jobs, pool.map(lambda j: j[1](), jobs)):
            if res is None:
                continue
            b, a = res
            t = totals.setdefault(tag, [0, 0, 0])
            t[0] += b
            t[1] += a
            t[2] += 1

    print("dry-run (ничего не записано)\n" if dry else "")
    for tag, (b, a, n) in sorted(totals.items()):
        print(f"{tag}: {n} файлов  {b/1e6:.1f} МБ → {a/1e6:.1f} МБ  (×{b/max(a,1):.2f}, минус {(b-a)/1e6:.1f} МБ)")
    if not totals:
        print("нечего оптимизировать — всё уже обработано")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--platform", choices=["ios", "android", "both"], default="both")
    a = ap.parse_args()
    if not subprocess.run(["which", "pngquant"], capture_output=True).returncode == 0:
        sys.exit("нужен pngquant: brew install pngquant")
    run(a.platform, a.dry_run)
