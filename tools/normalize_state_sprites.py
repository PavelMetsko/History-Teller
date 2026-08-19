#!/usr/bin/env python3
"""Привести варианты состояний персонажа к масштабу базового спрайта.

Проблема: базовый спрайт рисует фигуру ~590 px высотой на холсте 768, а варианты `_dead`,
`_defeated`, `_plot`, `_triumph` — на весь холст (~750 px). Доска вписывает картинку по высоте
холста, поэтому при смене состояния персонаж «вырастает» на четверть (Помпей на Фарсале).

Лечим данные, а не код: фигуру варианта масштабируем так, чтобы её высота совпала с базовой,
центрируем по горизонтали и ставим на ту же линию пола (отступ снизу как у базового).
"""
from __future__ import annotations
import sys, glob, os
import numpy as np
from PIL import Image

ART = os.path.join(os.path.dirname(__file__), "..", "Content", "art")
CANVAS = (512, 768)

def bbox(im: Image.Image):
    a = np.array(im.convert("RGBA"))[:, :, 3]
    ys, xs = np.nonzero(a > 16)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())

def head_width(im: Image.Image, bb) -> int:
    """Ширина головы: самая широкая строка в верхних 45 % фигуры (у чиби это щёки).
    Рост у стоящего и сидящего разный, а голова одна — по ней и ведём масштаб."""
    a = np.array(im.convert("RGBA"))[:, :, 3] > 16
    h = bb[3] - bb[1] + 1
    top = a[bb[1]: bb[1] + int(h * 0.45)]
    return int(top.sum(1).max())

def fit(variant: str, base: str) -> bool:
    bim = Image.open(base).convert("RGBA"); vim = Image.open(variant).convert("RGBA")
    bb, vb = bbox(bim), bbox(vim)
    if not bb or not vb:
        return False
    bh, vh = head_width(bim, bb), head_width(vim, vb)
    base_floor = CANVAS[1] - 1 - bb[3]                 # отступ фигуры от низа в базовом
    if abs(vh - bh) <= 10:                              # уже в масштабе — не трогаем
        return False
    fig = vim.crop((vb[0], vb[1], vb[2] + 1, vb[3] + 1))
    s = bh / vh
    nw, nh = max(1, round(fig.width * s)), max(1, round(fig.height * s))
    fig = fig.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    x = (CANVAS[0] - nw) // 2
    y = CANVAS[1] - base_floor - nh
    out.paste(fig, (x, max(0, y)), fig)
    out.save(variant, "WEBP", quality=92, method=6)
    return True

if __name__ == "__main__":
    only = set(sys.argv[1:])
    n = 0
    for v in sorted(glob.glob(os.path.join(ART, "char_*_*.webp"))):
        name = os.path.basename(v)[5:-5]
        for suf in ("_dead", "_defeated", "_plot", "_triumph"):
            if name.endswith(suf):
                cid = name[: -len(suf)]
                if only and cid not in only:
                    break
                base = os.path.join(ART, f"char_{cid}.webp")
                if os.path.exists(base) and fit(v, base):
                    n += 1; print("  ", os.path.basename(v))
                break
    print(f"приведено к базовому масштабу: {n}")
