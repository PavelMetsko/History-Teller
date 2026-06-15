#!/usr/bin/env python3
"""Генерация эмоций портретов из базовых SVG: char_X_love.svg, char_X_plot.svg.

Подменяет глаза/рот точечными заменами строк. Если строка не найдена —
падает с ошибкой (значит, базовый портрет изменился и таблицу нужно обновить).

Usage: python3 tools/make_emotions.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Art" / "src"


def love_eyes(y):
    return (f'<path d="M 100 {y} Q 108 {y-7} 116 {y} M 140 {y} Q 148 {y-7} 156 {y}" '
            f'fill="none" stroke="#2b2419" stroke-width="5" stroke-linecap="round"/>\n'
            f'  <circle cx="97" cy="{y+22}" r="8" fill="#d98a7a" opacity="0.5"/>\n'
            f'  <circle cx="159" cy="{y+22}" r="8" fill="#d98a7a" opacity="0.5"/>')


def plot_eyes(y):
    return (f'<path d="M 100 {y} L 116 {y} M 140 {y} L 156 {y}" '
            f'fill="none" stroke="#2b2419" stroke-width="6" stroke-linecap="round"/>')


LOVE_MOUTH = ('<path d="M 112 140 Q 128 154 144 140" fill="none" '
              'stroke="#2b2419" stroke-width="5" stroke-linecap="round"/>')
PLOT_MOUTH = ('<path d="M 112 146 Q 134 148 146 138" fill="none" '
              'stroke="#2b2419" stroke-width="5" stroke-linecap="round"/>')

# (файл, [строки глаз], рот, y глаз, особые рты для эмоций)
CHARS = {
    "char_caesar": dict(
        eyes=['<circle cx="108" cy="104" r="6" fill="#2b2419"/>',
              '<circle cx="148" cy="104" r="6" fill="#2b2419"/>'],
        mouth='<path d="M 110 142 Q 128 146 146 142" fill="none" stroke="#2b2419" stroke-width="5" stroke-linecap="round"/>',
        y=104),
    "char_brutus": dict(
        eyes=['<circle cx="108" cy="106" r="6" fill="#2b2419"/>',
              '<circle cx="148" cy="106" r="6" fill="#2b2419"/>'],
        mouth='<path d="M 114 144 Q 128 140 142 144" fill="none" stroke="#2b2419" stroke-width="5" stroke-linecap="round"/>',
        y=106),
    "char_cassius": dict(
        eyes=['<path d="M 104 106 L 116 106 M 140 106 L 152 106" fill="none" stroke="#2b2419" stroke-width="6" stroke-linecap="round"/>'],
        mouth='<path d="M 112 146 Q 128 142 144 146" fill="none" stroke="#2b2419" stroke-width="5" stroke-linecap="round"/>',
        y=106),
    "char_cleopatra": dict(
        eyes=['<circle cx="108" cy="108" r="5" fill="#2b2419"/>',
              '<circle cx="148" cy="108" r="5" fill="#2b2419"/>'],
        mouth='<path d="M 114 142 Q 128 150 142 142 Q 128 140 114 142 Z" fill="#a8443e" stroke="#2b2419" stroke-width="4"/>',
        y=108,
        love_mouth='<path d="M 112 140 Q 128 154 144 140 Q 128 147 112 140 Z" fill="#a8443e" stroke="#2b2419" stroke-width="4"/>',
        plot_mouth='<path d="M 114 144 Q 134 148 144 138 Q 128 142 114 144 Z" fill="#a8443e" stroke="#2b2419" stroke-width="4"/>'),
    "char_antony": dict(
        eyes=['<circle cx="108" cy="104" r="6" fill="#2b2419"/>',
              '<circle cx="148" cy="104" r="6" fill="#2b2419"/>'],
        mouth='<path d="M 110 140 Q 132 150 148 138" fill="none" stroke="#2b2419" stroke-width="5" stroke-linecap="round"/>',
        y=104),
}


def patch(svg, old, new, name, what):
    if old not in svg:
        sys.exit(f"!! {name}: не найден {what} — обновите таблицу в make_emotions.py")
    return svg.replace(old, new, 1)


def main():
    for name, d in CHARS.items():
        base = (SRC / f"{name}.svg").read_text(encoding="utf-8")

        for emo, eyes_fn, mouth_default, mouth_key in (
            ("love", love_eyes, LOVE_MOUTH, "love_mouth"),
            ("plot", plot_eyes, PLOT_MOUTH, "plot_mouth"),
        ):
            svg = base
            # глаза: первую строку заменяем вариантом, остальные убираем
            svg = patch(svg, d["eyes"][0], eyes_fn(d["y"]), name, "глаза")
            for extra in d["eyes"][1:]:
                svg = patch(svg, extra, "", name, "глаза-2")
            svg = patch(svg, d["mouth"], d.get(mouth_key, mouth_default), name, "рот")
            out = SRC / f"{name}_{emo}.svg"
            out.write_text(svg, encoding="utf-8")
            print(f"{out.name}")


if __name__ == "__main__":
    main()
