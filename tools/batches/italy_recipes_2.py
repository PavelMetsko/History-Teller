#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 2 главы «Италия» (1130–1706).

    python3 tools/batches/italy_recipes_2.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/italy_recipes_2.py --ids      только список id (для factory/build.py)
    python3 tools/batches/italy_recipes_2.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, colonial, ROOT, OUT  # noqa: F401
from england_recipes_2 import knight, noble, cleric, lady, cavalier
from france_recipes_2 import monk, peasant, renaissance

HELM = {"type": "helmet", "col": "#b9bfc6", "trim": "#8a6a2a"}
GOLD = "#d4a63c"


def pope(id, name, beard=None, **kw):
    """Папа: белая ряса, митра, красная мантия."""
    d = dict(beard=beard)
    d.update(kw)
    return cleric(id, name, col="#f4f1ea", **d)


def cardinal(id, name, **kw):
    """Кардинал: красная ряса и шапочка."""
    d = dict(hair=("short", "#5a3a22"), hat={"type": "cap", "col": "#a8312f", "fur": ""},
             outfit={"type": "robe", "col": "#a8312f", "rope": GOLD}, sleeves=sl("#a8312f", "#f4f1ea"),
             cape={"type": "cape", "col": "#a8312f"}, held=h("book"))
    d.update(kw)
    return R(id, name, **d)


def doge(id, name, col="#d8ad3c", **kw):
    """Дож Венеции: золотая мантия, шапочка-корно."""
    d = dict(age="old", hair=("receding", "#d8d4dc"), beard=("full", "#e6e0d6"), hat={"type": "cap", "col": col, "fur": "#f4f1ea"},
             outfit={"type": "emperor", "col": col, "gold": "#f4f1ea", "mantle": "#a8312f"}, sleeves=sl(col))
    d.update(kw)
    return R(id, name, **d)


def burgher(id, name, col="#a8312f", **kw):
    """Горожанин XIV–XV века: длинная туника-лукко, шапочка."""
    d = dict(hair=("bowl", "#3b2a20"), hat={"type": "cap", "col": col, "fur": ""},
             outfit={"type": "tunic", "col": col, "trim": "#3b2a20", "belt": "#3b2a20"}, sleeves=sl(col), legs=tr("#2a2a2e"),
             boots=bo("#3b2a20"))
    d.update(kw)
    return R(id, name, **d)


def admiral(id, name, surcoat="#2f4a7a", **kw):
    """Морской командир XIII–XIV века: кольчуга, сюрко с гербом, берет."""
    d = dict(hat={"type": "beret", "col": "#2a2a2e", "feather": ""}, beard=("full", "#5a3a22"))
    d.update(kw)
    return knight(id, name, surcoat=surcoat, **d)


