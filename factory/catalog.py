"""Каталог деталей для редактора: слот → варианты → параметры.

Рецепт персонажа (factory/recipes/<id>.json):
    {"id": "sobieski", "skin": "#f7c9aa", "old_ref": "hetman",
     "slots": {"hair": {"type": "short_sides", "col": "#4a2e1c"}, ...}}
Неуказанный слот берёт вариант по умолчанию (первый), неуказанный параметр — значение по умолчанию.
"""
from __future__ import annotations

import json
from pathlib import Path

import parts as P

RECIPES_DIR = Path(__file__).resolve().parent / "recipes"

C = lambda default, label: ("color", default, label)       # noqa: E731
B = lambda default, label: ("bool", default, label)        # noqa: E731
HAND = ("choice", "hand_r", "Рука", [["hand_r", "правая"], ["hand_l", "левая"]])
NONE = ("— нет —", lambda p: None, {})

# slot: (подпись, {вариант: (подпись, фабрика, параметры)})
SLOTS = {
    "body": ("Тело", {
        "male": ("Мужское", lambda p: P.body("male"), {}),
        "female": ("Женское", lambda p: P.body("female"), {}),
    }),
    "face": ("Лицо", {
        "std": ("Обычное", lambda p: P.face(eyes_iris=p["iris"], brow=p["brow"], bushy=p["bushy"]),
                {"iris": C("#6b3a1f", "Глаза"), "brow": C("#4a2e1c", "Брови"), "bushy": B(False, "Густые брови")}),
    }),
    "age": ("Возраст", {
        "young": ("Без морщин", lambda p: None, {}),
        "old": ("Морщины", lambda p: P.wrinkles(), {}),
    }),
    "hair": ("Волосы", {
        "none": NONE,
        "short": ("Короткие", lambda p: P.hair_short(p["col"]), {"col": C("#5a3a22", "Цвет")}),
        "short_sides": ("Бритые, виски", lambda p: P.hair_short_sides(p["col"]), {"col": C("#4a2e1c", "Цвет")}),
        "curly": ("Кудрявые", lambda p: P.hair_curly(p["col"]), {"col": C("#5a3a22", "Цвет")}),
        "long": ("Длинные", lambda p: P.hair_long(p["col"]), {"col": C("#b97a45", "Цвет")}),
        "bowl": ("Под горшок", lambda p: P.hair_bowl(p["col"]), {"col": C("#6b4426", "Цвет")}),
        "shoulder": ("До плеч", lambda p: P.hair_shoulder(p["col"]), {"col": C("#8a5a34", "Цвет")}),
        "receding": ("Залысины", lambda p: P.hair_receding(p["col"]), {"col": C("#b8b4c0", "Цвет")}),
    }),
    "beard": ("Борода / усы", {
        "none": NONE,
        "handlebar": ("Усы подкрученные", lambda p: P.moustache_handlebar(p["col"]), {"col": C("#4a2e1c", "Цвет")}),
        "walrus": ("Усы моржовые", lambda p: P.moustache_walrus(p["col"]), {"col": C("#a7a199", "Цвет")}),
        "full": ("Борода", lambda p: P.beard_full(p["col"]), {"col": C("#5a3a22", "Цвет")}),
        "long": ("Длинная борода", lambda p: P.beard_long(p["col"]), {"col": C("#8a5a34", "Цвет")}),
        "goatee": ("Бородка", lambda p: P.beard_goatee(p["col"]), {"col": C("#5a3a22", "Цвет")}),
    }),
    "hat": ("Головной убор", {
        "none": NONE,
        "kolpak": ("Колпак с пером", lambda p: P.hat_kolpak(p["fur"], p["top"]),
                   {"fur": C("#8a6a4a", "Мех"), "top": C("#9e2a2b", "Верх")}),
        "crown": ("Корона", lambda p: P.hat_crown(p["gold"]), {"gold": C("#d8ad3c", "Золото")}),
        "maciejowka": ("Мациеювка", lambda p: P.hat_maciejowka(p["col"]), {"col": C("#7b8794", "Цвет")}),
        "konfederatka": ("Конфедератка", lambda p: P.hat_konfederatka(p["col"], p["fur"]),
                         {"col": C("#a8262e", "Верх"), "fur": C("#3b2a20", "Мех")}),
        "helmet": ("Шлем", lambda p: P.hat_helmet(p["col"], p["trim"]),
                   {"col": C("#b9bfc6", "Сталь"), "trim": C("#8a6a2a", "Обод")}),
        "circlet": ("Княжеский обруч", lambda p: P.hat_circlet(p["gold"]), {"gold": C("#d8ad3c", "Золото")}),
        "nasal": ("Шлем с наносником", lambda p: P.hat_nasal(p["col"], p["trim"]),
                  {"col": C("#a9b0b8", "Сталь"), "trim": C("#8a6a2a", "Обод")}),
        "hood": ("Капюшон", lambda p: P.hat_hood(p["col"]), {"col": C("#6b5a4a", "Ткань")}),
        "laurel": ("Лавровый венок", lambda p: P.hat_laurel(p["col"]), {"col": C("#72b552", "Листья")}),
        "mitre": ("Митра", lambda p: P.hat_mitre(p["col"], p["trim"]),
                  {"col": C("#f1ece2", "Ткань"), "trim": C("#d4a63c", "Золото")}),
    }),
    "outfit": ("Одежда", {
        "coat": ("Кафтан", lambda p: P.coat(p["col"], p["trim"], p["belt"]),
                 {"col": C("#5a6b4a", "Ткань"), "trim": C("#d4a63c", "Отделка"), "belt": C("#6b4426", "Пояс")}),
        "zupan_hussar": ("Жупан + кираса", lambda p: P.zupan_hussar(p["cloth"], p["steel"], p["sash1"], p["sash2"]),
                         {"cloth": C("#9e2a2b", "Жупан"), "steel": C("#c6cbd1", "Кираса"),
                          "sash1": C("#d4a63c", "Кушак"), "sash2": C("#a8312f", "Полосы")}),
        "legion_tunic": ("Мундир", lambda p: P.legion_tunic(p["col"], p["belt"], p["button"]),
                         {"col": C("#7f8c99", "Сукно"), "belt": C("#6b4426", "Ремни"), "button": C("#4b5560", "Пуговицы")}),
        "robe": ("Ряса", lambda p: P.robe(p["col"], p["rope"]), {"col": C("#5b4636", "Ткань"), "rope": C("#d8c7a0", "Пояс")}),
        "tunic": ("Туника", lambda p: P.tunic_medieval(p["col"], p["trim"], p["belt"]),
                  {"col": C("#4f6b8a", "Ткань"), "trim": C("#d4a63c", "Кайма"), "belt": C("#6b4426", "Пояс")}),
        "fur_tunic": ("Рубаха с мехом", lambda p: P.fur_tunic(p["col"], p["fur"], p["rope"]),
                      {"col": C("#8a6b4a", "Ткань"), "fur": C("#c9b08a", "Мех"), "rope": C("#a88a5a", "Верёвка")}),
        "chainmail": ("Кольчуга", lambda p: P.chainmail(p["steel"], p["surcoat"], p["belt"]),
                      {"steel": C("#a9b0b8", "Кольчуга"), "surcoat": C("#9e2a2b", "Сюрко"), "belt": C("#5b3a22", "Пояс")}),
        "emperor": ("Императорская далматика", lambda p: P.emperor_robe(p["col"], p["gold"], p["mantle"]),
                    {"col": C("#5a2a6b", "Ткань"), "gold": C("#d8ad3c", "Золото"), "mantle": C("#a8262e", "Мантия")}),
        "toga": ("Тога", lambda p: P.toga(p["cloth"], p["band"], p["gold"]),
                 {"cloth": C("#f7ede2", "Ткань"), "band": C("#6b2f7a", "Полоса"), "gold": C("#d8ad3c", "Фибула")}),
        "gown": ("Платье с мантией", lambda p: P.gown(p["dress"], p["trim"], p["mantle"], p["shoes"]),
                 {"dress": C("#f1e9da", "Платье"), "trim": C("#d4a63c", "Отделка"),
                  "mantle": C("#a8262e", "Мантия"), "shoes": C("#a8262e", "Туфли")}),
    }),
    "cape": ("Плащ", {
        "none": NONE,
        "cape": ("Плащ", lambda p: P.cape(p["col"]), {"col": C("#2f4a7a", "Цвет")}),
    }),
    "sleeves": ("Рукава", {
        "std": ("Рукава", lambda p: P.sleeves(p["col"], cuff=p["cuff"]), {"col": C("#5a6b4a", "Ткань"), "cuff": C("#d4a63c", "Манжета")}),
        "bare": ("Голые руки", lambda p: P.bare_arms(), {}),
    }),
    "legs": ("Штаны", {
        "none": NONE,
        "trousers": ("Штаны", lambda p: P.trousers(p["col"]), {"col": C("#4a3a30", "Цвет")}),
    }),
    "boots": ("Обувь", {
        "boots": ("Сапоги", lambda p: P.boots(p["col"], top=p["top"]), {"col": C("#5a3a22", "Цвет"), "top": C("#7a5232", "Отворот")}),
        "sandals": ("Сандалии", lambda p: P.sandals(p["strap"]), {"strap": C("#8a5a2a", "Ремешки")}),
        "tall": ("Высокие сапоги", lambda p: P.boots(p["col"], tall=True), {"col": C("#2e2622", "Цвет")}),
        "none": NONE,
    }),
    "held": ("В руке", {
        "none": NONE,
        "bulawa": ("Булава", lambda p: P.bulawa(p["hand"]), {"hand": HAND}),
        "sword": ("Меч", lambda p: P.sword(p["hand"]), {"hand": HAND}),
        "spear": ("Копьё", lambda p: P.spear(p["hand"]), {"hand": HAND}),
        "staff": ("Посох", lambda p: P.staff(p["hand"]), {"hand": HAND}),
        "cross": ("Крест", lambda p: P.cross_held(p["hand"]), {"hand": HAND}),
        "scroll": ("Свиток", lambda p: P.scroll(p["hand"]), {"hand": HAND}),
    }),
}


