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


def _eye(expr, skin, iris, side=-1, look=0):
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
        e += (f'<path d="M-40,4 C-36,-26 -6,-37 18,-33 C32,-29 40,-14 40,0" fill="none" {st(6, "#2a1208")}/>'
              f'<path d="M-38,-4 L-46,-10" fill="none" {st(4, "#2a1208")}/>')
    return e


BROW = "M-32,10 C-24,-8 8,-12 30,-2 C26,6 10,4 0,5 C-12,6 -22,10 -32,16 Z"   # мягкая короткая дуга


def face(eyes_iris="#6b3a1f", brow="#6b4a2b", brow_w=6, bushy=False, nose=None):
    def part(ctx):
        expr, skin = ctx["expr"], ctx["c"]["skin"]
        look = ctx["pose"].get("look", 0)
        nz = nose or shade(skin, .88)
        f = (f'<defs><radialGradient id="blush"><stop offset="0" stop-color="#f6857a" stop-opacity=".55"/>'
             f'<stop offset=".6" stop-color="#f6857a" stop-opacity=".25"/>'
             f'<stop offset="1" stop-color="#f6857a" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="nose" cx=".45" cy=".4"><stop offset="0" stop-color="{shade(nz, 1.05)}"/>'
             f'<stop offset="1" stop-color="{shade(nz, .93)}"/></radialGradient></defs>')
        f += both('<ellipse cx="-100" cy="-86" rx="62" ry="42" fill="url(#blush)"/>')
        for s in (-1, 1):
            f += f'<g transform="translate({s * 78},-127) scale({-s * 0.86},1.04)">{_eye(expr, skin, eyes_iris, s, look)}</g>'
        # брови: наклон по выражению (внутренний конец вверх — грусть, вниз — хитрость)
        tilt = {"sad": 16, "sly": -22, "happy": 5, "dead": 10}.get(expr, 0)
        bdy = {"sad": 8, "sly": 14}.get(expr, 0)      # грусть и хитрость прижимают брови к глазам
        for s in (-1, 1):
            b = f'<path d="{BROW}" fill="{brow}" {st(2.5, shade(brow, .72))}/>'
            if bushy:
                b = (f'<path d="M-38,12 C-28,-14 10,-18 34,-4 C30,6 14,4 0,6 C-14,8 -28,12 -38,18 Z" fill="{brow}" {st(2.5, shade(brow, .7))}/>'
                     f'<path d="M-28,8 l6,-10 M-14,4 l6,-12 M0,2 l6,-12 M14,0 l6,-10" fill="none" {st(2.5, shade(brow, 1.3))}/>')
            f += f'<g transform="translate({s * 74},{-186 + bdy}) scale({-s * 1.1},1.05) rotate({-tilt})">{b}</g>'
        f += f'<ellipse cx="0" cy="-102" rx="12" ry="10" fill="url(#nose)"/>'
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
        return [("features", "head", f'<g transform="translate(0,{FDY})">{f + mouth}</g>')]
    return part


# ───────────────────────── волосы, бороды, уборы ─────────────────────────

def moustache_handlebar(col):
    half = ('M2,-102 C-14,-116 -42,-116 -60,-100 C-70,-91 -82,-93 -86,-104 C-88,-114 -82,-120 -75,-117 '
            'C-79,-109 -73,-103 -65,-107 C-50,-88 -22,-82 2,-90 Z')
    def part(ctx):
        s = f'<path d="{half}" fill="{col}" {st()}/>'
        s += f'<path d="M-10,-98 C-26,-104 -42,-102 -54,-96" fill="none" {st(3, shade(col, 1.45))}/>'
        s += f'<path d="M-8,-94 C-26,-90 -44,-94 -58,-100" fill="none" {st(2, shade(col, .7))}/>'
        return [("beard", "head", f'<g transform="translate(0,{FDY - 84}) scale(1.22) translate(0,96)">{both(s)}</g>')]
    return part


