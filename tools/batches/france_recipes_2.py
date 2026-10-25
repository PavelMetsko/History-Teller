#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 2 главы «Франция» (Капетинги … Нантский эдикт).

    python3 tools/batches/france_recipes_2.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/france_recipes_2.py --ids      только список id (для factory/build.py)
    python3 tools/batches/france_recipes_2.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, ROOT, OUT  # noqa: F401
from england_recipes_2 import knight, noble, cleric, lady, cavalier

CROWN = {"type": "crown", "gold": "#d8ad3c"}
NASAL = {"type": "nasal", "col": "#a9b0b8", "trim": "#8a6a2a"}
HELM = {"type": "helmet", "col": "#b9bfc6", "trim": "#8a6a2a"}


def monk(id, name, col="#f1ece2", **kw):
    """Монах/аббат: ряса с верёвкой, без митры."""
    d = dict(hair=("bowl", "#5a3a22"), outfit={"type": "robe", "col": col, "rope": "#7a5232"}, sleeves=sl(col), held=h("cross"))
    d.update(kw)
    return R(id, name, **d)


def peasant(id, name, tunic="#7a6a52", **kw):
    d = dict(hair=("short", "#5a3a22"), outfit={"type": "tunic", "col": tunic, "trim": "#5a4434", "belt": "#3b2a20"},
             sleeves=BARE, legs=tr("#5a4434"), boots=bo("#3b2a20"))
    d.update(kw)
    return R(id, name, **d)


