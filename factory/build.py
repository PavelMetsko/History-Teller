#!/usr/bin/env python3
"""Сборка персонажей: JSON-рецепты → SVG → PNG (headless Chrome) → WebP во всех позах.

Все позы всех персонажей рисуются одним SVG-листом и одним запуском Chrome (запуск ~15 с),
потом лист режется на кадры 512×768. Рост и линия пола — как в tools/normalize_sprites.py:
базовая поза масштабируется до TARGET_H кадра, остальные позы тем же коэффициентом.

Usage:
    /usr/bin/python3 factory/build.py            собрать все рецепты factory/recipes в Content/art_v2 + лист factory/out/sheet.png
    /usr/bin/python3 factory/build.py sobieski   только указанных
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import rig  # noqa: E402
import catalog  # noqa: E402

OUT_ART = ROOT / "Content" / "art_v2"
OUT = HERE / "out"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H = 512, 768
SCALE = 2                      # рендер в 2× и даунскейл — ровнее контур
TARGET_H = 0.77                # из normalize_sprites.py
FLOOR = H - 16                 # линия пола


def render_sheet(recipes):
    cols, rows = len(rig.POSE_ORDER), len(recipes)
    cells = []
    for r, rec in enumerate(recipes):
        for c, pose in enumerate(rig.POSE_ORDER):
            fid = f"f{r}{c}"
            cells.append(f'<defs>{rig.defs(fid)}<clipPath id="c{fid}"><rect width="{W}" height="{H}"/></clipPath></defs>'
                         f'<g transform="translate({c * W},{r * H})"><g clip-path="url(#c{fid})">'
                         f'{rig.render(rec, pose, fid)}</g></g>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{cols * W}" height="{rows * H}" '
           f'viewBox="0 0 {cols * W} {rows * H}">{"".join(cells)}</svg>')
    with tempfile.TemporaryDirectory() as td:
        src, png = Path(td) / "sheet.svg", Path(td) / "sheet.png"
        src.write_text(svg)
        (OUT / "stage0.svg").write_text(svg)
        # свой профиль: иначе headless цепляется к открытому Chrome пользователя и может зависнуть
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                        f"--user-data-dir={td}/profile",
                        f"--force-device-scale-factor={SCALE}", f"--window-size={cols * W},{rows * H}",
                        "--default-background-color=00000000", f"--screenshot={png}", src.as_uri()],
                       check=True, capture_output=True, timeout=180)
        sheet = Image.open(png).convert("RGBA")
    tiles = {}
    for r, rec in enumerate(recipes):
        for c, pose in enumerate(rig.POSE_ORDER):
            box = (c * W * SCALE, r * H * SCALE, (c + 1) * W * SCALE, (r + 1) * H * SCALE)
            tiles[rec["id"], pose] = sheet.crop(box).resize((W, H), Image.LANCZOS)
    return tiles


def bbox(im):
    a = np.array(im)[..., 3] > 40
    ys, xs = np.where(a)
    return xs.min(), ys.min(), xs.max(), ys.max()


def normalize(poses: dict) -> dict:
    """{поза: RGBA 512×768} → те же позы с ростом TARGET_H и линией пола FLOOR."""
    x0, y0, x1, y1 = bbox(poses["base"])
    k = TARGET_H * H / (y1 - y0)
    out = {}
    for pose in rig.POSE_ORDER:
        im = poses[pose].resize((round(W * k), round(H * k)), Image.LANCZOS)
        px0, py0, px1, py1 = bbox(im)
        bx0, _, bx1, _ = bbox(poses["base"].resize(im.size, Image.LANCZOS))
        dx = W // 2 - (bx0 + bx1) // 2          # центр по базовой позе — позы не «прыгают»
        dy = FLOOR - py1                        # каждая поза стоит на полу
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        canvas.paste(im, (dx, dy), im)
        out[pose] = canvas
    return out


def contact(final, refs):
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
    tw, th = 256, 384
    cols = 1 + len(rig.POSE_ORDER)
    sheet = Image.new("RGBA", (tw * cols, (th + 40) * len(final) + 40), (232, 227, 218, 255))
    d = ImageDraw.Draw(sheet)
    small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 15)
    for c, lab in enumerate(["старый стиль, для сравнения"] + rig.POSE_ORDER):
        d.text((c * tw + 10, 8), lab, fill=(60, 40, 30), font=font if c else small)
    for r, (rid, poses) in enumerate(final.items()):
        y = 40 + r * (th + 40)
        old = Image.open(ROOT / "Content" / "art" / f"char_{refs[rid]}.webp").convert("RGBA").resize((tw, th), Image.LANCZOS)
        sheet.alpha_composite(old, (0, y))
        d.text((10, y + th + 6), f"char_{refs[rid]}", fill=(110, 90, 80), font=font)
        for c, pose in enumerate(rig.POSE_ORDER):
            sheet.alpha_composite(poses[pose].resize((tw, th), Image.LANCZOS), ((c + 1) * tw, y))
        d.text((tw + 10, y + th + 6), rid, fill=(60, 40, 30), font=font)
    return sheet


def save_sprites(rid: str, poses: dict) -> list[Path]:
    OUT_ART.mkdir(parents=True, exist_ok=True)
    paths = []
    for pose, im in poses.items():
        path = OUT_ART / (f"char_{rid}" + ("" if pose == "base" else f"_{pose}") + ".webp")
        im.save(path, "WEBP", quality=92, method=6)
        paths.append(path)
    return paths


def main():
    OUT.mkdir(exist_ok=True)
    recipes = catalog.load_all()
    if len(sys.argv) > 1:
        recipes = [r for r in recipes if r["id"] in sys.argv[1:]]
    tiles = render_sheet([catalog.build(r) for r in recipes])
    final = {}
    for rec in recipes:
        rid = rec["id"]
        final[rid] = normalize({p: tiles[rid, p] for p in rig.POSE_ORDER})
        save_sprites(rid, final[rid])
    contact(final, {r["id"]: r.get("old_ref", "hetman") for r in recipes}).save(OUT / "sheet.png")
    print("ok:", ", ".join(final), "->", OUT_ART.relative_to(ROOT), "+", (OUT / "sheet.png").relative_to(ROOT))


if __name__ == "__main__":
    main()
