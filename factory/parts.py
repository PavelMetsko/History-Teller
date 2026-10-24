"""Библиотека деталей этапа 0. Каждая деталь — функция ctx -> [(слой, кость, svg)].

Координаты — локальные для кости (см. rig.py):
  head      — начало в основании шеи, центр лица в (0,-150), лицо ~310×290
  torso     — начало в тазу, шея на y=-168, плечи на (±88,-148)
  arm_u_*   — плечо, вниз на 62;  arm_l_* — локоть, вниз на 50;  hand_* — центр кисти
  leg_u_*   — тазобедренный сустав, вниз на 44;  leg_l_* — колено, вниз ~46 до подошвы
  root      — таз (юбки)
"""
from __future__ import annotations

from rig import INK


def shade(hexc: str, k: float) -> str:
    """Темнее (k<1) или светлее (k>1)."""
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    if k <= 1:
        r, g, b = (int(v * k) for v in (r, g, b))
    else:
        r, g, b = (int(v + (255 - v) * (k - 1)) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def st(w=3.5, col=INK):
    return f'stroke="{col}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def mirror(svg: str) -> str:
    return f'<g transform="scale(-1,1)">{svg}</g>'


def both(svg: str) -> str:
    return svg + mirror(svg)


SIDES = (("l", -1), ("r", 1))

# Лицо как у нарисованных спрайтов: чуть уже, полные щёки, глаза ниже середины (большой лоб).
# Замер силуэта со старых спрайтов: лицо полное до самого низа, подбородок широкий и плоский,
# глаза на ~2/3 высоты лица, уши на уровне глаз.
FACE = ("M-136,-172 C-140,-250 -96,-306 0,-306 C96,-306 140,-250 136,-172 C142,-112 146,-66 124,-34 "
        "C98,-4 50,2 0,2 C-50,2 -98,-4 -124,-34 C-146,-66 -142,-112 -136,-172 Z")
FDY = 26   # насколько глаза/нос/рот/усы опущены относительно чертёжных координат

# ───────────────────────── тело ─────────────────────────

def body(kind="male"):
    """Голова-основа, уши, шея, кисти. Руки и ноги одевает одежда."""
    def part(ctx):
        skin = ctx["c"]["skin"]
        out = [("neck", "head", f'<rect x="-30" y="-30" width="60" height="32" rx="10" fill="{shade(skin, .9)}"/>')]
        ear = (f'<ellipse cx="-152" cy="-96" rx="36" ry="42" fill="{skin}" {st()}/>'
               f'<ellipse cx="-158" cy="-94" rx="18" ry="24" fill="#f0a890" opacity=".75"/>'
               f'<ellipse cx="-144" cy="-112" rx="12" ry="8" fill="#fff" opacity=".25"/>'
               f'<path d="M-146,-116 C-170,-114 -174,-80 -152,-70" fill="none" {st(3, shade(skin, .7))}/>')
        out.append(("ear", "head", both(f'<g transform="translate(8,-10)">{ear}</g>')))
        h = skin.lstrip("#")
        out.append(("face", "head",
                    f'<defs><radialGradient id="sk{h}" cx=".45" cy=".38" r=".62">'
                    f'<stop offset="0" stop-color="{shade(skin, 1.12)}"/><stop offset=".7" stop-color="{skin}"/>'
                    f'<stop offset="1" stop-color="{shade(skin, .9)}"/></radialGradient></defs>'
                    f'<path d="{FACE}" fill="url(#sk{h})"/>'))
        for n, s in SIDES:
            fist = ctx["pose"].get(f"fist_{n}")
            # кисть-варежка как у нарисованных спрайтов: одна форма и линия большого пальца
            hand = (f'<ellipse cx="0" cy="2" rx="21" ry="24" fill="{skin}"/>'
                    f'<path d="M{-s * 4},-12 C{-s * 16},-6 {-s * 16},8 {-s * 6},14" fill="none" {st(3, shade(skin, .68))}/>')
            if fist:
                hand += f'<path d="M-12,-8 Q0,-14 12,-8 M-14,2 Q0,-4 14,2" fill="none" {st(3, shade(skin, .7))}/>'
            out.append(("hand", f"hand_{n}", hand))
        return out
    return part


# ───────────────────────── лицо ─────────────────────────

EYE = "M-36,6 C-34,-24 -6,-34 18,-30 C34,-26 40,-8 36,8 C30,30 -26,32 -36,6 Z"


def _eye(expr, skin, iris, side=-1, look=0, male=False):
    """Левый глаз (внешний уголок слева); правый — зеркально. side — сторона в мире (-1/1),
    чтобы блик у обоих глаз был с одной стороны (свет справа сверху), look — взгляд вбок."""
    if expr == "dead":
        return (f'<path d="{EYE}" fill="#fbf3ec" {st(3)}/>'
                f'<path d="M-14,-14 L16,14 M16,-14 L-14,14" {st(7, "#3a170c")}/>')
    h = iris.lstrip("#")
    w = lambda x: -x * side          # мировой сдвиг по X → локальный (группа отзеркалена)
    ix = 2 + w(look * 10)
    e = (f'<defs><linearGradient id="ir{h}" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{shade(iris, .55)}"/><stop offset=".55" stop-color="{shade(iris, 1.14)}"/>'
         f'<stop offset="1" stop-color="#b06c34"/></linearGradient>'
         f'<clipPath id="ec"><path d="{EYE}"/></clipPath></defs>'
         f'<path d="{EYE}" fill="#fdf8f4"/>'
         f'<g clip-path="url(#ec)"><ellipse cx="{ix}" cy="3" rx="29" ry="31" fill="url(#ir{h})"/>'
         f'<circle cx="{ix}" cy="0" r="12" fill="{shade(iris, .32)}" opacity=".75"/></g>'
         f'<circle cx="{ix + w(9)}" cy="-9" r="7" fill="#fff"/><circle cx="{ix + w(-9)}" cy="10" r="2.5" fill="#fff" opacity=".85"/>'
         f'<path d="M-30,20 C-12,30 14,30 32,14" fill="none" stroke="{shade(skin, .7)}" stroke-width="2.5" opacity=".75"/>')
    lid = {"sad": 0.42, "sly": 0.5}.get(expr)
    if lid:
        y = -32 + 64 * lid
        t = -7 if expr == "sly" else 7     # грусть: веко опущено к внешнему краю; хитрость — к переносице
        e += (f'<path d="M-44,-40 L44,-40 L44,{y - t} Q0,{y + 5} -44,{y + t} Z" fill="{skin}"/>'
              f'<path d="M-40,{y + t} Q0,{y + 5} 40,{y - t}" fill="none" {st(6, "#2a1208")}/>')
    else:
        e += f'<path d="M-40,4 C-36,-26 -6,-37 18,-33 C32,-29 40,-14 40,0" fill="none" {st(6, "#2a1208")}/>'
        if not male:
            e += f'<path d="M-38,-4 L-46,-10" fill="none" {st(4, "#2a1208")}/>'
    return e


BROW = "M-32,10 C-24,-8 8,-12 30,-2 C26,6 10,4 0,5 C-12,6 -22,10 -32,16 Z"   # мягкая короткая дуга


def face(eyes_iris="#6b3a1f", brow="#6b4a2b", brow_w=6, bushy=False, nose=None):
    def part(ctx):
        expr, skin = ctx["expr"], ctx["c"]["skin"]
        look = ctx["pose"].get("look", 0)
        nz = nose or "#f3b49c"
        f = (f'<defs><radialGradient id="blush"><stop offset="0" stop-color="#f6857a" stop-opacity=".55"/>'
             f'<stop offset=".6" stop-color="#f6857a" stop-opacity=".25"/>'
             f'<stop offset="1" stop-color="#f6857a" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="nose" cx=".45" cy=".4"><stop offset="0" stop-color="{nz}" stop-opacity=".9"/>'
             f'<stop offset=".7" stop-color="{nz}" stop-opacity=".6"/><stop offset="1" stop-color="{nz}" stop-opacity="0"/></radialGradient></defs>')
        blush = (f'<defs><radialGradient id="blush"><stop offset="0" stop-color="#f6857a" stop-opacity=".55"/>'
                 f'<stop offset=".6" stop-color="#f6857a" stop-opacity=".25"/>'
                 f'<stop offset="1" stop-color="#f6857a" stop-opacity="0"/></radialGradient></defs>'
                 + both('<ellipse cx="-100" cy="-86" rx="62" ry="42" fill="url(#blush)"/>'))
        for s in (-1, 1):
            f += f'<g transform="translate({s * 78},-127) scale({-s * 0.86},1.04)">{_eye(expr, skin, eyes_iris, s, look, ctx["c"].get("male", False))}</g>'
        # брови: наклон по выражению (внутренний конец вверх — грусть, вниз — хитрость)
        tilt = {"sad": 16, "sly": -22, "happy": 5, "dead": 10}.get(expr, 0)
        bdy = {"sad": 8, "sly": 14}.get(expr, 0)      # грусть и хитрость прижимают брови к глазам
        for s in (-1, 1):
            b = f'<path d="{BROW}" fill="{brow}" {st(2.5, shade(brow, .72))}/>'
            if bushy:
                b = (f'<path d="M-40,14 C-30,-16 12,-20 38,-4 C36,8 18,6 2,8 C-14,10 -28,14 -40,22 Z" fill="{brow}" {st(2.5, shade(brow, .7))}/>'
                     f'<path d="M-28,4 C-14,-6 6,-8 24,-2" fill="none" stroke="{shade(brow, 1.35)}" stroke-width="3" stroke-linecap="round" opacity=".6"/>')
            f += f'<g transform="translate({s * 74},{-186 + bdy}) scale({-s * 1.1},1.05) rotate({-tilt})">{b}</g>'
        f += (f'<ellipse cx="0" cy="-102" rx="15" ry="13" fill="url(#nose)"/>'
              f'<ellipse cx="-3" cy="-106" rx="4" ry="3" fill="#fff" opacity=".4"/>')
        lip = "#a0503e"
        mouth = {
            "neutral": f'<path d="M-30,-82 Q0,-62 30,-82" fill="none" {st(4, lip)}/>'
                       f'<path d="M-10,-58 Q0,-55 10,-58" fill="none" stroke="#d98a76" stroke-width="3" opacity=".7"/>',
            "happy": f'<path d="M-28,-84 Q0,-44 28,-84 Q0,-76 -28,-84 Z" fill="#8f3327" {st(3.5, lip)}/>'
                     f'<path d="M-13,-60 Q0,-52 13,-60" fill="none" stroke="#e98378" stroke-width="6"/>',
            "sad": f'<path d="M-18,-70 Q0,-82 18,-70" fill="none" {st(4, lip)}/>',
            "sly": f'<path d="M-22,-78 Q6,-68 26,-90" fill="none" {st(4, lip)}/>',
            "dead": f'<path d="M-16,-72 Q0,-80 16,-72" fill="none" {st(4, lip)}/>',
        }[expr]
        mdy = 12 if ctx["c"].get("beard") else 0      # под усами рот опускается, как у нарисованных
        return [("face", "head", f'<g transform="translate(0,{FDY})">{blush}</g>'),
                ("features", "head", f'<g transform="translate(0,{FDY})">{f}<g transform="translate(0,{mdy})">{mouth}</g></g>')]
    return part


# ───────────────────────── волосы, бороды, уборы ─────────────────────────

def hair_short_sides(col):
    def part(ctx):
        s = f'<path d="M-160,-232 C-166,-206 -164,-186 -156,-172 C-148,-184 -146,-204 -148,-228 Z" fill="{col}" {st(3)}/>'
        return [("hair_front", "head", both(s))]
    return part


def hair_long(col):
    def part(ctx):
        back = (f'<path d="M-164,-216 C-186,-186 -176,-160 -186,-136 C-198,-110 -178,-90 -188,-66 C-198,-40 -178,-22 -184,-2 '
                f'C-170,16 -142,12 -134,-6 C-146,-26 -130,-44 -134,-60 L134,-60 C130,-44 146,-26 134,-6 C142,12 170,16 184,-2 '
                f'C178,-22 198,-40 188,-66 C178,-90 198,-110 186,-136 C176,-160 186,-186 164,-216 '
                f'C150,-300 -150,-300 -164,-216 Z" fill="{shade(col, .92)}" {st()}/>'
                + both(f'<path d="M-172,-160 C-180,-134 -170,-112 -178,-88 M-176,-60 C-184,-38 -172,-22 -176,-8" fill="none" {st(2.5, shade(col, .7))}/>'))
        front = (f'<path d="M-162,-140 C-172,-252 -100,-304 0,-306 C100,-304 172,-252 162,-140 '
                 f'C150,-200 110,-250 24,-256 L0,-236 L-24,-256 C-110,-250 -150,-200 -162,-140 Z" fill="{col}" {st()}/>'
                 f'<path d="M-8,-246 C-50,-268 -110,-250 -142,-196 M8,-246 C50,-268 110,-250 142,-196" fill="none" {st(2.5, shade(col, .75))}/>'
                 + both(f'<path d="M-40,-286 C-80,-282 -118,-262 -136,-232 C-110,-248 -80,-262 -44,-270 Z" fill="{shade(col, 1.4)}" opacity=".55"/>'))
        locks = both(f'<path d="M-162,-200 C-170,-176 -150,-160 -160,-138 C-150,-150 -138,-170 -142,-196 Z" fill="{col}" {st(3)}/>')
        return [("hair_back", "head", back), ("hair_front", "head", front + locks)]
    return part


def hat_kolpak(fur="#8a6a4a", top="#9e2a2b"):
    def part(ctx):
        s = (f'<path d="M-118,-292 C-110,-350 110,-350 118,-292 Z" fill="{top}" {st()}/>'
             f'<path d="M-170,-236 C-186,-250 -180,-276 -166,-284 C-176,-300 -160,-318 -142,-312 C-130,-332 -100,-332 -88,-322 '
             f'C-70,-340 -36,-338 -24,-326 C-6,-342 26,-340 38,-326 C56,-340 90,-336 100,-320 C118,-334 146,-326 148,-308 '
             f'C168,-312 182,-292 168,-280 C184,-270 186,-248 170,-236 C120,-254 -120,-254 -170,-236 Z" fill="{fur}" {st()}/>')
        for x in range(-140, 141, 28):
            s += f'<path d="M{x},-262 q4,-14 10,-20 M{x + 14},-250 q3,-12 8,-16" fill="none" {st(2.5, shade(fur, .72))}/>'
        # перо цапли и брошь
        s += (f'<path d="M6,-310 C40,-360 30,-420 70,-450 C60,-400 64,-350 24,-306 Z" fill="#f2efe8" {st(3)}/>'
              f'<path d="M14,-312 C40,-350 44,-400 62,-434" fill="none" {st(2, "#b9b2a6")}/>'
              f'<circle cx="8" cy="-300" r="17" fill="#d8ad3c" {st(3)}/><circle cx="8" cy="-300" r="8" fill="#b3263a"/>')
        return [("hat", "head", s)]
    return part


def hat_crown(gold="#d8ad3c"):
    def part(ctx):
        pts = "M-78,-282 L-82,-336 L-52,-306 L-26,-350 L0,-312 L26,-350 L52,-306 L82,-336 L78,-282 Z"
        s = (f'<path d="{pts}" fill="{gold}" {st()}/>'
             f'<rect x="-80" y="-300" width="160" height="22" rx="6" fill="{shade(gold, .88)}" {st(3)}/>'
             f'<circle cx="0" cy="-289" r="7" fill="#2f9a8a"/><circle cx="-46" cy="-289" r="5" fill="#b3263a"/>'
             f'<circle cx="46" cy="-289" r="5" fill="#b3263a"/>'
             + "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#f4e1a0"/>' for x, y in ((-82, -338), (-26, -352), (26, -352), (82, -338))))
        return [("hat", "head", s)]
    return part


def hat_maciejowka(col="#7b8794"):
    def part(ctx):
        s = (f'<path d="M-150,-232 C-160,-280 -150,-322 -120,-338 C-60,-356 60,-356 120,-338 C150,-322 160,-280 150,-232 Z" '
             f'fill="{col}" {st()}/>'
             f'<path d="M-150,-246 C-80,-262 80,-262 150,-246 L150,-228 C80,-244 -80,-244 -150,-228 Z" fill="{shade(col, .72)}" {st(3)}/>'
             f'<path d="M-120,-232 C-60,-246 60,-246 120,-232 C100,-208 -100,-208 -120,-232 Z" fill="#3b2a20" {st()}/>'
             f'<path d="M-100,-330 C-40,-342 40,-342 100,-330" fill="none" {st(2.5, shade(col, .8))}/>'
             f'<path d="M0,-298 l-12,-8 l4,-10 l8,6 l8,-6 l4,10 Z" fill="#e8e4dc" {st(2)}/>')
        return [("hat", "head", s)]
    return part


# ───────────────────────── одежда ─────────────────────────

TORSO_M = ("M-34,-178 C-62,-170 -86,-150 -94,-120 C-100,-80 -104,-40 -102,0 Q-100,16 -84,20 L84,20 "
           "Q100,16 102,0 C104,-40 100,-80 94,-120 C86,-150 62,-170 34,-178 Z")
TORSO_F = ("M-64,-172 C-88,-170 -100,-158 -102,-136 L-86,-46 Q-84,-36 -70,-34 L70,-34 Q84,-36 86,-46 "
           "L102,-136 C100,-158 88,-170 64,-172 Z")


def sleeves(col, cuff=None, cuff_w=12):
    def part(ctx):
        out = []
        for n, s in SIDES:
            out.append(("arm", f"arm_u_{n}", f'<rect x="-22" y="-6" width="44" height="80" rx="22" fill="{col}"/>'))
            low = f'<rect x="-21" y="-16" width="42" height="60" rx="20" fill="{col}"/>'
            if cuff:
                low += f'<rect x="-23" y="{44 - cuff_w}" width="46" height="{cuff_w}" rx="5" fill="{cuff}" {st(3)}/>'
            out.append(("arm", f"arm_l_{n}", low))
        return out
    return part


def boots(col, top=None, tall=False):
    def part(ctx):
        out = []
        for n, s in SIDES:
            y0 = -8 if not tall else -48
            b = (f'<rect x="-24" y="{y0}" width="48" height="{52 - y0}" rx="14" fill="{col}" {st()}/>'
                 f'<ellipse cx="{s * 5}" cy="46" rx="30" ry="12" fill="{col}" {st()}/>')
            if top:
                b += f'<rect x="-26" y="{y0}" width="52" height="12" rx="5" fill="{top}" {st(3)}/>'
            out.append(("leg", f"leg_l_{n}", b))
        return out
    return part


def trousers(col):
    def part(ctx):
        return [("leg", f"leg_u_{n}", f'<rect x="-25" y="-10" width="50" height="64" rx="16" fill="{col}" {st()}/>')
                for n, _ in SIDES]
    return part


def zupan_hussar(cloth="#9e2a2b", steel="#c6cbd1", sash1="#d4a63c", sash2="#a8312f"):
    """Жупан + кираса + пояс-кушак + кунтушевые полы + леопардовая шкура через плечо."""
    def part(ctx):
        t = (f'<path d="{TORSO_M}" fill="{cloth}" {st()}/>'
             f'<path d="M-96,10 L-92,70 Q-50,82 -6,70 L-4,10 Z" fill="{shade(cloth, .9)}" {st()}/>'
             f'<path d="M96,10 L92,70 Q50,82 6,70 L4,10 Z" fill="{shade(cloth, .9)}" {st()}/>')
        over = (f'<path d="M-82,-160 C-40,-176 40,-176 82,-160 L88,-60 C50,-44 -50,-44 -88,-60 Z" fill="{steel}" {st()}/>'
                f'<path d="M0,-170 L0,-50" fill="none" {st(3, shade(steel, .7))}/>'
                f'<path d="M-70,-120 C-30,-110 30,-110 70,-120 M-76,-88 C-30,-78 30,-78 76,-88" fill="none" {st(3, shade(steel, .72))}/>'
                f'<ellipse cx="-30" cy="-140" rx="22" ry="12" fill="#fff" opacity=".35"/>'
                + "".join(f'<circle cx="{x}" cy="-60" r="4" fill="{shade(steel, .6)}"/>' for x in (-60, -30, 30, 60)))
        sash = f'<path d="M-104,-48 C-50,-36 50,-36 104,-48 L104,-14 C50,-2 -50,-2 -104,-14 Z" fill="{sash1}" {st()}/>'
        for y in (-38, -26):
            sash += f'<path d="M-100,{y} C-50,{y + 12} 50,{y + 12} 100,{y}" fill="none" stroke="{sash2}" stroke-width="5"/>'
        sash += f'<path d="M-30,-14 L-40,40 L-22,40 L-14,-12 Z" fill="{sash1}" {st(3)}/>'
        leo = (f'<path d="M30,-176 C80,-180 128,-150 132,-110 C136,-70 120,-40 104,-26 C96,-60 74,-96 40,-120 Z" '
               f'fill="#e2b75e" {st()}/>'
               + "".join(f'<ellipse cx="{x}" cy="{y}" rx="7" ry="5" fill="#7a4a1e"/>'
                         for x, y in ((60, -160), (90, -150), (110, -122), (78, -126), (112, -84), (96, -60), (54, -140))))
        return [("torso", "torso", t), ("torso_over", "torso", over + sash + leo)]
    return part


def bulawa(hand="hand_r"):
    def part(ctx):
        s = (f'<rect x="-6" y="-70" width="12" height="104" rx="5" fill="#8a5a2a" {st(3)}/>'
             f'<circle cx="0" cy="-82" r="22" fill="#d8ad3c" {st()}/>'
             f'<path d="M-20,-82 L20,-82 M0,-104 L0,-60 M-14,-96 L14,-68 M14,-96 L-14,-68" fill="none" {st(2.5, "#a07a22")}/>')
        return [("held", hand, s)]
    return part


def gown(dress="#f1e9da", trim="#d4a63c", mantle="#a8262e", shoes="#a8262e"):
    def part(ctx):
        sit = ctx["pose"].get("sit", False)
        hem_y, hem_x = (50, 150) if sit else (98, 122)
        t = (f'<path d="{TORSO_F}" fill="{dress}" {st()}/>'
             f'<path d="M-56,-170 Q0,-128 56,-170" fill="none" {st(6, trim)}/>'
             f'<rect x="-84" y="-52" width="168" height="18" rx="6" fill="{trim}" {st(3)}/>')
        skirt = (f'<path d="M-82,-48 C-100,0 -{hem_x},{hem_y - 30} -{hem_x},{hem_y} Q0,{hem_y + 16} {hem_x},{hem_y} '
                 f'C{hem_x},{hem_y - 30} 100,0 82,-48 Z" fill="{dress}" {st()}/>'
                 f'<path d="M-{hem_x - 4},{hem_y - 8} Q0,{hem_y + 8} {hem_x - 4},{hem_y - 8}" fill="none" {st(8, trim)}/>'
                 f'<path d="M-16,-40 L-24,{hem_y + 4} L24,{hem_y + 4} L16,-40 Z" fill="{shade(dress, .93)}" {st(3)}/>'
                 f'<path d="M-16,-40 L-24,{hem_y + 4} M16,-40 L24,{hem_y + 4}" fill="none" {st(4, trim)}/>')
        cape = (f'<path d="M-96,-170 C-150,-120 -170,0 -164,{hem_y - 4} L164,{hem_y - 4} C170,0 150,-120 96,-170 Z" '
                f'fill="{mantle}" {st()}/>')
        shoe = [("leg", f"leg_l_{n}", f'<ellipse cx="{s * 4}" cy="44" rx="26" ry="12" fill="{shoes}" {st()}/>') for n, s in SIDES]
        return [("cape_back", "torso", cape), ("skirt", "root", skirt), ("torso", "torso", t)] + shoe
    return part


def legion_tunic(col="#7f8c99", belt="#6b4426", button="#4b5560"):
    def part(ctx):
        t = (f'<path d="{TORSO_M}" fill="{col}" {st()}/>'
             f'<path d="M-98,0 L-96,58 Q0,72 96,58 L98,0 Z" fill="{col}" {st()}/>'
             f'<path d="M-46,-174 L-40,-146 Q0,-136 40,-146 L46,-174 Q0,-160 -46,-174 Z" fill="{shade(col, .8)}" {st(3)}/>'
             f'<path d="M0,-146 L0,58" fill="none" {st(3, shade(col, .7))}/>'
             + "".join(f'<circle cx="0" cy="{y}" r="6" fill="{button}" {st(2)}/>' for y in (-124, -92, -60, 30))
             + both(f'<rect x="-82" y="-128" width="44" height="34" rx="5" fill="{shade(col, .93)}" {st(3)}/>'
                    f'<circle cx="-60" cy="-116" r="4" fill="{button}"/>'))
        over = (f'<rect x="-106" y="-26" width="212" height="22" rx="6" fill="{belt}" {st(3)}/>'
                f'<rect x="-14" y="-28" width="28" height="26" rx="4" fill="#c9c4b8" {st(3)}/>'
                f'<path d="M70,-168 L-84,-20" fill="none" stroke="{belt}" stroke-width="12"/>'
                f'<path d="M70,-168 L-84,-20" fill="none" {st(2.5, shade(belt, .7))}/>'
                # сабля в ножнах на левом боку
                f'<path d="M-98,-12 C-112,30 -118,70 -112,120" fill="none" stroke="#3a3f46" stroke-width="12" stroke-linecap="round"/>'
                f'<path d="M-98,-12 C-104,-30 -96,-46 -84,-52" fill="none" stroke="#b9a46a" stroke-width="7" stroke-linecap="round"/>')
        return [("torso", "torso", t), ("torso_over", "torso", over)]
    return part


# ───────────────────────── добавлено для редактора ─────────────────────────

def hair_short(col):
    def part(ctx):
        s = (f'<path d="M-162,-150 C-172,-262 -100,-306 0,-306 C100,-306 172,-262 162,-150 C150,-196 120,-226 60,-236 '
             f'C20,-242 -20,-242 -60,-236 C-120,-226 -150,-196 -162,-150 Z" fill="{col}" {st()}/>'
             f'<path d="M-40,-286 C-60,-270 -90,-262 -120,-232 M30,-290 C20,-272 0,-262 -20,-250 M90,-276 C100,-256 120,-240 140,-214" '
             f'fill="none" {st(2.5, shade(col, .72))}/>'
             f'<path d="M-70,-286 C-100,-276 -126,-256 -140,-228 C-118,-246 -96,-262 -66,-272 Z" fill="{shade(col, 1.4)}" opacity=".5"/>')
        return [("hair_front", "head", s)]
    return part


def hair_curly(col):
    def part(ctx):
        bumps = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" {st(3)}/>'
                        for x, y, r in ((-150, -180, 34), (-130, -240, 40), (-80, -282, 42), (-20, -300, 42),
                                        (40, -298, 42), (96, -278, 40), (140, -236, 38), (156, -180, 32)))
        return [("hair_front", "head", bumps)]
    return part


# Шлем обхватывает голову: купол + нащёчные края до уровня ушей, лицо открыто в «окне»
_HELM_SHELL = ("M-166,-112 C-178,-250 -110,{top} 0,{top} C110,{top} 178,-250 166,-112 L136,-112 L136,-196 "
               "C82,-218 -82,-218 -136,-196 L-136,-112 Z")
_HELM_RIM = "M-150,-226 C-84,-246 84,-246 150,-226 L150,-202 C84,-222 -84,-222 -150,-202 Z"


def hat_helmet(col="#b9bfc6", trim="#8a6a2a"):
    def part(ctx):
        s = (f'<path d="{_HELM_SHELL.format(top=-336, ctop=-250)}" fill="{col}" {st()}/>'
             f'<path d="{_HELM_RIM}" fill="{trim}" {st(3)}/>'
             f'<path d="M-9,-206 L9,-206 L7,-112 C4,-104 -4,-104 -7,-112 Z" fill="{col}" {st(3)}/>'
             f'<path d="M0,-334 L0,-222" fill="none" {st(3, shade(col, .7))}/>'
             f'<ellipse cx="-70" cy="-290" rx="34" ry="16" fill="#fff" opacity=".35" transform="rotate(-25 -70 -290)"/>')
        return [("hat", "head", s)]
    return part


def hat_mitre(col="#f1ece2", trim="#d4a63c"):
    def part(ctx):
        s = (f'<path d="M-110,-236 L-96,-360 C-60,-420 -10,-440 0,-450 C10,-440 60,-420 96,-360 L110,-236 Z" fill="{col}" {st()}/>'
             f'<path d="M0,-446 L0,-238 M-104,-262 L104,-262" fill="none" {st(10, trim)}/>')
        return [("hat", "head", s)]
    return part


def hat_konfederatka(col="#a8262e", fur="#3b2a20"):
    def part(ctx):
        s = (f'<path d="M-150,-250 L-176,-350 L176,-350 L150,-250 Z" fill="{col}" {st()}/>'
             f'<path d="M-176,-350 L0,-330 L176,-350 M-150,-250 L0,-330 L150,-250" fill="none" {st(2.5, shade(col, .7))}/>'
             f'<path d="M-166,-218 C-176,-250 -160,-268 -140,-266 C-60,-276 60,-276 140,-266 C160,-268 176,-250 166,-218 '
             f'C100,-234 -100,-234 -166,-218 Z" fill="{fur}" {st()}/>'
             f'<path d="M40,-262 C60,-320 50,-380 84,-420 C82,-370 86,-320 56,-258 Z" fill="#f2efe8" {st(3)}/>')
        return [("hat", "head", s)]
    return part


def coat(col="#5a6b4a", trim="#d4a63c", belt="#6b4426"):
    def part(ctx):
        t = (f'<path d="{TORSO_M}" fill="{col}" {st()}/>'
             f'<path d="M-100,0 L-98,84 Q0,98 98,84 L100,0 Z" fill="{col}" {st()}/>'
             f'<path d="M0,-170 L0,90" fill="none" {st(6, trim)}/>'
             + "".join(f'<circle cx="0" cy="{y}" r="6" fill="{trim}" {st(2)}/>' for y in (-140, -110, -80, -50)))
        over = (f'<rect x="-106" y="-28" width="212" height="24" rx="6" fill="{belt}" {st(3)}/>'
                f'<rect x="-14" y="-30" width="28" height="28" rx="4" fill="{trim}" {st(3)}/>')
        return [("torso", "torso", t), ("torso_over", "torso", over)]
    return part


def robe(col="#5b4636", rope="#d8c7a0"):
    def part(ctx):
        t = (f'<path d="M-72,-172 C-98,-170 -112,-160 -114,-136 L-120,130 Q0,148 120,130 L114,-136 '
             f'C112,-160 98,-170 72,-172 Z" fill="{col}" {st()}/>'
             f'<path d="M-50,-120 L-60,130 M50,-120 L60,130" fill="none" {st(2.5, shade(col, .72))}/>')
        hood = f'<path d="M-96,-176 C-60,-206 60,-206 96,-176 C60,-150 -60,-150 -96,-176 Z" fill="{shade(col, .85)}" {st()}/>'
        over = (f'<path d="M-112,-30 C-40,-16 40,-16 112,-30" fill="none" {st(9, rope)}/>'
                f'<path d="M-20,-20 L-28,70 M-10,-20 L-6,64" fill="none" {st(6, rope)}/>')
        return [("cape_back", "torso", hood), ("torso", "torso", t), ("torso_over", "torso", over)]
    return part


def cape(col="#2f4a7a"):
    def part(ctx):
        return [("cape_back", "torso", f'<path d="M-96,-170 C-150,-120 -166,0 -160,96 L160,96 C166,0 150,-120 96,-170 Z" '
                                        f'fill="{col}" {st()}/>')]
    return part


def sword(hand="hand_r"):
    def part(ctx):
        s = (f'<rect x="-7" y="-4" width="14" height="120" rx="4" fill="#d9dde2" {st(3)}/>'
             f'<rect x="-30" y="-14" width="60" height="12" rx="5" fill="#b9934a" {st(3)}/>'
             f'<rect x="-6" y="-44" width="12" height="32" rx="4" fill="#6b4426" {st(3)}/>'
             f'<circle cx="0" cy="-48" r="9" fill="#b9934a" {st(3)}/>')
        return [("held", hand, s)]
    return part


def scroll(hand="hand_r"):
    def part(ctx):
        s = (f'<rect x="-14" y="-50" width="28" height="100" rx="12" fill="#f1e6c8" {st(3)}/>'
             f'<ellipse cx="0" cy="-50" rx="16" ry="7" fill="#e0cfa4" {st(3)}/>'
             f'<path d="M-14,10 L14,10" fill="none" {st(5, "#a8262e")}/>')
        return [("held", hand, s)]
    return part


# ───────────────────────── Рим: Цезарь ─────────────────────────

def hair_receding(col):
    """Седина как у эталона: плотная шапочка на макушке с мягкой дугой линии волос
    и прямые пряди на висках до верха ушей. Тень у линии волос — чтобы шапка лежала на голове."""
    def part(ctx):
        cap = ("M-144,-166 C-152,-244 -110,-312 0,-314 C110,-312 152,-244 144,-166 "
               "C134,-160 120,-164 112,-172 C110,-214 96,-246 72,-250 C48,-254 26,-240 0,-240 "
               "C-26,-240 -48,-254 -72,-250 C-96,-246 -110,-214 -112,-172 "
               "C-120,-164 -134,-160 -144,-166 Z")
        s = (f'<path d="{cap}" fill="{col}" {st()}/>'
             f'<path d="M-108,-176 C-106,-212 -94,-242 -72,-246 C-48,-250 -26,-236 0,-236 C26,-236 48,-250 72,-246 C94,-242 106,-212 108,-176" fill="none" '
             f'stroke="{shade(col, .85)}" stroke-width="7" stroke-linecap="round" opacity=".45"/>'
             + both(f'<path d="M-146,-170 C-148,-150 -146,-132 -140,-122 C-128,-126 -120,-140 -118,-162 Z" '
                    f'fill="{col}" {st(3)}/>'
                    f'<path d="M-140,-180 C-142,-160 -140,-140 -136,-122" fill="none" {st(2, shade(col, .8))}/>')
             + f'<path d="M-50,-300 C-20,-306 20,-306 50,-300" fill="none" {st(3, shade(col, 1.2))}/>')
        return [("hair_front", "head", s)]
    return part


def wrinkles(skin_line="#c98f74"):
    """Возрастные морщины: лоб, гусиные лапки, носогубки."""
    def part(ctx):
        c = f'stroke="{skin_line}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".6"'
        s = (f'<path d="M-56,-236 C-30,-246 -10,-238 0,-242 C14,-248 34,-240 56,-238 M-42,-218 C-20,-226 0,-220 14,-224 C26,-228 36,-224 44,-220" {c}/>'
             + both(f'<path d="M-118,-136 l-12,-6 M-118,-126 l-14,0 M-116,-116 l-12,6" {c}/>')
             + both(f'<path d="M-104,-100 C-90,-92 -68,-92 -56,-100" {c}/>')
             + both(f'<path d="M-36,-100 C-50,-86 -50,-70 -40,-58" {c}/>')
             + f'<path d="M-24,-38 Q0,-30 24,-38" {c}/>')
        return [("features", "head", f'<g transform="translate(0,{FDY})">{s}</g>')]
    return part


def hat_laurel(col="#72b552"):
    def part(ctx):
        ink = shade(col, .5)
        def leaf(x, y, a):
            return (f'<g transform="translate({x},{y}) rotate({a}) scale(1.06)">'
                    f'<path d="M0,0 C12,-15 42,-16 60,0 C42,16 12,15 0,0 Z" fill="{col}" {st(3, ink)}/>'
                    f'<path d="M6,0 C20,-3 36,-3 50,0" fill="none" {st(2.5, shade(col, 1.45))}/></g>')
        # ветка от виска к темени поверх волос; листья парами, смотрят вверх-наружу
        stem = (-142, -168), (-140, -204), (-128, -238), (-106, -264)
        s = f'<path d="M-144,-150 C-148,-212 -128,-260 -90,-284" fill="none" {st(4, ink)}/>'
        for i, (x, y) in enumerate(stem):
            s += leaf(x, y, -128 + i * 18) + leaf(x, y, -70 + i * 18)
        s += leaf(-96, -272, -36)
        return [("hat", "head", both(s))]
    return part


def toga(cloth="#f7ede2", band="#6b2f7a", gold="#d8ad3c"):
    """Тога как у эталона: открыто одно плечо, драпировка диагональной волной от фибулы,
    складки параллельно пурпурной полосе, с плеча свисает угол с грузиками, подол колоколом."""
    def part(ctx):
        skin = ctx["c"]["skin"]
        sit = ctx["pose"].get("sit", False)
        hem = 56 if sit else 86
        fold = "#d6bb98"
        roll = lambda d: (f'<path d="{d}" fill="none" stroke="{fold}" stroke-width="3.5" stroke-linecap="round"/>'
                          f'<path d="{d}" fill="none" stroke="#fffaf2" stroke-width="3" stroke-linecap="round" '
                          f'opacity=".8" transform="translate(0,6)"/>')
        bare = f'<path d="{TORSO_M}" fill="{skin}" {st()}/>'
        drape = (f'<path d="M-102,-66 C-60,-102 -10,-150 30,-178 L34,-178 C62,-170 86,-150 94,-120 C100,-80 104,-40 102,4 '
                 f'C82,34 -10,58 -102,18 Z" fill="{cloth}" {st()}/>'
                 + roll("M-100,-24 C-50,-52 10,-98 78,-138") + roll("M-100,4 C-40,-18 20,-58 92,-92")
                 + roll("M-96,16 C-20,38 60,22 98,0")
                 + f'<path d="M-104,-48 C-60,-86 -12,-144 38,-178 L68,-164 C22,-122 -40,-54 -104,0 Z" fill="{band}" {st(3)}/>'
                 f'<path d="M-96,-32 C-56,-70 -10,-124 44,-162" fill="none" stroke="#8d4a9c" stroke-width="3" opacity=".7"/>')
        over = (f'<path d="M54,-150 C70,-128 80,-100 80,-70 C80,-48 86,-30 92,-16 C80,-6 66,-8 58,-18 '
                f'C56,-50 50,-90 46,-120 Z" fill="{cloth}" {st()}/>' + roll("M60,-130 C68,-100 70,-70 72,-30")
                + f'<circle cx="64" cy="-92" r="10" fill="{gold}" {st(2.5)}/>'
                f'<path d="M78,-12 l-10,22 l20,0 Z" fill="{gold}" {st(2.5)}/>'
                f'<circle cx="50" cy="-164" r="18" fill="{gold}" {st(3)}/><circle cx="50" cy="-164" r="9" fill="{shade(gold, .8)}"/>'
                f'<circle cx="50" cy="-164" r="4" fill="#f6e2a0"/>')
        skirt = (f'<path d="M-90,-44 C-96,-6 -104,{hem - 22} -138,{hem} C-110,{hem + 10} -76,{hem + 2} -46,{hem + 10} '
                 f'C-20,{hem + 2} 20,{hem + 12} 46,{hem + 6} C76,{hem + 12} 110,{hem + 4} 138,{hem} '
                 f'C104,{hem - 22} 96,-6 90,-44 Z" fill="{cloth}" {st()}/>'
                 f'<path d="M-128,{hem - 24} C-100,{hem - 14} -70,{hem - 20} -44,{hem - 12} C-20,{hem - 20} 20,{hem - 10} '
                 f'44,{hem - 16} C70,{hem - 10} 100,{hem - 18} 128,{hem - 24}" fill="none" {st(13, band)}/>'
                 + roll(f"M-40,-30 C-60,0 -86,30 -104,{hem - 30}") + roll(f"M10,-24 C0,10 -20,40 -30,{hem - 24}")
                 + roll(f"M60,-30 C64,0 70,30 84,{hem - 30}"))
        if sit:   # сидя подол растекается по земле
            skirt = f'<g transform="scale(1.28,1)">{skirt}</g>'
        return [("torso", "torso", bare + drape), ("torso_over", "torso", over), ("skirt", "root", skirt)]
    return part


def bare_arms():
    def part(ctx):
        skin = ctx["c"]["skin"]
        out = []
        for n, _ in SIDES:
            out.append(("arm", f"arm_u_{n}", f'<rect x="-19" y="-6" width="38" height="80" rx="19" fill="{skin}"/>'))
            out.append(("arm", f"arm_l_{n}", f'<rect x="-18" y="-16" width="36" height="60" rx="18" fill="{skin}"/>'))
        return out
    return part


def sandals(strap="#8a5a2a"):
    def part(ctx):
        skin = ctx["c"]["skin"]
        return [("leg", f"leg_l_{n}", f'<ellipse cx="{s * 5}" cy="44" rx="28" ry="12" fill="{skin}" {st()}/>'
                                      f'<path d="M{s * 5 - 22},42 L{s * 5 + 22},42 M{s * 5 - 10},34 L{s * 5 - 10},50 M{s * 5 + 10},34 L{s * 5 + 10},50" '
                                      f'fill="none" {st(4, strap)}/>') for n, s in SIDES]
    return part


# ───────────────────────── Польша: раннее средневековье ─────────────────────────

def _hem_skirt(cloth, hem, trim=None, wide=1.0, folds=True):
    """Юбка-подол от пояса до hem (корень = таз), чуть расширяется книзу."""
    w = int(112 * wide)
    s = (f'<path d="M-92,-44 C-98,-6 -{w - 6},{hem - 22} -{w},{hem} C-60,{hem + 10} 60,{hem + 10} {w},{hem} '
         f'C{w - 6},{hem - 22} 98,-6 92,-44 Z" fill="{cloth}" {st()}/>')
    if trim:
        s += f'<path d="M-{w - 6},{hem - 10} C-60,{hem} 60,{hem} {w - 6},{hem - 10}" fill="none" {st(10, trim)}/>'
    if folds:
        s += (f'<path d="M-40,-24 C-46,10 -52,{hem - 30} -56,{hem - 16} M36,-24 C42,10 48,{hem - 30} 52,{hem - 16}" '
              f'fill="none" {st(2.5, shade(cloth, .78))}/>')
    return s


def tunic_medieval(col="#4f6b8a", trim="#d4a63c", belt="#6b4426"):
    """Туника до колен с каймой у ворота и подола, кожаный пояс с пряжкой."""
    def part(ctx):
        hem = 40 if ctx["pose"].get("sit") else 64
        t = (f'<path d="{TORSO_M}" fill="{col}" {st()}/>'
             f'<path d="M-40,-176 Q0,-150 40,-176" fill="none" {st(9, trim)}/>')
        over = (f'<path d="M-106,-30 C-40,-18 40,-18 106,-30 L106,-8 C40,4 -40,4 -106,-8 Z" fill="{belt}" {st(3)}/>'
                f'<rect x="-13" y="-30" width="26" height="24" rx="5" fill="#c9a24a" {st(3)}/>'
                f'<path d="M-8,-6 L-12,30" fill="none" {st(6, belt)}/>')
        return [("torso", "torso", t), ("torso_over", "torso", over), ("skirt", "root", _hem_skirt(col, hem, trim))]
    return part


def fur_tunic(col="#8a6b4a", fur="#c9b08a", rope="#a88a5a"):
    """Грубая рубаха, меховая накидка на плечах, верёвка вместо пояса — легенды, пруссы, крестьяне."""
    def part(ctx):
        hem = 40 if ctx["pose"].get("sit") else 56
        t = f'<path d="{TORSO_M}" fill="{col}" {st()}/>'
        tufts = "".join(f'<path d="M{x},-128 l6,14 l6,-14" fill="none" {st(2.5, shade(fur, .7))}/>' for x in range(-96, 90, 24))
        over = (f'<path d="M-104,-150 C-80,-186 80,-186 104,-150 C108,-130 100,-112 96,-104 C40,-122 -40,-122 -96,-104 '
                f'C-100,-112 -108,-130 -104,-150 Z" fill="{fur}" {st()}/>' + tufts
                + f'<path d="M-106,-22 C-40,-12 40,-12 106,-22" fill="none" {st(8, rope)}/>'
                f'<path d="M-24,-16 L-30,26 M-14,-16 L-12,22" fill="none" {st(5, rope)}/>')
        return [("torso", "torso", t), ("torso_over", "torso", over), ("skirt", "root", _hem_skirt(col, hem, folds=True))]
    return part


def chainmail(steel="#a9b0b8", surcoat="#9e2a2b", belt="#5b3a22"):
    """Кольчуга до колен; поверх — сюрко без рукавов с поясом (surcoat="none" — без него)."""
    def part(ctx):
        hem = 40 if ctx["pose"].get("sit") else 60
        rings = "".join(f'<path d="M{x - 7},{y} q7,8 14,0" fill="none" stroke="{shade(steel, .66)}" stroke-width="2"/>'
                        for y in range(-160, 20, 16) for x in range(-96 + (8 if (y // 16) % 2 else 0), 100, 16))
        t = (f'<path d="{TORSO_M}" fill="{steel}" {st()}/>'
             f'<g clip-path="url(#tm)">{rings}</g><defs><clipPath id="tm"><path d="{TORSO_M}"/></clipPath></defs>')
        skirt = _hem_skirt(steel, hem, folds=False)
        skirt += "".join(f'<path d="M{x - 7},{y} q7,8 14,0" fill="none" stroke="{shade(steel, .66)}" stroke-width="2"/>'
                         for y in range(-30, hem - 6, 16) for x in range(-100, 104, 16))
        out = [("torso", "torso", t), ("skirt", "root", skirt)]
        if surcoat != "none":
            over = (f'<path d="M-60,-172 L60,-172 L84,20 L-84,20 Z" fill="{surcoat}" {st()}/>'
                    f'<path d="M-104,-30 C-40,-18 40,-18 104,-30 L104,-10 C40,2 -40,2 -104,-10 Z" fill="{belt}" {st(3)}/>'
                    f'<rect x="-12" y="-30" width="24" height="22" rx="5" fill="#c9a24a" {st(3)}/>')
            out.append(("torso_over", "torso", over))
            out.append(("skirt", "root", f'<path d="M-70,-44 L-80,{hem - 6} L80,{hem - 6} L70,-44 Z" fill="{surcoat}" {st()}/>'
                                         f'<path d="M0,-40 L0,{hem - 8}" fill="none" {st(2.5, shade(surcoat, .72))}/>'))
        return out
    return part


def emperor_robe(col="#5a2a6b", gold="#d8ad3c", mantle="#a8262e"):
    """Долгая далматика до пола с золотой полосой, мантия за спиной, фибула на плече — император."""
    def part(ctx):
        hem = 50 if ctx["pose"].get("sit") else 96
        t = (f'<path d="{TORSO_M}" fill="{col}" {st()}/>'
             f'<path d="M-40,-176 Q0,-150 40,-176" fill="none" {st(10, gold)}/>'
             f'<path d="M0,-150 L0,20" fill="none" {st(16, gold)}/>'
             + "".join(f'<circle cx="0" cy="{y}" r="5" fill="#b3263a"/>' for y in (-120, -80, -40)))
        cape_ = (f'<path d="M-96,-170 C-150,-120 -166,0 -160,{hem + 20} L160,{hem + 20} C166,0 150,-120 96,-170 Z" '
                 f'fill="{mantle}" {st()}/>')
        over = f'<circle cx="74" cy="-160" r="16" fill="{gold}" {st(3)}/><circle cx="74" cy="-160" r="7" fill="#2f9a8a"/>'
        skirt = _hem_skirt(col, hem, gold, wide=1.1) + f'<path d="M0,-40 L0,{hem}" fill="none" {st(16, gold)}/>'
        return [("cape_back", "torso", cape_), ("torso", "torso", t), ("torso_over", "torso", over), ("skirt", "root", skirt)]
    return part


def hat_nasal(col="#a9b0b8", trim="#8a6a2a"):
    """Конический шлем с наносником (X–XI вв.)."""
    def part(ctx):
        s = (f'<path d="M-166,-112 C-176,-232 -96,-352 0,-380 C96,-352 176,-232 166,-112 L136,-112 L136,-196 '
             f'C82,-218 -82,-218 -136,-196 L-136,-112 Z" fill="{col}" {st()}/>'
             f'<path d="{_HELM_RIM}" fill="{trim}" {st(3)}/>'
             f'<path d="M-9,-206 L9,-206 L7,-112 C4,-104 -4,-104 -7,-112 Z" fill="{col}" {st(3)}/>'
             f'<path d="M0,-376 L0,-222" fill="none" {st(3, shade(col, .7))}/>'
             f'<ellipse cx="-62" cy="-288" rx="20" ry="44" fill="#fff" opacity=".3" transform="rotate(28 -62 -288)"/>')
        return [("hat", "head", s)]
    return part


def hat_hood(col="#6b5a4a"):
    """Капюшон странника: покрывает макушку и виски, лицо открыто."""
    def part(ctx):
        s = (f'<path d="M-170,-60 C-190,-200 -130,-336 0,-340 C130,-336 190,-200 170,-60 C150,-40 130,-50 124,-70 '
             f'C138,-150 110,-250 0,-252 C-110,-250 -138,-150 -124,-70 C-130,-50 -150,-40 -170,-60 Z" fill="{col}" {st()}/>'
             f'<path d="M-120,-80 C-130,-170 -96,-240 0,-246 C96,-240 130,-170 120,-80" fill="none" {st(4, shade(col, .7))}/>'
             f'<path d="M-60,-320 C-20,-330 20,-330 60,-320" fill="none" {st(3, shade(col, 1.25))}/>')
        return [("hat", "head", s)]
    return part


def hat_circlet(gold="#d8ad3c"):
    """Княжеский обруч с зубцами-лилиями — ниже короны, для князей до коронации."""
    def part(ctx):
        s = (f'<path d="M-132,-250 C-60,-266 60,-266 132,-250 L132,-228 C60,-244 -60,-244 -132,-228 Z" fill="{gold}" {st(3)}/>'
             + "".join(f'<path d="M{x},-256 l-10,-26 l10,8 l10,-8 Z" fill="{gold}" {st(2.5)}/>' for x in (-90, -30, 30, 90))
             + "".join(f'<circle cx="{x}" cy="-240" r="5" fill="{c}"/>' for x, c in ((-60, "#b3263a"), (0, "#2f9a8a"), (60, "#b3263a"))))
        return [("hat", "head", s)]
    return part


def hair_bowl(col):
    """Стрижка «под горшок» с чёлкой — молодые князья и рыцари."""
    def part(ctx):
        s = (f'<path d="M-156,-130 C-170,-250 -110,-318 0,-320 C110,-318 170,-250 156,-130 C146,-140 138,-160 134,-190 '
             f'C100,-206 50,-212 0,-212 C-50,-212 -100,-206 -134,-190 C-138,-160 -146,-140 -156,-130 Z" fill="{col}" {st()}/>'
             f'<path d="M-100,-206 l4,-30 M-50,-212 l2,-36 M0,-213 l0,-38 M50,-212 l-2,-36 M100,-206 l-4,-30" fill="none" '
             f'{st(2.5, shade(col, .72))}/>'
             f'<path d="M-70,-300 C-30,-310 30,-310 70,-300" fill="none" {st(3, shade(col, 1.35))}/>')
        return [("hair_front", "head", s)]
    return part


def hair_shoulder(col):
    """Прямые волосы до плеч — князья, легендарные братья."""
    def part(ctx):
        back = (f'<path d="M-170,-200 C-186,-120 -180,-40 -160,10 L160,10 C180,-40 186,-120 170,-200 '
                f'C150,-300 -150,-300 -170,-200 Z" fill="{shade(col, .88)}" {st()}/>')
        front = (f'<path d="M-160,-120 C-172,-250 -100,-312 0,-314 C100,-312 172,-250 160,-120 C150,-170 130,-210 90,-232 '
                 f'C50,-246 20,-244 0,-236 C-20,-244 -50,-246 -90,-232 C-130,-210 -150,-170 -160,-120 Z" fill="{col}" {st()}/>'
                 f'<path d="M-8,-240 C-50,-262 -110,-250 -140,-200 M8,-240 C50,-262 110,-250 140,-200" fill="none" {st(2.5, shade(col, .72))}/>'
                 + both(f'<path d="M-158,-150 C-166,-100 -164,-50 -156,-4" fill="none" {st(2.5, shade(col, .72))}/>'))
        return [("hair_back", "head", back), ("hair_front", "head", front)]
    return part


def spear(hand="hand_r"):
    def part(ctx):
        s = (f'<rect x="-6" y="-190" width="12" height="250" rx="5" fill="#8a5a2a" {st(3)}/>'
             f'<path d="M0,-250 L16,-200 L0,-188 L-16,-200 Z" fill="#d9dde2" {st(3)}/>')
        return [("held", hand, s)]
    return part


def staff(hand="hand_r"):
    def part(ctx):
        s = (f'<rect x="-7" y="-170" width="14" height="230" rx="6" fill="#7a5232" {st(3)}/>'
             f'<path d="M0,-170 C-30,-176 -34,-210 -10,-214" fill="none" {st(10, "#7a5232")}/>')
        return [("held", hand, s)]
    return part


def cross_held(hand="hand_r", gold="#d8ad3c"):
    def part(ctx):
        s = (f'<rect x="-6" y="-150" width="12" height="190" rx="5" fill="{gold}" {st(3)}/>'
             f'<rect x="-34" y="-128" width="68" height="12" rx="5" fill="{gold}" {st(3)}/>'
             f'<circle cx="0" cy="-122" r="7" fill="#b3263a"/>')
        return [("held", hand, s)]
    return part


# ───────────────────────── бороды и усы (v3, по эталонам Nano Banana) ─────────────────────────
# Приёмы эталона: чистая форма с толстым тёмным контуром, почти плоский цвет с тенью снизу,
# окно кожи вокруг рта и подбородок двумя дольками с клинышком бороды по центру;
# усы — плотная лента от носа к уголкам рта, светлый блик по верхнему краю.
# Координаты головы: нос ~-76, рот (у бородатых) -44…-34, подбородок ~0, уши ±150 на -100.

BEARD_INK = "#3a170c"


def _ink(w=4):
    return f'stroke="{BEARD_INK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def _zig(x0, y0, x1, y1, n, amp, side):
    """Мех по краю: n зубчиков от (x0,y0) к (x1,y1), наружу на amp (side=-1 влево, 1 вправо)."""
    d = ""
    for k in range(1, n + 1):
        t0, t1 = (k - .5) / n, k / n
        xm, ym = x0 + (x1 - x0) * t0 + side * amp, y0 + (y1 - y0) * t0
        xe, ye = x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1
        d += f" L{xm:.0f},{ym:.0f} L{xe:.0f},{ye:.0f}"
    return d


def _moustache(col, kind):
    hi = shade(col, 1.35)
    if kind == "handlebar":
        half = ("M0,-62 C-22,-72 -50,-68 -70,-58 C-82,-52 -90,-58 -94,-70 C-98,-58 -94,-44 -80,-40 "
                "C-60,-36 -30,-46 0,-50 Z")
        s = (f'<path d="{half}" fill="{col}" {_ink()}/>'
             f'<path d="M-6,-58 C-26,-64 -50,-60 -68,-50" fill="none" stroke="{hi}" stroke-width="5" stroke-linecap="round" opacity=".8"/>')
    elif kind == "walrus":
        half = "M0,-64 C-24,-72 -58,-66 -70,-46 C-76,-34 -74,-22 -64,-18 C-58,-32 -40,-44 0,-48 Z"
        s = (f'<path d="{half}" fill="{col}" {_ink()}/>'
             f'<path d="M-6,-60 C-28,-64 -52,-58 -64,-44" fill="none" stroke="{hi}" stroke-width="5" stroke-linecap="round" opacity=".8"/>'
             f'<path d="M-24,-50 l-4,10 M-40,-46 l-5,10 M-54,-40 l-5,9" fill="none" stroke="{shade(col, .7)}" stroke-width="2.5" stroke-linecap="round"/>')
    else:  # std — лента к уголкам рта, где она сливается с бородой
        half = "M0,-62 C-20,-70 -46,-66 -60,-52 C-66,-46 -66,-38 -62,-34 C-54,-42 -32,-48 0,-50 Z"
        s = (f'<path d="{half}" fill="{col}" {_ink()}/>'
             f'<path d="M-6,-58 C-24,-62 -44,-58 -56,-48" fill="none" stroke="{hi}" stroke-width="5" stroke-linecap="round" opacity=".8"/>')
    # проборчик под носом — маленькая ямка по центру; лента крупнее, как у эталона
    s = both(s) + f'<path d="M-6,-62 Q0,-56 6,-62" fill="none" {_ink(3)}/>'
    return f'<g transform="translate(0,-58) scale(1.35,1.55) translate(0,58)">{s}</g>'


def moustache_handlebar(col):
    def part(ctx):
        return [("beard", "head", _moustache(col, "handlebar"))]
    return part


def moustache_walrus(col):
    def part(ctx):
        return [("beard", "head", _moustache(col, "walrus"))]
    return part


def _chin_window(skin, deep=0):
    """Окно кожи вокруг рта: верх — под усами, низ — две дольки подбородка с клинышком бороды по центру."""
    d = (f"M-58,-40 C-60,-18 -50,{0 + deep} -30,{2 + deep} C-16,{2 + deep} -8,{-8 + deep} 0,{-12 + deep} "
         f"C8,{-8 + deep} 16,{2 + deep} 30,{2 + deep} C50,{0 + deep} 60,-18 58,-40 C34,-50 -34,-50 -58,-40 Z")
    return f'<path d="{d}" fill="{skin}" {_ink(3.5)}/>'


def _beard(col, skin, bottom, point=0, fur=True):
    """Борода от висков по челюсти; bottom — нижний край, point — клин книзу (длинная борода)."""
    sh = shade(col, .8)
    left_side = _zig(-146, -70, -128, 0, 4, 8, -1) if fur else " L-128,0"
    right_side = _zig(128, 0, 146, -70, 4, 8, 1) if fur else " L146,-70"
    outer = (f"M-140,-170 C-148,-130 -150,-100 -146,-70{left_side} "
             f"C-110,{bottom - 20} -60,{bottom + point * .6} 0,{bottom + point} "
             f"C60,{bottom + point * .6} 110,{bottom - 20} 128,0{right_side} "
             "C150,-100 148,-130 140,-170 C134,-120 122,-84 96,-56 C82,-44 70,-40 58,-40 "
             "L-58,-40 C-70,-40 -82,-44 -96,-56 C-122,-84 -134,-120 -140,-170 Z")
    shadow = (f'<path d="M-120,{bottom - 40} C-60,{bottom - 6 + point * .5} 60,{bottom - 6 + point * .5} 120,{bottom - 40} '
              f'L120,{bottom + point + 10} L-120,{bottom + point + 10} Z" fill="{sh}"/>')
    cid = f"bd{col[1:]}{bottom}{point}"
    return (f'<defs><clipPath id="{cid}"><path d="{outer}"/></clipPath></defs>'
            f'<path d="{outer}" fill="{col}"/><g clip-path="url(#{cid})">{shadow}'
            f'<path d="M-132,-150 C-136,-110 -132,-76 -118,-50" fill="none" stroke="{shade(col, 1.3)}" stroke-width="6" '
            f'stroke-linecap="round" opacity=".55"/></g>'
            f'<path d="{outer}" fill="none" {_ink()}/>')


def beard_full(col):
    """Окладистая борода как у эталона: виски — челюсть — подбородок, окно кожи под ртом, усы."""
    def part(ctx):
        skin = ctx["c"]["skin"]
        s = _beard(col, skin, 46) + _chin_window(skin) + _moustache(col, "std")
        return [("beard", "head", s)]
    return part


def beard_goatee(col):
    """Бородка: усы + клинышек на подбородке, щёки бритые."""
    def part(ctx):
        b = "M-32,-26 C-36,-4 -20,22 0,32 C20,22 36,-4 32,-26 C18,-18 8,-22 0,-16 C-8,-22 -18,-18 -32,-26 Z"
        s = (f'<path d="{b}" fill="{col}" {_ink(3.5)}/>'
             f'<path d="M-14,-12 C-14,6 -8,18 0,24" fill="none" stroke="{shade(col, 1.3)}" stroke-width="4" '
             f'stroke-linecap="round" opacity=".6"/>' + _moustache(col, "std"))
        return [("beard", "head", s)]
    return part


def beard_long(col):
    """Длинная борода клином до груди, с моржовыми усами."""
    def part(ctx):
        skin = ctx["c"]["skin"]
        s = (_beard(col, skin, 60, point=56)
             + f'<path d="M-40,20 C-36,50 -24,80 -10,104 M40,20 C36,50 24,80 10,104" fill="none" '
               f'stroke="{shade(col, .7)}" stroke-width="3" stroke-linecap="round"/>'
             + _chin_window(skin) + _moustache(col, "walrus"))
        return [("beard", "head", s)]
    return part


# ───────────────────────── Польша, пачка 2: XI–XIV вв. ─────────────────────────

def mermaid_tail(col="#3f8a8a", fin="#6fb5a8", top="#e9e0cc"):
    """Сирена: лиф и рыбий хвост вместо юбки и ног (варшавская Сирена)."""
    def part(ctx):
        t = (f'<path d="{TORSO_F}" fill="{top}" {st()}/>'
             f'<path d="M-56,-170 Q0,-130 56,-170" fill="none" {st(6, shade(top, .8))}/>')
        scales = "".join(f'<path d="M{x - 10},{y} q10,10 20,0" fill="none" stroke="{shade(col, .7)}" stroke-width="2.5"/>'
                         for y in range(-30, 90, 18) for x in range(-70 + (10 if (y // 18) % 2 else 0), 80, 20))
        tail = (f'<path d="M-84,-48 C-96,10 -80,60 -40,96 C-20,112 -8,118 0,124 C8,118 20,112 40,96 C80,60 96,10 84,-48 Z" '
                f'fill="{col}" {st()}/>'
                f'<g clip-path="url(#mt)">{scales}</g><defs><clipPath id="mt"><path d="M-84,-48 C-96,10 -80,60 -40,96 '
                f'C-20,112 -8,118 0,124 C8,118 20,112 40,96 C80,60 96,10 84,-48 Z"/></clipPath></defs>'
                f'<path d="M0,120 C-30,130 -70,150 -96,140 C-80,124 -40,110 0,116 C40,110 80,124 96,140 C70,150 30,130 0,120 Z" '
                f'fill="{fin}" {st()}/>')
        return [("torso", "torso", t), ("skirt", "root", tail)]
    return part


def teutonic(steel="#a9b0b8", belt="#5b3a22"):
    """Рыцарь Тевтонского ордена: кольчуга, белое сюрко и белый плащ с чёрным крестом."""
    def part(ctx):
        out = chainmail(steel, "#f4f1ea", belt)(ctx)
        cross = ('<path d="M-14,-150 L14,-150 L14,-118 L46,-118 L46,-90 L14,-90 L14,-40 L-14,-40 L-14,-90 L-46,-90 '
                 'L-46,-118 L-14,-118 Z" fill="#1e1e22" stroke="#3a170c" stroke-width="2"/>')
        cape_ = f'<path d="M-96,-170 C-150,-120 -166,0 -160,96 L160,96 C166,0 150,-120 96,-170 Z" fill="#f4f1ea" {st()}/>'
        return out + [("torso_over", "torso", cross), ("cape_back", "torso", cape_)]
    return part


def hat_mongol(fur="#6b4a2a", top="#a8312f"):
    """Монгольская шапка: меховой отворот, острый верх с кисточкой."""
    def part(ctx):
        s = (f'<path d="M-124,-236 C-120,-306 -50,-360 0,-370 C50,-360 120,-306 124,-236 Z" fill="{top}" {st()}/>'
             f'<path d="M-60,-300 C-30,-336 0,-350 20,-352" fill="none" {st(3, shade(top, 1.3))}/>'
             f'<path d="M-172,-196 C-184,-234 -160,-262 -126,-258 C-60,-272 60,-272 126,-258 C160,-262 184,-234 172,-196 '
             f'C108,-220 -108,-220 -172,-196 Z" fill="{fur}" {st()}/>'
             + "".join(f'<path d="M{x},-246 q4,-12 10,-16" fill="none" {st(2.5, shade(fur, .7))}/>' for x in range(-140, 141, 28))
             + f'<circle cx="0" cy="-376" r="12" fill="#d8ad3c" {st(3)}/>')
        return [("hat", "head", s)]
    return part


def hat_veil(col="#f4f1ea", band=None):
    """Средневековое покрывало замужней дамы: вимпл вокруг лица, ткань на плечи; поверх — обруч или корона."""
    def part(ctx):
        back = (f'<path d="M-176,-200 C-190,-100 -184,0 -150,60 L150,60 C184,0 190,-100 176,-200 C160,-310 -160,-310 -176,-200 Z" '
                f'fill="{shade(col, .93)}" {st()}/>')
        front = (f'<path d="M-170,-150 C-176,-262 -100,-318 0,-320 C100,-318 176,-262 170,-150 C156,-206 120,-246 0,-250 '
                 f'C-120,-246 -156,-206 -170,-150 Z" fill="{col}" {st()}/>'
                 + both(f'<path d="M-170,-150 C-176,-100 -166,-40 -150,0 C-140,-30 -138,-80 -146,-140 Z" fill="{col}" {st(3)}/>'))
        out = [("hair_back", "head", back), ("hair_front", "head", front)]
        if band:
            out.append(("hat", "head", f'<path d="M-150,-240 C-60,-262 60,-262 150,-240 L150,-218 C60,-240 -60,-240 -150,-218 Z" '
                                       f'fill="{band}" {st(3)}/>'))
        return out
    return part


def trumpet(hand="hand_r", gold="#d8ad3c"):
    def part(ctx):
        s = (f'<rect x="-6" y="-120" width="12" height="130" rx="5" fill="{gold}" {st(3)}/>'
             f'<path d="M-6,-120 L-26,-170 L26,-170 L6,-120 Z" fill="{gold}" {st(3)}/>'
             f'<rect x="-14" y="-60" width="28" height="18" rx="4" fill="#a8312f" {st(2.5)}/>')
        return [("held", hand, s)]
    return part


def pickaxe(hand="hand_r"):
    def part(ctx):
        s = (f'<rect x="-6" y="-150" width="12" height="190" rx="5" fill="#7a5232" {st(3)}/>'
             f'<path d="M-60,-140 C-30,-170 30,-170 60,-140 L54,-130 C26,-150 -26,-150 -54,-130 Z" fill="#9aa0a8" {st(3)}/>')
        return [("held", hand, s)]
    return part


def hat_cap(col="#a8312f", fur=None):
    """Мягкая шапочка-шаперон горожанина; fur — меховая опушка купца."""
    def part(ctx):
        s = (f'<path d="M-150,-214 C-178,-280 -110,-336 -10,-340 C90,-344 176,-310 172,-252 C170,-226 156,-214 148,-212 '
             f'C90,-232 -90,-232 -150,-214 Z" fill="{col}" {st()}/>'
             f'<path d="M-96,-304 C-40,-326 40,-326 110,-300 M-30,-238 C10,-262 70,-282 130,-282" fill="none" {st(3, shade(col, .75))}/>'
             f'<path d="M-90,-318 C-50,-332 -10,-334 30,-330" fill="none" {st(4, shade(col, 1.3))}/>')
        if fur:
            s += (f'<path d="M-160,-206 C-168,-236 -150,-252 -120,-250 C-60,-262 60,-262 120,-250 C150,-252 168,-236 160,-206 '
                  f'C100,-224 -100,-224 -160,-206 Z" fill="{fur}" {st()}/>')
        return [("hat", "head", s)]
    return part


# ───────────────────────── Польша, пачка 3: Ягеллоны, Ренессанс ─────────────────────────

def doublet(col="#2a2a2e", trim="#d4a63c", chain=True, shirt="#f4f1ea"):
    """Ренессансный дублет: широкие плечи, разрез с рубашкой, золотая цепь; подол-баска."""
    def part(ctx):
        hem = 30 if ctx["pose"].get("sit") else 46
        t = (f'<path d="{TORSO_M}" fill="{col}" {st()}/>'
             f'<path d="M-30,-176 L0,-120 L30,-176 Z" fill="{shirt}" {st(3)}/>'
             + "".join(f'<path d="M{x},-150 L{x},-30" fill="none" {st(5, trim)}/>' for x in (-60, 60)))
        over = (f'<path d="M-106,-30 C-40,-18 40,-18 106,-30 L106,-10 C40,2 -40,2 -106,-10 Z" fill="{shade(col, .8)}" {st(3)}/>')
        if chain:
            over += (f'<path d="M-70,-168 C-60,-100 60,-100 70,-168" fill="none" {st(8, trim)}/>'
                     f'<circle cx="0" cy="-112" r="14" fill="{trim}" {st(3)}/>')
        skirt = _hem_skirt(col, hem, trim, wide=1.05, folds=False)
        return [("torso", "torso", t), ("torso_over", "torso", over), ("skirt", "root", skirt)]
    return part


def hat_beret(col="#2a2a2e", feather="#f4f1ea"):
    """Плоский ренессансный берет набок, с пером."""
    def part(ctx):
        s = (f'<path d="M-170,-246 C-180,-286 -120,-318 0,-322 C120,-318 180,-286 170,-246 C110,-262 -110,-262 -170,-246 Z" '
             f'fill="{col}" {st()}/>'
             f'<path d="M-150,-252 C-80,-270 80,-270 150,-252" fill="none" {st(3, shade(col, 1.5))}/>')
        if feather:
            s += (f'<path d="M80,-290 C120,-330 170,-340 196,-316 C160,-312 120,-300 92,-276 Z" fill="{feather}" {st(3)}/>'
                  f'<circle cx="80" cy="-282" r="10" fill="#d8ad3c" {st(2.5)}/>')
        return [("hat", "head", s)]
    return part


def hat_turban(col="#f4f1ea", jewel="#2f9a8a"):
    """Османский тюрбан с пером и камнем."""
    def part(ctx):
        s = (f'<path d="M-170,-226 C-190,-300 -110,-372 0,-376 C110,-372 190,-300 170,-226 C110,-250 -110,-250 -170,-226 Z" '
             f'fill="{col}" {st()}/>'
             + "".join(f'<path d="M-160,{y} C-80,{y - 40} 80,{y - 40} 160,{y}" fill="none" {st(3, shade(col, .8))}/>'
                       for y in (-246, -280, -314))
             + f'<circle cx="0" cy="-300" r="16" fill="{jewel}" {st(3)}/>'
             f'<path d="M0,-312 C-10,-360 10,-390 24,-400 C20,-370 16,-340 8,-312 Z" fill="#f4f1ea" {st(2.5)}/>')
        return [("hat", "head", s)]
    return part


# ───────────────────────── Польша, пачка 4: Речь Посполитая, XVI–XVIII вв. ─────────────────────────

def kontusz(zupan="#e9d8a8", kontusz_col="#a8312f", sash="#d4a63c", sash2="#2f6a4a"):
    """Шляхетский наряд: жупан до щиколоток, поверх кунтуш с откидными рукавами, пояс-слуцкий кушак."""
    def part(ctx):
        hem = 50 if ctx["pose"].get("sit") else 92
        t = (f'<path d="{TORSO_M}" fill="{zupan}" {st()}/>'
             + "".join(f'<circle cx="0" cy="{y}" r="5" fill="#c9a24a" {st(2)}/>' for y in (-150, -122, -94, -66)))
        coat = (f'<path d="M-74,-172 C-100,-170 -112,-156 -112,-130 L-104,20 L-30,20 L-26,-150 C-34,-166 -52,-174 -74,-172 Z" '
                f'fill="{kontusz_col}" {st()}/>'
                f'<path d="M74,-172 C100,-170 112,-156 112,-130 L104,20 L30,20 L26,-150 C34,-166 52,-174 74,-172 Z" '
                f'fill="{kontusz_col}" {st()}/>')
        stripes = "".join(f'<path d="M-108,{y} C-40,{y + 12} 40,{y + 12} 108,{y}" fill="none" stroke="{sash2}" stroke-width="4"/>'
                          for y in (-40, -28, -16))
        over = (coat + f'<path d="M-108,-50 C-40,-38 40,-38 108,-50 L108,-6 C40,6 -40,6 -108,-6 Z" fill="{sash}" {st(3)}/>'
                + stripes + f'<path d="M-30,-6 L-40,52 L-18,52 L-12,-4 Z" fill="{sash}" {st(3)}/>')
        skirt = (_hem_skirt(zupan, hem, folds=True)
                 + f'<path d="M-96,-44 L-110,{hem} L-30,{hem} L-30,-44 Z M96,-44 L110,{hem} L30,{hem} L30,-44 Z" '
                   f'fill="{kontusz_col}" {st()}/>')
        return [("torso", "torso", t), ("torso_over", "torso", over), ("skirt", "root", skirt)]
    return part


def hussar_wings(col="#7a5232", feather="#f4f1ea"):
    """Крылья крылатого гусара — деревянная рама с перьями за спиной."""
    def part(ctx):
        def wing(s):
            feathers = "".join(f'<path d="M{s * 70},{y} C{s * 120},{y - 30} {s * 150},{y - 40} {s * 160},{y - 70} '
                               f'C{s * 140},{y - 50} {s * 110},{y - 30} {s * 78},{y + 6} Z" fill="{feather}" {st(2.5)}/>'
                               for y in range(-260, -40, 34))
            return (f'<path d="M{s * 60},-40 C{s * 80},-160 {s * 110},-280 {s * 150},-340" fill="none" {st(12, col)}/>'
                    f'<path d="M{s * 60},-40 C{s * 80},-160 {s * 110},-280 {s * 150},-340" fill="none" stroke="{shade(col, 1.3)}" '
                    f'stroke-width="5" stroke-linecap="round"/>' + feathers)
        return [("cape_back", "torso", wing(-1) + wing(1))]
    return part


def hat_wide(col="#2a2a2e", feather="#e9e0cc"):
    """Широкополая шляпа XVII века с пером (шведы, иноземцы)."""
    def part(ctx):
        s = (f'<path d="M-110,-250 C-110,-320 -60,-350 0,-352 C60,-350 110,-320 110,-250 Z" fill="{col}" {st()}/>'
             f'<path d="M-210,-238 C-200,-266 -120,-280 0,-282 C120,-280 200,-266 210,-238 C150,-224 -150,-224 -210,-238 Z" '
             f'fill="{col}" {st()}/>'
             f'<rect x="-110" y="-272" width="220" height="16" rx="6" fill="{shade(col, 1.6)}" {st(2.5)}/>'
             f'<path d="M60,-270 C110,-330 170,-330 200,-300 C150,-300 110,-286 76,-256 Z" fill="{feather}" {st(2.5)}/>')
        return [("hat", "head", s)]
    return part


def ruff(col="#f4f1ea"):
    """Брыжи — гофрированный воротник (французы, испанцы)."""
    def part(ctx):
        s = "".join(f'<circle cx="{x}" cy="-176" r="20" fill="{col}" {st(2.5)}/>' for x in range(-70, 71, 20))
        return [("neck", "head", f'<g transform="translate(0,190)">{s}</g>')]
    return part


def hat_horns(col="#3b1a12"):
    """Рожки (чёрт из легенды о Твардовском)."""
    def part(ctx):
        h = f'<path d="M-90,-270 C-110,-320 -130,-350 -150,-370 C-120,-360 -90,-330 -70,-290 Z" fill="{col}" {st()}/>'
        return [("hat", "head", both(h))]
    return part


def devil_tail(col="#a8262e"):
    def part(ctx):
        s = (f'<path d="M60,40 C140,60 170,0 150,-60" fill="none" {st(16, "#3a170c")}/>'
             f'<path d="M60,40 C140,60 170,0 150,-60" fill="none" stroke="{col}" stroke-width="9" stroke-linecap="round"/>'
             f'<path d="M150,-60 L130,-90 L176,-84 Z" fill="{col}" {st(3)}/>')
        return [("cape_back", "root", s)]
    return part


# ───────────────────────── Польша, пачка 5: XVIII–XX вв. ─────────────────────────

def hair_wig(col="#ece8e2"):
    """Напудренный парик XVIII века: валики-букли на висках, хвост сзади."""
    def part(ctx):
        back = (f'<path d="M-150,-200 C-166,-150 -160,-90 -140,-60 L140,-60 C160,-90 166,-150 150,-200 '
                f'C130,-300 -130,-300 -150,-200 Z" fill="{shade(col, .9)}" {st()}/>')
        front = (f'<path d="M-150,-170 C-160,-264 -96,-312 0,-314 C96,-312 160,-264 150,-170 C140,-210 110,-246 0,-250 '
                 f'C-110,-246 -140,-210 -150,-170 Z" fill="{col}" {st()}/>'
                 + both(f'<ellipse cx="-150" cy="-150" rx="26" ry="18" fill="{col}" {st(3)}/>'
                        f'<ellipse cx="-152" cy="-116" rx="26" ry="18" fill="{col}" {st(3)}/>')
                 + f'<path d="M-60,-298 C-20,-306 20,-306 60,-298" fill="none" {st(3, "#ffffff")}/>')
        return [("hair_back", "head", back), ("hair_front", "head", front)]
    return part


def hat_tricorne(col="#1e1e22", trim="#d4a63c"):
    def part(ctx):
        # тулья позади + поля, загнутые вверх к двум боковым углам, третий угол смотрит вперёд-вниз
        brim_top = "M-214,-318 C-150,-286 -60,-262 0,-238 C60,-262 150,-286 214,-318"
        s = (f'<path d="M-150,-226 C-128,-250 -122,-334 0,-358 C122,-334 128,-250 150,-226 Z" fill="{shade(col, .85)}" {st()}/>'
             f'<path d="{brim_top} C200,-270 160,-236 100,-224 C60,-218 20,-212 0,-206 C-20,-212 -60,-218 -100,-224 '
             f'C-160,-236 -200,-270 -214,-318 Z" fill="{col}" {st()}/>'
             f'<path d="{brim_top}" fill="none" {st(7, trim)}/>'
             f'<path d="M-150,-262 C-100,-246 -50,-236 -14,-224" fill="none" {st(3, shade(col, 1.6))}/>')
        return [("hat", "head", s)]
    return part


def hat_bicorne(col="#1e1e22", cockade="#a8312f"):
    def part(ctx):
        s = (f'<path d="M-230,-236 C-180,-300 -80,-350 0,-356 C80,-350 180,-300 230,-236 C120,-262 -120,-262 -230,-236 Z" '
             f'fill="{col}" {st()}/>'
             f'<path d="M-226,-240 C-120,-266 120,-266 226,-240" fill="none" {st(5, "#c9a24a")}/>'
             f'<circle cx="60" cy="-300" r="18" fill="{cockade}" {st(3)}/><circle cx="60" cy="-300" r="8" fill="#f4f1ea"/>')
        return [("hat", "head", s)]
    return part


def hat_czapka(col="#a8312f", band="#1e1e22", plume="#f4f1ea"):
    """Уланская конфедератка-чапка с квадратным верхом и султаном."""
    def part(ctx):
        s = (f'<path d="M-150,-240 L-130,-300 L130,-300 L150,-240 Z" fill="{band}" {st()}/>'
             f'<path d="M-160,-300 L-120,-380 L120,-380 L160,-300 Z" fill="{col}" {st()}/>'
             f'<path d="M-160,-300 L0,-330 L160,-300 M-120,-380 L0,-330 L120,-380" fill="none" {st(3, "#d4a63c")}/>'
             f'<path d="M-90,-386 C-110,-440 -60,-470 -40,-440 C-30,-420 -50,-396 -76,-382 Z" fill="{plume}" {st(3)}/>'
             f'<path d="M-130,-246 C-60,-262 60,-262 130,-246" fill="none" {st(4, "#c9c4b8")}/>')
        return [("hat", "head", s)]
    return part


def hat_krakuska(col="#2f4a7a", fur="#2a2a2e", feather="#2f9a8a"):
    """Краковская шапка косиньера: высокий верх, мех, павлинье перо."""
    def part(ctx):
        s = (f'<path d="M-130,-246 C-140,-330 -70,-372 0,-374 C70,-372 140,-330 130,-246 Z" fill="{col}" {st()}/>'
             f'<path d="M-164,-210 C-172,-246 -150,-262 -124,-260 C-60,-272 60,-272 124,-260 C150,-262 172,-246 164,-210 '
             f'C100,-228 -100,-228 -164,-210 Z" fill="{fur}" {st()}/>'
             f'<path d="M90,-300 C120,-380 150,-420 170,-460" fill="none" {st(4, "#2f6a4a")}/>'
             f'<ellipse cx="172" cy="-466" rx="16" ry="12" fill="{feather}" {st(3)}/><circle cx="172" cy="-466" r="5" fill="#1e3a6a"/>')
        return [("hat", "head", s)]
    return part


def hat_top(col="#1e1e22"):
    def part(ctx):
        s = (f'<path d="M-110,-250 L-120,-420 C-60,-432 60,-432 120,-420 L110,-250 Z" fill="{col}" {st()}/>'
             f'<path d="M-200,-246 C-150,-270 150,-270 200,-246 C150,-226 -150,-226 -200,-246 Z" fill="{col}" {st()}/>'
             f'<rect x="-112" y="-290" width="224" height="22" fill="{shade(col, 1.8)}" {st(2.5)}/>'
             f'<path d="M-80,-410 L-86,-300" fill="none" stroke="#ffffff" stroke-width="6" opacity=".25"/>')
        return [("hat", "head", s)]
    return part


def hat_pickelhaube(col="#1e1e22", metal="#c9a24a"):
    def part(ctx):
        s = (f'<path d="M-150,-226 C-150,-300 -80,-340 0,-342 C80,-340 150,-300 150,-226 C90,-240 -90,-240 -150,-226 Z" '
             f'fill="{col}" {st()}/>'
             f'<path d="M-170,-210 C-120,-232 120,-232 170,-210 L150,-200 C90,-220 -90,-220 -150,-200 Z" fill="{col}" {st(3)}/>'
             f'<path d="M-16,-336 L0,-420 L16,-336 Z" fill="{metal}" {st(3)}/>'
             f'<path d="M-40,-300 C-40,-260 40,-260 40,-300 C30,-320 -30,-320 -40,-300 Z" fill="{metal}" {st(3)}/>')
        return [("hat", "head", s)]
    return part


def glasses(col="#3a2a20", kind="round"):
    """Очки (Вильсон) или пенсне."""
    def part(ctx):
        r = 34 if kind == "round" else 28
        s = (f'<circle cx="-78" cy="-101" r="{r}" fill="#dfe8f0" fill-opacity=".25" {st(5, col)}/>'
             f'<circle cx="78" cy="-101" r="{r}" fill="#dfe8f0" fill-opacity=".25" {st(5, col)}/>'
             f'<path d="M-44,-105 Q0,-117 44,-105" fill="none" {st(5, col)}/>')
        if kind == "round":
            s += f'<path d="M-112,-105 L-146,-113 M112,-105 L146,-113" fill="none" {st(5, col)}/>'
        return [("features", "head", s)]
    return part


def frock(col="#4b6a9a", vest="#e9d8a8", trim="#d4a63c", cravat="#f4f1ea"):
    """Кафтан XVIII века: полы до колен, камзол, шейный платок."""
    def part(ctx):
        hem = 40 if ctx["pose"].get("sit") else 70
        t = (f'<path d="{TORSO_M}" fill="{col}" {st()}/>'
             f'<path d="M-40,-174 L40,-174 L46,20 L-46,20 Z" fill="{vest}" {st(3)}/>'
             + "".join(f'<circle cx="0" cy="{y}" r="5" fill="{trim}" {st(2)}/>' for y in (-130, -100, -70, -40, -10))
             + f'<path d="M-26,-176 C-30,-140 30,-140 26,-176 C14,-150 -14,-150 -26,-176 Z" fill="{cravat}" {st(3)}/>'
             + both(f'<path d="M-46,-170 L-50,20" fill="none" {st(6, trim)}/>'))
        skirt = (f'<path d="M-96,-44 C-104,0 -112,{hem - 20} -116,{hem} L-40,{hem} L-46,-44 Z" fill="{col}" {st()}/>'
                 f'<path d="M96,-44 C104,0 112,{hem - 20} 116,{hem} L40,{hem} L46,-44 Z" fill="{col}" {st()}/>'
                 f'<path d="M-112,{hem - 10} L-44,{hem - 10} M112,{hem - 10} L44,{hem - 10}" fill="none" {st(5, trim)}/>')
        return [("torso", "torso", t), ("skirt", "root", skirt)]
    return part


def uniform(col="#2f4a7a", facing="#a8312f", trim="#d4a63c", sash=None, epaulettes=True):
    """Мундир эпохи Наполеона/XIX в.: лацканы, пуговицы в два ряда, эполеты, кушак."""
    def part(ctx):
        hem = 30 if ctx["pose"].get("sit") else 46
        t = (f'<path d="{TORSO_M}" fill="{col}" {st()}/>'
             f'<path d="M-40,-176 L-24,-60 L24,-60 L40,-176 L22,-176 L0,-110 L-22,-176 Z" fill="{facing}" {st(3)}/>'
             + "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="{trim}" {st(2)}/>' for x in (-16, 16) for y in (-150, -120, -90))
             + f'<path d="M-40,-178 L40,-178 L36,-160 L-36,-160 Z" fill="{facing}" {st(3)}/>')
        over = ""
        if sash:
            over += f'<path d="M-106,-36 C-40,-24 40,-24 106,-36 L106,-12 C40,0 -40,0 -106,-12 Z" fill="{sash}" {st(3)}/>'
        else:
            over += f'<rect x="-106" y="-30" width="212" height="20" rx="5" fill="#f4f1ea" {st(3)}/>'
        if epaulettes:
            over += both(f'<path d="M-104,-170 C-120,-166 -128,-150 -120,-140 L-70,-150 L-70,-170 Z" fill="{trim}" {st(3)}/>'
                         + "".join(f'<path d="M{x},-142 l-2,14" fill="none" {st(3, trim)}/>' for x in (-118, -108, -98, -88)))
        skirt = _hem_skirt(col, hem, facing, folds=False)
        return [("torso", "torso", t), ("torso_over", "torso", over), ("skirt", "root", skirt)]
    return part


def sukmana(col="#f1ece2", trim="#a8312f", belt="#a8312f"):
    """Крестьянская сукмана косиньера: длинный белый кафтан с красной тесьмой."""
    def part(ctx):
        hem = 40 if ctx["pose"].get("sit") else 74
        t = (f'<path d="{TORSO_M}" fill="{col}" {st()}/>'
             f'<path d="M0,-176 L0,20" fill="none" {st(5, trim)}/>'
             + both(f'<path d="M-36,-176 C-40,-150 -30,-130 -10,-120" fill="none" {st(5, trim)}/>'))
        over = f'<path d="M-106,-30 C-40,-18 40,-18 106,-30 L106,-10 C40,2 -40,2 -106,-10 Z" fill="{belt}" {st(3)}/>'
        return [("torso", "torso", t), ("torso_over", "torso", over), ("skirt", "root", _hem_skirt(col, hem, trim))]
    return part


def suit(col="#2a2a2e", shirt="#f4f1ea", tie="#a8312f", long=True):
    """Костюм XIX–XX вв.: сюртук или пиджак, белая рубашка, галстук."""
    def part(ctx):
        hem = 34 if ctx["pose"].get("sit") else (70 if long else 30)
        t = (f'<path d="{TORSO_M}" fill="{col}" {st()}/>'
             f'<path d="M-36,-176 L0,-90 L36,-176 Z" fill="{shirt}" {st(3)}/>'
             f'<path d="M-8,-170 L8,-170 L10,-110 L0,-96 L-10,-110 Z" fill="{tie}" {st(2.5)}/>'
             + both(f'<path d="M-36,-176 L-6,-80 L-30,-60" fill="none" {st(4, shade(col, 1.5))}/>')
             + "".join(f'<circle cx="-8" cy="{y}" r="5" fill="{shade(col, 1.6)}"/>' for y in (-60, -30)))
        skirt = (f'<path d="M-96,-44 C-104,0 -110,{hem - 20} -112,{hem} L-6,{hem} L-6,-44 Z" fill="{col}" {st()}/>'
                 f'<path d="M96,-44 C104,0 110,{hem - 20} 112,{hem} L6,{hem} L6,-44 Z" fill="{col}" {st()}/>')
        return [("torso", "torso", t), ("skirt", "root", skirt)]
    return part


def scythe(hand="hand_r"):
    """Коса, насаженная торчком, — оружие косиньеров."""
    def part(ctx):
        s = (f'<rect x="-6" y="-230" width="12" height="290" rx="5" fill="#8a5a2a" {st(3)}/>'
             f'<path d="M0,-226 C10,-280 20,-330 14,-380 C30,-330 30,-270 6,-214 Z" fill="#d9dde2" {st(3)}/>')
        return [("held", hand, s)]
    return part


def flag_held(hand="hand_r", col="#f4f1ea", col2="#a8312f"):
    """Бело-красный флаг на древке."""
    def part(ctx):
        s = (f'<rect x="-5" y="-260" width="10" height="320" rx="4" fill="#7a5232" {st(3)}/>'
             f'<path d="M5,-256 L130,-246 L130,-196 L5,-206 Z" fill="{col}" {st(3)}/>'
             f'<path d="M5,-206 L130,-196 L130,-146 L5,-156 Z" fill="{col2}" {st(3)}/>')
        return [("held", hand, s)]
    return part


def book(hand="hand_r", col="#7a2a2a"):
    def part(ctx):
        s = (f'<rect x="-30" y="-40" width="60" height="76" rx="5" fill="{col}" {st(3)}/>'
             f'<rect x="-24" y="-34" width="48" height="64" rx="3" fill="none" {st(2.5, "#d4a63c")}/>')
        return [("held", hand, s)]
    return part


def flask(hand="hand_r"):
    """Колба с зелёным светящимся содержимым (лаборатория Кюри)."""
    def part(ctx):
        s = (f'<path d="M-10,-60 L-10,-20 L-34,24 C-40,36 -30,44 -18,44 L18,44 C30,44 40,36 34,24 L10,-20 L10,-60 Z" '
             f'fill="#e8f2f2" fill-opacity=".8" {st(3)}/>'
             f'<path d="M-28,20 L28,20 L34,30 C38,40 30,44 18,44 L-18,44 C-30,44 -38,40 -34,30 Z" fill="#7fe0a0"/>'
             f'<rect x="-14" y="-68" width="28" height="10" rx="3" fill="#c9c4b8" {st(2.5)}/>')
        return [("held", hand, s)]
    return part


# ───────────────────────── существа: Вавельский дракон ─────────────────────────

def dragon(col="#5f9a4a", belly="#e9d8a0", wing="#a8312f"):
    """Чиби-дракон целиком на кости корня: голова с мордой и рожками, брюшко, крылышки, хвост.
    Выражение глаз — по позе (злой, довольный, лопнувший)."""
    def part(ctx):
        expr = ctx["expr"]
        dark = shade(col, .7)
        wings = both(f'<path d="M-90,-200 C-170,-300 -260,-280 -280,-220 C-240,-230 -220,-200 -200,-170 '
                     f'C-180,-200 -150,-200 -130,-160 Z" fill="{wing}" {st()}/>'
                     f'<path d="M-110,-190 L-250,-230 M-130,-170 L-200,-180" fill="none" {st(3, shade(wing, .7))}/>')
        tail = (f'<path d="M80,-20 C200,0 250,-80 220,-150 C210,-170 236,-176 250,-160 C290,-90 240,60 70,40 Z" '
                f'fill="{col}" {st()}/>'
                f'<path d="M244,-164 L268,-196 L276,-150 Z" fill="{wing}" {st(3)}/>')
        legs = both(f'<path d="M-80,10 C-90,60 -100,80 -70,90 L-30,90 C-20,70 -30,40 -40,10 Z" fill="{col}" {st()}/>'
                    f'<path d="M-90,88 l-8,10 M-74,90 l-4,12 M-58,90 l0,12" fill="none" {st(4, "#f4f1ea")}/>')
        body = (f'<ellipse cx="0" cy="-90" rx="150" ry="130" fill="{col}" {st()}/>'
                f'<ellipse cx="0" cy="-60" rx="90" ry="90" fill="{belly}" {st(3)}/>'
                + "".join(f'<path d="M-70,{y} Q0,{y + 14} 70,{y}" fill="none" {st(3, shade(belly, .78))}/>' for y in (-110, -80, -50, -20)))
        spikes = "".join(f'<path d="M{x},{y} l14,-28 l14,28 Z" fill="{wing}" {st(3)}/>'
                         for x, y in ((-40, -470), (-14, -478), (12, -474)))
        horns = both(f'<path d="M-80,-430 C-100,-480 -110,-500 -126,-510 C-96,-500 -70,-470 -56,-440 Z" fill="#f1ece2" {st()}/>')
        head = (f'<ellipse cx="0" cy="-330" rx="150" ry="130" fill="{col}" {st()}/>'
                f'<ellipse cx="0" cy="-260" rx="110" ry="70" fill="{shade(col, 1.15)}" {st(3)}/>'
                + both('<ellipse cx="-34" cy="-268" rx="10" ry="14" fill="#2a3a20"/>'))
        if expr == "dead":
            eyes = both(f'<g transform="translate(-60,-360)"><path d="M-18,-18 L18,18 M18,-18 L-18,18" {st(8, "#2a1208")}/></g>')
            mouth = f'<path d="M-40,-222 Q0,-236 40,-222" fill="none" {st(5)}/>'
        else:
            lid = {"happy": "M-30,-4 Q0,-30 30,-4", "sad": "M-30,-14 Q0,-2 30,-14", "sly": "M-30,-6 L30,-16"}.get(expr, "M-30,-12 L30,-2")
            eyes = both(f'<g transform="translate(-62,-366)"><ellipse rx="34" ry="38" fill="#fbf4c0" {st(4)}/>'
                        f'<ellipse cx="6" cy="6" rx="12" ry="24" fill="#2a1208"/><circle cx="0" cy="-8" r="6" fill="#fff"/>'
                        f'<path d="{lid}" fill="none" {st(8, dark)}/></g>')
            mouth = (f'<path d="M-70,-224 Q0,-180 70,-224" fill="#7a1a12" {st(4)}/>'
                     + both('<path d="M-50,-222 l8,16 l8,-16 Z" fill="#f4f1ea" stroke="#3a170c" stroke-width="2"/>'))
        smoke = ""
        if expr in ("neutral", "sly"):
            smoke = (f'<circle cx="140" cy="-280" r="18" fill="#c9c4b8" opacity=".8"/>'
                     f'<circle cx="170" cy="-310" r="24" fill="#c9c4b8" opacity=".6"/>')
        s = wings + tail + legs + body + spikes + horns + head + eyes + mouth + smoke
        return [("torso", "root", s)]
    return part
