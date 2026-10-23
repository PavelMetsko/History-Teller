#!/usr/bin/env python3
"""Сравнить новый спрайт со старым: наложение контуров + замеры.

    /usr/bin/python3 factory/compare.py caesar      → factory/out/compare_caesar.png

Слева — старый спрайт бледно, его контур красным, контур нового синим; дальше старый и новый
рядом. В консоль: совпадение силуэтов (IoU) и рамки глаз (по тёмным пикселям внутри лица).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
rid = sys.argv[1] if len(sys.argv) > 1 else "caesar"
old_im = Image.open(ROOT / f"Content/art/char_{rid}.webp").convert("RGBA")
new_im = Image.open(ROOT / f"Content/art_v2/char_{rid}.webp").convert("RGBA")
a, b = np.array(old_im).astype(int), np.array(new_im).astype(int)
A, B = a[..., 3] > 128, b[..., 3] > 128


def edge(m, w=2):
    inner = m.copy()
    inner[1:] &= m[:-1]; inner[:-1] &= m[1:]; inner[:, 1:] &= m[:, :-1]; inner[:, :-1] &= m[:, 1:]
    e = m & ~inner
    for _ in range(w):
        e = e | np.roll(e, 1, 0) | np.roll(e, 1, 1)
    return e


out = np.full(a.shape, 235)
out[..., 3] = 255
out[..., :3] = np.where(A[..., None], a[..., :3] * 0.5 + 235 * 0.5, out[..., :3])
out[edge(A)] = [220, 30, 30, 255]
out[edge(B)] = [30, 60, 220, 255]
sheet = Image.new("RGBA", (512 * 3, 768), (235, 230, 220, 255))
sheet.alpha_composite(Image.fromarray(out.astype(np.uint8)), (0, 0))
sheet.alpha_composite(old_im, (512, 0))
sheet.alpha_composite(new_im, (1024, 0))
dst = ROOT / f"factory/out/compare_{rid}.png"
sheet.crop((0, 130, 1536, 768)).save(dst)
print("IoU силуэтов:", round((A & B).sum() / (A | B).sum(), 3))
for name, x in (("старый", a), ("новый", b)):
    dark = (x[..., 3] > 128) & (x[..., :3].sum(-1) < 150)
    for x0, x1 in ((140, 250), (262, 370)):
        ys, xs = np.where(dark[280:440, x0:x1])
        if len(xs):
            print(f"{name}: глаз x {x0 + xs.min()}–{x0 + xs.max()}, y {280 + ys.min()}–{280 + ys.max()}")
print("->", dst.relative_to(ROOT))
