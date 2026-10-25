#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 3 главы «Англия» (1707–1857).

    python3 tools/batches/england_recipes_3.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/england_recipes_3.py --ids      только список id (для factory/build.py)
    python3 tools/batches/england_recipes_3.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, colonial, regency, victorian, worker, ROOT, OUT  # noqa: F401

RECIPES = [
    # ---------- уния 1707
    colonial("godolphin", "Лорд Годолфин", coat="#2a2a2e", vest="#d8c7a0", hat=None, age="old", held=h("scroll")),
    colonial("queensberry", "Герцог Куинсберри", coat="#2f4a7a", vest="#f4f1ea", hat=None, hair_col="#5a3a22",
             cape={"type": "cape", "col": "#a8312f"}),
    colonial("andrew_fletcher", "Эндрю Флетчер из Солтуна", coat="#3b4a5a", vest="#e9d8a8", hat=None, wig=False,
             hair_col="#3b2a20", held=h("book")),
    # ---------- Кромфорд
    colonial("arkwright", "Ричард Аркрайт", coat="#7a5232", vest="#e9d8a8", hat=None, hair_col="#d8d4dc", age="old"),
    worker("john_kay_clock", "Часовщик Джон Кей", shirt="#f4f1ea", pants="#5a4434", hair=("receding", "#5a3a22"),
           glasses={"type": "round", "col": "#3a2a20"}, held=h("pickaxe")),
    worker("thomas_highs", "Томас Хайс", shirt="#e9e0cc", pants="#3b4a5a", hair=("shoulder", "#8a5a34"),
           hat={"type": "tricorne", "col": "#3b2a20", "trim": "#5a4434"}),
    colonial("jedediah_strutt", "Джедедайя Стратт", coat="#5a6b4a", vest="#e9d8a8", hat=None, wig=False, hair_col="#5a3a22"),
    worker("mill_children", "Фабричные дети", shirt="#e9e0cc", pants="#7a6a52", hair=("bowl", "#8a5a34"),
           hat={"type": "cap", "col": "#7a6a52", "fur": ""}),
    # ---------- «Зонг»
    colonial("luke_collingwood", "Капитан Люк Коллингвуд", coat="#2f4a7a", vest="#e9d8a8", wig=False, hair_col="#5a3a22",
             boots=tall(), held=h("sword")),
    colonial("william_gregson", "Судовладелец Уильям Грегсон", coat="#3b2a20", vest="#d4a63c", hat=None, age="old"),
    colonial("granville_sharp", "Гранвилл Шарп", coat="#1e1e22", vest="#f4f1ea", hat=None, held=h("book")),
    colonial("equiano", "Олауда Эквиано", skin="african", coat="#a8312f", vest="#f4f1ea", hat=None, wig=False,
             hair_col="#1e1a18", held=h("scroll")),
    R("lord_mansfield", "Лорд Мэнсфилд", age="old", hair=("wig", "#ece8e2"),
      outfit={"type": "robe", "col": "#a8312f", "rope": "#f4f1ea"}, sleeves=sl("#a8312f", "#f4f1ea"),
      cape={"type": "cape", "col": "#a8312f"}, held=h("scroll")),
    # ---------- 1798
    colonial("wolfe_tone", "Теобальд Вулф Тон", coat="#2f6a4a", vest="#f4f1ea", wig=False, hair_col="#3b2a20",
             hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#2f6a4a"}, boots=tall(), held=h("sword")),
    worker("mccracken", "Генри Джой Маккракен", shirt="#f4f1ea", pants="#2f6a4a", hair=("shoulder", "#5a3a22"),
           hat={"type": "wide", "col": "#2f6a4a", "feather": ""}, held=h("spear")),
    regency("castlereagh", "Лорд Каслри", coat="#1e1e22", hair=("short", "#8a5a34")),
    # ---------- луддиты
    worker("george_mellor", "Джордж Меллор", shirt="#e9e0cc", pants="#5a4434", hair=("short", "#b9672e"),
           held=h("pickaxe")),
    regency("william_horsfall", "Фабрикант Уильям Хорсфолл", coat="#3b4a5a", hair=("short", "#3b2a20"),
            hat={"type": "top", "col": "#1e1e22"}),
    regency("william_cartwright", "Фабрикант Уильям Картрайт", coat="#2a2a2e", hair=("short", "#5a3a22"),
            beard=("goatee", "#5a3a22")),
    worker("benjamin_walker", "Бенджамин Уокер", shirt="#d8c7a0", pants="#3b3a38", hair=("bowl", "#3b2a20"),
           hat={"type": "cap", "col": "#3b3a38", "fur": ""}),
    R("baron_thomson", "Барон Томсон", age="old", hair=("wig", "#ece8e2"),
      outfit={"type": "robe", "col": "#1e1e22", "rope": "#f4f1ea"}, sleeves=sl("#1e1e22", "#f4f1ea"), held=h("book")),
    # ---------- Питерлоо
    regency("henry_hunt", "Генри Хант", coat="#2f4a7a", hair=("short", "#8a5a34"), hat={"type": "top", "col": "#f4f1ea"}),
    worker("samuel_bamford", "Сэмюэл Бэмфорд", shirt="#f4f1ea", pants="#3b4a5a", hair=("short", "#5a3a22"),
           hat={"type": "wide", "col": "#3b2a20", "feather": ""}, held=h("flag", "hand_r")),
    regency("william_hulton", "Магистрат Уильям Халтон", coat="#2a2a2e", hair=("short", "#3b2a20"), held=h("scroll")),
    regency("lord_sidmouth", "Лорд Сидмут", coat="#1e1e22", hair=("receding", "#d8d4dc"), age="old"),
    worker("peterloo_crowd", "Толпа на поле Святого Петра", male=False, shirt="#e9e0cc", pants="#5a6b4a",
           hair=("long", "#5a3a22"), hat={"type": "veil", "col": "#f4f1ea", "band": ""}, held=h("flag")),
    # ---------- Голод
    regency("robert_peel", "Роберт Пиль", coat="#2a2a2e", hair=("short", "#b9672e")),
    victorian("charles_trevelyan", "Чарльз Тревельян", coat="#1e1e22", hair=("short", "#3b2a20"), held=h("book")),
    victorian("lord_john_russell", "Лорд Джон Рассел", coat="#2a2a2e", hair=("receding", "#8a7a6a"), age="old"),
    worker("irish_tenants", "Ирландские арендаторы", shirt="#d8c7a0", pants="#5a4434", hair=("short", "#3b2a20"),
           beard=("full", "#3b2a20"), hat={"type": "wide", "col": "#5a4434", "feather": ""}, age="old"),
    victorian("john_mitchel", "Джон Митчел", coat="#2f6a4a", hair=("short", "#3b2a20"), beard=("goatee", "#3b2a20"), held=h("scroll")),
    # ---------- чартисты
    victorian("feargus_oconnor", "Фергюс О'Коннор", coat="#3b4a5a", hair=("short", "#b9672e"), hat={"type": "top", "col": "#1e1e22"}),
    worker("william_lovett", "Уильям Ловетт", shirt="#f4f1ea", pants="#2a2a2e", hair=("receding", "#3b2a20"), held=h("scroll")),
    # ---------- Индия 1857
    R("mangal_pandey", "Мангал Панди", skin="tan", hair=("short", "#1e1a18"), beard=("handlebar", "#1e1a18"),
      hat={"type": "turban", "col": "#f4f1ea", "jewel": "#a8312f"},
      outfit={"type": "uniform", "col": "#a8312f", "facing": "#f4f1ea", "trim": "#d4a63c", "sash": "", "epaulettes": False},
      sleeves=sl("#a8312f"), legs=tr("#f4f1ea"), boots=bo("#3b2a20"), held=h("spear")),
    R("meerut_sepoys", "Сипаи из Мирута", skin="tan", hair=("short", "#1e1a18"), beard=("full", "#1e1a18"),
      hat={"type": "turban", "col": "#2f4a7a", "jewel": "#d4a63c"},
      outfit={"type": "uniform", "col": "#a8312f", "facing": "#2f4a7a", "trim": "#d4a63c", "sash": "", "epaulettes": False},
      sleeves=sl("#a8312f"), legs=tr("#f4f1ea"), boots=bo("#3b2a20"), held=h("sword")),
    R("bahadur_shah", "Бахадур-шах Зафар", skin="olive", age="old", hair=("short", "#e6e0d6"), beard=("long", "#e6e0d6"),
      hat={"type": "turban", "col": "#f4f1ea", "jewel": "#2f9a8a"},
      outfit={"type": "robe", "col": "#e9d8a8", "rope": "#d4a63c"}, sleeves=sl("#e9d8a8"),
      cape={"type": "cape", "col": "#2f6a4a"}, held=h("book")),
    R("lakshmi_bai", "Рани Лакшми Бай", male=False, skin="tan", hair=("long", "#1e1a18"),
      hat={"type": "turban", "col": "#a8312f", "jewel": "#d4a63c"},
      outfit={"type": "gown", "dress": "#d8ad3c", "trim": "#a8312f", "mantle": "#a8312f", "shoes": "#3b2a20"},
      sleeves=sl("#d8ad3c"), held=h("sword")),
    victorian("lord_canning", "Лорд Каннинг", coat="#1e1e22", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"), held=h("scroll")),
]


if __name__ == "__main__":
    if "--ids" in sys.argv:
        print(" ".join(r["id"] for r in RECIPES))
        sys.exit()
    if "--missing" in sys.argv:   # ещё не отрисованные фабрикой
        art = os.path.join(ROOT, "Content", "art_v2")
        print(" ".join(r["id"] for r in RECIPES if not os.path.exists(os.path.join(art, f"char_{r['id']}_dead.webp"))))
        sys.exit()
    for r in RECIPES:
        with open(os.path.join(OUT, f"{r['id']}.json"), "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)
    print(len(RECIPES), "рецептов")
