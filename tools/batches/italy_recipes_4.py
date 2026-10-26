#!/usr/bin/env python3
"""Рецепты фабрики для персонажей пачки 4 главы «Италия» (1861–1918).

    python3 tools/batches/italy_recipes_4.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/italy_recipes_4.py --ids      только список id (для factory/build.py)
    python3 tools/batches/italy_recipes_4.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, victorian, edwardian, worker, ROOT, OUT

IT_BLUE, GREY_GREEN, AUSTRIAN, FELDGRAU = "#2f3f5a", "#6e7458", "#8a95a0", "#6e7468"


def it_general(id, name, coat=IT_BLUE, **kw):
    """Итальянский генерал второй половины XIX века: тёмно-синий мундир, кепи."""
    d = dict(hair=("short", "#8a7a6a"), hat={"type": "cap", "col": coat, "fur": ""},
             outfit={"type": "uniform", "col": coat, "facing": "#a8312f", "trim": "#d4a63c", "sash": "#2f6aa8", "epaulettes": True},
             sleeves=sl(coat), legs=tr("#3b4a6a"), boots=tall(), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


def ww1(id, name, col=GREY_GREEN, **kw):
    """Генерал Первой мировой: полевой китель, фуражка."""
    d = dict(hair=("short", "#b8b4c0"), hat={"type": "cap", "col": col, "fur": ""},
             outfit={"type": "legion_tunic", "col": col, "belt": "#5a3a22", "button": "#d4a63c"},
             sleeves=sl(col), legs=tr(col), boots=tall("#3b2a20"))
    d.update(kw)
    return R(id, name, **d)


def ethiopian(id, name, male=True, robe="#f4f1ea", cape_col="#a8312f", **kw):
    """Эфиопская знать: белая шамма, плащ."""
    d = dict(male=male, skin="african2", hair=("curly", "#1e1a18") if male else ("long", "#1e1a18"),
             outfit={"type": "robe", "col": robe, "rope": "#d4a63c"} if male else
             {"type": "gown", "dress": robe, "trim": "#d4a63c", "mantle": cape_col, "shoes": "#3b2a20"},
             cape={"type": "cape", "col": cape_col}, sleeves=sl(robe))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- brigantaggio
    R("crocco_it", "Кармине Крокко", skin="tan", hair=("long", "#1e1a18"), beard=("full", "#1e1a18"), bushy=True,
      hat={"type": "wide", "col": "#2a2a2e", "feather": ""}, outfit={"type": "coat", "col": "#5a4434", "trim": "#a8312f", "belt": "#3b2a20"},
      sleeves=sl("#5a4434"), legs=tr("#3b2a20"), boots=tall("#3b2a20"), held=h("spear")),
    it_general("borjes_it", "Генерал Хосе Борхес", coat="#3b3a38", skin="olive", hair=("short", "#2a1a12"), beard=("goatee", "#2a1a12"),
               hat={"type": "beret", "col": "#a8312f", "feather": ""}, held=h("scroll")),
    it_general("cialdini_it", "Генерал Энрико Чальдини", beard=("walrus", "#8a7a6a")),
    victorian("ricasoli_it", "Премьер Беттино Рикасоли", hair=("receding", "#d8d4dc"), beard=("walrus", "#d8d4dc"), age="old"),
    # ---------- 1866, 1871
    it_general("lamarmora_it", "Генерал Альфонсо Ла Мармора", hair=("receding", "#8a7a6a"), beard=("handlebar", "#8a7a6a"), held=h("scroll")),
    victorian("lanza_it", "Премьер Джованни Ланца", hair=("receding", "#b8b4c0"), beard=("full", "#b8b4c0"), age="old"),
    victorian("sella_it", "Министр Квинтино Селла", hair=("short", "#3b2a20"), beard=("full", "#3b2a20"), held=h("book")),
    # ---------- Догали
    victorian("depretis_it", "Премьер Агостино Депретис", hair=("receding", "#e6e0d6"), beard=("long", "#e6e0d6"), age="old"),
    it_general("de_cristoforis_it", "Полковник Томмазо Де Кристофорис", coat="#f4f1ea", hat={"type": "cap", "col": "#f4f1ea", "fur": ""},
               hair=("short", "#3b2a20"), beard=("handlebar", "#3b2a20")),
    ethiopian("ras_alula_it", "Рас Алула Энгида", cape_col="#2f6a4a", held=h("spear"), beard=("goatee", "#1e1a18")),
    ethiopian("yohannes_it", "Император Йоханныс IV", cape_col="#a8312f", hat={"type": "crown", "gold": "#d8ad3c"},
              beard=("full", "#1e1a18"), held=h("cross")),
    # ---------- Fasci Siciliani
    edwardian("barbato_it", "Врач Никола Барбато", coat="#2a2a2e", hair=("curly", "#1e1a18"), beard=("full", "#1e1a18"), skin="olive"),
    worker("verro_it", "Бернардино Верро", skin="olive", shirt="#f4f1ea", pants="#5a4434", hair=("short", "#1e1a18"),
           beard=("handlebar", "#1e1a18"), hat={"type": "cap", "col": "#2a2a2e", "fur": ""}),
    edwardian("giolitti_it", "Джованни Джолитти", coat="#1e1e22", hair=("short", "#b8b4c0"), beard=("walrus", "#b8b4c0")),
    victorian("crispi_it", "Франческо Криспи", hair=("receding", "#e6e0d6"), beard=("walrus", "#e6e0d6"), age="old", bushy=True),
    # ---------- Адуа
    it_general("baratieri_it", "Генерал Оресте Баратьери", coat="#f4f1ea", hat={"type": "cap", "col": "#f4f1ea", "fur": ""},
               hair=("receding", "#8a7a6a"), beard=("goatee", "#8a7a6a")),
    ethiopian("menelik_it", "Император Менелик II", cape_col="#2f4a7a", hat={"type": "wide", "col": "#1e1e22", "feather": ""},
              beard=("full", "#1e1a18"), held=h("sword")),
    ethiopian("taytu_it", "Императрица Таиту Бетул", male=False, robe="#f4f1ea", cape_col="#5a2a6b",
              hat={"type": "circlet", "gold": "#d8ad3c"}),
    # ---------- Милан 1898
    victorian("rudini_it", "Премьер Антонио ди Рудини", hair=("receding", "#3b2a20"), beard=("walrus", "#3b2a20")),
    it_general("bava_it", "Генерал Фьоренцо Бава Беккарис", hair=("receding", "#e6e0d6"), beard=("walrus", "#e6e0d6"), age="old"),
    edwardian("turati_it", "Филиппо Турати", coat="#3b3a38", hair=("curly", "#5a3a22"), beard=("full", "#5a3a22"),
              glasses={"type": "pince", "col": "#3a2a20"}, held=h("book")),
    it_general("umberto_it", "Король Умберто I", hair=("short", "#b8b4c0"), beard=("handlebar", "#b8b4c0"),
               hat={"type": "crown", "gold": "#d8ad3c"}, held=None),
    # ---------- эмиграция
    edwardian("agnelli_it", "Джованни Аньелли", coat="#2a2a2e", hair=("short", "#3b2a20"), beard=("handlebar", "#3b2a20")),
    edwardian("bodio_it", "Статистик Луиджи Бодио", coat="#1e1e22", hair=("receding", "#b8b4c0"), beard=("full", "#b8b4c0"),
              glasses={"type": "round", "col": "#3a2a20"}, held=h("book"), age="old"),
    R("cabrini_it", "Франческа Кабрини", male=False, hair=("long", "#3b2a20"), hat={"type": "veil", "col": "#1e1e22", "band": ""},
      outfit={"type": "gown", "dress": "#1e1e22", "trim": "#f4f1ea", "mantle": "#1e1e22", "shoes": "#1e1e22"},
      sleeves=sl("#1e1e22", "#f4f1ea"), held=h("cross")),
    worker("emigrant_family_it", "Семья из Базиликаты", skin="tan", shirt="#e9e0cc", pants="#5a4434", hair=("short", "#1e1a18"),
           beard=("handlebar", "#1e1a18"), hat={"type": "wide", "col": "#5a4434", "feather": ""}, held=h("flask")),
    # ---------- Ливия
    edwardian("san_giuliano_it", "Министр Антонино ди Сан-Джулиано", coat="#1e1e22", hair=("receding", "#8a7a6a"),
              beard=("goatee", "#8a7a6a"), glasses={"type": "pince", "col": "#3a2a20"}),
    ww1("enver_it", "Энвер-бей", col="#6e7468", skin="olive", hair=("short", "#1e1a18"), beard=("handlebar", "#1e1a18"),
        hat={"type": "cap", "col": "#a8312f", "fur": "#3b2a20"}),
    R("omar_mukhtar_it", "Омар аль-Мухтар", skin="olive", hair=("short", "#d8d4dc"), beard=("full", "#e6e0d6"), age="old",
      hat={"type": "turban", "col": "#f4f1ea", "jewel": "#f4f1ea"}, outfit={"type": "robe", "col": "#e9d8a8", "rope": "#7a5232"},
      cape={"type": "cape", "col": "#f4f1ea"}, sleeves=sl("#e9d8a8"), glasses={"type": "round", "col": "#3a2a20"}),
    # ---------- 1915
    edwardian("salandra_it", "Премьер Антонио Саландра", coat="#1e1e22", hair=("receding", "#b8b4c0"), beard=("walrus", "#b8b4c0")),
    edwardian("sonnino_it", "Министр Сидней Соннино", coat="#2a2a2e", hair=("receding", "#e6e0d6"), beard=("walrus", "#e6e0d6"),
              held=h("scroll")),
    ww1("ve3_it", "Король Виктор Эммануил III", hair=("short", "#8a7a6a"), beard=("handlebar", "#8a7a6a")),
    # ---------- Капоретто, Витторио-Венето
    ww1("cadorna_luigi_it", "Генерал Луиджи Кадорна", hair=("receding", "#e6e0d6"), beard=("walrus", "#e6e0d6"), age="old"),
    ww1("otto_below_it", "Генерал Отто фон Белов", col=FELDGRAU, hat={"type": "pickelhaube", "col": "#1e1e22", "metal": "#c9a24a"},
        beard=("walrus", "#b8b4c0")),
    ww1("boroevic_it", "Фельдмаршал Светозар Бороевич", col=AUSTRIAN, beard=("walrus", "#e6e0d6"), age="old"),
    ww1("diaz_it", "Генерал Армандо Диас", hair=("short", "#3b2a20"), beard=("handlebar", "#3b2a20")),
    ww1("fanti_it", "Пехотинцы 2-й армии", hat={"type": "helmet", "col": GREY_GREEN, "trim": GREY_GREEN}, hair=("short", "#3b2a20"),
        beard=("handlebar", "#3b2a20"), held=h("spear")),
    ww1("badoglio_it", "Генерал Пьетро Бадольо", hair=("receding", "#3b2a20"), held=h("scroll")),
    ww1("karl1_it", "Император Карл I", col=AUSTRIAN, hair=("short", "#8a5a34"), beard=("handlebar", "#8a5a34"),
        hat={"type": "crown", "gold": "#d8ad3c"}),
    ww1("weber_it", "Генерал Виктор Вебер фон Вебенау", col=AUSTRIAN, hair=("receding", "#b8b4c0"), beard=("goatee", "#b8b4c0"),
        held=h("book")),
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
