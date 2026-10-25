#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 1 главы «Франция» (легенды, Галлия, франки, Каролинги).

    python3 tools/batches/france_recipes_1.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/france_recipes_1.py --ids      только список id (для factory/build.py)
    python3 tools/batches/france_recipes_1.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, ROOT, OUT
from england_recipes_1 import saxon, lady, roman, SANDALS
from england_recipes_2 import cleric


def gaul(id, name, tunic="#5a6b4a", hair=("long", "#b97a45"), beard=("walrus", "#b97a45"), **kw):
    """Галл / франк-язычник: рубаха с мехом, длинные волосы, усы."""
    d = dict(hair=hair, beard=beard, outfit={"type": "fur_tunic", "col": tunic, "fur": "#c9b08a", "rope": "#7a5232"},
             sleeves=sl(tunic), legs=tr("#7a6a52"), boots=bo("#5b3a22"))
    d.update(kw)
    return R(id, name, **d)


def frank(id, name, surcoat="#2f4a7a", hair=("shoulder", "#8a5a34"), beard=("full", "#8a5a34"), **kw):
    """Франкский воин / знатный: кольчуга с сюрко."""
    d = dict(hair=hair, beard=beard, outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": surcoat, "belt": "#5b3a22"},
             sleeves=sl("#a9b0b8"), legs=tr("#5a4434"), boots=bo("#5b3a22"), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


def carolingian(id, name, col="#2f4a7a", mantle="#a8262e", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"), **kw):
    """Каролингский король: далматика, корона."""
    d = dict(hair=hair, beard=beard, hat={"type": "crown", "gold": "#d8ad3c"},
             outfit={"type": "emperor", "col": col, "gold": "#d8ad3c", "mantle": mantle}, sleeves=sl(col))
    d.update(kw)
    return R(id, name, **d)


def moor(id, name, col="#e9e0cc", **kw):
    """Омейядский эмир / воин: тюрбан, кафтан."""
    d = dict(skin="olive", hair=("short", "#1e1a18"), beard=("full", "#1e1a18"), hat={"type": "turban", "col": "#f4f1ea", "jewel": "#2f9a8a"},
             outfit={"type": "coat", "col": col, "trim": "#d4a63c", "belt": "#a8312f"}, sleeves=sl(col), legs=tr("#7a6a52"),
             boots=bo("#7a5232"), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- легенды
    R("protis_fr", "Протис", skin="olive", hair=("curly", "#2a1a12"), beard=("full", "#2a1a12"),
      outfit={"type": "toga", "cloth": "#f7ede2", "band": "#2f4a7a", "gold": "#d8ad3c"}, sleeves=sl("#f7ede2"), boots=SANDALS),
    lady("gyptis_fr", "Гиптис", dress="#e9d8a8", mantle="#2f6a4a", hair=("long", "#d8b070"), veil=False,
         hat={"type": "circlet", "gold": "#d8ad3c"}),
    gaul("nannus_fr", "Царь Нанн", tunic="#a8312f", age="old", hair=("long", "#d8d4dc"), beard=("long", "#e6e0d6"),
         hat={"type": "circlet", "gold": "#d8ad3c"}, cape={"type": "cape", "col": "#7a5232"}, held=h("staff")),
    gaul("gaul_suitor_fr", "Галльский жених", tunic="#2f4a7a", held=h("spear")),
    R("melusine_fr", "Мелюзина", male=False, hair=("long", "#b9672e"), hat={"type": "circlet", "gold": "#d8ad3c"},
      outfit={"type": "mermaid", "col": "#2f6a4a", "fin": "#6fb5a8", "top": "#e9e0cc"}, iris="#2f8a6a"),
    frank("raymondin_fr", "Раймондин", surcoat="#7a2a5a", hair=("short", "#3b2a20"), beard=None),
    frank("forez_fr", "Граф Форе", surcoat="#3b4a5a", hair=("short", "#3b2a20"), beard=("goatee", "#3b2a20"), held=None),
    frank("frank_warrior_fr", "Франкский воин", surcoat="#7a6a52", hair=("long", "#d8b070"), beard=("walrus", "#d8b070"),
          bushy=True, held=h("pickaxe")),
    cleric("remigius_fr", "Епископ Ремигий"),
    frank("roland_fr", "Роланд", surcoat="#a8312f", hair=("short", "#d8b070"), beard=None, hat={"type": "nasal", "col": "#a9b0b8", "trim": "#d4a63c"},
          held=h("trumpet")),
    frank("oliver_fr", "Оливье", surcoat="#2f6a4a", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22")),
    frank("ganelon_fr", "Граф Ганелон", surcoat="#3b2a20", hair=("short", "#2a1a12"), beard=("goatee", "#2a1a12"), held=h("scroll"),
          cape={"type": "cape", "col": "#5a2a6b"}),
    moor("marsile_fr", "Царь Марсилий", col="#5a2a6b", age="old", beard=("long", "#8a8a8a"), held=h("bulawa")),
    # ---------- Галлия
    gaul("litaviccus_fr", "Литавикк", tunic="#a8794e", held=h("spear")),
    gaul("convictolitavis_fr", "Конвиктолитав", tunic="#e9d8a8", hair=("shoulder", "#8a5a34"), cape={"type": "cape", "col": "#2f4a7a"}),
    lady("blandina_fr", "Бландина", dress="#e9e0cc", mantle="#7a6a52", hair=("long", "#3b2a20")),
    cleric("pothinus_fr", "Епископ Потин", mitre=False, hair=("receding", "#e6e0d6"), beard=("long", "#e6e0d6"), held=h("staff")),
    R("irenaeus_fr", "Пресвитер Ириней", skin="olive", hair=("short", "#3b2a20"), beard=("full", "#3b2a20"),
      outfit={"type": "robe", "col": "#5b4636", "rope": "#d8c7a0"}, sleeves=sl("#5b4636"), held=h("scroll")),
    roman("legatus_lyon_fr", "Наместник Лугдунской Галлии", tunic="#5a2a6b", hat=None, held=h("scroll")),
    # ---------- франки и Каролинги
    frank("clovis_fr", "Хлодвиг", surcoat="#a8312f", hair=("long", "#d8b070"), beard=("goatee", "#d8b070"),
          hat={"type": "crown", "gold": "#d8ad3c"}),
    roman("syagrius_fr", "Сиагрий", tunic="#7a2a2a", hair=("short", "#5a3a22")),
    R("alaric2_fr", "Аларих II", hair=("long", "#8a5a34"), beard=("full", "#8a5a34"), hat={"type": "crown", "gold": "#d8ad3c"},
      outfit={"type": "tunic", "col": "#2f4a7a", "trim": "#d4a63c", "belt": "#6b4426"}, cape={"type": "cape", "col": "#5a2a6b"},
      sleeves=sl("#2f4a7a"), legs=tr("#5a4434"), boots=bo("#5b3a22"), held=h("sword")),
    lady("clotilde_fr", "Королева Клотильда", dress="#f4f1ea", mantle="#2f4a7a", held=h("cross")),
    frank("charles_martel_fr", "Карл Мартелл", surcoat="#2f4a7a", hair=("short", "#5a3a22"), beard=("full", "#5a3a22"),
          hat={"type": "nasal", "col": "#a9b0b8", "trim": "#d4a63c"}, held=h("pickaxe")),
    moor("abd_rahman_fr", "Абд ар-Рахман аль-Гафики", col="#2f6a4a"),
    frank("eudes_fr", "Эд Аквитанский", surcoat="#d8ad3c", hair=("shoulder", "#3b2a20"), beard=("goatee", "#3b2a20"),
          hat={"type": "circlet", "gold": "#d8ad3c"}),
    carolingian("pepin_fr", "Пипин Короткий", col="#5a6b4a", hat={"type": "none"}, beard=("goatee", "#5a3a22")),
    R("childeric3_fr", "Хильдерик III", hair=("long", "#d8b070"), hat={"type": "crown", "gold": "#d8ad3c"},
      outfit={"type": "tunic", "col": "#e9d8a8", "trim": "#d4a63c", "belt": "#6b4426"}, sleeves=sl("#e9d8a8"),
      legs=tr("#5a4434"), boots=bo("#5b3a22")),
    cleric("zachary_fr", "Папа Захарий", col="#f4f1ea"),
    cleric("boniface_fr", "Архиепископ Бонифаций", col="#5a6b4a", beard=("full", "#d8d4dc")),
    carolingian("charlemagne_fr", "Карл Великий", col="#2f4a7a", age="old", hair=("short", "#d8d4dc"), beard=("long", "#e6e0d6"),
                held=h("sword")),
    cleric("leo3_fr", "Папа Лев III", col="#f4f1ea", age="young", hair=("short", "#5a3a22")),
    R("einhard_fr", "Эйнхард", hair=("bowl", "#8a5a34"), outfit={"type": "robe", "col": "#7a6a52", "rope": "#d8c7a0"},
      sleeves=sl("#7a6a52"), held=h("book")),
    carolingian("lothair_fr", "Лотарь I", col="#5a2a6b", hair=("short", "#3b2a20"), beard=("full", "#3b2a20")),
    carolingian("louis_german_fr", "Людовик Немецкий", col="#5a6b4a", hair=("short", "#8a5a34"), beard=("goatee", "#8a5a34"),
                hat={"type": "circlet", "gold": "#d8ad3c"}),
    carolingian("charles_bald_fr", "Карл Лысый", col="#a8312f", hair=("receding", "#8a5a34"), beard=("goatee", "#8a5a34"),
                hat={"type": "circlet", "gold": "#d8ad3c"}),
    R("nithard_fr", "Нитхард", hair=("short", "#5a3a22"), outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": "#7a6a52",
      "belt": "#5b3a22"}, sleeves=sl("#a9b0b8"), legs=tr("#5a4434"), boots=bo("#5b3a22"), held=h("book")),
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
