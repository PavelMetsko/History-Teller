# -*- coding: utf-8 -*-
"""Собирает витринный скриншот из сырого снимка симулятора.

Повторяет оформление релиза 1.0: бордовый градиент, тонкая золотая рамка,
золотой заголовок с подчёркиванием и «устройство», уходящее за нижний край.
"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SERIF = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
GOLD = (232, 192, 106)
PLUM = (59, 36, 48)


def gradient(size):
    """Бордовый фон: светлее вверху по центру, темнее к краям."""
    w, h = size
    base = Image.new("RGB", (64, 64))
    px = base.load()
    for y in range(64):
        for x in range(64):
            dx, dy = (x - 32) / 32.0, (y - 6) / 58.0
            d = min(1.0, (dx * dx * 0.55 + dy * dy) ** 0.5)
            px[x, y] = (
                int(138 - 92 * d),
                int(34 - 18 * d),
                int(38 - 17 * d),
            )
    return base.resize(size, Image.BICUBIC)


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    out = im.convert("RGBA")
    out.putalpha(m)
    return out


def device(shot, target_w, radius=58, bezel=26):
    """Кладёт снимок в плашку-«устройство» с тёмной рамкой.

    Островок рисовать не нужно — он уже есть на сыром кадре симулятора.
    """
    s = shot.convert("RGB")
    s = s.resize((target_w - 2 * bezel, round(s.height * (target_w - 2 * bezel) / s.width)), Image.LANCZOS)
    body = Image.new("RGBA", (target_w, s.height + 2 * bezel), PLUM + (255,))
    body = rounded(body, radius)
    body.alpha_composite(rounded(s, radius - 14), (bezel, bezel))
    return body


def compose(shot_path, caption, out_path, size=(2778, 1284)):
    W, H = size
    bg = gradient(size).convert("RGBA")
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle([14, 14, W - 15, H - 15], 18, outline=GOLD + (110,), width=3)

    # заголовок ужимаем, если длинный, чтобы не лез в золотую рамку
    size = round(H * 0.052)
    while size > 20:
        font = ImageFont.truetype(SERIF, size)
        tw = d.textlength(caption, font=font)
        if tw <= W * 0.80:
            break
        size -= 2
    ty = round(H * 0.030)
    d.text(((W - tw) / 2, ty), caption, font=font, fill=GOLD)
    uy = ty + round(H * 0.075)
    d.line([(W / 2 - W * 0.028, uy), (W / 2 + W * 0.028, uy)], fill=GOLD, width=4)

    dev_w = round(W * 0.695)
    dev = device(Image.open(shot_path), dev_w)
    dev_x = (W - dev_w) // 2
    dev_y = round(H * 0.135)

    # мягкая тень под устройством
    sh = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    sh.alpha_composite(Image.new("RGBA", dev.size, (0, 0, 0, 120)), (dev_x, dev_y + 16))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    bg.alpha_composite(sh)
    bg.alpha_composite(dev, (dev_x, dev_y))

    # внутренняя золотая рамка: шире устройства, уходит за нижний край кадра
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle(
        [round(W * 0.058), round(H * 0.128), round(W * 0.942), H + 40],
        22, outline=GOLD + (150,), width=2,
    )
    bg.convert("RGB").save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    shot, caption, out = sys.argv[1], sys.argv[2], sys.argv[3]
    w, h = (int(x) for x in (sys.argv[4].split("x") if len(sys.argv) > 4 else ["2778", "1284"]))
    print(compose(shot, caption, out, (w, h)))
