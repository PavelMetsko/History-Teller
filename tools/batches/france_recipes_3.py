#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 3 главы «Франция» (1643–1851).

    python3 tools/batches/france_recipes_3.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/france_recipes_3.py --ids      только список id (для factory/build.py)
    python3 tools/batches/france_recipes_3.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, colonial, puritan, regency, victorian, worker, ROOT, OUT  # noqa: F401


def grand_siecle(id, name, coat="#5a2a6b", hair=("shoulder", "#3b2a20"), **kw):
    """XVII век: дублет с брыжами, длинные локоны, широкополая шляпа с пером."""
    d = dict(hair=hair, collar={"type": "ruff", "col": "#f4f1ea"},
             outfit={"type": "doublet", "col": coat, "trim": "#d4a63c", "chain": False}, sleeves=sl(coat, "#f4f1ea"),
             legs=tr(coat), boots=tall("#5a3a22"))
    d.update(kw)
    return R(id, name, **d)


def lady(id, name, dress="#2f4a7a", hair=("long", "#3b2a20"), **kw):
    d = dict(male=False, hair=hair, outfit={"type": "gown", "dress": dress, "trim": "#f4f1ea", "mantle": dress, "shoes": "#1e1e22"},
             sleeves=sl(dress, "#f4f1ea"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Рокруа
    R("francisco_melo", "Франсиско де Мело", skin="olive", age="old", hair=("short", "#8a7a6a"), beard=("goatee", "#8a7a6a"),
      collar={"type": "ruff", "col": "#f4f1ea"}, outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": "#a8312f", "belt": "#5b3a22"},
      sleeves=sl("#a9b0b8"), legs=tr("#2a2a2e"), boots=tall("#3b2a20"), held=h("bulawa")),
    grand_siecle("lhopital_fr", "Маршал Л'Опиталь", coat="#3b4a5a", age="old", hair=("shoulder", "#d8d4dc"), beard=("goatee", "#d8d4dc"),
                 held=h("bulawa")),
    lady("anne_austria", "Анна Австрийская", dress="#1e1e22", hair=("curly", "#b9672e"), hat={"type": "veil", "col": "#1e1e22", "band": "#d8ad3c"}),
    # ---------- отмена Нантского эдикта
    grand_siecle("louvois", "Маркиз де Лувуа", coat="#2f4a7a", hair=("wig", "#3b2a20"), held=h("scroll")),
    puritan("claude_brousson", "Пастор Клод Бруссон", held=h("book")),
    R("huguenot_family", "Семья гугенотов из Пуату", male=False, hair=("long", "#8a5a34"), hat={"type": "veil", "col": "#f4f1ea", "band": ""},
      outfit={"type": "gown", "dress": "#3b3a38", "trim": "#f4f1ea", "mantle": "#5a4434", "shoes": "#3b2a20"}, sleeves=sl("#3b3a38")),
    # ---------- Энциклопедия
    colonial("dalembert", "Жан д'Аламбер", coat="#5a6b4a", vest="#f4f1ea", hat=None, held=h("book")),
    colonial("malesherbes", "Мальзерб", coat="#1e1e22", vest="#f4f1ea", hat=None, age="old", held=h("scroll")),
    colonial("le_breton", "Издатель Ле Бретон", coat="#7a5232", vest="#e9d8a8", hat=None, glasses={"type": "round", "col": "#3a2a20"}),
    # ---------- Парижский мир
    colonial("louis15", "Людовик XV", coat="#2f4a7a", vest="#f4f1ea", hat={"type": "crown", "gold": "#d8ad3c"},
             cape={"type": "cape", "col": "#2f4a7a"}),
    colonial("choiseul", "Герцог де Шуазёль", coat="#a8312f", vest="#e9d8a8", hat=None, held=h("scroll")),
    colonial("lord_bute", "Лорд Бьют", coat="#2f6a4a", vest="#f4f1ea", hat=None),
    # ---------- права человека
    colonial("sieyes", "Аббат Сийес", coat="#1e1e22", vest="#1e1e22", hat=None, wig=False, hair_col="#5a3a22", held=h("book")),
    colonial("mounier", "Жан-Жозеф Мунье", coat="#3b3a38", vest="#f4f1ea", hat=None, wig=False, hair_col="#3b2a20"),
    worker("market_women", "Рыночные торговки Парижа", male=False, shirt="#e9e0cc", pants="#a8312f", hair=("long", "#5a3a22"),
           hat={"type": "veil", "col": "#f4f1ea", "band": ""}, held=h("pickaxe")),
    # ---------- Гаити
    R("toussaint", "Туссен-Лувертюр", skin="african", age="old", hair=("short", "#8a8a8a"),
      hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#a8312f"},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#a8312f", "trim": "#d4a63c", "sash": "#d8ad3c", "epaulettes": True},
      sleeves=sl("#2f4a7a"), legs=tr("#f4f1ea"), boots=tall(), held=h("sword")),
    R("dessalines", "Жан-Жак Дессалин", skin="african", hair=("short", "#1e1a18"),
      hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#a8312f"},
      outfit={"type": "uniform", "col": "#1e1e22", "facing": "#a8312f", "trim": "#d4a63c", "sash": "#a8312f", "epaulettes": True},
      sleeves=sl("#1e1e22"), legs=tr("#f4f1ea"), boots=tall(), held=h("sword")),
    colonial("sonthonax", "Комиссар Сонтонакс", coat="#2f4a7a", vest="#f4f1ea", hat=None, wig=False, hair_col="#5a3a22",
             cape={"type": "cape", "col": "#a8312f"}, held=h("scroll")),
    R("leclerc_fr", "Генерал Леклерк", hair=("short", "#d8b070"), hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#2f4a7a"},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#a8312f", "trim": "#d4a63c", "sash": "", "epaulettes": True},
      sleeves=sl("#2f4a7a"), legs=tr("#f4f1ea"), boots=tall()),
    R("rochambeau_fils", "Генерал Рошамбо-сын", hair=("short", "#3b2a20"), beard=("handlebar", "#3b2a20"),
      hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#a8312f"},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#1e1e22", "trim": "#d4a63c", "sash": "#a8312f", "epaulettes": True},
      sleeves=sl("#2f4a7a"), legs=tr("#f4f1ea"), boots=tall(), held=h("sword")),
    # ---------- Гражданский кодекс
    regency("portalis", "Жан-Этьен Порталис", coat="#1e1e22", hair=("receding", "#8a7a6a"), age="old", held=h("book")),
    regency("tronchet", "Франсуа Тронше", coat="#3b3a38", hair=("receding", "#d8d4dc"), age="old", held=h("scroll")),
    regency("cambaceres", "Второй консул Камбасерес", coat="#a8312f", hair=("wig", "#ece8e2"), cape={"type": "cape", "col": "#a8312f"}),
    regency("benjamin_constant", "Трибун Бенжамен Констан", coat="#2f4a7a", hair=("long", "#b9672e"), glasses={"type": "round", "col": "#3a2a20"}),
    # ---------- 1830
    regency("charles10", "Карл X", coat="#2f4a7a", hair=("receding", "#d8d4dc"), age="old", cape={"type": "cape", "col": "#2f4a7a"},
            hat={"type": "crown", "gold": "#d8ad3c"}),
    regency("polignac", "Князь Полиньяк", coat="#1e1e22", hair=("short", "#3b2a20"), held=h("scroll")),
    victorian("louis_philippe", "Луи-Филипп Орлеанский", coat="#2f4a7a", hair=("short", "#8a7a6a"), beard=("goatee", "#8a7a6a"),
              hat={"type": "top", "col": "#1e1e22"}),
    worker("parisians_1830", "Повстанцы Парижа", shirt="#f4f1ea", pants="#2f4a7a", hair=("short", "#3b2a20"),
           hat={"type": "cap", "col": "#a8312f", "fur": ""}, held=h("flag", "hand_r")),
    # ---------- Алжир
    R("bourmont", "Генерал де Бурмон", age="old", hair=("short", "#d8d4dc"), hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#f4f1ea"},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#a8312f", "trim": "#d4a63c", "sash": "#f4f1ea", "epaulettes": True},
      sleeves=sl("#2f4a7a"), legs=tr("#a8312f"), boots=tall(), held=h("bulawa")),
    R("hussein_dey", "Хусейн-дей", skin="olive", age="old", hair=None, beard=("full", "#d8d4dc"),
      hat={"type": "turban", "col": "#f4f1ea", "jewel": "#a8312f"}, outfit={"type": "robe", "col": "#2f6a4a", "rope": "#d8ad3c"},
      cape={"type": "cape", "col": "#a8312f"}, sleeves=sl("#2f6a4a"), held=h("flag")),
    R("abd_al_qadir", "Эмир Абд аль-Кадир", skin="tan", hair=None, beard=("goatee", "#2a1a12"), hat={"type": "hood", "col": "#f4f1ea"},
      outfit={"type": "robe", "col": "#f4f1ea", "rope": "#7a5232"}, cape={"type": "cape", "col": "#e9e0cc"}, sleeves=sl("#f4f1ea"),
      held=h("sword")),
    R("bugeaud", "Маршал Бюжо", age="old", hair=("receding", "#d8d4dc"), hat={"type": "cap", "col": "#a8312f", "fur": ""},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#a8312f", "trim": "#d4a63c", "sash": "#a8312f", "epaulettes": True},
      sleeves=sl("#2f4a7a"), legs=tr("#a8312f"), boots=tall(), held=h("bulawa")),
    regency("pierre_deval", "Консул Деваль", coat="#2a2a2e", hair=("short", "#5a3a22"), hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#f4f1ea"}),
    # ---------- 1848
    victorian("guizot", "Франсуа Гизо", coat="#1e1e22", hair=("receding", "#8a7a6a"), age="old"),
    victorian("lamartine", "Альфонс де Ламартин", coat="#2a2a2e", hair=("short", "#8a7a6a"), held=h("flag")),
    victorian("ledru_rollin", "Ледрю-Роллен", coat="#3b3a38", tie="#a8312f", hair=("short", "#3b2a20"), beard=("full", "#3b2a20")),
    lady("duchess_orleans", "Герцогиня Орлеанская", dress="#1e1e22", hair=("long", "#d8b070"), hat={"type": "veil", "col": "#1e1e22", "band": ""}),
    victorian("schoelcher", "Виктор Шёльшер", coat="#1e1e22", hair=("receding", "#3b2a20"), beard=("walrus", "#3b2a20"), held=h("scroll")),
    victorian("francois_arago", "Министр Франсуа Араго", coat="#2f4a7a", hair=("curly", "#8a7a6a"), age="old", held=h("book")),
    worker("louisy_mathieu", "Луизи Матьё", skin="african2", shirt="#f4f1ea", pants="#3b3a38", hair=("short", "#1e1a18"),
           beard=("goatee", "#1e1a18"), held=h("scroll")),
    worker("martinique_rebels", "Восставшие Сен-Пьера", skin="african", shirt="#e9e0cc", pants="#7a5232", hair=("short", "#1e1a18"),
           held=h("spear")),
    victorian("cyrille_bissette", "Сириль Биссетт", skin="tan", coat="#5a4434", hair=("curly", "#2a1a12"), held=h("book")),
    # ---------- 1851
    victorian("louis_napoleon", "Президент Луи-Наполеон", coat="#1e1e22", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22"),
              cape={"type": "cape", "col": "#a8312f"}),
    victorian("morny", "Герцог де Морни", coat="#2a2a2e", hair=("receding", "#5a3a22"), beard=("handlebar", "#5a3a22"),
              hat={"type": "top", "col": "#1e1e22"}),
    victorian("victor_hugo", "Виктор Гюго", coat="#1e1e22", hair=("short", "#5a3a22"), held=h("book")),
    victorian("baudin", "Депутат Боден", coat="#3b3a38", hair=("short", "#3b2a20"), beard=("full", "#3b2a20"),
              cape={"type": "cape", "col": "#2f4a7a"}, held=h("flag")),
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
