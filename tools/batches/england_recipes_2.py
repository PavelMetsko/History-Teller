#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 2 главы «Англия» (Средние века + Стюарты).

    python3 tools/batches/england_recipes_2.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/england_recipes_2.py --ids      только список id (для factory/build.py)
    python3 tools/batches/england_recipes_2.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, puritan, colonial, ROOT, OUT  # noqa: F401


def knight(id, name, surcoat="#a8312f", helm=None, **kw):
    """Рыцарь XI–XIV века: кольчуга с сюрко."""
    d = dict(hair=("short", "#5a3a22"), outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": surcoat, "belt": "#5b3a22"},
             sleeves=sl("#a9b0b8"), legs=tr("#7a7f86"), boots=bo("#3b2a20"), held=h("sword"),
             hat=helm or {"type": "none"})
    d.update(kw)
    return R(id, name, **d)


def noble(id, name, col="#2f4a7a", trim="#d4a63c", **kw):
    """Знатный мирянин Средних веков: туника с поясом."""
    d = dict(hair=("shoulder", "#5a3a22"), outfit={"type": "tunic", "col": col, "trim": trim, "belt": "#6b4426"},
             sleeves=sl(col), legs=tr("#3b2a20"), boots=bo("#3b2a20"))
    d.update(kw)
    return R(id, name, **d)


def cleric(id, name, col="#f1ece2", mitre=True, **kw):
    """Епископ: ряса, митра, посох."""
    d = dict(age="old", hair=("receding", "#b8b4c0"), outfit={"type": "robe", "col": col, "rope": "#d4a63c"},
             sleeves=sl(col), hat={"type": "mitre", "col": "#f1ece2", "trim": "#d4a63c"} if mitre else {"type": "none"},
             cape={"type": "cape", "col": "#a8312f"}, held=h("cross"))
    d.update(kw)
    return R(id, name, **d)


def lady(id, name, dress="#2f4a7a", mantle="#a8312f", hair_col="#6b4426", **kw):
    d = dict(male=False, hair=("long", hair_col), hat={"type": "veil", "col": "#f4f1ea", "band": "#d8ad3c"},
             outfit={"type": "gown", "dress": dress, "trim": "#d4a63c", "mantle": mantle, "shoes": "#3b2a20"}, sleeves=sl(dress))
    d.update(kw)
    return R(id, name, **d)


