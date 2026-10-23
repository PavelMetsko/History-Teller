"""Риг фабрики персонажей: кости, позы, сборка SVG из деталей.

Холст 512×768, как у спрайтов игры. Каждая деталь рисуется в локальных координатах своей
кости (точка крепления — начало координат), риг сам ставит её на место и поворачивает.
Деталь не знает про позу — поэтому любая деталь работает во всех позах.

Контур «наклейки» общий для всей фигуры: фильтр раздувает силуэт и подкладывает тёмную
обводку снизу. Внутренние границы деталей — тонкой линией самой детали.
"""
from __future__ import annotations

import re

OUTLINE = "#3a170c"   # внешний контур, замер по нынешним спрайтам ~ (55,23,13)
INK = "#5b2c19"       # внутренние линии
OUTLINE_R = 9         # радиус раздувания силуэта = толщина внешнего контура

# Кости: (родитель, смещение точки крепления в системе родителя)
#   s = -1 — левая сторона картинки (правая рука персонажа), s = 1 — правая
ROOT_XY = (256, 600)
HEAD_AT = (0, -132)
SHOULDER = (76, -104)
UPPER_ARM = 58
LOWER_ARM = 46
HIP = (30, 4)
THIGH = 42

# Детали нарисованы в «чертёжных» координатах; масштаб приводит их к пропорциям чиби
# нынешних спрайтов: голова ~57 % роста, короткое тело. Кость → дополнительный transform.
DRAW = {
    "head": "translate(0,-160) scale(1.02,0.95) translate(0,150)",
    "torso": "scale(0.86,0.82)",
    "root": "scale(0.98,0.95)",
    "arm_u": "scale(1,1.02)",
    "arm_l": "scale(1,1.05)",
    "leg_u": "scale(1,0.9)",
    "leg_l": "scale(1,0.95)",
    "hand": "scale(0.95)",
}

# Позы: углы в градусах (по часовой стрелке), смещение корня, выражение лица.
# Для рук и ног ключи с суффиксом _l — левая сторона картинки, _r — правая.
POSES = {
    "base": dict(expr="neutral", arm_u_l=22, arm_u_r=-22, arm_l_l=-8, arm_l_r=8),
    "triumph": dict(expr="happy", arm_u_l=38, arm_l_l=-118, arm_u_r=-148, arm_l_r=-22, head=-4,
                    fist_r=True, front=["r"]),
    "defeated": dict(expr="sad", head=8, torso=2, arm_u_l=4, arm_u_r=-4, arm_l_l=-16, arm_l_r=16,
                     leg_u_l=55, leg_l_l=-60, leg_u_r=-55, leg_l_r=60),
    # заговорщик: кулак на бедре, кинжал лезвием вниз-наружу, брови сдвинуты, ухмылка
    "plot": dict(expr="sly", head=-6, torso=-2, arm_u_l=14, arm_l_l=-6, arm_u_r=-34, arm_l_r=46,
                 dagger="r", front=["r"]),
    # убит: сидит на земле — подол лежит кругом, ноги под ним; без подола ноги скрещены
    "dead": dict(expr="dead", sit=True, head=12, arm_u_l=30, arm_l_l=-18, arm_u_r=-30, arm_l_r=18,
                 leg_u_l=72, leg_l_l=-112, leg_u_r=-72, leg_l_r=112),
}
POSE_ORDER = ["base", "triumph", "defeated", "plot", "dead"]

# Порядок слоёв снизу вверх
# руки под туловищем: верх рукава прячется под плечо, как у нарисованных спрайтов;
# руку перед телом (жесты) выносит поза через "front"
Z = ["cape_back", "hair_back", "leg", "held_back", "arm", "hand", "skirt", "torso", "torso_over", "held",
     "neck", "ear", "face", "features", "beard", "hair_front", "hat"]


