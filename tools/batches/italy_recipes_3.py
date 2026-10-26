#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 3 главы «Италия» (1720–1849).
Виктор Амадей II (victor_amadeus_it) — общий с пачкой 2, его рецепт там.

    python3 tools/batches/italy_recipes_3.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/italy_recipes_3.py --ids      только список id (для factory/build.py)
    python3 tools/batches/italy_recipes_3.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, colonial, regency, victorian, ROOT, OUT  # noqa: F401


def monarch(id, name, coat="#2f4a7a", mantle="#a8312f", hair=("wig", "#ece8e2"), **kw):
    """Государь XVIII века: кафтан с золотом, мантия, корона."""
    d = dict(hair=hair, hat={"type": "crown", "gold": "#d8ad3c"},
             outfit={"type": "frock", "col": coat, "vest": "#e9d8a8", "trim": "#d4a63c"}, sleeves=sl(coat, "#f4f1ea"),
             cape={"type": "cape", "col": mantle}, legs=tr("#e9d8a8"), boots=bo("#1e1e22"))
    d.update(kw)
    return R(id, name, **d)


def cardinal(id, name, red="#a8312f", hair=("short", "#8a7a6a"), **kw):
    d = dict(age="old", hair=hair, hat={"type": "cap", "col": red, "fur": ""},
             outfit={"type": "robe", "col": red, "rope": "#d4a63c"}, sleeves=sl(red, "#f4f1ea"), held=h("cross"))
    d.update(kw)
    return R(id, name, **d)


