#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 1 главы «Англия» (легенды, римляне, саксы, викинги).

    python3 tools/batches/england_recipes_1.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/england_recipes_1.py --ids      только список id (для factory/build.py)
    python3 tools/batches/england_recipes_1.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, ROOT, OUT

SANDALS = {"type": "sandals", "strap": "#8a5a2a"}


def saxon(id, name, tunic="#4f6b8a", trim="#d4a63c", hair=("shoulder", "#8a5a34"), beard=("full", "#8a5a34"), **kw):
    """Англосакс / бритт: туника с поясом, штаны, плащ по желанию."""
    d = dict(hair=hair, beard=beard, outfit={"type": "tunic", "col": tunic, "trim": trim, "belt": "#6b4426"},
             sleeves=sl(tunic), legs=tr("#5a4434"), boots=bo("#5b3a22"))
    d.update(kw)
    return R(id, name, **d)


def lady(id, name, dress="#4f6b8a", mantle="#a8262e", hair=("long", "#8a5a34"), veil=True, **kw):
    """Дама раннего средневековья: платье, мантия, покрывало."""
    d = dict(male=False, hair=hair, hat={"type": "veil", "col": "#f4f1ea", "band": ""} if veil else None,
             outfit={"type": "gown", "dress": dress, "trim": "#d4a63c", "mantle": mantle, "shoes": "#5b3a22"}, sleeves=sl(dress))
    d.update(kw)
    return R(id, name, **d)