def renaissance(id, name, col="#2a2a2e", **kw):
    """Дворянин XVI века: дублет с брыжами, бородка."""
    d = dict(hair=("short", "#3b2a20"), beard=("goatee", "#3b2a20"), collar={"type": "ruff", "col": "#f4f1ea"},
             outfit={"type": "doublet", "col": col, "trim": "#d4a63c", "chain": True}, sleeves=sl(col, "#f4f1ea"),
             legs=tr("#2a2a2e"), boots=bo("#1e1e22"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Роллон
    R("rollo_fr", "Роллон", hair=("long", "#c98a3a"), beard=("long", "#c98a3a"), bushy=True, hat=NASAL,
      outfit={"type": "fur_tunic", "col": "#5a6b4a", "fur": "#c9b08a", "rope": "#5a3a22"}, sleeves=BARE, legs=tr("#5a4434"),
      boots=bo("#3b2a20"), held=h("pickaxe")),
    noble("charles_simple_fr", "Карл III Простоватый", col="#2f4a7a", hat=CROWN, beard=("full", "#8a5a34"), hair=("shoulder", "#8a5a34"),
          cape={"type": "cape", "col": "#a8312f"}),
    cleric("franco_rouen_fr", "Архиепископ Франкон Руанский", col="#f1ece2"),
    knight("robert_neustria_fr", "Маркиз Роберт Нейстрийский", surcoat="#2f4a7a", helm=NASAL, beard=("full", "#5a3a22")),
    # ---------- Гуго Капет
    noble("hugh_capet_fr", "Гуго Капет", col="#2f4a7a", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22"),
          hat={"type": "hood", "col": "#2f4a7a"}, cape={"type": "cape", "col": "#d8ad3c"}),
    cleric("adalberon_fr", "Архиепископ Адальберон Реймсский", col="#5a2a6b"),
    noble("charles_lorraine_fr", "Карл Лотарингский", col="#a8312f", hat={"type": "circlet", "gold": "#d8ad3c"},
          beard=("full", "#3b2a20"), hair=("shoulder", "#3b2a20"), held=h("sword")),
    monk("gerbert_fr", "Учёный Герберт Орильякский", col="#3b2a20", age="old", hair=("receding", "#8a7a6a"), held=h("book")),
    # ---------- Клермон
    cleric("urban2_fr", "Папа Урбан II", col="#f4f1ea", hat={"type": "mitre", "col": "#f4f1ea", "trim": "#d4a63c"},
           cape={"type": "cape", "col": "#d8ad3c"}, beard=("full", "#d8d4dc")),
    cleric("adhemar_fr", "Епископ Адемар Монтейский", col="#a8312f", age="young", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22")),
    knight("raymond_toulouse_fr", "Граф Раймунд Тулузский", surcoat="#a8312f", hair=("short", "#b8b4c0"), beard=("full", "#d8d4dc"),
           age="old", cape={"type": "cape", "col": "#d8ad3c"}),
    monk("peter_hermit_fr", "Пётр Пустынник", col="#7a6a52", age="old", hair=("long", "#8a7a6a"), beard=("long", "#8a7a6a"),
         held=h("staff")),
    # ---------- Алиенора
    noble("louis7_fr", "Людовик VII", col="#2f4a7a", hat=CROWN, hair=("shoulder", "#d8b070"), cape={"type": "cape", "col": "#2f4a7a"}),
    monk("bernard_clairvaux_fr", "Аббат Бернар Клервоский", col="#f1ece2", age="old", hair=("receding", "#b8b4c0")),
    knight("theobald_blois_fr", "Граф Тибо Блуаский", surcoat="#5a2a6b", beard=("goatee", "#3b2a20")),
    # ---------- Шато-Гайар
    knight("roger_lacy_fr", "Комендант Роже де Ласи", surcoat="#d8ad3c", helm=HELM, beard=("full", "#3b2a20")),
    knight("pierre_preaux_fr", "Пьер де Прео, комендант Руана", surcoat="#a8312f", beard=("goatee", "#8a5a34"), held=h("scroll")),
    # ---------- Безье
    cleric("arnaud_amalric_fr", "Легат Арно Амальрик", col="#f1ece2", hat={"type": "mitre", "col": "#f1ece2", "trim": "#a8312f"},
           cape={"type": "cape", "col": "#1e1e22"}),
    knight("trencavel_fr", "Виконт Раймунд-Роже Транкавель", surcoat="#d8ad3c", hair=("long", "#3b2a20"),
           cape={"type": "cape", "col": "#a8312f"}),
    cleric("bishop_renaud_fr", "Епископ Рено де Монпейру", col="#2f4a7a", held=h("scroll")),
    knight("simon4_montfort_fr", "Симон IV де Монфор", surcoat="#a8312f", helm=HELM, beard=("full", "#2a1a12")),
    # ---------- Мансура
    noble("louis9_fr", "Людовик IX Святой", col="#2f4a7a", hat=CROWN, hair=("shoulder", "#d8b070"), cape={"type": "cape", "col": "#f4f1ea"},
          held=h("cross")),
    lady("marguerite_provence_fr", "Королева Маргарита Прованская", dress="#d8ad3c", mantle="#2f4a7a", hat=CROWN, hair_col="#8a5a34"),
    knight("joinville_fr", "Сенешаль Жан де Жуанвиль", surcoat="#2f6a4a", held=h("book"), hair=("shoulder", "#8a5a34")),
    R("turanshah_fr", "Султан Туран-шах", skin="olive", hair=("short", "#1e1a18"), beard=("goatee", "#1e1a18"),
      hat={"type": "turban", "col": "#f4f1ea", "jewel": "#2f9a8a"}, outfit={"type": "coat", "col": "#2f6a4a", "trim": "#d4a63c", "belt": "#d4a63c"},
      sleeves=sl("#2f6a4a"), legs=tr("#f4f1ea"), boots=bo("#a8312f"), held=h("sword")),
    knight("robert_artois_fr", "Граф Робер д'Артуа", surcoat="#2f4a7a", helm=HELM, held=h("sword")),
    # ---------- Жакерия
    peasant("guillaume_cale_fr", "Гильом Каль", tunic="#7a6a52", beard=("full", "#5a3a22"), held=h("scythe")),
    noble("charles_navarre_fr", "Карл Злой, король Наварры", col="#a8312f", hat=CROWN, hair=("shoulder", "#2a1a12"),
          beard=("goatee", "#2a1a12"), cape={"type": "cape", "col": "#1e1e22"}),
    noble("etienne_marcel_fr", "Этьен Марсель, купеческий старшина Парижа", col="#2f4a7a", trim="#a8312f",
          hat={"type": "hood", "col": "#a8312f"}, beard=("full", "#5a3a22")),
    # ---------- Кастийон
    noble("jean_bureau_fr", "Жан Бюро, мастер артиллерии", col="#3b3a38", hair=("bowl", "#5a3a22"), hat={"type": "cap", "col": "#2a2a2e", "fur": ""},
          held=h("flask")),
    knight("talbot_fr", "Джон Толбот, граф Шрусбери", surcoat="#a8312f", age="old", hair=("short", "#d8d4dc"), held=h("sword")),
    peasant("castillon_scout_fr", "Гонец из Кастийона", tunic="#a8794e", hat={"type": "cap", "col": "#5a6b4a", "fur": ""}),
    # ---------- Виллер-Котре
    renaissance("poyet_fr", "Канцлер Гийом Пойе", col="#1e1e22", beard=("full", "#5a3a22"), held=h("scroll"),
                hat={"type": "beret", "col": "#1e1e22", "feather": ""}),
    monk("cure_fr", "Сельский кюре", col="#1e1e22", hair=("bowl", "#8a5a34"), held=h("book")),
    lady("marguerite_navarre_fr", "Маргарита Наваррская", dress="#2a2a2e", mantle="#5a2a6b", hair_col="#8a5a34", held=h("book")),
    # ---------- Васси
    renaissance("louis_conde_fr", "Людовик Бурбон, принц Конде", col="#f4f1ea", beard=("goatee", "#5a3a22"),
                hat={"type": "beret", "col": "#1e1e22", "feather": "#f4f1ea"}, held=h("sword")),
    peasant("wassy_flock_fr", "Гугеноты Васси", tunic="#3b3a38", hair=("short", "#8a7a6a"), age="old", collar={"type": "ruff", "col": "#f4f1ea"},
            held=h("book")),
    # ---------- Нантский эдикт
    renaissance("mercoeur_fr", "Герцог де Меркёр", col="#a8312f", hat={"type": "beret", "col": "#1e1e22", "feather": "#a8312f"},
                cape={"type": "cape", "col": "#1e1e22"}),
    renaissance("duplessis_mornay_fr", "Филипп Дюплесси-Морне", col="#1e1e22", beard=("full", "#8a7a6a"), age="old", held=h("book")),
    renaissance("harlay_fr", "Первый президент Ашиль де Арле", col="#a8312f", beard=("full", "#d8d4dc"), age="old",
                hair=("receding", "#d8d4dc"), held=h("scroll")),
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
