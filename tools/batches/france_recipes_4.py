#!/usr/bin/env python3
"""Рецепты фабрики для персонажей пачки 4 главы «Франция» (1853–1918).

    python3 tools/batches/france_recipes_4.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/france_recipes_4.py --ids      только список id (для factory/build.py)
    python3 tools/batches/france_recipes_4.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, victorian, edwardian, ROOT, OUT

HORIZON, FIELD_GREY, KEPI_RED, FR_BLUE = "#6f8fae", "#6e7468", "#a8312f", "#2f3f6a"


def french_1870(id, name, **kw):
    """Французский генерал 1870 года: тёмно-синий мундир, красные брюки, кепи."""
    d = dict(hair=("short", "#8a7a6a"), hat={"type": "cap", "col": KEPI_RED, "fur": ""},
             outfit={"type": "uniform", "col": FR_BLUE, "facing": FR_BLUE, "trim": "#d4a63c", "sash": "", "epaulettes": True},
             sleeves=sl(FR_BLUE), legs=tr(KEPI_RED), boots=tall(), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


def prussian(id, name, **kw):
    """Прусский офицер: тёмно-синий мундир, пикельхельм."""
    d = dict(hair=("receding", "#8a7a6a"), hat={"type": "pickelhaube", "col": "#1e1e22", "metal": "#d4a63c"},
             outfit={"type": "uniform", "col": "#1e2a44", "facing": "#a8312f", "trim": "#d4a63c", "sash": "", "epaulettes": True},
             sleeves=sl("#1e2a44"), legs=tr("#1e1e22"), boots=tall())
    d.update(kw)
    return R(id, name, **d)


def horizon(id, name, **kw):
    """Французский генерал ВПМ: «голубой горизонт», кепи."""
    d = dict(hair=("short", "#b8b4c0"), hat={"type": "cap", "col": HORIZON, "fur": ""},
             outfit={"type": "legion_tunic", "col": HORIZON, "belt": "#5a3a22", "button": "#d4a63c"},
             sleeves=sl(HORIZON), legs=tr(HORIZON), boots=tall("#3b2a20"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Париж Османа
    victorian("haussmann_fr", "Барон Осман", coat="#1e1e22", hair=("receding", "#8a5a34"), beard=("goatee", "#8a5a34"), held=h("scroll")),
    victorian("belgrand_fr", "Инженер Эжен Бельгран", coat="#3b3a38", hair=("short", "#5a3a22"), beard=("full", "#5a3a22"), held=h("pickaxe")),
    victorian("jules_ferry_fr", "Жюль Ферри", coat="#1e1e22", hair=("short", "#3b2a20"), beard=("walrus", "#3b2a20"), held=h("book")),
    # ---------- Седан
    prussian("bismarck_fr", "Отто фон Бисмарк", age="old", hair=None, beard=("walrus", "#b8b4c0"), bushy=True),
    prussian("moltke_elder_fr", "Фельдмаршал Мольтке Старший", age="old", hair=("receding", "#d8d4dc"), held=h("scroll")),
    french_1870("macmahon_fr", "Маршал Мак-Магон", age="old", hair=("short", "#d8d4dc"), beard=("walrus", "#d8d4dc")),
    victorian("gambetta_fr", "Леон Гамбетта", coat="#2a2a2e", hair=("shoulder", "#1e1a18"), beard=("full", "#1e1a18"), held=h("flag")),
    # ---------- Коммуна
    victorian("thiers_fr", "Адольф Тьер", coat="#1e1e22", age="old", hair=("short", "#d8d4dc"), glasses={"type": "round", "col": "#3a2a20"}),
    R("louise_michel_fr", "Луиза Мишель", male=False, hair=("long", "#2a1a12"), outfit={"type": "gown", "dress": "#1e1e22", "trim": "#a8312f",
      "mantle": "#1e1e22", "shoes": "#1e1e22"}, sleeves=sl("#1e1e22"), held=h("flag")),
    R("varlin_fr", "Эжен Варлен", hair=("short", "#3b2a20"), beard=("full", "#3b2a20"), outfit={"type": "tunic", "col": "#3b4a6a",
      "trim": "#a8312f", "belt": "#a8312f"}, sleeves=sl("#3b4a6a"), legs=tr("#5a4434"), boots=bo("#3b2a20"), held=h("book")),
    victorian("valles_fr", "Жюль Валлес", coat="#3b3a38", hair=("curly", "#2a1a12"), beard=("full", "#2a1a12"), bushy=True, held=h("scroll")),
    # ---------- школа Ферри
    victorian("paul_bert_fr", "Поль Бер", coat="#2a2a2e", hair=("receding", "#3b2a20"), beard=("full", "#3b2a20"), held=h("flask")),
    victorian("camille_see_fr", "Камиль Се", coat="#3b4a5a", hair=("short", "#5a3a22"), beard=("handlebar", "#5a3a22"), held=h("scroll")),
    R("freppel_fr", "Епископ Фреппель", age="old", hair=("receding", "#b8b4c0"), hat={"type": "mitre", "col": "#5a2a6b", "trim": "#d4a63c"},
      outfit={"type": "robe", "col": "#5a2a6b", "rope": "#d4a63c"}, sleeves=sl("#5a2a6b"), held=h("cross")),
    # ---------- Тонкин
    victorian("clemenceau_fr", "Жорж Клемансо", coat="#1e1e22", hair=("receding", "#b8b4c0"), beard=("walrus", "#d8d4dc"), bushy=True),
    french_1870("courbet_fr", "Адмирал Курбе", hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#a8312f"}, legs=tr(FR_BLUE),
                beard=("goatee", "#8a7a6a")),
    R("ton_that_thuyet_fr", "Регент Тон Тхат Тхюет", skin="tan", hair=("bowl", "#1e1a18"), beard=("goatee", "#1e1a18"),
      hat={"type": "turban", "col": "#1e1e22", "jewel": "#d8ad3c"}, outfit={"type": "robe", "col": "#2f4a7a", "rope": "#d8ad3c"},
      sleeves=sl("#2f4a7a"), held=h("scroll")),
    # ---------- Дрейфус
    french_1870("dreyfus_fr", "Капитан Альфред Дрейфус", hair=("short", "#3b2a20"), beard=("handlebar", "#3b2a20"),
                glasses={"type": "pince", "col": "#3a2a20"}, held=None),
    victorian("zola_fr", "Эмиль Золя", coat="#2a2a2e", hair=("receding", "#3b2a20"), beard=("full", "#5a4434"),
              glasses={"type": "pince", "col": "#3a2a20"}, held=h("scroll")),
    french_1870("picquart_fr", "Подполковник Жорж Пикар", hair=("short", "#5a3a22"), beard=("handlebar", "#5a3a22"), held=h("book")),
    french_1870("esterhazy_fr", "Майор Эстерхази", hair=("short", "#1e1a18"), beard=("walrus", "#1e1a18"), bushy=True, held=None),
    # ---------- 1905
    edwardian("briand_fr", "Аристид Бриан", coat="#2a2a2e", hair=("shoulder", "#3b2a20"), beard=("walrus", "#3b2a20")),
    edwardian("combes_fr", "Эмиль Комб", coat="#1e1e22", hair=("receding", "#d8d4dc"), beard=("goatee", "#d8d4dc"), age="old"),
    edwardian("jaures_fr", "Жан Жорес", coat="#3b3a38", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"), bushy=True),
    R("pius10_fr", "Папа Пий X", age="old", hair=("short", "#d8d4dc"), hat={"type": "cap", "col": "#f4f1ea", "fur": ""},
      outfit={"type": "robe", "col": "#f4f1ea", "rope": "#d4a63c"}, sleeves=sl("#f4f1ea"), held=h("cross")),
    # ---------- Марна, Верден, 1917
    horizon("joffre_fr", "Генерал Жоффр", hair=("short", "#d8d4dc"), beard=("walrus", "#f4f1ea"), bushy=True),
    horizon("gallieni_fr", "Генерал Гальени", hair=("short", "#d8d4dc"), beard=("walrus", "#d8d4dc"), glasses={"type": "pince", "col": "#3a2a20"}),
    R("moltke_younger_fr", "Генерал Мольтке Младший", hair=("receding", "#b8b4c0"), hat={"type": "pickelhaube", "col": FIELD_GREY, "metal": "#a9b0b8"},
      outfit={"type": "legion_tunic", "col": FIELD_GREY, "belt": "#3b2a20", "button": "#c9a24a"}, sleeves=sl(FIELD_GREY),
      legs=tr(FIELD_GREY), boots=tall()),
    horizon("petain_fr", "Генерал Петен", hair=("short", "#f4f1ea"), beard=("walrus", "#f4f1ea"), iris="#5f7a9a"),
    horizon("nivelle_fr", "Генерал Нивель", hair=("short", "#8a7a6a"), beard=("handlebar", "#8a7a6a"), held=h("trumpet")),
    R("falkenhayn_fr", "Генерал Фалькенхайн", hair=("short", "#d8d4dc"), beard=("handlebar", "#d8d4dc"), hat={"type": "cap", "col": FIELD_GREY, "fur": ""},
      outfit={"type": "legion_tunic", "col": FIELD_GREY, "belt": "#3b2a20", "button": "#c9a24a"}, sleeves=sl(FIELD_GREY),
      legs=tr(FIELD_GREY), boots=tall(), held=h("scroll")),
    horizon("mangin_fr", "Генерал Манжен", hair=("short", "#1e1a18"), beard=("handlebar", "#1e1a18"), bushy=True, held=h("sword")),
    edwardian("painleve_fr", "Военный министр Поль Пенлеве", coat="#1e1e22", hair=("receding", "#3b2a20"), beard=("full", "#3b2a20")),
    horizon("poilus_fr", "Солдаты-пуалю", hat={"type": "helmet", "col": HORIZON, "trim": "#5a6a7a"}, hair=("short", "#5a3a22"),
            beard=("full", "#5a3a22"), held=h("spear")),
]


if __name__ == "__main__":
    if "--ids" in sys.argv:
        print(" ".join(r["id"] for r in RECIPES))
        sys.exit()
    if "--missing" in sys.argv:
        art = os.path.join(ROOT, "Content", "art_v2")
        print(" ".join(r["id"] for r in RECIPES if not os.path.exists(os.path.join(art, f"char_{r['id']}_dead.webp"))))
        sys.exit()
    for r in RECIPES:
        with open(os.path.join(OUT, f"{r['id']}.json"), "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)
    print(len(RECIPES), "рецептов")
