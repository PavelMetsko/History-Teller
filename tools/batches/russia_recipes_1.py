#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 1 главы «Россия» (легенды, ранняя и удельная Русь).

    python3 tools/batches/russia_recipes_1.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/russia_recipes_1.py --ids      только список id (для factory/build.py)
    python3 tools/batches/russia_recipes_1.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, ROOT, OUT
from england_recipes_1 import lady
from england_recipes_2 import cleric


def rus_prince(id, name, cloak="#a8312f", tunic="#2f4a7a", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"), fur="#6b4a2a", **kw):
    """Князь Руси: шапка с меховой опушкой, кафтан-туника, корзно (плащ)."""
    d = dict(hair=hair, beard=beard, hat={"type": "cap", "col": cloak, "fur": fur},
             outfit={"type": "tunic", "col": tunic, "trim": "#d4a63c", "belt": "#6b4426"}, sleeves=sl(tunic),
             cape={"type": "cape", "col": cloak}, legs=tr("#5a4434"), boots=bo("#7a2a2a"))
    d.update(kw)
    return R(id, name, **d)


def druzhinnik(id, name, surcoat="#5a6b4a", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"), **kw):
    """Дружинник / варяг: кольчуга, шлем с наносником, меч."""
    d = dict(hair=hair, beard=beard, hat={"type": "nasal", "col": "#a9b0b8", "trim": "#8a6a2a"},
             outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": surcoat, "belt": "#5b3a22"},
             sleeves=sl("#a9b0b8"), legs=tr("#5a4434"), boots=bo("#5b3a22"), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


def folk(id, name, shirt="#e9e0cc", trim="#a8312f", hair=("bowl", "#8a5a34"), beard=("full", "#8a5a34"), **kw):
    """Простолюдин / старейшина: рубаха с вышивкой, пояс."""
    d = dict(hair=hair, beard=beard, outfit={"type": "sukmana", "col": shirt, "trim": trim, "belt": trim},
             sleeves=sl(shirt), legs=tr("#7a6a52"), boots=bo("#7a5232"))
    d.update(kw)
    return R(id, name, **d)


def nomad(id, name, col="#7a5232", **kw):
    """Степняк: меховой кафтан, монгольская шапка, лук-копьё."""
    d = dict(skin="tan", hair=("long", "#1e1a18"), beard=("walrus", "#1e1a18"), hat={"type": "mongol", "fur": "#6b4a2a", "top": "#a8312f"},
             outfit={"type": "fur_tunic", "col": col, "fur": "#c9b08a", "rope": "#a8312f"}, sleeves=sl(col),
             legs=tr("#5a4434"), boots=bo("#3b2a20"), held=h("spear"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Призвание варягов
    druzhinnik("rurik_ru", "Рюрик", surcoat="#a8312f", hair=("long", "#d8b070"), beard=("full", "#d8b070"), cape={"type": "cape", "col": "#2f4a7a"}),
    druzhinnik("sineus_ru", "Синеус", surcoat="#2f4a7a", hair=("long", "#b9672e"), beard=("goatee", "#b9672e"), held=h("spear")),
    druzhinnik("truvor_ru", "Трувор", surcoat="#5a6b4a", hair=("long", "#8a5a34"), beard=("long", "#8a5a34")),
    folk("gostomysl_ru", "Старейшина Гостомысл", age="old", hair=("long", "#d8d4dc"), beard=("long", "#e6e0d6"), held=h("staff")),
    # ---------- Вещий Олег
    rus_prince("oleg_ru", "Вещий Олег", cloak="#2f4a7a", tunic="#7a2a2a", hair=("long", "#8a7a6a"), beard=("long", "#b8b4c0"),
               age="old", held=h("sword")),
    R("volkhv_ru", "Кудесник-волхв", age="old", hair=("long", "#e6e0d6"), beard=("long", "#e6e0d6"), bushy=True,
      hat={"type": "hood", "col": "#5a4434"}, outfit={"type": "robe", "col": "#e9e0cc", "rope": "#7a5232"}, sleeves=sl("#e9e0cc"),
      held=h("staff")),
    folk("groom_ru", "Старый конюший", age="old", shirt="#c9b08a", trim="#5a4434", hair=("receding", "#b8b4c0"), beard=("full", "#b8b4c0")),
    rus_prince("igor_ru", "Князь Игорь", cloak="#a8312f", tunic="#5a6b4a", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22")),
    # ---------- Илья Муромец
    druzhinnik("ilya_ru", "Илья Муромец", surcoat="#7a2a2a", hair=("short", "#5a3a22"), beard=("full", "#5a3a22"), bushy=True,
               hat={"type": "helmet", "col": "#b9bfc6", "trim": "#d4a63c"}, held=h("bulawa")),
    R("solovei_ru", "Соловей-разбойник", hair=("curly", "#1e1a18"), beard=("handlebar", "#1e1a18"), bushy=True,
      outfit={"type": "fur_tunic", "col": "#3b4a2a", "fur": "#6b4a2a", "rope": "#3b2a20"}, sleeves=BARE, legs=tr("#3b2a20"),
      boots=bo("#3b2a20"), held=h("trumpet")),
    R("kaliki_ru", "Калики перехожие", age="old", hair=("long", "#b8b4c0"), beard=("long", "#b8b4c0"), hat={"type": "hood", "col": "#7a6a52"},
      outfit={"type": "robe", "col": "#a88a5a", "rope": "#7a5232"}, sleeves=sl("#a88a5a"), held=h("staff")),
    druzhinnik("dobrynya_ru", "Добрыня Никитич", surcoat="#2f4a7a", hair=("short", "#b9672e"), beard=("full", "#b9672e"),
               hat={"type": "helmet", "col": "#b9bfc6", "trim": "#d4a63c"}),
    # ---------- Садко
    folk("sadko_ru", "Садко", shirt="#2f6a8a", trim="#d4a63c", hair=("curly", "#b9672e"), beard=("goatee", "#b9672e"), held=h("book")),
    R("sea_tsar_ru", "Царь Морской", skin="#9fc4c0", age="old", hair=("long", "#3f8a8a"), beard=("long", "#6fb5a8"), bushy=True,
      hat={"type": "crown", "gold": "#d8ad3c"}, outfit={"type": "emperor", "col": "#2f6a6a", "gold": "#d8ad3c", "mantle": "#1f4a5a"},
      sleeves=sl("#2f6a6a"), held=h("spear"), iris="#2f6a6a"),
    R("nikola_ru", "Никола Можайский", age="old", hair=("receding", "#e6e0d6"), beard=("full", "#e6e0d6"),
      outfit={"type": "robe", "col": "#f1ece2", "rope": "#d4a63c"}, sleeves=sl("#f1ece2"), cape={"type": "cape", "col": "#a8312f"},
      held=h("book")),
    lady("chernava_ru", "Чернава", dress="#e9e0cc", mantle="#3b4a5a", hair=("long", "#2a1a12"), veil=False),
    R("sea_princess_ru", "Морская царевна", male=False, skin="#d8eae6", hair=("long", "#6fb5a8"), hat={"type": "circlet", "gold": "#d8ad3c"},
      outfit={"type": "mermaid", "col": "#3f8a8a", "fin": "#6fb5a8", "top": "#e9e0cc"}, iris="#2f6a6a"),
    # ---------- Киев 882
    druzhinnik("askold_ru", "Аскольд", surcoat="#7a2a2a", hair=("long", "#d8b070"), beard=("full", "#d8b070"), cape={"type": "cape", "col": "#5a4434"}),
    druzhinnik("dir_ru", "Дир", surcoat="#3b4a5a", hair=("long", "#8a5a34"), beard=("goatee", "#8a5a34"), held=h("spear")),
    # ---------- Ольга
    lady("olga_ru", "Княгиня Ольга", dress="#2f4a7a", mantle="#a8312f", hair=("long", "#8a5a34"), hat={"type": "veil", "col": "#f4f1ea", "band": "#d8ad3c"}),
    R("mal_ru", "Древлянский князь Мал", hair=("long", "#5a3a22"), beard=("full", "#5a3a22"), bushy=True,
      hat={"type": "cap", "col": "#2f6a4a", "fur": "#6b4a2a"}, outfit={"type": "fur_tunic", "col": "#5a6b4a", "fur": "#c9b08a", "rope": "#7a5232"},
      sleeves=sl("#5a6b4a"), legs=tr("#5a4434"), boots=bo("#5b3a22"), held=h("spear")),
    druzhinnik("sveneld_ru", "Воевода Свенельд", surcoat="#5a2a6b", age="old", hair=("short", "#b8b4c0"), beard=("long", "#b8b4c0")),
    # ---------- Святослав
    R("svyatoslav_ru", "Князь Святослав", hair=("short_sides", "#8a5a34"), beard=("walrus", "#8a5a34"),
      outfit={"type": "tunic", "col": "#f4f1ea", "trim": "#a8312f", "belt": "#6b4426"}, sleeves=sl("#f4f1ea"),
      cape={"type": "cape", "col": "#a8312f"}, legs=tr("#5a4434"), boots=bo("#5b3a22"), held=h("sword")),
    R("joseph_khazar_ru", "Хазарский царь Иосиф", skin="olive", hair=("short", "#2a1a12"), beard=("long", "#2a1a12"),
      hat={"type": "turban", "col": "#d8ad3c", "jewel": "#a8312f"}, outfit={"type": "emperor", "col": "#5a2a6b", "gold": "#d8ad3c", "mantle": "#2f4a7a"},
      sleeves=sl("#5a2a6b")),
    nomad("kurya_ru", "Печенежский хан Куря", col="#7a5232"),
    # ---------- Крещение
    druzhinnik("dobrynya_hist_ru", "Воевода Добрыня", surcoat="#2f4a7a", age="old", hair=("short", "#8a7a6a"), beard=("full", "#b8b4c0")),
    # ---------- Ярослав, Борис и Глеб
    rus_prince("yaroslav_ru", "Ярослав Мудрый", cloak="#5a2a6b", tunic="#2f4a7a", hair=("short", "#5a3a22"), beard=("full", "#5a3a22"), held=h("book")),
    rus_prince("svyatopolk_ru", "Святополк Окаянный", cloak="#1e1e22", tunic="#7a2a2a", hair=("short", "#1e1a18"), beard=("goatee", "#1e1a18"),
               held=h("sword")),
    rus_prince("boris_ru", "Князь Борис", cloak="#a8312f", tunic="#f4f1ea", hair=("shoulder", "#d8b070"), beard=None, held=h("cross")),
    rus_prince("gleb_ru", "Князь Глеб", cloak="#2f6a4a", tunic="#f4f1ea", hair=("shoulder", "#b9672e"), beard=None),
    # ---------- Любеч
    rus_prince("monomakh_ru", "Владимир Мономах", cloak="#a8312f", tunic="#5a2a6b", age="old", hair=("short", "#8a7a6a"), beard=("full", "#b8b4c0"),
               held=h("scroll")),
    rus_prince("svyatopolk2_ru", "Святополк Изяславич", cloak="#d4a63c", tunic="#2f4a7a", hair=("short", "#3b2a20"), beard=("long", "#3b2a20")),
    rus_prince("oleg_svyat_ru", "Олег Святославич", cloak="#2f6a4a", tunic="#7a2a2a", hair=("short", "#b9672e"), beard=("full", "#b9672e"), held=h("sword")),
    rus_prince("davyd_ru", "Давыд Игоревич", cloak="#3b3a38", tunic="#5a6b4a", hair=("short", "#1e1a18"), beard=("goatee", "#1e1a18")),
    rus_prince("vasilko_ru", "Василько Теребовльский", cloak="#2f4a7a", tunic="#e9d8a8", hair=("short", "#d8b070"), beard=("goatee", "#d8b070")),
    # ---------- Разграбление Киева
    rus_prince("bogolyubsky_ru", "Андрей Боголюбский", cloak="#f1ece2", tunic="#2f4a7a", hair=("short", "#5a3a22"), beard=("full", "#5a3a22"),
               hat={"type": "crown", "gold": "#d8ad3c"}),
    rus_prince("mstislav_iz_ru", "Мстислав Изяславич", cloak="#a8312f", tunic="#3b4a5a", hair=("short", "#8a5a34"), beard=("goatee", "#8a5a34")),
    rus_prince("gleb_yur_ru", "Глеб Юрьевич", cloak="#2f6a4a", tunic="#e9d8a8", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22")),
    rus_prince("roman_rost_ru", "Роман Ростиславич", cloak="#5a2a6b", tunic="#7a2a2a", hair=("short", "#b9672e"), beard=("full", "#b9672e")),
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
