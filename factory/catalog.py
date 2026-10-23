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
        "wig": ("Парик XVIII века", lambda p: P.hair_wig(p["col"]), {"col": C("#ece8e2", "Пудра")}),
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
        "mongol": ("Монгольская шапка", lambda p: P.hat_mongol(p["fur"], p["top"]),
                   {"fur": C("#6b4a2a", "Мех"), "top": C("#a8312f", "Верх")}),
        "veil": ("Покрывало дамы", lambda p: P.hat_veil(p["col"], p["band"] or None),
                 {"col": C("#f4f1ea", "Ткань"), "band": C("", "Обруч (пусто — нет)")}),
        "cap": ("Шапочка горожанина", lambda p: P.hat_cap(p["col"], p["fur"] or None),
                {"col": C("#a8312f", "Ткань"), "fur": C("", "Мех (пусто — нет)")}),
        "beret": ("Берет с пером", lambda p: P.hat_beret(p["col"], p["feather"] or None),
                  {"col": C("#2a2a2e", "Ткань"), "feather": C("#f4f1ea", "Перо (пусто — нет)")}),
        "turban": ("Тюрбан", lambda p: P.hat_turban(p["col"], p["jewel"]),
                   {"col": C("#f4f1ea", "Ткань"), "jewel": C("#2f9a8a", "Камень")}),
        "wide": ("Широкополая шляпа", lambda p: P.hat_wide(p["col"], p["feather"]),
                 {"col": C("#2a2a2e", "Фетр"), "feather": C("#e9e0cc", "Перо")}),
        "horns": ("Рожки", lambda p: P.hat_horns(p["col"]), {"col": C("#3b1a12", "Цвет")}),
        "tricorne": ("Треуголка", lambda p: P.hat_tricorne(p["col"], p["trim"]), {"col": C("#1e1e22", "Фетр"), "trim": C("#d4a63c", "Галун")}),
        "bicorne": ("Двууголка", lambda p: P.hat_bicorne(p["col"], p["cockade"]), {"col": C("#1e1e22", "Фетр"), "cockade": C("#a8312f", "Кокарда")}),
        "czapka": ("Уланская чапка", lambda p: P.hat_czapka(p["col"], p["band"], p["plume"]),
                   {"col": C("#a8312f", "Верх"), "band": C("#1e1e22", "Околыш"), "plume": C("#f4f1ea", "Султан")}),
        "krakuska": ("Краковская шапка", lambda p: P.hat_krakuska(p["col"], p["fur"], p["feather"]),
                     {"col": C("#2f4a7a", "Верх"), "fur": C("#2a2a2e", "Мех"), "feather": C("#2f9a8a", "Перо")}),
        "top": ("Цилиндр", lambda p: P.hat_top(p["col"]), {"col": C("#1e1e22", "Цвет")}),
        "pickelhaube": ("Пикельхельм", lambda p: P.hat_pickelhaube(p["col"], p["metal"]),
                        {"col": C("#1e1e22", "Кожа"), "metal": C("#c9a24a", "Металл")}),
        "laurel": ("Лавровый венок", lambda p: P.hat_laurel(p["col"]), {"col": C("#72b552", "Листья")}),
        "mitre": ("Митра", lambda p: P.hat_mitre(p["col"], p["trim"]),
                  {"col": C("#f1ece2", "Ткань"), "trim": C("#d4a63c", "Золото")}),
    }),
    "glasses": ("Очки", {
        "none": NONE,
        "round": ("Круглые очки", lambda p: P.glasses(p["col"], "round"), {"col": C("#3a2a20", "Оправа")}),
        "pince": ("Пенсне", lambda p: P.glasses(p["col"], "pince"), {"col": C("#3a2a20", "Оправа")}),
    }),
    "collar": ("Воротник", {
        "none": NONE,
        "ruff": ("Брыжи", lambda p: P.ruff(p["col"]), {"col": C("#f4f1ea", "Ткань")}),
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
        "mermaid": ("Хвост сирены", lambda p: P.mermaid_tail(p["col"], p["fin"], p["top"]),
                    {"col": C("#3f8a8a", "Хвост"), "fin": C("#6fb5a8", "Плавник"), "top": C("#e9e0cc", "Лиф")}),
        "teutonic": ("Тевтонский рыцарь", lambda p: P.teutonic(p["steel"], p["belt"]),
                     {"steel": C("#a9b0b8", "Кольчуга"), "belt": C("#5b3a22", "Пояс")}),
        "doublet": ("Ренессансный дублет", lambda p: P.doublet(p["col"], p["trim"], p["chain"]),
                    {"col": C("#2a2a2e", "Ткань"), "trim": C("#d4a63c", "Отделка"), "chain": B(True, "Золотая цепь")}),
        "kontusz": ("Жупан и кунтуш", lambda p: P.kontusz(p["zupan"], p["kontusz"], p["sash"], p["sash2"]),
                    {"zupan": C("#e9d8a8", "Жупан"), "kontusz": C("#a8312f", "Кунтуш"), "sash": C("#d4a63c", "Кушак"),
                     "sash2": C("#2f6a4a", "Полосы кушака")}),
        "frock": ("Кафтан XVIII века", lambda p: P.frock(p["col"], p["vest"], p["trim"]),
                  {"col": C("#4b6a9a", "Кафтан"), "vest": C("#e9d8a8", "Камзол"), "trim": C("#d4a63c", "Галун")}),
        "uniform": ("Мундир", lambda p: P.uniform(p["col"], p["facing"], p["trim"], p["sash"] or None, p["epaulettes"]),
                    {"col": C("#2f4a7a", "Сукно"), "facing": C("#a8312f", "Лацканы"), "trim": C("#d4a63c", "Металл"),
                     "sash": C("", "Кушак (пусто — пояс)"), "epaulettes": B(True, "Эполеты")}),
        "sukmana": ("Сукмана", lambda p: P.sukmana(p["col"], p["trim"], p["belt"]),
                    {"col": C("#f1ece2", "Сукно"), "trim": C("#a8312f", "Тесьма"), "belt": C("#a8312f", "Пояс")}),
        "suit": ("Костюм", lambda p: P.suit(p["col"], p["shirt"], p["tie"], p["long"]),
                 {"col": C("#2a2a2e", "Ткань"), "shirt": C("#f4f1ea", "Рубашка"), "tie": C("#a8312f", "Галстук"), "long": B(True, "Сюртук")}),
        "toga": ("Тога", lambda p: P.toga(p["cloth"], p["band"], p["gold"]),
                 {"cloth": C("#f7ede2", "Ткань"), "band": C("#6b2f7a", "Полоса"), "gold": C("#d8ad3c", "Фибула")}),
        "gown": ("Платье с мантией", lambda p: P.gown(p["dress"], p["trim"], p["mantle"], p["shoes"]),
                 {"dress": C("#f1e9da", "Платье"), "trim": C("#d4a63c", "Отделка"),
                  "mantle": C("#a8262e", "Мантия"), "shoes": C("#a8262e", "Туфли")}),
    }),
    "cape": ("Плащ", {
        "none": NONE,
        "wings": ("Крылья гусара", lambda p: P.hussar_wings(p["col"], p["feather"]),
                  {"col": C("#7a5232", "Рама"), "feather": C("#f4f1ea", "Перья")}),
        "tail": ("Хвост чёрта", lambda p: P.devil_tail(p["col"]), {"col": C("#a8262e", "Цвет")}),
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
        "trumpet": ("Труба", lambda p: P.trumpet(p["hand"]), {"hand": HAND}),
        "pickaxe": ("Кирка", lambda p: P.pickaxe(p["hand"]), {"hand": HAND}),
        "scythe": ("Коса торчком", lambda p: P.scythe(p["hand"]), {"hand": HAND}),
        "flag": ("Флаг", lambda p: P.flag_held(p["hand"]), {"hand": HAND}),
        "book": ("Книга", lambda p: P.book(p["hand"]), {"hand": HAND}),
        "flask": ("Колба", lambda p: P.flask(p["hand"]), {"hand": HAND}),
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