def chains(p: dict) -> dict[str, str]:
    """Строки transform для каждой кости в данной позе."""
    g = lambda k, d=0: p.get(k, d)
    root = f"translate({ROOT_XY[0] + g('dx')},{ROOT_XY[1] + g('dy')}) rotate({g('root')})"
    torso = f"{root} rotate({g('torso')})"
    c = {"root": root, "torso": torso,
         "head": f"{torso} translate({HEAD_AT[0]},{HEAD_AT[1]}) rotate({g('head')})"}
    for s, n in ((-1, "l"), (1, "r")):
        au = f"{torso} translate({s * SHOULDER[0]},{SHOULDER[1]}) rotate({g('arm_u_' + n)})"
        al = f"{au} translate(0,{UPPER_ARM}) rotate({g('arm_l_' + n)})"
        lu = f"{root} translate({s * HIP[0]},{HIP[1]}) rotate({g('leg_u_' + n)})"
        c.update({f"arm_u_{n}": au, f"arm_l_{n}": al, f"hand_{n}": f"{al} translate(0,{LOWER_ARM})",
                  f"leg_u_{n}": lu, f"leg_l_{n}": f"{lu} translate(0,{THIGH}) rotate({g('leg_l_' + n)})"})
    return c


def render(recipe, pose_name: str, defs_id: str = "f") -> str:
    """SVG-группа одной позы персонажа (без обёртки <svg>)."""
    pose = POSES[pose_name]
    ctx = dict(pose=pose, pose_name=pose_name, expr=pose["expr"], c=recipe["colors"], r=recipe)
    items = []  # (z, bone, svg)
    for part in recipe["parts"]:
        for z, bone, svg in part(ctx):
            items.append((Z.index(z), bone, svg))
    if pose.get("dagger"):
        n = pose["dagger"]
        # кисть смотрит внутрь (рука за спиной) — разворачиваем лезвие наружу и вниз
        items.append((Z.index("held"), f"hand_{n}", f'<g transform="rotate({-50 if n == "r" else 50})">{DAGGER}</g>'))
    if pose.get("sit") and any(Z[z] == "skirt" for z, _, _ in items):
        items = [t for t in items if not t[1].startswith("leg_")]   # ноги под подолом
    front = {f"{k}_{n}" for n in pose.get("front", []) for k in ("arm_u", "arm_l", "hand")}
    items = [(len(Z) if b in front else z, b, s) for z, b, s in items]   # руку перед лицом
    items.sort(key=lambda t: t[0])
    ch = chains(pose)
    draw = lambda b: DRAW.get(b, DRAW.get(b.rsplit("_", 1)[0], ""))
    # рука = одна фигура: плечо, предплечье и кисть одной стороны рисуются в общей группе,
    # поэтому объём и контур ложатся на всю руку целиком, без стыков в локте и запястье
    limbs = {}
    rest = []
    for z, b, s in items:
        side = b.rsplit("_", 1)[-1]
        if Z[min(z, len(Z) - 1)] in ("arm", "hand") or (z == len(Z) and b.split("_")[0] in ("arm", "hand")):
            limbs.setdefault(side, [z, []])
            limbs[side][0] = max(limbs[side][0], z)
            limbs[side][1].append((b, s))
        else:
            rest.append((z, b, s))
    order = {"arm_u": 0, "arm_l": 1, "hand": 2}
    for side, (z, parts_) in limbs.items():
        parts_.sort(key=lambda t: order[t[0].rsplit("_", 1)[0]])
        rest.append((z, ("limb", tuple(parts_)), None))
    rest.sort(key=lambda t: t[0])
    items = rest

    used: set[str] = set()
    out = []
    for z, b, s in items:
        if isinstance(b, tuple):
            inner = "".join(f'<g transform="{ch[bb]} {draw(bb)}">{_shaded(ss, used)}</g>' for bb, ss in b[1])
            out.append(f'<g filter="url(#vol)">{inner}</g>')
            continue
        if Z[min(z, len(Z) - 1)] not in FLAT:
            s = _shaded(s, used)
            s = f'<g filter="url(#vol)">{s}</g>'
        out.append(f'<g transform="{ch[b]} {draw(b)}">{s}</g>')
    grads = "".join(_grad(c) for c in sorted(used))
    return f'<defs>{grads}</defs><g filter="url(#{defs_id})">{"".join(out)}</g>'


