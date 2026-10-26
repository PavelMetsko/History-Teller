#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 1 главы «Италия» (легенды, 476–1077).

    python3 tools/batches/italy_recipes_1.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/italy_recipes_1.py --ids      только список id (для factory/build.py)
    python3 tools/batches/italy_recipes_1.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, ROOT, OUT
from england_recipes_1 import lady, roman
from england_recipes_2 import knight, noble, cleric
from france_recipes_2 import monk, peasant


def barbarian(id, name, tunic="#5a6b4a", hair=("long", "#b97a45"), beard=("full", "#b97a45"), **kw):
    """Германский вождь V–VI века: рубаха с мехом, длинные волосы, меч."""
    d = dict(hair=hair, beard=beard, outfit={"type": "fur_tunic", "col": tunic, "fur": "#c9b08a", "rope": "#6b4426"},
             sleeves=sl(tunic), cape={"type": "cape", "col": "#7a2a2a"}, legs=tr("#5a4434"), boots=bo("#5b3a22"), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


def byzantine(id, name, col="#5a2a6b", **kw):
    """Византиец: далматика с золотом."""
    d = dict(hair=("short", "#3b2a20"), beard=("full", "#3b2a20"), skin="olive",
             outfit={"type": "emperor", "col": col, "gold": "#d8ad3c", "mantle": "#a8262e"}, sleeves=sl(col))
    d.update(kw)
    return R(id, name, **d)


def pope(id, name, col="#f1ece2", **kw):
    """Папа: белая ряса, митра, крест."""
    return cleric(id, name, col=col, cape={"type": "cape", "col": "#a8262e"}, **kw)


def arab(id, name, robe="#e9e0cc", turban="#f4f1ea", **kw):
    """Аглабидский эмир / учёный: халат, тюрбан."""
    d = dict(skin="tan", hair=("short", "#1e1a18"), beard=("full", "#1e1a18"), hat={"type": "turban", "col": turban, "jewel": "#2f6a4a"},
             outfit={"type": "robe", "col": robe, "rope": "#d4a63c"}, sleeves=sl(robe))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- легенды
    knight("galgano_it", "Рыцарь Гальгано", surcoat="#2f6a4a", hair=("shoulder", "#5a3a22"), held=h("sword")),
    R("michael_it", "Архангел Михаил", hair=("curly", "#d8b070"), outfit={"type": "chainmail", "steel": "#d8d4dc", "surcoat": "#f4f1ea", "belt": "#d4a63c"},
      sleeves=sl("#d8d4dc"), cape={"type": "wings", "col": "#e9e0cc", "feather": "#f4f1ea"}, hat={"type": "circlet", "gold": "#d8ad3c"},
      legs=tr("#e9e0cc"), boots=bo("#d4a63c"), held=h("spear")),
    lady("dionisia_it", "Мать Дионисия", dress="#5a4434", mantle="#3b2a20", hair=("long", "#b8b4c0"), age="old"),
    lady("polissena_it", "Невеста Полиссена", dress="#f4f1ea", mantle="#a8312f", hair=("long", "#8a5a34"), veil=False,
         hat={"type": "circlet", "gold": "#d8ad3c"}),
    R("colapesce_it", "Кола-Рыба", hair=("curly", "#2a1a12"), outfit={"type": "mermaid", "col": "#3f8a8a", "fin": "#6fb5a8", "top": "#e9e0cc"},
      sleeves=BARE, skin="tan"),
    lady("cola_mother_it", "Мать Колы", dress="#5a6b4a", mantle="#2a2a2e", hair=("long", "#3b2a20"), age="old", skin="tan"),
    knight("alberto_it", "Альберто да Джуссано", surcoat="#f4f1ea", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"),
           helm={"type": "nasal", "col": "#a9b0b8", "trim": "#a8312f"}, cape={"type": "cape", "col": "#a8312f"}),
    peasant("milan_exiles_it", "Изгнанники Милана", tunic="#7a6a52", hair=("shoulder", "#5a3a22"), beard=("full", "#5a3a22"), held=h("staff")),
    noble("cremona_it", "Консул Кремоны", col="#a8312f", hair=("short", "#3b2a20"), beard=("goatee", "#3b2a20"),
          hat={"type": "cap", "col": "#2f4a7a", "fur": ""}, held=h("scroll")),
    monk("pontida_abbot_it", "Аббат Понтиды", col="#1e1e22", age="old", hair=("receding", "#b8b4c0")),
    R("angels_it", "Ангелы с Домом", hair=("curly", "#d8b070"), outfit={"type": "gown", "dress": "#f4f1ea", "trim": "#d4a63c", "mantle": "#8fb5d8", "shoes": "#d4a63c"},
      sleeves=sl("#f4f1ea"), cape={"type": "wings", "col": "#e9e0cc", "feather": "#f4f1ea"}, male=False, iris="#5f7a9a"),
    lady("laureta_it", "Вдова Лорета", dress="#2f6a4a", mantle="#5a4434", hair=("long", "#5a3a22"), age="old"),
    peasant("recanati_brothers_it", "Братья из Реканати", tunic="#a88a5a", hair=("bowl", "#8a5a34"), beard=("full", "#8a5a34")),
    monk("hermit_paul_it", "Отшельник Павел", col="#7a6a52", age="old", hair=("long", "#d8d4dc"), beard=("long", "#e6e0d6"), held=h("staff")),
    # ---------- после Империи
    roman("orestes_it", "Патриций Орест", tunic="#5a2a6b", age="old", hair=("short", "#8a7a6a"), beard=("goatee", "#8a7a6a")),
    byzantine("zeno_it", "Император Зенон", hat={"type": "crown", "gold": "#d8ad3c"}, held=h("cross")),
    barbarian("theodoric_it", "Теодорих Остготский", tunic="#2f4a7a", hair=("long", "#d8b070"), beard=("handlebar", "#d8b070"),
              hat={"type": "circlet", "gold": "#d8ad3c"}),
    cleric("john_ravenna_it", "Епископ Иоанн Равеннский"),
    barbarian("alboin_it", "Король Альбоин", tunic="#7a2a2a", hat={"type": "circlet", "gold": "#d8ad3c"}),
    lady("rosamund_it", "Королева Розамунда", dress="#5a2a6b", mantle="#1e1e22", hair=("long", "#d8b070"), veil=False,
         hat={"type": "circlet", "gold": "#d8ad3c"}),
    barbarian("gisulf_it", "Гизульф Фриульский", tunic="#5a6b4a", hair=("long", "#8a5a34"), beard=("goatee", "#8a5a34"),
              hat={"type": "nasal", "col": "#a9b0b8", "trim": "#8a6a2a"}),
    byzantine("longinus_it", "Префект Лонгин", col="#2f4a7a", hair=("receding", "#3b2a20"), held=h("scroll")),
    noble("desiderius_it", "Король Дезидерий", col="#5a2a6b", hair=("long", "#8a7a6a"), beard=("long", "#b8b4c0"), age="old",
          hat={"type": "crown", "gold": "#d8ad3c"}, cape={"type": "cape", "col": "#a8312f"}),
    knight("adelchis_it", "Королевич Адельхиз", surcoat="#5a2a6b", hair=("long", "#8a5a34"), beard=("goatee", "#8a5a34"),
           helm={"type": "nasal", "col": "#a9b0b8", "trim": "#d4a63c"}),
    pope("hadrian1_it", "Папа Адриан I"),
    # ---------- Сицилия, Оттон
    byzantine("euphemius_it", "Турмарх Евфимий", col="#2f4a7a", hat={"type": "helmet", "col": "#b9bfc6", "trim": "#d4a63c"}, held=h("sword")),
    arab("ziyadat_it", "Эмир Зиядат-Аллах I", robe="#2f6a4a", turban="#f4f1ea", cape={"type": "cape", "col": "#d8ad3c"}),
    arab("asad_it", "Кади Асад ибн аль-Фурат", robe="#e9e0cc", age="old", beard=("long", "#e6e0d6"), held=h("book")),
    byzantine("theodotus_it", "Стратиг Феодот", col="#7a2a2a", hat={"type": "helmet", "col": "#b9bfc6", "trim": "#d4a63c"}, held=h("spear")),
    noble("otto1_it", "Оттон I", col="#a8312f", hair=("long", "#b97a45"), beard=("long", "#b97a45"),
          hat={"type": "crown", "gold": "#d8ad3c"}, cape={"type": "cape", "col": "#5a2a6b"}, held=h("sword")),
    lady("adelaide_it", "Королева Аделаида", dress="#2f4a7a", mantle="#a8312f", hair=("long", "#d8b070"), veil=False,
         hat={"type": "crown", "gold": "#d8ad3c"}),
    knight("berengar2_it", "Беренгар Иврейский", surcoat="#2a2a2e", hair=("short", "#2a1a12"), beard=("goatee", "#2a1a12")),
    pope("john12_it", "Папа Иоанн XII", hair=("short", "#3b2a20"), age="young"),
    # ---------- Мельфи, Каносса
    pope("nicholas2_pope_it", "Папа Николай II"),
    knight("guiscard_it", "Роберт Гвискар", surcoat="#2f4a7a", hair=("short", "#d8b070"), beard=("full", "#d8b070"),
           helm={"type": "nasal", "col": "#a9b0b8", "trim": "#8a6a2a"}, cape={"type": "cape", "col": "#d8ad3c"}),
    knight("richard_aversa_it", "Ричард Аверсский", surcoat="#a8312f", hair=("short", "#8a5a34"), beard=("goatee", "#8a5a34")),
    monk("hildebrand_it", "Архидиакон Гильдебранд", col="#1e1e22", hair=("receding", "#3b2a20"), held=h("scroll")),
    noble("henry4_it", "Король Генрих IV", col="#f4f1ea", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"), boots=bo("#f3c4a6")),
    pope("gregory7_it", "Папа Григорий VII", hair=("receding", "#8a7a6a"), beard=("goatee", "#b8b4c0")),
    lady("matilda_tus_it", "Матильда Тосканская", dress="#2f6a4a", mantle="#a8312f", hair=("long", "#b9672e"), veil=False,
         hat={"type": "circlet", "gold": "#d8ad3c"}),
    monk("hugh_cluny_it", "Аббат Гуго Клюнийский", col="#1e1e22", age="old", hair=("receding", "#d8d4dc")),
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
