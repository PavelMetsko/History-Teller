#!/usr/bin/env python3
"""Пакетная генерация арта прямо в Content/art (персонажи и сцены) через Nano-Banana.

Отличие от tools/genart.py: тот кладёт PNG в Assets.xcassets и res/drawable — раскладку
времён вшитого арта. Сейчас источник правды один — `Content/art/*.webp`, откуда контент
уезжает в облако через publish_content.py. Здесь и формат сразу целевой:
    персонаж — 512×768 RGBA (магента вырезана в прозрачность)
    сцена    — 1024×1024 RGB

Стиль держится референсом: в запрос кладётся уже существующая картинка того же типа,
и модель просят повторить её манеру. Готовые файлы не перегенерируются (идемпотентно),
так что скрипт можно гонять повторно после сбоев и докидывания кредитов.

Usage:
    python3 tools/genart_batch.py --list                 что ещё не нарисовано
    python3 tools/genart_batch.py --only sabines         только персонажи/сцены уровня
    python3 tools/genart_batch.py --kind scene           только сцены
    python3 tools/genart_batch.py --force char_brennus   перерисовать конкретный файл
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize_sprites import TARGET_H, figure_bbox, place   # общее правило роста и линии пола

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "Content" / "art"
RAW = ROOT / "Art" / "source" / "batch"
MODEL = "gemini-2.5-flash-image"

CHAR_SIZE = (512, 768)
SCENE_SIZE = (1024, 1024)

# Референсы стиля: берём уже принятый арт того же типа.
REF_CHAR = ART / "char_cicero.webp"
REF_SCENE = ART / "scene_forum.webp"

STYLE_CHAR = (
    "Reproduce EXACTLY the art style of the reference image: a small chibi-proportioned "
    "storybook figure with a big head and short body, thick dark-brown ink outline, flat "
    "warm muted paper-palette colours, soft simple shading, friendly readable face. "
    "Full body from head to feet, standing in a neutral pose facing the viewer, arms relaxed. "
    "Character: {desc}. "
    "Background must be PURE MAGENTA #FF00FF and completely empty — no shadow, no ground, "
    "no frame, no text, no props lying around. Vertical 2:3 framing, small margin around the figure."
)

STYLE_SCENE = (
    "Reproduce EXACTLY the art style of the reference image: a painted storybook background, "
    "warm muted paper palette, soft daylight, thick-ink illustrated look, slightly stylised shapes. "
    "Scene: {desc}. "
    "IMPORTANT: no people, no characters, no animals in the foreground, no text, no frame, no UI. "
    "Square 1:1 composition with an empty, uncluttered middle ground where characters will later stand."
)


def api_key() -> str:
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        sys.exit("нет GEMINI_API_KEY в окружении")
    return k


def generate(prompt: str, ref: Path) -> Image.Image:
    """Один запрос к модели. Возвращает картинку; кидает наверх понятную ошибку."""
    buf = BytesIO()
    Image.open(ref).convert("RGB").save(buf, "PNG")
    body = json.dumps({
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/png",
                             "data": base64.b64encode(buf.getvalue()).decode()}}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key()}"

    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=240))
            parts = r["candidates"][0]["content"]["parts"]
            for p in parts:
                d = p.get("inlineData") or p.get("inline_data")
                if d:
                    return Image.open(BytesIO(base64.b64decode(d["data"])))
            raise RuntimeError("ответ без картинки: " + str([p.get("text") for p in parts])[:160])
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:300]
            if e.code == 429:
                raise RuntimeError(f"кредиты кончились или лимит: {detail}") from None
            last = RuntimeError(f"HTTP {e.code}: {detail}")
        except Exception as e:                                  # noqa: BLE001 — ретраим что угодно
            last = e
    raise last


def cut_magenta(img: Image.Image) -> Image.Image:
    """Магента-фон → alpha=0. Красное/золото/кожу не трогает (у них b≈g)."""
    a = np.array(img.convert("RGBA")).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bg = (r - g > 40) & (b - g > 22) & (r > 120)
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    alpha = np.array(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.8)))
    alpha = np.where(alpha < 40, 0, np.where(alpha > 200, 255, alpha)).astype(np.uint8)
    out = a.copy()
    out[:, :, 3] = alpha
    # заодно гасим магентовую бахрому по краю силуэта
    edge = (alpha > 0) & (alpha < 255)
    out[:, :, 0] = np.where(edge & (r - g > 40), g, out[:, :, 0])
    return Image.fromarray(out.astype(np.uint8))


def fit(img: Image.Image, size: tuple[int, int], alpha: bool) -> Image.Image:
    """Вписать в целевой кадр. Для персонажей — общий рост и общая линия пола.

    Раньше спрайт растягивался «на сколько влезет», и рост фигуры гулял от 59 % до 99 % кадра:
    на доске персонажи стоят рядом, и это читалось как случайные коротышки и великаны.
    Правило нормализации теперь одно на весь арт и живёт в tools/normalize_sprites.py.
    """
    if not alpha:
        return img.convert("RGB").resize(size, Image.LANCZOS)
    fig_h = figure_bbox(img)[3] - figure_bbox(img)[1]
    return place(img, (TARGET_H * size[1]) / max(1, fig_h))


# Ниже этой доли прозрачных пикселей считаем, что модель нарисовала фон не магентой
# (тогда вырез не сработал и вместо спрайта получается картинка с подложкой).
MIN_TRANSPARENT = 0.25


def render(name: str, desc: str) -> str:
    kind = "char" if name.startswith("char_") else "scene"
    ref = REF_CHAR if kind == "char" else REF_SCENE
    base = (STYLE_CHAR if kind == "char" else STYLE_SCENE).format(desc=desc)
    RAW.mkdir(parents=True, exist_ok=True)

    if kind == "scene":
        img = fit(generate(base, ref), SCENE_SIZE, alpha=False)
        img.save(ART / f"{name}.webp", "WEBP", quality=88, method=6)
        return f"{name}: фон готов"

    best, best_frac = None, -1.0
    for attempt in range(3):
        prompt = base if attempt == 0 else (
            base + " CRITICAL: the entire background must be one flat solid magenta colour "
                   "RGB(255,0,255) with absolutely nothing else — no dark backdrop, no scenery, "
                   "no vignette, no gradient.")
        raw = generate(prompt, ref)
        cut = fit(cut_magenta(raw), CHAR_SIZE, alpha=True)
        frac = float((np.array(cut)[:, :, 3] == 0).mean())
        if frac > best_frac:
            best, best_frac = cut, frac
            raw.save(RAW / f"{name}_raw.png")
        if frac >= MIN_TRANSPARENT:
            break

    best.save(ART / f"{name}.webp", "WEBP", quality=92, method=6)
    warn = "" if best_frac >= MIN_TRANSPARENT else "  ← фон не вырезался, глянь глазами"
    return f"{name}: прозрачно {best_frac*100:.0f}%{warn}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="показать, чего не хватает")
    ap.add_argument("--only", default="", help="id уровня из art_prompts.json")
    ap.add_argument("--kind", choices=["char", "scene"], default="")
    ap.add_argument("--force", default="", help="перерисовать эти имена через запятую")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--recrop", action="store_true",
                    help="пересобрать webp из сохранённых Art/source/batch без запросов к модели")
    a = ap.parse_args()

    if a.recrop:
        n = 0
        for raw in sorted(RAW.glob("char_*_raw.png")):
            name = raw.name[:-len("_raw.png")]
            img = fit(cut_magenta(Image.open(raw)), CHAR_SIZE, alpha=True)
            img.save(ART / f"{name}.webp", "WEBP", quality=92, method=6)
            n += 1
        print(f"пересобрано {n} спрайтов из исходников")
        return

    prompts = json.loads((ROOT / "tools" / "art_prompts.json").read_text(encoding="utf-8"))
    force = {x for x in a.force.split(",") if x}

    todo = []
    for level, items in prompts.items():
        if level.startswith("_"):          # служебные ключи каталога (комментарий)
            continue
        if a.only and level != a.only:
            continue
        for name, desc in items.items():
            if a.kind and not name.startswith(a.kind + "_"):
                continue
            if (ART / f"{name}.webp").exists() and name not in force:
                continue
            todo.append((name, desc))

    if not todo:
        print("всё нарисовано")
        return
    if a.list:
        print(f"не хватает {len(todo)}:")
        for n, _ in todo:
            print("  " + n)
        return

    print(f"генерю {len(todo)} картинок в {a.jobs} потока")
    failed = []
    with ThreadPoolExecutor(max_workers=a.jobs) as pool:
        futures = {pool.submit(render, n, d): n for n, d in todo}
        for f in futures:
            n = futures[f]
            try:
                print("  " + f.result(), flush=True)
            except Exception as e:                              # noqa: BLE001
                failed.append(n)
                print(f"  !! {n}: {e}", flush=True)
    if failed:
        print(f"\nне вышло ({len(failed)}): {', '.join(failed)} — перезапусти, готовое не тронется")


if __name__ == "__main__":
    main()