# Объём «как у Nano Banana»: каждая деталь получает вертикальный градиент заливки (светлее сверху)
# и мягкое затемнение по краю снизу-справа + блик по краю сверху-слева. Лицо (глаза, рот) — без.
FLAT = {"features", "ear", "face"}   # мелкие детали: общий фильтр объёма их «залил» бы тенью
_FILL = re.compile(r'fill="#([0-9a-fA-F]{6})"')


def _shaded(svg: str, used: set) -> str:
    """Плоские заливки #rrggbb → вертикальный градиент того же цвета."""
    def sub(m):
        used.add(m.group(1))
        return f'fill="url(#gv{m.group(1)})"'
    return _FILL.sub(sub, svg)


def _grad(hexc: str) -> str:
    from parts import shade
    c = "#" + hexc
    return (f'<linearGradient id="gv{hexc}" x1="0" y1="0" x2="0.25" y2="1">'
            f'<stop offset="0" stop-color="{shade(c, 1.08)}"/><stop offset=".55" stop-color="{c}"/>'
            f'<stop offset="1" stop-color="{shade(c, .91)}"/></linearGradient>')


VOL = ('<filter id="vol" x="-15%" y="-15%" width="130%" height="130%" color-interpolation-filters="sRGB">'
       '<feGaussianBlur in="SourceAlpha" stdDeviation="10" result="b"/>'
       '<feOffset in="b" dx="-4" dy="-8" result="bo"/>'
       '<feComposite in="SourceAlpha" in2="bo" operator="arithmetic" k2="1" k3="-1" result="edge"/>'
       '<feFlood flood-color="#b8664a" flood-opacity=".26"/><feComposite in2="edge" operator="in" result="sh"/>'
       '<feOffset in="b" dx="4" dy="8" result="bh"/>'
       '<feComposite in="SourceAlpha" in2="bh" operator="arithmetic" k2="1" k3="-1" result="edge2"/>'
       '<feFlood flood-color="#fff6e8" flood-opacity=".32"/><feComposite in2="edge2" operator="in" result="hl"/>'
       '<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="sh"/><feMergeNode in="hl"/></feMerge>'
       '<feComposite in2="SourceAlpha" operator="in"/></filter>')


# кинжал позы «заговорщик»: лезвие по оси кисти, рукоять в кулаке
DAGGER = ('<rect x="-6" y="8" width="12" height="70" rx="4" fill="#dfe3e8" stroke="#5b2c19" stroke-width="3"/>'
          '<path d="M-6,78 L0,96 L6,78 Z" fill="#dfe3e8" stroke="#5b2c19" stroke-width="3" stroke-linejoin="round"/>'
          '<path d="M0,12 L0,84" stroke="#ffffff" stroke-width="2" opacity=".7"/>'
          '<rect x="-22" y="0" width="44" height="10" rx="4" fill="#c9a24a" stroke="#5b2c19" stroke-width="3"/>'
          '<rect x="-6" y="-22" width="12" height="24" rx="4" fill="#6b4426" stroke="#5b2c19" stroke-width="3"/>')


def defs(defs_id: str = "f") -> str:
    return VOL + (f'<filter id="{defs_id}" x="-20%" y="-20%" width="140%" height="140%">'
            f'<feMorphology in="SourceAlpha" operator="dilate" radius="{OUTLINE_R}" result="d"/>'
            f'<feFlood flood-color="{OUTLINE}"/><feComposite in2="d" operator="in" result="o"/>'
            f'<feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