def roman(id, name, tunic="#a8312f", **kw):
    """Римский военачальник: мундир-лорика, шлем, плащ, сандалии."""
    d = dict(hair=("short", "#3b2a20"), skin="olive", hat={"type": "helmet", "col": "#b9bfc6", "trim": "#d4a63c"},
             outfit={"type": "legion_tunic", "col": tunic, "belt": "#6b4426", "button": "#d4a63c"}, cape={"type": "cape", "col": "#a8262e"},
             sleeves=BARE, boots=SANDALS, held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- легенды
    saxon("arthur_en", "Юный Артур", tunic="#2f4a7a", hair=("short", "#d8b070"), beard=None, held=h("sword")),
    R("merlin_en", "Мерлин", age="old", hair=("long", "#d8d4dc"), beard=("long", "#e6e0d6"), hat={"type": "hood", "col": "#2f4a7a"},
      outfit={"type": "robe", "col": "#2f4a7a", "rope": "#d8ad3c"}, sleeves=sl("#2f4a7a"), held=h("staff"), iris="#5f7a9a"),
    R("kay_en", "Сэр Кей", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22"),
      outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": "#a8312f", "belt": "#5b3a22"}, sleeves=sl("#a9b0b8"),
      legs=tr("#3b2a20"), boots=bo("#3b2a20"), held=h("spear")),
    lady("guinevere_en", "Гвиневра", dress="#f4f1ea", mantle="#2f6a4a", hair=("long", "#d8b070"), veil=False,
         hat={"type": "circlet", "gold": "#d8ad3c"}, iris="#2f6a4a"),
    lady("godiva_en", "Леди Годива", dress="#e9d8a8", mantle="#5a2a6b", hair=("long", "#d8b070"), veil=False,
         hat={"type": "circlet", "gold": "#d8ad3c"}),
    saxon("leofric_en", "Граф Леофрик", tunic="#5a2a6b", hair=("shoulder", "#b8b4c0"), beard=("full", "#d8d4dc"), age="old",
          cape={"type": "cape", "col": "#a8262e"}, hat={"type": "circlet", "gold": "#d8ad3c"}),
    saxon("peeping_tom_en", "Подглядывающий Том", tunic="#7a6a52", trim="#5a4434", hair=("bowl", "#8a5a34"), beard=None,
          hat={"type": "cap", "col": "#5a6b4a", "fur": ""}),
    R("robin_hood_en", "Робин Гуд", hair=("short", "#8a5a34"), beard=("goatee", "#8a5a34"), hat={"type": "hood", "col": "#2f6a4a"},
      outfit={"type": "tunic", "col": "#2f6a4a", "trim": "#7a5232", "belt": "#5b3a22"}, sleeves=sl("#2f6a4a"),
      legs=tr("#5a6b4a"), boots=bo("#5b3a22"), held=h("spear")),
    saxon("little_john_en", "Маленький Джон", tunic="#7a5232", trim="#5a4434", hair=("curly", "#3b2a20"), beard=("full", "#3b2a20"),
          bushy=True, held=h("staff")),
    R("sheriff_nott_en", "Шериф Ноттингемский", hair=("short", "#2a1a12"), beard=("goatee", "#2a1a12"), hat={"type": "cap", "col": "#1e1e22", "fur": "#5a4434"},
      outfit={"type": "coat", "col": "#1e1e22", "trim": "#a8312f", "belt": "#5b3a22"}, cape={"type": "cape", "col": "#a8312f"},
      sleeves=sl("#1e1e22"), legs=tr("#2a2a2e"), boots=tall()),
    lady("marian_en", "Дева Мэриан", dress="#5a6b4a", mantle="#7a5232", hair=("long", "#b9672e"), veil=False),
    saxon("whittington_en", "Дик Уиттингтон", tunic="#7a6a52", trim="#5a4434", hair=("bowl", "#8a5a34"), beard=None,
          hat={"type": "cap", "col": "#a8312f", "fur": ""}, held=h("staff")),
    R("fitzwarren_en", "Купец Фицуорин", age="old", hair=("receding", "#b8b4c0"), beard=("full", "#d8d4dc"),
      hat={"type": "cap", "col": "#2a2a2e", "fur": "#5a4434"}, outfit={"type": "coat", "col": "#7a2a2a", "trim": "#d4a63c", "belt": "#5b3a22"},
      sleeves=sl("#7a2a2a"), legs=tr("#2a2a2e"), boots=bo("#3b2a20"), held=h("scroll")),
    lady("alice_fitz_en", "Алиса Фицуорин", dress="#a8312f", mantle="#e9d8a8", hair=("long", "#8a5a34")),
    # ---------- римляне и бритты
    roman("plautius_en", "Авл Плавтий", hair=("short", "#8a7a6a"), age="old"),
    saxon("caratacus_en", "Каратак", tunic="#2f6a4a", trim="#d8ad3c", hair=("long", "#b9672e"), beard=("handlebar", "#b9672e"),
          sleeves=BARE, cape={"type": "cape", "col": "#5a6b4a"}, held=h("spear"), iris="#5f7a9a"),
    saxon("togodumnus_en", "Тогодумн", tunic="#a8312f", trim="#d8ad3c", hair=("long", "#8a5a34"), beard=("walrus", "#8a5a34"),
          sleeves=BARE, held=h("sword")),
    lady("boudica_en", "Боудикка", dress="#2f6a4a", mantle="#a8312f", hair=("long", "#b9672e"), veil=False,
         hat={"type": "circlet", "gold": "#d8ad3c"}, held=h("spear"), iris="#5f7a9a"),
    roman("suetonius_en", "Светоний Паулин", hair=("receding", "#5a5a5a"), age="old"),
    R("catus_en", "Прокуратор Кат Дециан", skin="olive", hair=("receding", "#3b2a20"),
      outfit={"type": "toga", "cloth": "#f7ede2", "band": "#a8312f", "gold": "#d8ad3c"}, sleeves=sl("#f7ede2"), boots=SANDALS, held=h("scroll")),
    # ---------- Кент, Уэссекс, датчане
    R("augustine_en", "Августин", skin="olive", age="old", hair=("receding", "#8a7a6a"),
      outfit={"type": "robe", "col": "#3b2a20", "rope": "#d8c7a0"}, sleeves=sl("#3b2a20"), held=h("cross")),
    saxon("aethelberht_en", "Король Этельберт", tunic="#7a2a2a", hair=("shoulder", "#d8b070"), beard=("full", "#d8b070"),
          hat={"type": "crown", "gold": "#d8ad3c"}, cape={"type": "cape", "col": "#2f4a7a"}),
    lady("bertha_en", "Королева Берта", dress="#2f4a7a", mantle="#d8ad3c", hair=("long", "#3b2a20"), held=h("cross")),
    R("gregory_en", "Папа Григорий Великий", skin="olive", age="old", hair=("receding", "#d8d4dc"), beard=("full", "#d8d4dc"),
      hat={"type": "mitre", "col": "#f1ece2", "trim": "#d4a63c"}, outfit={"type": "robe", "col": "#f1ece2", "rope": "#d4a63c"},
      cape={"type": "cape", "col": "#a8262e"}, sleeves=sl("#f1ece2"), held=h("book")),
    saxon("alfred_en", "Альфред Великий", tunic="#2f4a7a", hair=("shoulder", "#8a5a34"), beard=("full", "#8a5a34"),
          hat={"type": "crown", "gold": "#d8ad3c"}, cape={"type": "cape", "col": "#a8262e"}, held=h("sword")),
    R("guthrum_en", "Гутрум", hair=("long", "#d8b070"), beard=("long", "#d8b070"), bushy=True, hat={"type": "nasal", "col": "#a9b0b8", "trim": "#8a6a2a"},
      outfit={"type": "fur_tunic", "col": "#7a5232", "fur": "#c9b08a", "rope": "#5a3a22"}, sleeves=BARE, legs=tr("#5a4434"),
      boots=bo("#5b3a22"), held=h("spear"), iris="#5f7a9a"),
    R("odda_en", "Олдермен Одда", age="old", hair=("short", "#b8b4c0"), beard=("full", "#b8b4c0"), hat={"type": "nasal", "col": "#a9b0b8", "trim": "#8a6a2a"},
      outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": "#5a6b4a", "belt": "#5b3a22"}, sleeves=sl("#a9b0b8"),
      legs=tr("#5a4434"), boots=bo("#5b3a22"), held=h("spear")),
    lady("ealhswith_en", "Королева Эалсвита", dress="#7a2a2a", mantle="#2f4a7a", hair=("long", "#5a3a22")),
    R("cnut_en", "Кнуд", hair=("long", "#d8b070"), beard=("goatee", "#d8b070"), hat={"type": "crown", "gold": "#d8ad3c"},
      outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": "#a8312f", "belt": "#5b3a22"}, cape={"type": "cape", "col": "#1e1e22"},
      sleeves=sl("#a9b0b8"), legs=tr("#3b2a20"), boots=bo("#3b2a20"), held=h("sword"), iris="#5f7a9a"),
    R("edmund_ironside_en", "Эдмунд Железнобокий", hair=("shoulder", "#5a3a22"), beard=("full", "#5a3a22"),
      hat={"type": "nasal", "col": "#a9b0b8", "trim": "#d4a63c"},
      outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": "#2f4a7a", "belt": "#5b3a22"}, sleeves=sl("#a9b0b8"),
      legs=tr("#3b2a20"), boots=bo("#3b2a20"), held=h("sword")),
    saxon("eadric_en", "Эдрик Стреона", tunic="#5a6b4a", trim="#d4a63c", hair=("short", "#2a1a12"), beard=("goatee", "#2a1a12"),
          cape={"type": "cape", "col": "#3b3a38"}),
    lady("emma_en", "Эмма Нормандская", dress="#5a2a6b", mantle="#d8ad3c", hair=("long", "#8a5a34"), hat={"type": "crown", "gold": "#d8ad3c"}),
    R("edward_conf_en", "Эдуард Исповедник", age="old", hair=("long", "#e6e0d6"), beard=("long", "#e6e0d6"), hat={"type": "crown", "gold": "#d8ad3c"},
      outfit={"type": "emperor", "col": "#2f4a7a", "gold": "#d8ad3c", "mantle": "#a8262e"}, sleeves=sl("#2f4a7a"), held=h("cross")),
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