def baroque(id, name, col="#2a2a2e", **kw):
    """XVII век: тёмный камзол с белым воротником, длинные волосы."""
    d = dict(hair=("shoulder", "#3b2a20"), beard=("goatee", "#3b2a20"), collar={"type": "ruff", "col": "#f4f1ea"},
             outfit={"type": "doublet", "col": col, "trim": "#f4f1ea", "chain": False}, sleeves=sl(col, "#f4f1ea"),
             legs=tr(col), boots=bo("#1e1e22"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Рожер II
    R("roger2_it", "Рожер II Сицилийский", hair=("long", "#5a3a22"), beard=("full", "#5a3a22"), hat={"type": "crown", "gold": GOLD},
      outfit={"type": "emperor", "col": "#2f4a7a", "gold": GOLD, "mantle": "#a8312f"}, sleeves=sl("#2f4a7a"), held=h("staff")),
    pope("anacletus_it", "Антипапа Анаклет II", beard=("goatee", "#d8d4dc"), held=h("scroll")),
    pope("innocent2_it", "Папа Иннокентий II", beard=("full", "#e6e0d6")),
    # ---------- Леньяно
    knight("barbarossa_it", "Фридрих Барбаросса", surcoat="#d8ad3c", hair=("short", "#b9672e"), beard=("full", "#b9672e"),
           hat={"type": "crown", "gold": GOLD}, cape={"type": "cape", "col": "#a8312f"}),
    pope("alexander3_it", "Папа Александр III", beard=("full", "#d8d4dc")),
    knight("guido_landriano_it", "Гвидо да Ландриано", surcoat="#f4f1ea", hat=HELM, beard=("goatee", "#3b2a20")),
    noble("henry_lion_it", "Генрих Лев", col="#a8312f", hair=("shoulder", "#8a5a34"), beard=("full", "#8a5a34"),
          hat={"type": "circlet", "gold": GOLD}, cape={"type": "cape", "col": "#d8ad3c"}),
    # ---------- Мелория
    admiral("oberto_doria_it", "Адмирал Оберто Дориа", surcoat="#f4f1ea", age="old", beard=("full", "#d8d4dc")),
    admiral("zaccaria_it", "Бенедетто Дзаккария", surcoat="#a8312f", beard=("goatee", "#3b2a20"), held=h("scroll")),
    knight("morosini_it", "Подеста Альбертино Морозини", surcoat="#2f4a7a", hat={"type": "cap", "col": "#a8312f", "fur": ""},
           beard=("goatee", "#5a3a22")),
    noble("ugolino_it", "Граф Уголино делла Герардеска", col="#2a2a2e", age="old", hair=("shoulder", "#b8b4c0"),
          beard=("long", "#d8d4dc"), cape={"type": "cape", "col": "#a8312f"}),
    # ---------- Чомпи
    peasant("michele_lando_it", "Микеле ди Ландо", tunic="#7a6a52", beard=("goatee", "#3b2a20"), held=h("flag", "hand_r")),
    burgher("salvestro_it", "Сальвестро Медичи", col="#a8312f", age="old", hair=("receding", "#8a7a6a")),
    peasant("scali_it", "Джорджо Скали", tunic="#5a6b4a", beard=("full", "#5a3a22"), hat={"type": "cap", "col": "#5a4434", "fur": ""}),
    burgher("alberti_it", "Бенедетто Альберти", col="#2f4a7a", beard=("goatee", "#3b2a20")),
    # ---------- Кьоджа
    doge("contarini_it", "Дож Андреа Контарини"),
    admiral("pisani_it", "Веттор Пизани", surcoat="#a8312f", beard=("full", "#3b2a20"), held=h("sword")),
    admiral("pietro_doria_it", "Пьетро Дориа", surcoat="#f4f1ea", beard=("handlebar", "#5a3a22"), hat=HELM),
    admiral("carlo_zeno_it", "Карло Дзено", surcoat="#2f6a4a", beard=("goatee", "#8a5a34")),
    # ---------- Лоди
    renaissance("francesco_sforza_it", "Франческо Сфорца", col="#a8312f", beard=None, hair=("bowl", "#3b2a20"), collar=None,
                held=h("bulawa")),
    doge("foscari_it", "Дож Франческо Фоскари", col="#d8ad3c", beard=None, hair=("receding", "#b8b4c0")),
    pope("nicholas5_it", "Папа Николай V"),
    noble("alfonso5_it", "Альфонсо Арагонский", col="#d8ad3c", hair=("bowl", "#2a1a12"), hat={"type": "crown", "gold": GOLD},
          cape={"type": "cape", "col": "#a8312f"}),
    # ---------- Карл VIII
    renaissance("charles8_it", "Карл VIII", col="#2f4a7a", hair=("shoulder", "#8a5a34"), beard=None, collar=None,
                hat={"type": "crown", "gold": GOLD}, cape={"type": "cape", "col": "#2f4a7a"}),
    renaissance("piero_medici_it", "Пьеро Медичи", col="#a8312f", hair=("shoulder", "#2a1a12"), beard=None, collar=None,
                hat={"type": "cap", "col": "#a8312f", "fur": ""}, held=h("book")),
    # ---------- Гетто
    doge("loredan_it", "Дож Леонардо Лоредан", col="#f4f1ea"),
    burgher("anselmo_it", "Ансельмо дель Банко", col="#5a2a6b", age="old", hair=("short", "#8a7a6a"), beard=("long", "#b8b4c0"),
            hat={"type": "cap", "col": "#d8ad3c", "fur": ""}, held=h("scroll")),
    burgher("sanudo_it", "Хронист Марино Санудо", col="#2a2a2e", hat={"type": "cap", "col": "#2a2a2e", "fur": ""}, held=h("book")),
    monk("friar_preacher_it", "Проповедник-францисканец", col="#7a5232", hair=("bowl", "#3b2a20"), beard=("goatee", "#3b2a20")),
    # ---------- Флоренция 1530
    renaissance("charles5_emp_it", "Император Карл V", col="#1e1e22", beard=("full", "#8a5a34"), hair=("short", "#8a5a34"),
                hat={"type": "crown", "gold": GOLD}, cape={"type": "cape", "col": "#a8312f"}),
    knight("ferruccio_it", "Франческо Ферруччи", surcoat="#a8312f", hat=HELM, beard=("full", "#2a1a12")),
    knight("malatesta_it", "Малатеста Бальони", surcoat="#2a2a2e", hat={"type": "beret", "col": "#2a2a2e", "feather": "#f4f1ea"},
           beard=("goatee", "#3b2a20")),
    # ---------- Тридент
    pope("pius4_it", "Папа Пий IV", beard=("full", "#e6e0d6")),
    cardinal("carlo_borromeo_it", "Кардинал Карло Борромео", hair=("short", "#3b2a20")),
    cardinal("madruzzo_it", "Кардинал Кристофоро Мадруццо", beard=("full", "#5a3a22"), held=h("cross")),
    monk("lainez_it", "Иезуит Диего Лаинес", col="#1e1e22", hair=("receding", "#3b2a20"), beard=("full", "#3b2a20"), skin="olive",
         held=h("book")),
    # ---------- Чума 1630
    cardinal("federico_borromeo_it", "Кардинал Федерико Борромео", age="old", hair=("receding", "#b8b4c0"), beard=("full", "#d8d4dc"),
             held=h("cross")),
    baroque("cordoba_it", "Губернатор Гонсало де Кордоба", col="#1e1e22", skin="olive", hat={"type": "wide", "col": "#1e1e22", "feather": "#a8312f"},
            held=h("bulawa")),
    baroque("tadino_it", "Протофизик Алессандро Тадино", col="#2a2a2e", age="old", hair=("receding", "#b8b4c0"), beard=("full", "#d8d4dc"),
            held=h("flask")),
    baroque("piazza_it", "Гульельмо Пьяцца", col="#5a4434", beard=("goatee", "#5a3a22"), held=h("scroll")),
    lady("caterina_rosa_it", "Катерина Роза", dress="#7a6a52", mantle="#5a4434", hair_col="#3b2a20",
         hat={"type": "veil", "col": "#f4f1ea", "band": ""}),
    # ---------- Турин 1706
    colonial("victor_amadeus_it", "Виктор Амадей II Савойский", coat="#2f4a7a", vest="#a8312f", hair_col="#3b2a20",
             cape={"type": "cape", "col": "#a8312f"}, held=h("bulawa")),
    colonial("eugene_savoy_it", "Принц Евгений Савойский", coat="#a8312f", vest="#f4f1ea", hair_col="#2a1a12", held=h("sword")),
    colonial("feuillade_it", "Маршал Ла Фейяд", coat="#f4f1ea", vest="#2f4a7a", hat="tricorne", held=h("bulawa")),
    R("micca_it", "Минёр Пьетро Микка", hair=("short", "#3b2a20"), beard=("handlebar", "#3b2a20"),
      hat={"type": "cap", "col": "#2f4a7a", "fur": ""}, outfit={"type": "coat", "col": "#2f4a7a", "trim": "#a8312f", "belt": "#3b2a20"},
      sleeves=sl("#2f4a7a"), legs=tr("#5a4434"), boots=bo("#3b2a20"), held=h("pickaxe")),
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
