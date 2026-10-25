#!/usr/bin/env python3
"""Рецепты фабрики для персонажей пачки 4 главы «Англия» (1859–1918).

    python3 tools/batches/england_recipes_4.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/england_recipes_4.py --ids      только список id (для factory/build.py)
    python3 tools/batches/england_recipes_4.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, victorian, edwardian, ROOT, OUT

KHAKI, FIELD_GREY, HORIZON = "#7a7a4a", "#6e7468", "#6f8fae"


def khaki(id, name, cap=KHAKI, **kw):
    """Британский офицер ВПМ: френч хаки, фуражка, сапоги."""
    d = dict(hair=("short", "#5a3a22"), hat={"type": "cap", "col": cap, "fur": ""},
             outfit={"type": "legion_tunic", "col": KHAKI, "belt": "#5a3a22", "button": "#c9a24a"},
             sleeves=sl(KHAKI), legs=tr(KHAKI), boots=tall("#5a3a22"))
    d.update(kw)
    return R(id, name, **d)


def lady(id, name, dress="#2a2a2e", **kw):
    """Дама рубежа веков: длинное платье, широкая шляпа."""
    d = dict(male=False, hair=("long", "#3b2a20"), hat={"type": "wide", "col": "#1e1e22", "feather": ""},
             outfit={"type": "gown", "dress": dress, "trim": "#f4f1ea", "mantle": dress, "shoes": "#1e1e22"},
             sleeves=sl(dress, "#f4f1ea"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Дарвин
    victorian("charles_darwin", "Чарльз Дарвин", coat="#3b3a38", age="old", hair=("receding", "#e6e0d6"),
              beard=("long", "#ece8e2"), bushy=True, held=h("book")),
    victorian("alfred_wallace", "Альфред Рассел Уоллес", coat="#5a4434", hair=("short", "#d8d4dc"), beard=("full", "#e6e0d6"),
              glasses={"type": "round", "col": "#3a2a20"}),
    victorian("thomas_huxley", "Томас Гексли", coat="#1e1e22", hair=("shoulder", "#2a1a12"), bushy=True),
    R("samuel_wilberforce", "Епископ Сэмюэл Уилберфорс", age="old", hair=("receding", "#8a7a6a"),
      collar={"type": "ruff", "col": "#f4f1ea"}, outfit={"type": "robe", "col": "#1e1e22", "rope": "#f4f1ea"},
      sleeves=sl("#f4f1ea"), held=h("cross")),
    lady("emma_darwin", "Эмма Дарвин", dress="#3b4a5a", hair=("long", "#5a3a22"), hat={"type": "veil", "col": "#f4f1ea", "band": ""}),
    # ---------- Гомруль
    victorian("charles_parnell", "Чарльз Стюарт Парнелл", coat="#1e1e22", tie="#2f6a4a", hair=("receding", "#5a3a22"),
              beard=("full", "#5a3a22")),
    victorian("joseph_chamberlain", "Джозеф Чемберлен", coat="#2a2a2e", tie="#a8312f", hair=("short", "#1e1a18"),
              glasses={"type": "pince", "col": "#3a2a20"}),
    victorian("randolph_churchill", "Лорд Рэндольф Черчилль", coat="#3b3a38", tie="#d4a63c", hair=("receding", "#5a3a22"),
              beard=("walrus", "#5a3a22")),
    # ---------- Англо-бурская война
    khaki("kitchener", "Лорд Китченер", hair=("short", "#8a7a6a"), beard=("handlebar", "#8a7a6a"), bushy=True, held=h("bulawa")),
    R("louis_botha", "Генерал Луис Бота", hair=("short", "#3b2a20"), beard=("full", "#3b2a20"),
      hat={"type": "wide", "col": "#5a4434", "feather": ""}, outfit={"type": "coat", "col": "#7a6a52", "trim": "#5a4434", "belt": "#3b2a20"},
      sleeves=sl("#7a6a52"), legs=tr("#5a4434"), boots=tall("#3b2a20"), held=h("spear")),
    lady("emily_hobhouse", "Эмили Хобхаус", dress="#5a6b4a", held=h("book")),
    edwardian("sol_plaatje", "Сол Плаатье", skin="african", coat="#2a2a2e", hair=("short", "#1e1a18"),
              beard=("handlebar", "#1e1a18"), glasses={"type": "round", "col": "#3a2a20"}, held=h("scroll")),
    victorian("paul_kruger", "Президент Пауль Крюгер", coat="#1e1e22", age="old", hair=("short", "#8a8a8a"),
              beard=("full", "#b8b4c0"), hat={"type": "top", "col": "#1e1e22"}),
    # ---------- суфражистки 1913
    lady("emmeline_pankhurst", "Эммелин Панкхёрст", dress="#5a2a6b", hat={"type": "wide", "col": "#1e1e22", "feather": "#2f6a4a"},
         held=h("flag")),
    lady("millicent_fawcett", "Миллисент Фосетт", dress="#2f4a3a", age="old", hair=("long", "#8a7a6a"),
         hat={"type": "veil", "col": "#2a2a2e", "band": ""}, held=h("scroll")),
    lady("emily_davison", "Эмили Дэвисон", dress="#f4f1ea", hair=("long", "#b9672e"),
         hat={"type": "wide", "col": "#5a2a6b", "feather": "#2f6a4a"}, held=h("flag")),
    edwardian("herbert_asquith", "Премьер Герберт Асквит", coat="#1e1e22", age="old", hair=("receding", "#e6e0d6")),
    R("george5", "Король Георг V", hair=("short", "#5a3a22"), beard=("full", "#5a3a22"),
      outfit={"type": "uniform", "col": "#1e2a44", "facing": "#1e2a44", "trim": "#d4a63c", "sash": "#2f4a9a", "epaulettes": True},
      sleeves=sl("#1e2a44"), legs=tr("#1e2a44"), boots=tall()),
    # ---------- 1914
    edwardian("edward_grey", "Сэр Эдвард Грей", coat="#2a2a2e", hair=("receding", "#8a7a6a")),
    R("wilhelm2", "Кайзер Вильгельм II", hair=("short", "#5a3a22"), beard=("handlebar", "#5a3a22"), bushy=True,
      hat={"type": "pickelhaube", "col": "#1e1e22", "metal": "#d4a63c"},
      outfit={"type": "uniform", "col": FIELD_GREY, "facing": "#a8312f", "trim": "#d4a63c", "sash": "", "epaulettes": True},
      sleeves=sl(FIELD_GREY), legs=tr(FIELD_GREY), boots=tall(), held=h("bulawa")),
    edwardian("lloyd_george", "Дэвид Ллойд Джордж", coat="#3b3a38", hair=("shoulder", "#d8d4dc"), beard=("walrus", "#d8d4dc")),
    # ---------- Пасхальное восстание
    R("patrick_pearse", "Патрик Пирс", hair=("short", "#3b2a20"), hat={"type": "wide", "col": "#4a5a3a", "feather": ""},
      outfit={"type": "legion_tunic", "col": "#4a5a3a", "belt": "#5a3a22", "button": "#c9a24a"}, sleeves=sl("#4a5a3a"),
      legs=tr("#4a5a3a"), boots=tall("#5a3a22"), held=h("scroll")),
    R("james_connolly", "Джеймс Коннолли", hair=("receding", "#5a3a22"), beard=("walrus", "#5a3a22"), hat={"type": "cap", "col": "#2f4a3a", "fur": ""},
      outfit={"type": "legion_tunic", "col": "#2f4a3a", "belt": "#5a3a22", "button": "#c9a24a"}, sleeves=sl("#2f4a3a"),
      legs=tr("#2f4a3a"), boots=tall("#5a3a22")),
    lady("constance_markievicz", "Графиня Констанция Маркевич", dress="#4a5a3a", hat={"type": "wide", "col": "#2f4a3a", "feather": "#f4f1ea"},
         hair=("long", "#5a3a22")),
    khaki("john_maxwell", "Генерал Джон Максвелл", cap="#a8312f", hair=("short", "#8a7a6a"), beard=("walrus", "#8a7a6a")),
    edwardian("john_redmond", "Джон Редмонд", coat="#1e1e22", hair=("receding", "#5a3a22")),
    # ---------- Сомма
    khaki("douglas_haig", "Генерал Дуглас Хейг", cap="#a8312f", hair=("short", "#b8b4c0"), beard=("walrus", "#b8b4c0")),
    khaki("henry_rawlinson", "Генерал Генри Роулинсон", cap="#a8312f", hair=("short", "#5a3a22"), beard=("handlebar", "#5a3a22")),
    R("fritz_von_below", "Генерал Фриц фон Белов", age="old", hair=("short", "#d8d4dc"), beard=("handlebar", "#d8d4dc"),
      hat={"type": "pickelhaube", "col": "#1e1e22", "metal": "#a9b0b8"},
      outfit={"type": "uniform", "col": FIELD_GREY, "facing": "#a8312f", "trim": "#a9b0b8", "sash": "", "epaulettes": True},
      sleeves=sl(FIELD_GREY), legs=tr(FIELD_GREY), boots=tall()),
    khaki("siegfried_sassoon", "Лейтенант Зигфрид Сассун", hair=("short", "#3b2a20"), held=h("book")),
    # ---------- 1918
    R("ferdinand_foch", "Маршал Фердинанд Фош", age="old", hair=("short", "#b8b4c0"), beard=("walrus", "#b8b4c0"),
      hat={"type": "cap", "col": "#a8312f", "fur": ""},
      outfit={"type": "legion_tunic", "col": HORIZON, "belt": "#5a3a22", "button": "#d4a63c"}, sleeves=sl(HORIZON),
      legs=tr("#a8312f"), boots=tall("#1e1e22"), held=h("bulawa")),
    edwardian("matthias_erzberger", "Маттиас Эрцбергер", coat="#2a2a2e", hair=("short", "#3b2a20"),
              glasses={"type": "round", "col": "#3a2a20"}, held=h("scroll")),
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