def schema() -> dict:
    """Каталог для редактора (JSON-совместимый)."""
    out = []
    for slot, (label, opts) in SLOTS.items():
        options = []
        for oid, (olabel, _, params) in opts.items():
            ps = []
            for k, spec in params.items():
                d = {"key": k, "type": spec[0], "default": spec[1], "label": spec[2]}
                if spec[0] == "choice":
                    d["options"] = spec[3]
                ps.append(d)
            options.append({"id": oid, "label": olabel, "params": ps})
        out.append({"slot": slot, "label": label, "options": options})
    return {"slots": out, "poses": ["base", "triumph", "defeated", "plot", "dead"]}


def build(recipe: dict) -> dict:
    """JSON-рецепт → рецепт для rig.render."""
    plist = []
    for slot, (_, opts) in SLOTS.items():
        sel = recipe.get("slots", {}).get(slot, {})
        oid = sel.get("type") if sel.get("type") in opts else next(iter(opts))
        _, make, params = opts[oid]
        p = {k: sel.get(k, spec[1]) for k, spec in params.items()}
        part = make(p)
        if part:
            plist.append(part)
    sl = recipe.get("slots", {})
    colors = {"skin": recipe.get("skin", "#f7c9aa"),
              "beard": sl.get("beard", {}).get("type", "none") not in ("none", "handlebar", "walrus"),
              "male": sl.get("body", {}).get("type", "male") == "male"}
    return {"id": recipe["id"], "colors": colors, "parts": plist}


def load_all() -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(RECIPES_DIR.glob("*.json"))]
