#!/usr/bin/env python3
"""Привести всех персонажей к единому росту и общей линии пола.

Зачем: спрайты генерятся по одному, и каждый занимал в кадре сколько получится — замер по
417 файлам показал разброс высоты фигуры от 59 % до 99 % кадра. На доске персонажи стоят рядом,
кадры одинаковые, поэтому разница читается как «этот коротышка, а этот великан» — и это не
художественный замысел, а шум генерации.

Что делает: находит рамку самой фигуры (одинокие точки-артефакты игнорируются), масштабирует её
до TARGET_H кадра и ставит на общую линию пола BASE_MARGIN. Позы (dead/defeated/plot/triumph)
масштабируются ТЕМ ЖЕ коэффициентом, что и базовый спрайт: у лежащего мёртвого рамка ниже, и
нормализуй его отдельно — он раздулся бы во весь кадр.

Считает из исходников Art/source (1024×1536) — так webp не пересжимается дважды.

Usage:
    python3 tools/normalize_sprites.py --dry-run     показать, кого и насколько подвинет
    python3 tools/normalize_sprites.py               применить
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "Content" / "art"
SRC = ROOT / "Art" / "source"
BATCH = SRC / "batch"

OUT_SIZE = (512, 768)
TARGET_H = 0.77          # доля кадра под фигуру — медиана исторически сложившегося набора
BASE_MARGIN = 16 / 768   # линия пола: столько кадра остаётся под ступнями
POSES = ("dead", "defeated", "plot", "triumph")


def cut_magenta(img: Image.Image) -> Image.Image:
    a = np.array(img.convert("RGBA")).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bg = (r - g > 40) & (b - g > 22) & (r > 120)
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    alpha = np.array(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.8)))
    alpha = np.where(alpha < 40, 0, np.where(alpha > 200, 255, alpha)).astype(np.uint8)
    out = a.copy()
    out[:, :, 3] = alpha
    return Image.fromarray(out.astype(np.uint8))


def _main_span(occupied: np.ndarray, size: int) -> tuple[int, int]:
    """Из занятых строк/столбцов оставить сплошной массив самой фигуры.

    У части картинок вдоль верхней кромки идёт бледная полоска-артефакт: она проходит порог
    по числу пикселей, рамка растягивается до края, и фигура после масштабирования выходит
    мельче всех (так вышло с архипиратом — 57 % вместо 77 %). Поэтому режем занятые полосы на
    группы по разрывам и берём ту, где больше всего пикселей, добирая соседние группы,
    отстоящие меньше чем на 6 % кадра, — чтобы не отрезать поднятое копьё или высокий убор.
    """
    idx = np.nonzero(occupied)[0]
    if not len(idx):
        return (0, size)
    gap = max(2, int(size * 0.02))
    groups, start = [], idx[0]
    for a, b in zip(idx, idx[1:]):
        if b - a > gap:
            groups.append((start, a))
            start = b
    groups.append((start, idx[-1]))

    weight = [occupied[s:e + 1].sum() for s, e in groups]
    lo, hi = groups[int(np.argmax(weight))]
    reach = int(size * 0.06)
    for s, e in groups:
        if s < lo and lo - e <= reach:
            lo = s
        if e > hi and s - hi <= reach:
            hi = e
    return (int(lo), int(hi) + 1)


def figure_bbox(img: Image.Image) -> tuple[int, int, int, int]:
    """Рамка фигуры: порог по числу пикселей в строке/столбце плюс отсев оторванных полосок."""
    a = np.array(img.convert("RGBA"))[:, :, 3] > 200
    min_run = max(4, img.width // 64)
    y0, y1 = _main_span(a.sum(axis=1) >= min_run, img.height)
    x0, x1 = _main_span(a.sum(axis=0) >= min_run, img.width)
    if y1 <= y0 or x1 <= x0:
        return (0, 0, img.width, img.height)
    return (x0, y0, x1, y1)


def place(img: Image.Image, scale: float) -> Image.Image:
    """Вписать фигуру в целевой кадр: по центру, ступни на общей линии пола."""
    img = img.convert("RGBA").crop(figure_bbox(img))
    w = max(1, int(round(img.width * scale)))
    h = max(1, int(round(img.height * scale)))
    img = img.resize((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", OUT_SIZE, (0, 0, 0, 0))
    x = (OUT_SIZE[0] - w) // 2
    y = OUT_SIZE[1] - int(round(BASE_MARGIN * OUT_SIZE[1])) - h
    canvas.paste(img, (x, y), img)
    return canvas


def source_for(name: str) -> tuple[Path, bool] | None:
    """(файл, нужен ли вырез магенты). Новый арт лежит сырым в Art/source/batch."""
    p = SRC / f"{name}.png"
    if p.exists():
        return p, False
    p = BATCH / f"{name}_raw.png"
    if p.exists():
        return p, True
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="", help="имена через запятую (перечинить точечно)")
    a = ap.parse_args()

    only = {x for x in a.only.split(",") if x}
    bases = sorted(p.stem for p in ART.glob("char_*.webp")
                   if not re.search(r"_(%s)$" % "|".join(POSES), p.stem)
                   and (not only or p.stem in only))
    changed = worst = 0
    missing: list[str] = []

    for base in bases:
        src = source_for(base)
        if not src:
            missing.append(base)
            continue
        img = Image.open(src[0])
        if src[1]:
            img = cut_magenta(img)
        x0, y0, x1, y1 = figure_bbox(img)
        fig_h = y1 - y0
        scale = (TARGET_H * OUT_SIZE[1]) / fig_h

        было = np.array(Image.open(ART / f"{base}.webp").convert("RGBA"))[:, :, 3] > 200
        rows = np.nonzero(было.sum(axis=1) >= 8)[0]
        prev = (rows[-1] - rows[0] + 1) / OUT_SIZE[1] * 100 if len(rows) else 0
        if abs(prev - TARGET_H * 100) > 1.5:
            changed += 1
            worst = max(worst, abs(prev - TARGET_H * 100))
            print(f"  {base:26} {prev:5.1f}% → {TARGET_H*100:.0f}%")

        if not a.dry_run:
            place(img, scale).save(ART / f"{base}.webp", "WEBP", quality=92, method=6)
            # позы — тем же коэффициентом, иначе лежащий «мёртвый» растянется во весь рост
            for pose in POSES:
                name = f"{base}_{pose}"
                if not (ART / f"{name}.webp").exists():
                    continue
                psrc = source_for(name)
                if not psrc:
                    continue
                pimg = Image.open(psrc[0])
                if psrc[1]:
                    pimg = cut_magenta(pimg)
                place(pimg, scale).save(ART / f"{name}.webp", "WEBP", quality=92, method=6)

    print(f"\nбазовых спрайтов: {len(bases)}, выбивались из нормы: {changed} "
          f"(максимальное отклонение {worst:.0f} п.п.)")
    if missing:
        print(f"без исходника ({len(missing)}): {', '.join(missing[:8])}")


if __name__ == "__main__":
    main()