def cavalier(id, name, col="#a8312f", **kw):
    """Роялист 1640-х: дублет, длинные локоны, широкополая шляпа с пером."""
    d = dict(hair=("long", "#3b2a20"), beard=("goatee", "#3b2a20"), hat={"type": "wide", "col": "#1e1e22", "feather": "#f4f1ea"},
             collar={"type": "ruff", "col": "#f4f1ea"}, outfit={"type": "doublet", "col": col, "trim": "#d4a63c", "chain": False},
             sleeves=sl(col, "#f4f1ea"), legs=tr("#2a2a2e"), boots=tall("#3b2a20"), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


def roundhead(id, name, coat="#a8794e", **kw):
    """Парламентарий армии нового образца: буфф-кафтан, кираса, шлем-«горшок»."""
    d = dict(hair=("shoulder", "#5a3a22"), hat={"type": "helmet", "col": "#7a7f86", "trim": "#3b3a38"},
             outfit={"type": "coat", "col": coat, "trim": "#a8312f", "belt": "#5b3a22"}, sleeves=sl(coat),
             legs=tr("#3b3a38"), boots=tall("#3b2a20"), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Domesday
    cleric("st_calais", "Епископ Вильгельм де Сен-Кале", age="young", hair=("bowl", "#3b2a20"), held=h("book")),
    knight("picot_en", "Шериф Пико Кембриджский", surcoat="#5a4434", hair=("bowl", "#2a1a12"), beard=("full", "#2a1a12"), bushy=True,
           helm={"type": "nasal", "col": "#a9b0b8", "trim": "#8a6a2a"}),
    R("thegn_en", "Тэн-держатель", age="old", hair=("long", "#b8b4c0"), beard=("long", "#d8d4dc"),
      outfit={"type": "fur_tunic", "col": "#7a6a52", "fur": "#c9b08a", "rope": "#5a3a22"}, sleeves=sl("#7a6a52"), legs=tr("#5a4434"),
      boots=bo("#3b2a20"), held=h("staff")),
    # ---------- Анархия
    lady("matilda_emp", "Императрица Матильда", dress="#f4f1ea", mantle="#f4f1ea", hat={"type": "crown", "gold": "#d8ad3c"}),
    noble("stephen_king", "Король Стефан", col="#a8312f", hat={"type": "crown", "gold": "#d8ad3c"}, beard=("full", "#5a3a22"),
          cape={"type": "cape", "col": "#2f4a7a"}, held=h("sword")),
    knight("robert_gloucester", "Роберт Глостерский", surcoat="#d8ad3c", beard=("goatee", "#3b2a20"), cape={"type": "cape", "col": "#a8312f"}),
    cleric("henry_blois", "Епископ Генрих Блуаский", col="#5a2a6b", beard=("goatee", "#3b2a20"), hair=("short", "#3b2a20")),
    # ---------- де Монфор
    knight("simon_montfort", "Симон де Монфор", surcoat="#a8312f", hair=("short", "#3b2a20"), beard=("full", "#3b2a20"),
           cape={"type": "cape", "col": "#f4f1ea"}),
    noble("henry3", "Генрих III", col="#2f4a7a", age="old", hair=("shoulder", "#b8b4c0"), beard=("full", "#d8d4dc"),
          hat={"type": "crown", "gold": "#d8ad3c"}, cape={"type": "cape", "col": "#a8312f"}),
    knight("mortimer_wigmore", "Роджер Мортимер из Вигмора", surcoat="#2f6a4a", beard=("goatee", "#5a3a22"),
           helm={"type": "helmet", "col": "#b9bfc6", "trim": "#8a6a2a"}),
    # ---------- Уэльс
    noble("llywelyn_ap", "Лливелин ап Грифид", col="#2f6a4a", trim="#a8312f", hat={"type": "circlet", "gold": "#d8ad3c"},
          beard=("full", "#5a3a22"), cape={"type": "cape", "col": "#a8312f"}, held=h("spear")),
    knight("dafydd_ap", "Давид ап Грифид", surcoat="#2f6a4a", hair=("shoulder", "#8a5a34"), beard=("goatee", "#8a5a34")),
    cleric("pecham", "Архиепископ Джон Пекхэм", col="#5b4636", held=h("scroll")),
    # ---------- Шотландия
    knight("robert_bruce", "Роберт Брюс", surcoat="#d8ad3c", hair=("shoulder", "#8a5a34"), beard=("full", "#8a5a34"),
           hat={"type": "circlet", "gold": "#d8ad3c"}, held=h("pickaxe")),
    knight("thomas_randolph", "Томас Рэндольф", surcoat="#f4f1ea", beard=("goatee", "#5a3a22"), held=h("spear"),
           helm={"type": "helmet", "col": "#b9bfc6", "trim": "#8a6a2a"}),
    knight("henry_bohun", "Сэр Генри де Богун", surcoat="#2f4a7a", hair=("short", "#d8b070"), held=h("spear"),
           helm={"type": "nasal", "col": "#b9bfc6", "trim": "#d4a63c"}),
    # ---------- чума
    cleric("islip", "Архиепископ Симон Ислип"),
    R("knighton", "Хронист Генри Найтон", hair=("bowl", "#8a7a6a"), outfit={"type": "robe", "col": "#2a2a2e", "rope": "#f4f1ea"},
      sleeves=sl("#2a2a2e"), held=h("book")),
    R("reaper_en", "Жнец-подёнщик", hair=("bowl", "#8a5a34"), beard=("goatee", "#8a5a34"), hat={"type": "hood", "col": "#7a6a52"},
      outfit={"type": "tunic", "col": "#a88a5a", "trim": "#7a6a52", "belt": "#5a3a22"}, sleeves=BARE, legs=tr("#7a6a52"),
      boots=bo("#5a3a22"), held=h("scythe")),
    # ---------- Уиклиф
    R("wycliffe", "Джон Уиклиф", age="old", hair=("receding", "#d8d4dc"), beard=("long", "#e6e0d6"),
      outfit={"type": "robe", "col": "#3b2a20", "rope": "#d8c7a0"}, sleeves=sl("#3b2a20"), held=h("book")),
    noble("john_gaunt", "Джон Гонт", col="#a8312f", trim="#2f4a7a", beard=("full", "#5a3a22"), hat={"type": "cap", "col": "#2f4a7a", "fur": "#e9e0cc"},
          cape={"type": "cape", "col": "#2f4a7a"}),
    cleric("courtenay", "Архиепископ Уильям Куртене", age="young", hair=("short", "#3b2a20")),
    lady("anne_bohemia", "Анна Богемская", dress="#5a2a6b", mantle="#d8ad3c", hair_col="#d8b070", hat={"type": "crown", "gold": "#d8ad3c"}),
    # ---------- Фелтон
    R("buckingham_v", "Джордж Вильерс, герцог Бекингем", hair=("shoulder", "#8a5a34"), beard=("goatee", "#8a5a34"), collar={"type": "ruff", "col": "#f4f1ea"},
      hat={"type": "wide", "col": "#2a2a2e", "feather": "#f4f1ea"}, outfit={"type": "doublet", "col": "#d8c7a0", "trim": "#d4a63c", "chain": True},
      sleeves=sl("#d8c7a0"), legs=tr("#2a2a2e"), boots=tall("#3b2a20")),
    R("john_eliot", "Сэр Джон Элиот", hair=("shoulder", "#3b2a20"), beard=("goatee", "#3b2a20"), collar={"type": "ruff", "col": "#f4f1ea"},
      outfit={"type": "doublet", "col": "#1e1e22", "trim": "#f4f1ea", "chain": False}, sleeves=sl("#1e1e22"), legs=tr("#1e1e22"),
      boots=bo("#1e1e22"), held=h("scroll")),
    R("john_felton", "Лейтенант Джон Фелтон", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22"),
      outfit={"type": "coat", "col": "#7a6a52", "trim": "#5a4434", "belt": "#3b2a20"}, sleeves=sl("#7a6a52"), legs=tr("#5a4434"),
      boots=tall("#3b2a20"), held=h("sword")),
    # ---------- Гражданская война
    cavalier("prince_rupert", "Принц Руперт", col="#a8312f", hair=("long", "#1e1a18"), beard=None),
    roundhead("fairfax", "Сэр Томас Фэрфакс", coat="#a8794e", hair=("long", "#1e1a18"), beard=("handlebar", "#1e1a18"), hat=None,
              cape={"type": "cape", "col": "#a8312f"}),
    roundhead("ireton", "Генри Айртон", coat="#7a6a52", hat=None, beard=("goatee", "#5a3a22"), held=h("scroll")),
    roundhead("rainsborough", "Полковник Томас Рейнсборо", coat="#a8794e", hat={"type": "wide", "col": "#1e1e22", "feather": ""},
              beard=("handlebar", "#3b2a20")),
    puritan("sexby", "Агитатор Эдвард Сексби", coat="#5a4434", hat={"type": "wide", "col": "#3b2a20", "feather": "#2f6a4a"}, held=h("flag")),
    cavalier("arthur_aston", "Сэр Артур Астон", col="#5a2a6b", age="old", hair=("long", "#b8b4c0"), beard=("goatee", "#d8d4dc"),
             hat={"type": "helmet", "col": "#7a7f86", "trim": "#d4a63c"}, held=h("staff")),
    cavalier("ormond", "Маркиз Ормонд", col="#2f4a7a", hair=("long", "#8a5a34"), beard=("handlebar", "#8a5a34"), held=h("bulawa")),
    # ---------- «Начала»
    colonial("newton", "Исаак Ньютон", coat="#5a2a6b", vest="#e9d8a8", hat=None, held=h("book")),
    colonial("hooke", "Роберт Гук", coat="#3b3a38", vest="#7a6a52", hat=None, wig=False, hair_col="#3b2a20", held=h("flask")),
    colonial("halley", "Эдмонд Галлей", coat="#2f4a7a", vest="#f4f1ea", hat=None, hair_col="#d8c7a0", held=h("scroll")),
    colonial("flamsteed", "Королевский астроном Джон Флемстид", coat="#1e1e22", vest="#5a4434", hat=None, wig=False,
             hair_col="#5a3a22", age="old"),
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