def officer(id, name, coat="#2f4a7a", facing="#a8312f", hat=None, **kw):
    """Офицер начала XIX века: мундир с эполетами, двууголка."""
    d = dict(hair=("short", "#3b2a20"), hat=hat if hat is not None else {"type": "bicorne", "col": "#1e1e22", "cockade": "#2f6a4a"},
             outfit={"type": "uniform", "col": coat, "facing": facing, "trim": "#d4a63c", "sash": "", "epaulettes": True},
             sleeves=sl(coat), legs=tr("#f4f1ea"), boots=tall(), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Сардиния 1720, Неаполь 1734
    monarch("charles6_it", "Император Карл VI", coat="#1e1e22", mantle="#d8ad3c", hair=("wig", "#5a3a22")),
    monarch("philip5_it", "Филипп V Испанский", coat="#a8312f", mantle="#2f4a7a", hair=("wig", "#8a5a34")),
    cardinal("alberoni_it", "Кардинал Джулио Альберони", held=h("scroll")),
    colonial("charles_bourbon_it", "Инфант Карл Бурбон", coat="#2f4a7a", vest="#f4f1ea", hat=None, hair_col="#d8d4dc", held=h("sword")),
    R("elisabetta_farnese_it", "Королева Елизавета Фарнезе", male=False, hair=("long", "#5a3a22"), hat={"type": "crown", "gold": "#d8ad3c"},
      outfit={"type": "gown", "dress": "#a8312f", "trim": "#d4a63c", "mantle": "#2f4a7a", "shoes": "#1e1e22"}, sleeves=sl("#a8312f", "#f4f1ea")),
    colonial("montemar_it", "Граф Монтемар", coat="#f4f1ea", vest="#a8312f", hair_col="#d8d4dc", held=h("sword")),
    # ---------- Беккариа
    colonial("beccaria_it", "Чезаре Беккариа", coat="#5a6b4a", vest="#e9d8a8", hat=None, hair_col="#ece8e2", held=h("book")),
    colonial("pietro_verri_it", "Пьетро Верри", coat="#7a2a2a", vest="#e9d8a8", hat=None, hair_col="#d8d4dc", held=h("scroll")),
    colonial("alessandro_verri_it", "Алессандро Верри", coat="#3b4a6a", vest="#f4f1ea", hat=None, hair_col="#ece8e2", held=h("book")),
    # ---------- Венеция 1797
    R("manin_it", "Дож Лудовико Манин", age="old", hair=("short", "#d8d4dc"), hat={"type": "cap", "col": "#d8ad3c", "fur": ""},
      outfit={"type": "robe", "col": "#d8ad3c", "rope": "#a8312f"}, cape={"type": "cape", "col": "#a8312f"}, sleeves=sl("#d8ad3c")),
    R("pesaro_it", "Сенатор Франческо Пезаро", age="old", hair=("wig", "#ece8e2"), outfit={"type": "robe", "col": "#7a2a2a", "rope": "#1e1e22"},
      sleeves=sl("#7a2a2a"), held=h("sword")),
    colonial("cobenzl_it", "Граф Людвиг Кобенцль", coat="#f4f1ea", vest="#d8ad3c", hat=None, held=h("scroll")),
    # ---------- Неаполь 1799
    R("pimentel_it", "Элеонора Фонсека Пиментел", male=False, hair=("curly", "#3b2a20"),
      outfit={"type": "gown", "dress": "#f4f1ea", "trim": "#2f6a4a", "mantle": "#a8312f", "shoes": "#1e1e22"}, sleeves=sl("#f4f1ea"), held=h("scroll")),
    cardinal("ruffo_it", "Кардинал Фабрицио Руффо", held=h("flag")),
    monarch("ferdinand_bourbon_it", "Король Фердинанд Бурбон", coat="#2f4a7a", mantle="#a8312f", hair=("wig", "#ece8e2"), age="old"),
    # ---------- Королевство Италия 1805
    officer("eugene_it", "Евгений Богарне", coat="#2f6a4a", facing="#a8312f", hair=("short", "#5a3a22")),
    regency("melzi_it", "Франческо Мельци д'Эриль", coat="#1e1e22", hair=("receding", "#b8b4c0"), age="old", held=h("scroll")),
    regency("prina_it", "Министр Джузеппе Прина", coat="#5a4434", hair=("short", "#8a7a6a"), held=h("book")),
    # ---------- Вена 1815
    R("pius7_it", "Папа Пий VII", age="old", hair=("short", "#d8d4dc"), hat={"type": "mitre", "col": "#f1ece2", "trim": "#d4a63c"},
      outfit={"type": "robe", "col": "#f4f1ea", "rope": "#d4a63c"}, cape={"type": "cape", "col": "#a8312f"}, sleeves=sl("#f4f1ea"), held=h("cross")),
    officer("victor_emmanuel1_it", "Виктор Эммануил I Савойский", coat="#2f4a7a", facing="#a8312f", hair=("wig", "#ece8e2"), age="old",
            hat={"type": "crown", "gold": "#d8ad3c"}),
    # ---------- карбонарии 1820
    officer("pepe_it", "Генерал Гульельмо Пепе", coat="#2f4a7a", facing="#a8312f", beard=("handlebar", "#3b2a20")),
    regency("santarosa_it", "Санторре ди Сантароза", coat="#1e1e22", hair=("curly", "#2a1a12"), held=h("sword")),
    officer("charles_albert_it", "Принц Карл Альберт", coat="#2f4a7a", facing="#d8ad3c", hair=("short", "#5a3a22"),
            beard=("handlebar", "#5a3a22"), hat={"type": "none"}),
    # ---------- Молодая Италия
    victorian("mazzini_it", "Джузеппе Мадзини", coat="#1e1e22", hair=("short", "#2a1a12"), beard=("goatee", "#2a1a12"), held=h("book")),
    regency("menotti_it", "Чиро Менотти", coat="#5a2a2a", hair=("curly", "#3b2a20"), beard=("full", "#3b2a20")),
    # ---------- 1848–1849
    victorian("balbo_it", "Чезаре Бальбо", coat="#3b3a38", hair=("receding", "#8a7a6a"), age="old", glasses={"type": "round", "col": "#3a2a20"},
              held=h("book")),
    victorian("cattaneo_it", "Карло Каттанео", coat="#2a2a2e", hair=("receding", "#5a3a22"), beard=("full", "#5a3a22"), held=h("scroll")),
    victorian("casati_it", "Подеста Габрио Казати", coat="#1e1e22", tie="#a8312f", hair=("short", "#b8b4c0"), age="old"),
    R("radetzky_it", "Маршал Йозеф Радецкий", age="old", hair=("receding", "#e6e0d6"), beard=("walrus", "#e6e0d6"),
      outfit={"type": "uniform", "col": "#f4f1ea", "facing": "#a8312f", "trim": "#d4a63c", "sash": "#d8ad3c", "epaulettes": True},
      sleeves=sl("#f4f1ea"), legs=tr("#a8312f"), boots=tall(), held=h("bulawa")),
    R("manara_it", "Лучано Манара", hair=("short", "#3b2a20"), beard=("goatee", "#3b2a20"), hat={"type": "wide", "col": "#1e1e22", "feather": "#1e1e22"},
      outfit={"type": "coat", "col": "#2f4a7a", "trim": "#a8312f", "belt": "#3b2a20"}, sleeves=sl("#2f4a7a"), legs=tr("#3b3a38"),
      boots=bo("#3b2a20"), held=h("spear")),
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