def moustache_walrus(col):
    half = 'M2,-104 C-30,-116 -70,-108 -88,-82 C-94,-70 -84,-62 -74,-70 C-60,-84 -30,-84 2,-86 Z'
    def part(ctx):
        s = f'<path d="{half}" fill="{col}" {st()}/>'
        s += f'<path d="M-14,-100 C-36,-102 -56,-94 -70,-80 M-20,-92 C-40,-92 -54,-86 -62,-78" fill="none" {st(2.5, shade(col, .78))}/>'
        return [("beard", "head", f'<g transform="translate(0,{FDY})">{both(s)}</g>')]
    return part


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


def beard_full(col):
    def part(ctx):
        s = (f'<path d="M-150,-150 C-150,-60 -90,10 0,16 C90,10 150,-60 150,-150 C132,-110 100,-96 62,-96 '
             f'C40,-56 -40,-56 -62,-96 C-100,-96 -132,-110 -150,-150 Z" fill="{col}" {st()}/>'
             f'<path d="M-90,-60 C-60,-30 -30,-16 0,-14 M90,-60 C60,-30 30,-16 0,-14 M-120,-110 C-110,-80 -100,-60 -80,-40 '
             f'M120,-110 C110,-80 100,-60 80,-40" fill="none" {st(2.5, shade(col, .72))}/>')
        return [("beard", "head", s)]
    return part


def beard_goatee(col):
    def part(ctx):
        s = f'<path d="M-30,-40 C-30,-10 -14,8 0,12 C14,8 30,-10 30,-40 C16,-32 -16,-32 -30,-40 Z" fill="{col}" {st()}/>'
        return [("beard", "head", s)]
    return part


def hat_helmet(col="#b9bfc6", trim="#8a6a2a"):
    def part(ctx):
        s = (f'<path d="M-158,-212 C-160,-296 -90,-346 0,-346 C90,-346 160,-296 158,-212 C100,-228 -100,-228 -158,-212 Z" '
             f'fill="{col}" {st()}/>'
             f'<rect x="-160" y="-226" width="320" height="22" rx="8" fill="{trim}" {st(3)}/>'
             f'<rect x="-9" y="-226" width="18" height="96" rx="6" fill="{col}" {st(3)}/>'
             f'<path d="M0,-346 L0,-230" fill="none" {st(3, shade(col, .7))}/>'
             f'<ellipse cx="-60" cy="-300" rx="30" ry="14" fill="#fff" opacity=".35"/>')
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
    """Редкие волосы с высокими залысинами: шапочка сверху и виски."""
    def part(ctx):
        s = (f'<path d="M-140,-124 C-152,-222 -112,-312 0,-314 C112,-312 152,-222 140,-124 '
             f'C126,-146 114,-170 108,-192 C94,-214 66,-226 30,-230 C10,-232 -10,-232 -30,-230 C-66,-226 -94,-214 -108,-192 '
             f'C-114,-170 -126,-146 -140,-124 Z" fill="{col}" {st()}/>'
             + both(f'<path d="M-140,-150 C-144,-190 -132,-226 -106,-250 M-126,-140 C-130,-170 -124,-196 -110,-214 '
                    f'M-60,-282 C-80,-276 -100,-266 -114,-252" fill="none" {st(2.5, shade(col, .78))}/>')
             + f'<path d="M-60,-300 C-20,-306 20,-306 60,-300" fill="none" {st(3, shade(col, 1.25))}/>')
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


def hat_laurel(col="#7cb85a"):
    def part(ctx):
        ink = shade(col, .5)
        def leaf(x, y, a):
            return (f'<g transform="translate({x},{y}) rotate({a}) scale(0.84)">'
                    f'<path d="M0,0 C12,-15 42,-16 60,0 C42,16 12,15 0,0 Z" fill="{col}" {st(3, ink)}/>'
                    f'<path d="M6,0 C20,-3 36,-3 50,0" fill="none" {st(2.5, shade(col, 1.45))}/></g>')
        # ветка от виска к темени поверх волос; листья парами, смотрят вверх-наружу
        stem = (-140, -150), (-142, -192), (-128, -232), (-100, -264)
        s = f'<path d="M-138,-130 C-152,-200 -130,-258 -84,-284" fill="none" {st(4, ink)}/>'
        for i, (x, y) in enumerate(stem):
            s += leaf(x, y, -100 + i * 14) + leaf(x, y, -48 + i * 14)
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
