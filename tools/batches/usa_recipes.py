#!/usr/bin/env python3
"""Рецепты фабрики для персонажей главы «США»: типажи эпох + точечные настройки.

    python3 tools/batches/usa_recipes.py            записать все рецепты (перезаписывает свои id)
    python3 tools/batches/usa_recipes.py --ids      только список id (для factory/build.py)
"""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "factory", "recipes")

SKIN = {"light": "#f3c4a6", "fair": "#f7d4bc", "tan": "#e8b290", "native": "#c68a5e", "native2": "#b97c52",
        "african": "#7a4a30", "african2": "#8f5a3a", "olive": "#dcae88"}
INK = "#2a1a12"


def R(id, name, skin="light", male=True, age="young", hair=("short", "#5a3a22"), beard=None, hat=None, outfit=None,
      sleeves=None, legs=None, boots=None, held=None, cape=None, glasses=None, collar=None, bushy=False, brow=None,
      iris="#6b3a1f", face=True):
    s = {"body": {"type": "male" if male else "female"}, "age": {"type": age},
         "face": {"type": "std", "brow": brow or (hair[1] if hair else INK), "iris": iris, "bushy": bushy} if face else {"type": "none"},
         "hair": {"type": hair[0], "col": hair[1]} if hair else {"type": "none"},
         "beard": {"type": beard[0], "col": beard[1]} if beard else {"type": "none"},
         "hat": hat or {"type": "none"}, "cape": cape or {"type": "none"}, "held": held or {"type": "none"},
         "collar": collar or {"type": "none"}, "glasses": glasses or {"type": "none"},
         "outfit": outfit, "sleeves": sleeves or {"type": "std", "col": "#5a4434", "cuff": "#5a4434"},
         "legs": legs or {"type": "none"}, "boots": boots or {"type": "none"}}
    return {"id": id, "name": name, "skin": SKIN.get(skin, skin), "slots": s}


def sl(c, cuff=None): return {"type": "std", "col": c, "cuff": cuff or c}
def tr(c): return {"type": "trousers", "col": c}
def bo(c, t=None): return {"type": "boots", "col": c, "top": t or c}
def tall(c="#1e1e22"): return {"type": "tall", "col": c}
def h(kind, hand="hand_r"): return {"type": kind, "hand": hand}
BARE = {"type": "bare"}


# ---------------- типажи ----------------
def colonial(id, name, coat="#4b6a9a", vest="#e9d8a8", hat="tricorne", wig=True, hair_col="#ece8e2", **kw):
    """Джентльмен XVIII века: кафтан-фрак, парик, треуголка."""
    d = dict(hair=("wig", hair_col) if wig else ("shoulder", hair_col),
             hat={"type": "tricorne", "col": "#1e1e22", "trim": "#d4a63c"} if hat == "tricorne" else (hat or {"type": "none"}),
             outfit={"type": "frock", "col": coat, "vest": vest, "trim": "#d4a63c"}, sleeves=sl(coat, "#f4f1ea"),
             legs=tr(vest), boots=bo("#1e1e22"))
    d.update(kw)
    return R(id, name, **d)


def puritan(id, name, male=True, coat="#2a2a2e", **kw):
    """Пуританин XVII века: тёмная одежда, белый воротник, широкополая шляпа."""
    d = dict(male=male, hair=("shoulder", "#5a3a22") if male else ("long", "#6b4426"),
             hat={"type": "wide", "col": "#1e1e22", "feather": ""} if male else {"type": "veil", "col": "#f4f1ea", "band": ""},
             collar={"type": "ruff", "col": "#f4f1ea"} if male else None,
             outfit={"type": "doublet", "col": coat, "trim": "#f4f1ea", "chain": False} if male else
             {"type": "gown", "dress": coat, "trim": "#f4f1ea", "mantle": coat, "shoes": "#1e1e22"},
             sleeves=sl(coat, "#f4f1ea"), legs=tr(coat) if male else None, boots=bo("#1e1e22") if male else None)
    d.update(kw)
    return R(id, name, **d)


def native(id, name, male=True, skin="native", deer="#a8794e", fur="#e9d8a8", hair_col="#1e1a18", **kw):
    """Восточные лесные народы: оленья кожа, бахрома меха, длинные волосы."""
    d = dict(male=male, skin=skin, hair=("long", hair_col),
             outfit={"type": "fur_tunic", "col": deer, "fur": fur, "rope": "#7a5232"} if male else
             {"type": "gown", "dress": deer, "trim": fur, "mantle": "#7a5232", "shoes": "#7a5232"},
             sleeves=BARE if male else sl(deer), legs=tr(deer) if male else None, boots=bo("#7a5232") if male else None)
    d.update(kw)
    return R(id, name, **d)


def spaniard(id, name, armor=False, col="#a8312f", **kw):
    """Испанец XV–XVI века: дублет с брыжами или кольчуга."""
    d = dict(hair=("short", "#2a1a12"), beard=("goatee", "#2a1a12"), skin="olive",
             outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": col, "belt": "#5b3a22"} if armor else
             {"type": "doublet", "col": col, "trim": "#d4a63c", "chain": True},
             collar=None if armor else {"type": "ruff", "col": "#f4f1ea"},
             sleeves=sl("#a9b0b8" if armor else col), legs=tr("#2a2a2e"), boots=bo("#3b2a20"))
    d.update(kw)
    return R(id, name, **d)


def worker(id, name, skin="light", shirt="#e9e0cc", pants="#4b6a9a", **kw):
    """Рабочий XIX века: рубаха с закатанными рукавами, штаны на подтяжках."""
    d = dict(skin=skin, outfit={"type": "tunic", "col": shirt, "trim": pants, "belt": "#3b2a20"}, sleeves=BARE,
             legs=tr(pants), boots=bo("#3b2a20"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- легенды
    R("betsy_ross", "Бетси Росс", male=False, hair=("long", "#6b4426"), hat={"type": "veil", "col": "#f4f1ea", "band": ""},
      outfit={"type": "gown", "dress": "#4b6a9a", "trim": "#f4f1ea", "mantle": "#a8312f", "shoes": "#1e1e22"},
      sleeves=sl("#4b6a9a", "#f4f1ea"), held=h("flag")),
    colonial("robert_morris", "Роберт Моррис", coat="#2a2a2e", vest="#e9d8a8", hat=None, age="old"),
    R("rip_van_winkle", "Рип ван Винкль", age="old", hair=("long", "#d8d4dc"), beard=("long", "#e6e0d6"),
      hat={"type": "tricorne", "col": "#5a4434", "trim": "#7a5232"}, outfit={"type": "coat", "col": "#7a6a52", "trim": "#5a4434", "belt": "#3b2a20"},
      sleeves=sl("#7a6a52"), legs=tr("#5a4434"), boots=bo("#3b2a20"), held=h("spear")),
    R("dame_van_winkle", "Дама ван Винкль", male=False, age="old", hair=("long", "#8a7a6a"), hat={"type": "veil", "col": "#f4f1ea", "band": ""},
      outfit={"type": "gown", "dress": "#5a6b4a", "trim": "#f4f1ea", "mantle": "#7a6a52", "shoes": "#3b2a20"}, sleeves=sl("#5a6b4a", "#f4f1ea"),
      held=h("staff")),
    R("hudson_ghost", "Призрак Хендрика Гудзона", skin="#c9d6dc", age="old", hair=("shoulder", "#e6e0d6"), beard=("full", "#e6e0d6"),
      hat={"type": "wide", "col": "#3b4a5a", "feather": "#e6e0d6"}, collar={"type": "ruff", "col": "#e6e0d6"},
      outfit={"type": "doublet", "col": "#3b4a5a", "trim": "#c9d6dc", "chain": False}, sleeves=sl("#3b4a5a"), legs=tr("#3b4a5a"),
      boots=bo("#2a2a2e"), iris="#7fa0b8"),
    R("vedder", "Трактирщик Веддер", age="old", hair=("receding", "#b8b4c0"), outfit={"type": "tunic", "col": "#f4f1ea", "trim": "#7a5232", "belt": "#7a5232"},
      sleeves=sl("#f4f1ea"), legs=tr("#5a4434"), boots=bo("#3b2a20")),
    R("ichabod_crane", "Икабод Крейн", hair=("bowl", "#8a5a34"), hat={"type": "tricorne", "col": "#2a2a2e", "trim": "#5a4434"},
      outfit={"type": "frock", "col": "#2a2a2e", "vest": "#7a6a52", "trim": "#5a4434"}, sleeves=sl("#2a2a2e"), legs=tr("#7a6a52"),
      boots=bo("#1e1e22"), held=h("book")),
    R("katrina", "Катрина ван Тассел", male=False, hair=("long", "#d8b070"), outfit={"type": "gown", "dress": "#a8312f", "trim": "#f4f1ea",
      "mantle": "#e9d8a8", "shoes": "#1e1e22"}, sleeves=sl("#a8312f", "#f4f1ea"), iris="#5f7a9a"),
    R("brom_bones", "Бром Бонс", hair=("curly", "#2a1a12"), beard=("handlebar", "#2a1a12"), bushy=True,
      outfit={"type": "coat", "col": "#5a6b4a", "trim": "#7a5232", "belt": "#3b2a20"}, sleeves=sl("#5a6b4a"), legs=tr("#5a4434"), boots=bo("#3b2a20")),
    R("headless_horseman", "Всадник без головы", face=False, hair=None,
      outfit={"type": "uniform", "col": "#1e1e22", "facing": "#5a2a2a", "trim": "#8a6a2a", "sash": "", "epaulettes": False},
      cape={"type": "cape", "col": "#1e1e22"}, sleeves=sl("#1e1e22"), legs=tr("#1e1e22"), boots=tall(), held=h("sword")),
    R("chapman", "Джонни Эплсид", hair=("long", "#8a5a34"), beard=("goatee", "#8a5a34"), hat={"type": "hood", "col": "#7a6a52"},
      outfit={"type": "robe", "col": "#a88a5a", "rope": "#7a5232"}, sleeves=sl("#a88a5a"), held=h("staff")),
    worker("cider_miller", "Мельник-сидродел", shirt="#f4f1ea", pants="#7a5232", hair=("short", "#5a3a22"), beard=("full", "#5a3a22")),
    R("settler_us", "Переселенец", hair=("short", "#8a5a34"), beard=("goatee", "#8a5a34"), hat={"type": "wide", "col": "#7a5232", "feather": ""},
      outfit={"type": "fur_tunic", "col": "#7a6a52", "fur": "#c9b08a", "rope": "#5a3a22"}, sleeves=sl("#7a6a52"), legs=tr("#5a4434"),
      boots=bo("#3b2a20"), held=h("spear")),
    worker("john_henry", "Джон Генри", skin="african", shirt="#e9e0cc", pants="#3b4a6a", hair=("short", "#1e1a18"), held=h("pickaxe")),
    R("polly_ann", "Полли Энн", male=False, skin="african", hair=("curly", "#1e1a18"), outfit={"type": "gown", "dress": "#a8312f",
      "trim": "#f4f1ea", "mantle": "#5a4434", "shoes": "#3b2a20"}, sleeves=sl("#a8312f")),
    R("rail_captain", "Капитан бригады", hair=("short", "#5a3a22"), beard=("walrus", "#5a3a22"), hat={"type": "top", "col": "#3b2a20"},
      outfit={"type": "suit", "col": "#5a4434", "shirt": "#f4f1ea", "tie": "#a8312f", "long": True}, sleeves=sl("#5a4434"),
      legs=tr("#3b2a20"), boots=bo("#1e1e22")),
    R("drill_salesman", "Продавец паровой дрели", hair=("short", "#2a1a12"), beard=("handlebar", "#2a1a12"), hat={"type": "top", "col": "#1e1e22"},
      outfit={"type": "suit", "col": "#2a2a2e", "shirt": "#f4f1ea", "tie": "#2f6a4a", "long": True}, sleeves=sl("#2a2a2e"),
      legs=tr("#2a2a2e"), boots=bo("#1e1e22"), glasses={"type": "pince", "col": "#3a2a20"}),
    worker("paul_bunyan", "Пол Баньян", shirt="#a8312f", pants="#3b4a6a", hair=("short", "#1e1a18"), beard=("full", "#1e1a18"),
           bushy=True, hat={"type": "cap", "col": "#a8312f", "fur": ""}, held=h("spear")),
    R("inkslinger", "Джонни Инкслингер", hair=("receding", "#5a3a22"), glasses={"type": "round", "col": "#3a2a20"},
      outfit={"type": "tunic", "col": "#f4f1ea", "trim": "#2a2a2e", "belt": "#2a2a2e"}, sleeves=sl("#f4f1ea"), legs=tr("#2a2a2e"),
      boots=bo("#1e1e22"), held=h("book")),
    worker("sourdough_sam", "Повар Саурдо Сэм", shirt="#f4f1ea", pants="#7a6a52", hair=("receding", "#8a7a6a"), beard=("walrus", "#8a7a6a"),
           age="old"),
    # ---------- Кахокия, хауденосауни
    native("cahokia_elder", "Старейшина Кахокии", age="old", hair_col="#8a8a8a", cape={"type": "cape", "col": "#a8312f"}, held=h("staff")),
    native("sun_priestess", "Жрица Солнца", male=False, deer="#d8ad3c", fur="#f4f1ea"),
    native("shell_master", "Мастер раковин", deer="#8a6a4a", fur="#f4f1ea", hair=("short_sides", "#1e1a18")),
    native("aztalan_envoy", "Посланник из Азталана", skin="native2", deer="#7a6a52", held=h("spear")),
    native("deganawida", "Деганавида, Миротворец", deer="#e9d8a8", fur="#f4f1ea", held=h("staff")),
    native("hiawatha", "Хайавата", deer="#a8794e", fur="#2f6a4a", hair=("short_sides", "#1e1a18")),
    native("jigonsaseh", "Джигонсаси, мать кланов", male=False, age="old", deer="#5a6b4a", fur="#e9d8a8", hair_col="#8a8a8a"),
    native("tadodaho", "Тадодахо", skin="native2", deer="#3b2a20", fur="#5a6b4a", bushy=True, cape={"type": "cape", "col": "#2f6a4a"}),
    # ---------- Колумб, Флорида
    spaniard("columbus", "Христофор Колумб", col="#2f4a7a", hair=("shoulder", "#d8d4dc"), beard=None, age="old",
             cape={"type": "cape", "col": "#a8312f"}, skin="fair"),
    native("guacanagari", "Касик Гуаканагари", skin="native", deer="#d8ad3c", fur="#a8312f", hair=("bowl", "#1e1a18"),
           hat={"type": "circlet", "gold": "#d8ad3c"}),
    spaniard("rodrigo_triana", "Матрос Родриго де Триана", col="#7a6a52", collar=None, beard=("full", "#2a1a12"),
             hat={"type": "cap", "col": "#a8312f", "fur": ""}),
    spaniard("luis_torres", "Переводчик Луис де Торрес", col="#5a2a6b", held=h("scroll")),
    spaniard("menendez_aviles", "Педро Менендес де Авилес", armor=True, col="#a8312f", hat={"type": "helmet", "col": "#b9bfc6", "trim": "#d4a63c"},
             held=h("sword")),
    R("ribault", "Жан Рибо", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"), collar={"type": "ruff", "col": "#f4f1ea"},
      hat={"type": "beret", "col": "#2f4a7a", "feather": "#f4f1ea"}, outfit={"type": "doublet", "col": "#2f4a7a", "trim": "#d4a63c", "chain": False},
      sleeves=sl("#2f4a7a"), legs=tr("#2a2a2e"), boots=bo("#3b2a20")),
    native("saturiwa", "Вождь Сатурива", deer="#a8312f", fur="#d8ad3c", cape={"type": "cape", "col": "#7a5232"}, held=h("spear")),
    R("lopez_mendoza", "Капеллан Лопес де Мендоса", skin="olive", age="old", hair=("receding", "#8a7a6a"),
      outfit={"type": "robe", "col": "#3b2a20", "rope": "#d8c7a0"}, sleeves=sl("#3b2a20"), held=h("cross")),
    # ---------- Роанок, Джеймстаун, Вирджиния
    R("john_white", "Губернатор Джон Уайт", age="old", hair=("short", "#b8b4c0"), beard=("full", "#d8d4dc"), collar={"type": "ruff", "col": "#f4f1ea"},
      hat={"type": "beret", "col": "#2a2a2e", "feather": ""}, outfit={"type": "doublet", "col": "#5a4434", "trim": "#d4a63c", "chain": False},
      sleeves=sl("#5a4434"), legs=tr("#2a2a2e"), boots=bo("#3b2a20"), held=h("scroll")),
    R("eleanor_dare", "Элинор Дэр", male=False, hair=("long", "#8a5a34"), hat={"type": "veil", "col": "#f4f1ea", "band": ""},
      outfit={"type": "gown", "dress": "#7a6a52", "trim": "#f4f1ea", "mantle": "#5a4434", "shoes": "#3b2a20"}, sleeves=sl("#7a6a52")),
    native("manteo", "Мантео", deer="#a8794e", fur="#f4f1ea", hair=("short_sides", "#1e1a18"), collar={"type": "ruff", "col": "#f4f1ea"}),
    R("john_smith", "Капитан Джон Смит", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"), bushy=True,
      outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": "#5a6b4a", "belt": "#5b3a22"}, sleeves=sl("#a9b0b8"), legs=tr("#3b2a20"),
      boots=bo("#3b2a20"), held=h("sword")),
    native("powhatan", "Вахунсенакау (Похатан)", age="old", hair_col="#8a8a8a", deer="#7a5232", fur="#e9d8a8",
           cape={"type": "cape", "col": "#a8794e"}, held=h("staff")),
    native("matoaka", "Матоака (Покахонтас)", male=False, deer="#a8794e", fur="#f4f1ea"),
    R("john_rolfe", "Джон Рольф", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22"), collar={"type": "ruff", "col": "#f4f1ea"},
      hat={"type": "wide", "col": "#3b2a20", "feather": ""}, outfit={"type": "doublet", "col": "#2f6a4a", "trim": "#d4a63c", "chain": False},
      sleeves=sl("#2f6a4a"), legs=tr("#3b2a20"), boots=bo("#3b2a20")),
    R("yeardley", "Губернатор Джордж Йердли", hair=("short", "#3b2a20"), beard=("goatee", "#3b2a20"), collar={"type": "ruff", "col": "#f4f1ea"},
      outfit={"type": "doublet", "col": "#a8312f", "trim": "#d4a63c", "chain": True}, sleeves=sl("#a8312f"), legs=tr("#2a2a2e"), boots=bo("#1e1e22")),
    R("john_pory", "Спикер Джон Пори", hair=("receding", "#5a3a22"), beard=("goatee", "#5a3a22"), collar={"type": "ruff", "col": "#f4f1ea"},
      outfit={"type": "doublet", "col": "#2a2a2e", "trim": "#f4f1ea", "chain": False}, sleeves=sl("#2a2a2e"), legs=tr("#2a2a2e"),
      boots=bo("#1e1e22"), held=h("scroll")),
    R("burgess_us", "Бёрджесс", hair=("shoulder", "#8a5a34"), hat={"type": "wide", "col": "#5a4434", "feather": ""},
      outfit={"type": "doublet", "col": "#7a6a52", "trim": "#f4f1ea", "chain": False}, sleeves=sl("#7a6a52"), legs=tr("#5a4434"), boots=bo("#3b2a20")),
    # ---------- пилигримы
    puritan("bradford", "Уильям Брэдфорд", held=h("book")),
    puritan("carver", "Джон Карвер", age="old", hair=("shoulder", "#b8b4c0"), beard=("goatee", "#d8d4dc")),
    puritan("hopkins_s", "Стивен Хопкинс", coat="#5a4434", beard=("full", "#5a3a22"), bushy=True),
    R("standish", "Майлз Стэндиш", hair=("short", "#a8562a"), beard=("full", "#a8562a"), bushy=True,
      hat={"type": "helmet", "col": "#b9bfc6", "trim": "#8a6a2a"}, outfit={"type": "chainmail", "steel": "#a9b0b8", "surcoat": "#a8312f", "belt": "#5b3a22"},
      sleeves=sl("#a9b0b8"), legs=tr("#3b2a20"), boots=bo("#3b2a20"), held=h("sword")),
    native("squanto", "Тисквантум (Скуанто)", deer="#a8794e", fur="#e9d8a8", hair=("short_sides", "#1e1a18")),
    native("massasoit", "Осамекин (Массасоит)", age="old", hair_col="#5a5a5a", deer="#7a5232", fur="#a8312f",
           cape={"type": "cape", "col": "#a8794e"}, held=h("staff")),
    puritan("winslow_e", "Эдвард Уинслоу", coat="#3b4a5a", held=h("scroll")),
]

RECIPES += [
    # ---------- пачка 2: Род-Айленд … Семилетняя война
    puritan("roger_williams", "Роджер Уильямс", coat="#3b2a20", held=h("book")),
    puritan("winthrop", "Губернатор Джон Уинтроп", age="old", beard=("full", "#8a7a6a"), hair=("receding", "#8a7a6a")),
    puritan("hutchinson", "Энн Хатчинсон", male=False, coat="#3b4a5a", held=h("book")),
    native("canonicus", "Сахем Каноникус", age="old", hair_col="#8a8a8a", deer="#5a4434", fur="#e9d8a8", cape={"type": "cape", "col": "#a8794e"}),
    native("metacom", "Метаком (король Филип)", deer="#7a5232", fur="#a8312f", hair=("short_sides", "#1e1a18"), cape={"type": "cape", "col": "#a8312f"},
           held=h("spear")),
    native("weetamoo", "Витаму, сахем поккассет", male=False, deer="#5a6b4a", fur="#d8ad3c", hat={"type": "circlet", "gold": "#e9d8a8"}),
    puritan("josiah_winslow", "Губернатор Джосайя Уинслоу", coat="#3b2a20", hair=("wig", "#5a3a22")),
    R("benjamin_church", "Капитан Бенджамин Чёрч", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22"),
      hat={"type": "wide", "col": "#5a4434", "feather": ""}, outfit={"type": "fur_tunic", "col": "#5a6b4a", "fur": "#c9b08a", "rope": "#3b2a20"},
      sleeves=sl("#5a6b4a"), legs=tr("#5a4434"), boots=bo("#3b2a20"), held=h("spear")),
    R("bacon_n", "Натаниел Бэкон", hair=("long", "#3b2a20"), beard=("handlebar", "#3b2a20"),
      hat={"type": "wide", "col": "#1e1e22", "feather": "#a8312f"}, outfit={"type": "doublet", "col": "#a8312f", "trim": "#d4a63c", "chain": False},
      sleeves=sl("#a8312f"), legs=tr("#2a2a2e"), boots=tall("#3b2a20"), held=h("sword")),
    R("berkeley_w", "Губернатор Уильям Беркли", age="old", hair=("wig", "#8a7a6a"), collar={"type": "ruff", "col": "#f4f1ea"},
      outfit={"type": "doublet", "col": "#2f4a7a", "trim": "#d4a63c", "chain": True}, sleeves=sl("#2f4a7a"), legs=tr("#2a2a2e"), boots=bo("#1e1e22")),
    native("cockacoeske", "Кокакоэске, царица памунки", male=False, deer="#a8794e", fur="#2f9a8a", hat={"type": "circlet", "gold": "#d8ad3c"},
           cape={"type": "cape", "col": "#7a5232"}),
    native("pope_pueblo", "Попе", age="old", hair_col="#5a5a5a", deer="#e9d8a8", fur="#a8312f", hair=("bowl", "#3b3a38"), held=h("staff")),
    native("catiti", "Алонсо Катити", deer="#d8ad3c", fur="#2f6a4a", hair=("bowl", "#1e1a18")),
    spaniard("otermin", "Губернатор Антонио де Отермин", armor=True, col="#d8ad3c", hat={"type": "helmet", "col": "#b9bfc6", "trim": "#d4a63c"},
             held=h("sword")),
    R("tituba", "Титуба", male=False, skin="native2", hair=("long", "#1e1a18"), hat={"type": "veil", "col": "#e9e0cc", "band": ""},
      outfit={"type": "gown", "dress": "#7a6a52", "trim": "#e9e0cc", "mantle": "#5a4434", "shoes": "#3b2a20"}, sleeves=sl("#7a6a52")),
    puritan("abigail_williams", "Абигейл Уильямс", male=False, coat="#5a6b4a", hair=("long", "#b97a45")),
    puritan("samuel_parris", "Пастор Сэмюэл Пэррис", held=h("book"), hat={"type": "none"}, hair=("shoulder", "#3b2a20")),
    puritan("rebecca_nurse", "Ребекка Нёрс", male=False, age="old", coat="#3b2a20", hair=("long", "#d8d4dc")),
    colonial("zenger", "Печатник Джон Питер Зенгер", coat="#7a6a52", hat=None, wig=False, hair_col="#5a3a22", hair=("short", "#5a3a22"), held=h("book")),
    colonial("andrew_hamilton", "Адвокат Эндрю Хэмилтон", coat="#1e1e22", hat=None, age="old", held=h("scroll")),
    colonial("cosby", "Губернатор Уильям Косби", coat="#a8312f", vest="#d8ad3c"),
    colonial("lewis_morris", "Судья Льюис Моррис", coat="#2a2a2e", hat=None, age="old"),
    worker("jemmy", "Джемми (Катон)", skin="african", shirt="#e9e0cc", pants="#7a6a52", hair=("short", "#1e1a18"), held=h("flag")),
    colonial("william_bull", "Вице-губернатор Уильям Булл", coat="#2f4a7a", held=h("sword"), boots=tall()),
    spaniard("montiano", "Губернатор Флориды Мануэль де Монтиано", col="#d8ad3c", hair=("wig", "#ece8e2"), beard=None,
             outfit={"type": "frock", "col": "#d8ad3c", "vest": "#a8312f", "trim": "#f4f1ea"}, collar=None),
    R("francisco_menendez", "Франсиско Менендес", skin="african2", hair=("short", "#1e1a18"), beard=("goatee", "#1e1a18"),
      hat={"type": "tricorne", "col": "#1e1e22", "trim": "#d4a63c"},
      outfit={"type": "uniform", "col": "#f4f1ea", "facing": "#a8312f", "trim": "#d4a63c", "sash": "#a8312f", "epaulettes": False},
      sleeves=sl("#f4f1ea", "#a8312f"), legs=tr("#f4f1ea"), boots=tall(), held=h("sword")),
    colonial("edwards_j", "Джонатан Эдвардс", coat="#1e1e22", vest="#1e1e22", hat=None, held=h("book"), collar={"type": "ruff", "col": "#f4f1ea"}),
    R("whitefield", "Джордж Уайтфилд", hair=("wig", "#ece8e2"), outfit={"type": "robe", "col": "#1e1e22", "rope": "#1e1e22"},
      sleeves=sl("#1e1e22", "#f4f1ea"), collar={"type": "ruff", "col": "#f4f1ea"}, held=h("book")),
    colonial("franklin", "Бенджамин Франклин", coat="#7a5232", vest="#e9d8a8", hat=None, wig=False, hair_col="#b8b4c0",
             hair=("receding", "#b8b4c0"), age="old", glasses={"type": "round", "col": "#3a2a20"}),
    colonial("chauncy", "Пастор Чарльз Чонси", coat="#1e1e22", vest="#1e1e22", hat=None, collar={"type": "ruff", "col": "#f4f1ea"}),
    native("tanaghrisson", "Танахарисон, Полукороль", age="old", hair=("short_sides", "#5a5a5a"), deer="#7a5232", fur="#a8312f", held=h("spear")),
    R("jumonville", "Энсин Жозеф де Жюмонвиль", hair=("wig", "#ece8e2"), hat={"type": "tricorne", "col": "#1e1e22", "trim": "#d4a63c"},
      outfit={"type": "uniform", "col": "#e9e0cc", "facing": "#2f4a7a", "trim": "#d4a63c", "sash": "", "epaulettes": False},
      sleeves=sl("#e9e0cc", "#2f4a7a"), legs=tr("#e9e0cc"), boots=tall(), held=h("scroll")),
    native("pontiac", "Понтиак", deer="#7a5232", fur="#2f9a8a", hair=("short_sides", "#1e1a18"), held=h("spear"), bushy=True),
    colonial("amherst", "Генерал Джеффри Амхерст", coat="#a8312f", vest="#f4f1ea", held=h("sword"), boots=tall()),
]

RECIPES += [
    # ---------- пачка 3: Революция
    R("patrick_henry", "Патрик Генри", hair=("wig", "#ece8e2"), outfit={"type": "frock", "col": "#1e1e22", "vest": "#1e1e22", "trim": "#5a4434"},
      sleeves=sl("#1e1e22", "#f4f1ea"), legs=tr("#1e1e22"), boots=bo("#1e1e22"), glasses={"type": "round", "col": "#3a2a20"}),
    colonial("grenville", "Министр Джордж Гренвилл", coat="#5a2a6b", vest="#e9d8a8", hat=None, held=h("scroll")),
    colonial("andrew_oliver", "Сборщик Эндрю Оливер", coat="#7a6a52", hat=None, age="old"),
    colonial("samuel_adams", "Сэмюэл Адамс", coat="#a8312f", vest="#5a4434", hat=None, wig=False, hair=("receding", "#b8b4c0"), age="old"),
    colonial("john_adams", "Джон Адамс", coat="#3b2a20", vest="#e9d8a8", hat=None, hair=("wig", "#d8d4dc"), held=h("book")),
    worker("crispus_attucks", "Криспус Аттакс", skin="african2", shirt="#e9e0cc", pants="#3b4a6a", hair=("short", "#1e1a18"),
           hat={"type": "cap", "col": "#3b4a6a", "fur": ""}, held=h("staff")),
    colonial("preston_t", "Капитан Томас Престон", coat="#a8312f", vest="#f4f1ea", held=h("sword"), boots=tall()),
    colonial("thomas_hutchinson", "Губернатор Томас Хатчинсон", coat="#2a2a2e", vest="#d8ad3c", hat=None, age="old"),
    colonial("francis_rotch", "Судовладелец Фрэнсис Ротч", coat="#3b4a5a", vest="#e9d8a8", hat={"type": "wide", "col": "#1e1e22", "feather": ""}, wig=False,
             hair=("short", "#5a3a22")),
    colonial("galloway", "Джозеф Гэллоуэй", coat="#5a6b4a", hat=None),
    colonial("paul_revere", "Пол Ревир", coat="#4b6a9a", vest="#e9d8a8", hat=None, wig=False, hair=("short", "#3b2a20"), boots=tall("#3b2a20")),
    colonial("robert_newman", "Пономарь Роберт Ньюман", coat="#3b2a20", vest="#7a6a52", hat=None, wig=False, hair=("bowl", "#5a3a22")),
    colonial("gage", "Генерал Томас Гейдж", coat="#a8312f", vest="#f4f1ea", held=h("bulawa"), boots=tall()),
    colonial("prescott_w", "Полковник Уильям Прескотт", coat="#4b6a9a", vest="#e9d8a8", hat={"type": "wide", "col": "#3b2a20", "feather": ""},
             held=h("sword"), boots=tall("#3b2a20")),
    colonial("joseph_warren", "Доктор Джозеф Уоррен", coat="#e9e0cc", vest="#7a6a52", hat=None, held=h("flask")),
    colonial("howe_w", "Генерал Уильям Хоу", coat="#a8312f", vest="#f4f1ea", held=h("sword"), boots=tall(), age="old"),
    worker("peter_salem", "Питер Салем", skin="african", shirt="#7a6a52", pants="#3b4a6a", hair=("short", "#1e1a18"),
           hat={"type": "tricorne", "col": "#3b2a20", "trim": "#5a4434"}, held=h("spear")),
    colonial("thomas_paine", "Томас Пейн", coat="#5a4434", vest="#e9d8a8", hat=None, held=h("book")),
    colonial("jefferson", "Томас Джефферсон", coat="#7a5232", vest="#a8312f", hat=None, wig=False, hair=("shoulder", "#b9672e"), held=h("scroll")),
    colonial("dickinson", "Джон Дикинсон", coat="#3b4a5a", hat=None),
    R("abigail_adams", "Абигейл Адамс", male=False, hair=("long", "#3b2a20"), hat={"type": "veil", "col": "#f4f1ea", "band": ""},
      outfit={"type": "gown", "dress": "#5a6b4a", "trim": "#f4f1ea", "mantle": "#3b2a20", "shoes": "#1e1e22"}, sleeves=sl("#5a6b4a", "#f4f1ea"),
      held=h("scroll")),
    R("rall", "Полковник Иоганн Ралль", hair=("wig", "#ece8e2"), beard=("handlebar", "#8a7a6a"),
      hat={"type": "pickelhaube", "col": "#2f4a7a", "metal": "#c9a24a"},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#a8312f", "trim": "#d4a63c", "sash": "", "epaulettes": True},
      sleeves=sl("#2f4a7a", "#a8312f"), legs=tr("#e9d8a8"), boots=tall()),
    colonial("glover", "Полковник Джон Гловер", coat="#3b4a5a", vest="#e9e0cc", hat={"type": "cap", "col": "#3b4a5a", "fur": ""}, wig=False,
             hair=("short", "#5a3a22")),
    colonial("knox", "Генри Нокс", coat="#2f4a7a", vest="#e9d8a8", wig=False, hair=("short", "#3b2a20"), boots=tall()),
    colonial("gates", "Генерал Горацио Гейтс", coat="#2f4a7a", vest="#e9d8a8", age="old", glasses={"type": "round", "col": "#3a2a20"}, boots=tall()),
    colonial("burgoyne", "Генерал Джон Бёргойн", coat="#a8312f", vest="#f4f1ea", held=h("sword"), boots=tall()),
    colonial("arnold", "Бенедикт Арнольд", coat="#2f4a7a", vest="#e9d8a8", wig=False, hair=("short", "#2a1a12"), held=h("sword"), boots=tall()),
    colonial("george_clinton", "Губернатор Джордж Клинтон", coat="#2a2a2e", hat=None),
    colonial("steuben", "Барон фон Штойбен", coat="#2f4a7a", vest="#e9d8a8", age="old", held=h("bulawa"), boots=tall(),
             cape={"type": "cape", "col": "#2f4a7a"}),
    colonial("lafayette", "Маркиз де Лафайет", coat="#2f4a7a", vest="#f4f1ea", wig=False, hair=("wig", "#d8b070"), held=h("sword"), boots=tall()),
    R("peggy_shippen", "Пегги Шиппен", male=False, hair=("long", "#d8b070"), outfit={"type": "gown", "dress": "#d48aa0", "trim": "#f4f1ea",
      "mantle": "#a8312f", "shoes": "#1e1e22"}, sleeves=sl("#d48aa0", "#f4f1ea"), iris="#5f7a9a"),
    colonial("john_andre", "Майор Джон Андре", coat="#a8312f", vest="#f4f1ea", hat=None, wig=False, hair=("short", "#3b2a20"), held=h("scroll")),
    colonial("rochambeau", "Граф де Рошамбо", coat="#f4f1ea", vest="#2f4a7a", age="old", held=h("bulawa"), boots=tall()),
    colonial("john_jay", "Джон Джей", coat="#1e1e22", vest="#1e1e22", hat=None, held=h("scroll")),
    colonial("vergennes", "Граф де Верженн", coat="#5a2a6b", vest="#d8ad3c", hat=None, age="old"),
    worker("daniel_shays", "Дэниел Шейс", shirt="#7a6a52", pants="#5a4434", hair=("short", "#5a3a22"),
           hat={"type": "tricorne", "col": "#5a4434", "trim": "#7a5232"}, held=h("scythe")),
    colonial("bowdoin", "Губернатор Джеймс Боудойн", coat="#3b2a20", hat=None, age="old"),
    colonial("benjamin_lincoln", "Генерал Бенджамин Линкольн", coat="#2f4a7a", vest="#e9d8a8", held=h("sword"), boots=tall()),
    colonial("madison", "Джеймс Мэдисон", coat="#1e1e22", vest="#1e1e22", hat=None, held=h("book")),
    colonial("roger_sherman", "Роджер Шерман", coat="#5a4434", hat=None, age="old"),
    colonial("alexander_hamilton", "Александр Гамильтон", coat="#2f6a4a", vest="#f4f1ea", hat=None, wig=False, hair=("wig", "#b9672e"),
             held=h("book")),
    colonial("george_mason", "Джордж Мейсон", coat="#3b4a5a", hat=None, age="old", held=h("scroll")),
]


def regency(id, name, coat="#1e1e22", vest="#f4f1ea", hair=("short", "#5a3a22"), **kw):
    """Начало XIX века: фрак, высокий воротник, свои волосы без парика."""
    d = dict(hair=hair, outfit={"type": "suit", "col": coat, "shirt": vest, "tie": "#f4f1ea", "long": True},
             sleeves=sl(coat, "#f4f1ea"), legs=tr("#e9d8a8"), boots=bo("#1e1e22"))
    d.update(kw)
    return R(id, name, **d)


RECIPES += [
    # ---------- пачка 4: Молодая республика
    regency("eli_whitney", "Эли Уитни", coat="#3b4a5a", held=h("pickaxe")),
    R("catharine_greene", "Кэтрин Грин", male=False, hair=("curly", "#3b2a20"), outfit={"type": "gown", "dress": "#f4f1ea", "trim": "#2f6a4a",
      "mantle": "#2f6a4a", "shoes": "#1e1e22"}, sleeves=sl("#f4f1ea")),
    regency("phineas_miller", "Финеас Миллер", coat="#5a4434", held=h("book")),
    regency("gallatin", "Альберт Галлатин", coat="#2a2a2e", hair=("receding", "#5a3a22")),
    colonial("david_bradford", "Дэвид Брэдфорд", coat="#5a6b4a", wig=False, hair=("short", "#3b2a20"), hat={"type": "tricorne", "col": "#3b2a20", "trim": "#5a4434"}),
    regency("matthew_lyon", "Конгрессмен Мэтью Лайон", coat="#5a4434", hair=("receding", "#a8562a")),
    regency("aaron_burr", "Аарон Бёрр", coat="#1e1e22", hair=("receding", "#2a1a12"), held=h("sword")),
    R("john_marshall", "Верховный судья Джон Маршалл", age="old", hair=("short", "#b8b4c0"), outfit={"type": "robe", "col": "#1e1e22", "rope": "#1e1e22"},
      sleeves=sl("#1e1e22", "#f4f1ea"), collar={"type": "ruff", "col": "#f4f1ea"}, held=h("book")),
    regency("marbury", "Уильям Марбери", coat="#3b4a5a", held=h("scroll")),
    colonial("robert_livingston", "Посол Роберт Ливингстон", coat="#2a2a2e", hat=None, age="old"),
    colonial("james_monroe", "Джеймс Монро", coat="#1e1e22", hat=None, wig=False, hair=("receding", "#b8b4c0")),
    R("meriwether_lewis", "Капитан Мериуэзер Льюис", hair=("short", "#5a3a22"), hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#1e1e22"},
      outfit={"type": "fur_tunic", "col": "#a8794e", "fur": "#e9d8a8", "rope": "#5a3a22"}, sleeves=sl("#a8794e"), legs=tr("#7a5232"),
      boots=bo("#5a3a22"), held=h("spear")),
    R("william_clark", "Капитан Уильям Кларк", hair=("short", "#b9672e"), outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#a8312f",
      "trim": "#d4a63c", "sash": "", "epaulettes": True}, sleeves=sl("#2f4a7a"), legs=tr("#7a5232"), boots=bo("#5a3a22"), held=h("scroll")),
    native("sacagawea", "Сакагавея", male=False, deer="#c9a06a", fur="#f4f1ea", hair=("long", "#1e1a18")),
    R("charbonneau", "Туссен Шарбонно", age="old", hair=("long", "#8a7a6a"), beard=("full", "#8a7a6a"), hat={"type": "cap", "col": "#a8312f", "fur": ""},
      outfit={"type": "fur_tunic", "col": "#7a5232", "fur": "#e9d8a8", "rope": "#a8312f"}, sleeves=sl("#7a5232"), legs=tr("#5a4434"), boots=bo("#5a3a22")),
    native("cameahwait", "Вождь Камеавайт", deer="#e9d8a8", fur="#a8312f", cape={"type": "cape", "col": "#7a5232"}, held=h("spear")),
    native("tecumseh", "Текумсе", deer="#7a5232", fur="#e9d8a8", hair=("short_sides", "#1e1a18"), held=h("spear"),
           cape={"type": "cape", "col": "#a8312f"}),
    native("tenskwatawa", "Тенскватава, Пророк", deer="#3b2a20", fur="#d8ad3c", hair=("long", "#1e1a18"), held=h("staff")),
    R("w_h_harrison", "Губернатор Уильям Генри Гаррисон", hair=("short", "#5a3a22"), hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#a8312f"},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#a8312f", "trim": "#d4a63c", "sash": "#a8312f", "epaulettes": True},
      sleeves=sl("#2f4a7a"), legs=tr("#e9d8a8"), boots=tall(), held=h("sword")),
    R("isaac_brock", "Генерал Айзек Брок", hair=("short", "#d8b070"), hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#1e1e22"},
      outfit={"type": "uniform", "col": "#a8312f", "facing": "#2f4a7a", "trim": "#d4a63c", "sash": "#a8312f", "epaulettes": True},
      sleeves=sl("#a8312f"), legs=tr("#e9d8a8"), boots=tall(), held=h("sword"), iris="#5f7a9a"),
    R("dolley_madison", "Долли Мэдисон", male=False, hair=("curly", "#2a1a12"), hat={"type": "turban", "col": "#f4f1ea", "jewel": "#a8312f"},
      outfit={"type": "gown", "dress": "#a8312f", "trim": "#f4f1ea", "mantle": "#d8ad3c", "shoes": "#1e1e22"}, sleeves=sl("#a8312f")),
    regency("francis_scott_key", "Фрэнсис Скотт Ки", coat="#2f4a7a", held=h("scroll")),
    R("andrew_jackson", "Генерал Эндрю Джексон", age="old", hair=("short", "#d8d4dc"), bushy=True,
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#d8ad3c", "trim": "#d4a63c", "sash": "#d8ad3c", "epaulettes": True},
      sleeves=sl("#2f4a7a"), legs=tr("#e9d8a8"), boots=tall(), held=h("sword")),
    regency("henry_clay", "Генри Клей", coat="#1e1e22", hair=("short", "#d8b070")),
    regency("tallmadge", "Конгрессмен Джеймс Толмадж", coat="#3b4a5a", hair=("receding", "#3b2a20")),
    regency("jq_adams", "Джон Куинси Адамс", coat="#1e1e22", hair=("receding", "#8a7a6a")),
    regency("george_canning", "Министр Джордж Каннинг", coat="#2a2a2e", hair=("receding", "#8a5a34")),
    R("bolivar", "Симон Боливар", skin="olive", hair=("curly", "#2a1a12"), beard=("handlebar", "#2a1a12"),
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#a8312f", "trim": "#d4a63c", "sash": "#d8ad3c", "epaulettes": True},
      sleeves=sl("#2f4a7a"), legs=tr("#f4f1ea"), boots=tall(), held=h("sword")),
]

RECIPES += [
    # ---------- пачка 5: Реформы и экспансия
    regency("dewitt_clinton", "Губернатор Девитт Клинтон", coat="#2a2a2e", hair=("short", "#8a7a6a")),
    regency("kirk_boott", "Управляющий Кирк Бутт", coat="#3b2a20", hat={"type": "top", "col": "#1e1e22"}),
    R("sarah_bagley", "Сара Бэгли", male=False, hair=("long", "#5a3a22"), outfit={"type": "gown", "dress": "#7f8c99", "trim": "#f4f1ea",
      "mantle": "#5a4434", "shoes": "#3b2a20"}, sleeves=sl("#7f8c99", "#f4f1ea"), held=h("scroll")),
    regency("samuel_slater", "Сэмюэл Слейтер", coat="#5a4434", hair=("receding", "#8a5a34")),
    regency("charles_finney", "Чарльз Финни", coat="#1e1e22", hair=("short", "#8a7a6a"), held=h("book"), iris="#5f7a9a"),
    regency("lyman_beecher", "Лайман Бичер", coat="#1e1e22", hair=("receding", "#b8b4c0"), age="old", held=h("book")),
    R("dorothea_dix", "Доротея Дикс", male=False, hair=("long", "#5a3a22"), outfit={"type": "gown", "dress": "#2a2a2e", "trim": "#f4f1ea",
      "mantle": "#2a2a2e", "shoes": "#1e1e22"}, sleeves=sl("#2a2a2e", "#f4f1ea"), held=h("book")),
    R("sojourner_truth", "Соджорнер Трут", male=False, skin="african", age="old", hat={"type": "veil", "col": "#f4f1ea", "band": ""},
      hair=("short", "#8a8a8a"), outfit={"type": "gown", "dress": "#3b3a38", "trim": "#f4f1ea", "mantle": "#3b3a38", "shoes": "#1e1e22"},
      sleeves=sl("#3b3a38", "#f4f1ea"), held=h("staff")),
    regency("john_ross", "Вождь Джон Росс", skin="native", coat="#2a2a2e", hair=("short", "#3b2a20"), held=h("scroll")),
    native("major_ridge", "Мейджор Ридж", age="old", hair=("short", "#8a8a8a"), deer="#2f4a7a", fur="#a8312f",
           hat={"type": "turban", "col": "#a8312f", "jewel": "#d8ad3c"}),
    R("winfield_scott", "Генерал Уинфилд Скотт", age="old", hair=("short", "#d8d4dc"), hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#d8ad3c"},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#d8ad3c", "trim": "#d4a63c", "sash": "#d8ad3c", "epaulettes": True},
      sleeves=sl("#2f4a7a"), legs=tr("#2f4a7a"), boots=tall(), held=h("sword")),
    worker("nat_turner", "Нат Тёрнер", skin="african", shirt="#e9e0cc", pants="#5a4434", hair=("short", "#1e1a18"), beard=("goatee", "#1e1a18"),
           held=h("book")),
    regency("garrison", "Уильям Ллойд Гаррисон", coat="#1e1e22", hair=("receding", "#8a7a6a"), glasses={"type": "round", "col": "#3a2a20"},
            held=h("book")),
    regency("thomas_gray", "Адвокат Томас Грей", coat="#3b2a20", held=h("scroll")),
    regency("john_floyd", "Губернатор Джон Флойд", coat="#2f4a7a", hair=("short", "#3b2a20")),
    regency("john_calhoun", "Джон Кэлхун", coat="#1e1e22", hair=("curly", "#8a7a6a"), bushy=True),
    regency("nicholas_biddle", "Банкир Николас Биддл", coat="#2f4a7a", hair=("curly", "#8a5a34")),
    R("santa_anna", "Генерал Санта-Анна", skin="olive", hair=("short", "#2a1a12"), hat={"type": "bicorne", "col": "#1e1e22", "cockade": "#2f6a4a"},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#a8312f", "trim": "#d4a63c", "sash": "#2f6a4a", "epaulettes": True},
      sleeves=sl("#2f4a7a"), legs=tr("#f4f1ea"), boots=tall(), held=h("sword")),
    R("sam_houston", "Сэм Хьюстон", hair=("short", "#8a5a34"), hat={"type": "wide", "col": "#e9d8a8", "feather": ""},
      outfit={"type": "fur_tunic", "col": "#7a5232", "fur": "#e9d8a8", "rope": "#a8312f"}, sleeves=sl("#7a5232"), legs=tr("#5a4434"),
      boots=tall("#3b2a20"), held=h("sword")),
    R("juan_seguin", "Хуан Сегин", skin="olive", hair=("short", "#2a1a12"), beard=("handlebar", "#2a1a12"),
      hat={"type": "wide", "col": "#3b2a20", "feather": ""}, outfit={"type": "coat", "col": "#a8312f", "trim": "#d4a63c", "belt": "#3b2a20"},
      sleeves=sl("#a8312f"), legs=tr("#2a2a2e"), boots=tall("#3b2a20")),
    R("davy_crockett", "Дэви Крокетт", hair=("long", "#5a3a22"), hat={"type": "cap", "col": "#8a6a4a", "fur": "#5a3a22"},
      outfit={"type": "fur_tunic", "col": "#a8794e", "fur": "#e9d8a8", "rope": "#5a3a22"}, sleeves=sl("#a8794e"), legs=tr("#a8794e"),
      boots=bo("#5a3a22"), held=h("spear")),
    regency("brigham_young", "Бригам Янг", coat="#3b2a20", hair=("short", "#8a5a34"), beard=("goatee", "#8a5a34"), held=h("staff")),
    R("emma_smith", "Эмма Смит", male=False, hair=("long", "#2a1a12"), outfit={"type": "gown", "dress": "#3b4a5a", "trim": "#f4f1ea",
      "mantle": "#3b4a5a", "shoes": "#1e1e22"}, sleeves=sl("#3b4a5a"), held=h("book")),
    regency("lilburn_boggs", "Губернатор Лилберн Боггс", coat="#2a2a2e", hair=("receding", "#5a3a22"), held=h("scroll")),
    regency("james_polk", "Президент Джеймс Полк", coat="#1e1e22", hair=("receding", "#8a7a6a"), held=h("scroll")),
    R("john_fremont", "Капитан Джон Фремонт", hair=("short", "#3b2a20"), beard=("full", "#3b2a20"), hat={"type": "wide", "col": "#7a5232", "feather": ""},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#2f4a7a", "trim": "#d4a63c", "sash": "", "epaulettes": False},
      sleeves=sl("#2f4a7a"), legs=tr("#7a5232"), boots=tall(), held=h("flag")),
    R("elizabeth_stanton", "Элизабет Кэди Стэнтон", male=False, hair=("curly", "#3b2a20"), outfit={"type": "gown", "dress": "#2a2a2e",
      "trim": "#f4f1ea", "mantle": "#5a2a6b", "shoes": "#1e1e22"}, sleeves=sl("#2a2a2e", "#f4f1ea"), held=h("scroll")),
    R("lucretia_mott", "Лукреция Мотт", male=False, age="old", hat={"type": "veil", "col": "#f4f1ea", "band": ""}, hair=("long", "#8a7a6a"),
      outfit={"type": "gown", "dress": "#7a6a52", "trim": "#f4f1ea", "mantle": "#7a6a52", "shoes": "#3b2a20"}, sleeves=sl("#7a6a52", "#f4f1ea")),
    regency("frederick_douglass", "Фредерик Дуглас", skin="african2", coat="#1e1e22", hair=("curly", "#2a1a12"), beard=("goatee", "#2a1a12"),
            held=h("book")),
    R("martha_wright", "Марта Коффин Райт", male=False, hair=("long", "#5a3a22"), hat={"type": "veil", "col": "#f4f1ea", "band": ""},
      outfit={"type": "gown", "dress": "#5a6b4a", "trim": "#f4f1ea", "mantle": "#5a6b4a", "shoes": "#3b2a20"}, sleeves=sl("#5a6b4a")),
]


def victorian(id, name, coat="#1e1e22", tie="#1e1e22", hair=("short", "#3b2a20"), **kw):
    """Середина–конец XIX века: сюртук, жилет, галстук."""
    d = dict(hair=hair, outfit={"type": "suit", "col": coat, "shirt": "#f4f1ea", "tie": tie, "long": True},
             sleeves=sl(coat, "#f4f1ea"), legs=tr(coat), boots=bo("#1e1e22"))
    d.update(kw)
    return R(id, name, **d)


def union(id, name, rank_sash="", **kw):
    d = dict(hair=("short", "#5a3a22"), outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#2f4a7a", "trim": "#d4a63c",
             "sash": rank_sash, "epaulettes": True}, sleeves=sl("#2f4a7a"), legs=tr("#4b6a9a"), boots=tall(), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


def confed(id, name, **kw):
    d = dict(hair=("short", "#8a7a6a"), outfit={"type": "uniform", "col": "#7f8c99", "facing": "#7f8c99", "trim": "#d4a63c",
             "sash": "#d8ad3c", "epaulettes": True}, sleeves=sl("#7f8c99"), legs=tr("#7f8c99"), boots=tall(), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


def plains(id, name, male=True, deer="#c9a06a", fur="#f4f1ea", **kw):
    d = dict(male=male, skin="native", hair=("long", "#1e1a18"),
             outfit={"type": "fur_tunic", "col": deer, "fur": fur, "rope": "#a8312f"} if male else
             {"type": "gown", "dress": deer, "trim": fur, "mantle": "#7a5232", "shoes": "#7a5232"},
             sleeves=sl(deer), legs=tr(deer) if male else None, boots=bo("#a8794e") if male else None)
    d.update(kw)
    return R(id, name, **d)


RECIPES += [
    # ---------- пачка 6: Раскол и Реконструкция
    R("harriet_tubman", "Гарриет Табмен", male=False, skin="african", hair=("short", "#1e1a18"), hat={"type": "veil", "col": "#a8312f", "band": ""},
      outfit={"type": "gown", "dress": "#5a4434", "trim": "#e9e0cc", "mantle": "#3b3a38", "shoes": "#3b2a20"}, sleeves=sl("#5a4434"), held=h("spear")),
    victorian("william_still", "Уильям Стилл", skin="african2", hair=("short", "#1e1a18"), beard=("goatee", "#1e1a18"), held=h("book")),
    worker("anthony_burns", "Энтони Бёрнс", skin="african", shirt="#e9e0cc", pants="#5a4434", hair=("short", "#1e1a18")),
    victorian("millard_fillmore", "Президент Миллард Филлмор", hair=("short", "#b8b4c0"), age="old"),
    victorian("stephen_douglas", "Сенатор Стивен Дуглас", hair=("shoulder", "#3b2a20"), bushy=True),
    victorian("abraham_lincoln", "Авраам Линкольн", hair=("short", "#1e1a18"), beard=("full", "#1e1a18"), hat={"type": "top", "col": "#1e1e22"},
              bushy=True),
    victorian("salmon_chase", "Сэлмон Чейз", hair=("receding", "#5a3a22")),
    victorian("charles_robinson", "Чарльз Робинсон", coat="#5a4434", beard=("goatee", "#5a3a22"), hat={"type": "wide", "col": "#3b2a20", "feather": ""}),
    R("john_brown", "Джон Браун", age="old", hair=("short", "#b8b4c0"), beard=("long", "#d8d4dc"), bushy=True,
      outfit={"type": "coat", "col": "#3b2a20", "trim": "#1e1e22", "belt": "#1e1e22"}, sleeves=sl("#3b2a20"), legs=tr("#3b2a20"), boots=bo("#1e1e22"),
      held=h("spear"), iris="#5f7a9a"),
    victorian("charles_sumner", "Сенатор Чарльз Самнер", hair=("shoulder", "#5a3a22")),
    victorian("preston_brooks", "Конгрессмен Престон Брукс", coat="#3b4a5a", hair=("short", "#2a1a12"), held=h("staff")),
    R("sheriff_jones", "Шериф Сэмюэл Джонс", hair=("short", "#5a3a22"), beard=("walrus", "#5a3a22"), hat={"type": "wide", "col": "#3b2a20", "feather": ""},
      outfit={"type": "coat", "col": "#7a5232", "trim": "#d4a63c", "belt": "#1e1e22"}, sleeves=sl("#7a5232"), legs=tr("#3b2a20"), boots=tall("#3b2a20"),
      held=h("spear")),
    victorian("dred_scott", "Дред Скотт", skin="african", hair=("short", "#3b3a38"), beard=("goatee", "#3b3a38"), coat="#3b2a20", age="old"),
    R("harriet_scott", "Гарриет Скотт", male=False, skin="african", hair=("short", "#1e1a18"), hat={"type": "veil", "col": "#f4f1ea", "band": ""},
      outfit={"type": "gown", "dress": "#3b4a5a", "trim": "#f4f1ea", "mantle": "#3b4a5a", "shoes": "#3b2a20"}, sleeves=sl("#3b4a5a")),
    R("roger_taney", "Верховный судья Роджер Тони", age="old", hair=("shoulder", "#b8b4c0"), outfit={"type": "robe", "col": "#1e1e22", "rope": "#1e1e22"},
      sleeves=sl("#1e1e22"), held=h("book")),
    R("mary_lincoln", "Мэри Тодд Линкольн", male=False, hair=("long", "#2a1a12"), outfit={"type": "gown", "dress": "#5a2a6b", "trim": "#f4f1ea",
      "mantle": "#2a2a2e", "shoes": "#1e1e22"}, sleeves=sl("#5a2a6b")),
    victorian("horace_greeley", "Редактор Хорас Грили", coat="#e9e0cc", tie="#1e1e22", hair=("receding", "#e6e0d6"), beard=("goatee", "#e6e0d6"),
              glasses={"type": "round", "col": "#3a2a20"}, held=h("book")),
    confed("robert_lee", "Генерал Роберт Э. Ли", hair=("short", "#8a7a6a"), beard=("full", "#d8d4dc"), age="old"),
    worker("dangerfield_newby", "Дэнджерфилд Ньюби", skin="african2", shirt="#e9e0cc", pants="#3b4a6a", hair=("short", "#1e1a18"), held=h("scroll")),
    victorian("breckinridge", "Джон Брекинридж", hair=("short", "#3b2a20"), beard=("handlebar", "#3b2a20")),
    victorian("jefferson_davis", "Джефферсон Дэвис", coat="#3b3a38", hair=("short", "#8a7a6a"), beard=("goatee", "#8a7a6a"), age="old"),
    union("robert_anderson", "Майор Роберт Андерсон", hair=("short", "#8a7a6a")),
    confed("beauregard", "Генерал П. Г. Т. Борегар", hair=("short", "#2a1a12"), beard=("handlebar", "#2a1a12"), skin="olive"),
    union("mcclellan", "Генерал Джордж Макклеллан", hair=("short", "#8a5a34"), beard=("handlebar", "#8a5a34"), rank_sash="#d8ad3c"),
    union("george_meade", "Генерал Джордж Мид", hair=("receding", "#8a7a6a"), beard=("full", "#8a7a6a"), glasses={"type": "round", "col": "#3a2a20"}),
    union("ulysses_grant", "Генерал Улисс Грант", hair=("short", "#5a3a22"), beard=("full", "#5a3a22"), hat={"type": "wide", "col": "#1e1e22", "feather": ""}),
    union("william_sherman", "Генерал Уильям Шерман", hair=("short", "#b9672e"), beard=("goatee", "#b9672e"), bushy=True),
    union("ely_parker", "Полковник Эли Паркер", skin="native", hair=("short", "#1e1a18"), held=h("scroll")),
    victorian("john_wilkes_booth", "Актёр Джон Уилкс Бут", hair=("curly", "#1e1a18"), beard=("handlebar", "#1e1a18"), cape={"type": "cape", "col": "#1e1e22"}),
    victorian("andrew_johnson", "Президент Эндрю Джонсон", hair=("short", "#3b2a20"), held=h("scroll")),
    victorian("thaddeus_stevens", "Таддеус Стивенс", hair=("wig", "#3b2a20"), age="old", held=h("staff")),
    R("robert_smalls", "Роберт Смоллс", skin="african", hair=("short", "#1e1a18"), beard=("handlebar", "#1e1a18"), hat={"type": "cap", "col": "#2f4a7a", "fur": ""},
      outfit={"type": "uniform", "col": "#2f4a7a", "facing": "#2f4a7a", "trim": "#d4a63c", "sash": "", "epaulettes": False},
      sleeves=sl("#2f4a7a"), legs=tr("#2f4a7a"), boots=bo("#1e1e22")),
    victorian("jourdon_anderson", "Джордон Андерсон", skin="african2", hair=("short", "#3b3a38"), beard=("goatee", "#3b3a38"), coat="#3b2a20",
              held=h("scroll")),
    victorian("john_bingham", "Конгрессмен Джон Бингем", hair=("receding", "#5a3a22"), held=h("book")),
    victorian("leland_stanford", "Лиланд Стэнфорд", hair=("short", "#3b2a20"), beard=("full", "#3b2a20"), hat={"type": "top", "col": "#1e1e22"}),
    union("grenville_dodge", "Генерал Гренвилл Додж", hair=("short", "#5a3a22"), beard=("handlebar", "#5a3a22"), held=h("scroll")),
    victorian("charles_crocker", "Чарльз Крокер", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"), bushy=True),
    worker("chin_lin_sou", "Бригадир Чин Лин Соу", skin="#efc79a", shirt="#2f4a7a", pants="#2f4a7a", hair=("short", "#1e1a18"),
           hat={"type": "wide", "col": "#d8c7a0", "feather": ""}, held=h("pickaxe")),
    victorian("hiram_revels", "Сенатор Хайрам Ревелс", skin="african2", hair=("short", "#3b3a38"), beard=("goatee", "#3b3a38"), held=h("book")),
    confed("nathan_forrest", "Натан Бедфорд Форрест", hair=("short", "#8a7a6a"), beard=("goatee", "#8a7a6a"), cape={"type": "cape", "col": "#1e1e22"}),
    victorian("blanche_bruce", "Сенатор Бланш Брюс", skin="african2", hair=("short", "#1e1a18"), beard=("handlebar", "#1e1a18")),
    plains("sitting_bull", "Сидящий Бык", age="old", hair=("long", "#3b3a38"), deer="#a8794e", fur="#a8312f",
           cape={"type": "cape", "col": "#7a5232"}, held=h("staff")),
    plains("crazy_horse", "Бешеный Конь", deer="#c9a06a", fur="#f4f1ea", held=h("spear")),
    plains("gall_lakota", "Галл", deer="#7a5232", fur="#d8ad3c", held=h("spear"), bushy=True),
    R("custer", "Подполковник Джордж Кастер", hair=("shoulder", "#d8b070"), beard=("handlebar", "#d8b070"), hat={"type": "wide", "col": "#e9d8a8", "feather": ""},
      outfit={"type": "fur_tunic", "col": "#c9a06a", "fur": "#e9d8a8", "rope": "#a8312f"}, sleeves=sl("#c9a06a"), legs=tr("#2f4a7a"), boots=tall(),
      held=h("sword"), iris="#5f7a9a"),
    victorian("rutherford_hayes", "Резерфорд Хейс", hair=("receding", "#8a5a34"), beard=("long", "#8a5a34")),
    victorian("samuel_tilden", "Сэмюэл Тилден", hair=("receding", "#8a7a6a"), age="old"),
    confed("wade_hampton", "Уэйд Хэмптон", hair=("receding", "#8a7a6a"), beard=("full", "#8a7a6a"), hat={"type": "wide", "col": "#3b3a38", "feather": ""}),
]


def edwardian(id, name, male=True, coat="#2a2a2e", **kw):
    """Рубеж XIX–XX веков: костюм-тройка / блузка и длинная юбка."""
    d = dict(male=male, hair=("short", "#3b2a20") if male else ("long", "#3b2a20"),
             outfit={"type": "suit", "col": coat, "shirt": "#f4f1ea", "tie": "#a8312f", "long": False} if male else
             {"type": "gown", "dress": coat, "trim": "#f4f1ea", "mantle": coat, "shoes": "#1e1e22"},
             sleeves=sl(coat, "#f4f1ea"), legs=tr(coat) if male else None, boots=bo("#1e1e22") if male else None)
    d.update(kw)
    return R(id, name, **d)


RECIPES += [
    # ---------- пачка 7: Позолоченный век и Прогрессивная эра
    victorian("chester_arthur", "Президент Честер Артур", hair=("short", "#5a3a22"), beard=("walrus", "#5a3a22")),
    worker("denis_kearney", "Денис Кирни", shirt="#f4f1ea", pants="#3b4a6a", hair=("short", "#8a5a34"), beard=("handlebar", "#8a5a34"),
           hat={"type": "cap", "col": "#3b4a6a", "fur": ""}),
    victorian("wong_kim_ark", "Вонг Ким Арк", skin="#efc79a", coat="#2f4a7a", hair=("short", "#1e1a18")),
    edwardian("emma_lazarus", "Эмма Лазарус", male=False, coat="#3b4a5a", hair=("curly", "#2a1a12"), held=h("book")),
    edwardian("emily_roebling", "Эмили Рёблинг", male=False, coat="#5a2a6b", hair=("long", "#3b2a20"), held=h("scroll")),
    victorian("washington_roebling", "Вашингтон Рёблинг", hair=("short", "#8a7a6a"), beard=("walrus", "#8a7a6a"), age="old"),
    victorian("edison", "Томас Эдисон", hair=("short", "#8a7a6a"), coat="#3b3a38"),
    victorian("tesla", "Никола Тесла", hair=("short", "#1e1a18"), beard=("handlebar", "#1e1a18")),
    victorian("albert_parsons", "Альберт Парсонс", hair=("short", "#2a1a12"), beard=("handlebar", "#2a1a12")),
    victorian("august_spies", "Август Шпис", hair=("short", "#8a5a34"), beard=("handlebar", "#8a5a34"), held=h("book")),
    edwardian("lucy_parsons", "Люси Парсонс", male=False, skin="african2", coat="#1e1e22", hair=("curly", "#1e1a18")),
    victorian("gompers", "Сэмюэл Гомперс", hair=("receding", "#3b2a20"), beard=("handlebar", "#3b2a20")),
    victorian("henry_dawes", "Сенатор Генри Доуз", hair=("short", "#b8b4c0"), beard=("long", "#d8d4dc"), age="old"),
    plains("kicking_bear", "Кикинг-Беар", deer="#f4f1ea", fur="#2f6a4a", held=h("staff")),
    union("forsyth", "Полковник Джеймс Форсайт", hair=("short", "#8a7a6a"), beard=("walrus", "#8a7a6a"), age="old"),
    plains("spotted_elk", "Пятнистый Лось (Большая Нога)", age="old", hair=("long", "#3b3a38"), deer="#7a5232", fur="#e9d8a8",
           cape={"type": "cape", "col": "#4b6a9a"}),
    victorian("carnegie", "Эндрю Карнеги", hair=("short", "#d8d4dc"), beard=("full", "#d8d4dc"), age="old"),
    victorian("frick", "Генри Фрик", hair=("receding", "#5a3a22"), beard=("full", "#5a3a22")),
    victorian("eugene_debs", "Юджин Дебс", hair=("receding", "#8a7a6a"), glasses={"type": "pince", "col": "#3a2a20"}),
    edwardian("mary_lease", "Мэри Элизабет Лиз", male=False, coat="#2f4a7a", hair=("long", "#2a1a12")),
    victorian("homer_plessy", "Гомер Плесси", skin="#e2b48f", hair=("short", "#2a1a12"), beard=("handlebar", "#2a1a12"), hat={"type": "top", "col": "#1e1e22"}),
    victorian("albion_tourgee", "Адвокат Альбион Турже", hair=("receding", "#5a3a22"), beard=("handlebar", "#5a3a22"), held=h("book")),
    R("henry_brown_j", "Судья Генри Билингс Браун", age="old", hair=("receding", "#b8b4c0"), beard=("full", "#d8d4dc"),
      outfit={"type": "robe", "col": "#1e1e22", "rope": "#1e1e22"}, sleeves=sl("#1e1e22"), held=h("book")),
    R("harlan_j", "Судья Джон Маршалл Харлан", age="old", hair=("receding", "#b8b4c0"), outfit={"type": "robe", "col": "#1e1e22", "rope": "#1e1e22"},
      sleeves=sl("#1e1e22"), held=h("scroll")),
    R("liliuokalani", "Королева Лилиуокалани", male=False, skin="#b97c52", age="old", hair=("long", "#3b3a38"), hat={"type": "crown", "gold": "#d8ad3c"},
      outfit={"type": "gown", "dress": "#1e1e22", "trim": "#d8ad3c", "mantle": "#d8ad3c", "shoes": "#1e1e22"}, sleeves=sl("#1e1e22")),
    victorian("mckinley", "Президент Уильям Мак-Кинли", hair=("receding", "#3b2a20"), tie="#a8312f"),
    R("aguinaldo", "Эмилио Агинальдо", skin="#c9925e", hair=("short", "#1e1a18"), hat={"type": "wide", "col": "#e9d8a8", "feather": ""},
      outfit={"type": "uniform", "col": "#e9e0cc", "facing": "#2f4a7a", "trim": "#d4a63c", "sash": "#a8312f", "epaulettes": False},
      sleeves=sl("#e9e0cc"), legs=tr("#e9e0cc"), boots=tall(), held=h("sword")),
    edwardian("mark_twain", "Марк Твен", coat="#f4f1ea", hair=("curly", "#f4f1ea"), beard=("walrus", "#f4f1ea"), age="old", bushy=True),
    R("teddy_roosevelt", "Теодор Рузвельт", hair=("short", "#8a5a34"), beard=("walrus", "#8a5a34"), glasses={"type": "pince", "col": "#3a2a20"},
      hat={"type": "wide", "col": "#7a5232", "feather": ""}, outfit={"type": "uniform", "col": "#a8794e", "facing": "#2f4a7a", "trim": "#7a5232",
      "sash": "", "epaulettes": False}, sleeves=sl("#a8794e"), legs=tr("#a8794e"), boots=tall("#5a3a22")),
    edwardian("jp_morgan", "Дж. П. Морган", coat="#1e1e22", hair=("receding", "#d8d4dc"), beard=("walrus", "#d8d4dc"), age="old",
              hat={"type": "top", "col": "#1e1e22"}),
    edwardian("gifford_pinchot", "Гиффорд Пинчо", coat="#5a6b4a", hair=("short", "#3b2a20"), beard=("handlebar", "#3b2a20")),
    R("john_muir", "Джон Мьюр", age="old", hair=("long", "#b8b4c0"), beard=("long", "#d8d4dc"), hat={"type": "wide", "col": "#5a4434", "feather": ""},
      outfit={"type": "coat", "col": "#7a6a52", "trim": "#5a4434", "belt": "#3b2a20"}, sleeves=sl("#7a6a52"), legs=tr("#5a4434"), boots=bo("#3b2a20"),
      held=h("staff")),
    edwardian("orville_wright", "Орвилл Райт", hair=("receding", "#5a3a22"), beard=("handlebar", "#5a3a22"), hat={"type": "cap", "col": "#5a4434", "fur": ""}),
    edwardian("wilbur_wright", "Уилбур Райт", hair=("receding", "#8a7a6a"), iris="#5f7a9a"),
    edwardian("katharine_wright", "Кэтрин Райт", male=False, coat="#5a6b4a", hair=("long", "#5a3a22"), glasses={"type": "pince", "col": "#3a2a20"}),
    victorian("octave_chanute", "Октав Шанют", hair=("receding", "#d8d4dc"), beard=("goatee", "#d8d4dc"), age="old"),
    edwardian("bunau_varilla", "Филипп Бюно-Варийя", coat="#1e1e22", hair=("receding", "#2a1a12"), beard=("handlebar", "#2a1a12")),
    edwardian("manuel_amador", "Мануэль Амадор Герреро", skin="olive", coat="#f4f1ea", hair=("short", "#b8b4c0"), beard=("walrus", "#d8d4dc"), age="old"),
    edwardian("john_hay", "Госсекретарь Джон Хэй", coat="#2a2a2e", hair=("short", "#8a7a6a"), beard=("goatee", "#8a7a6a")),
    edwardian("upton_sinclair", "Эптон Синклер", coat="#3b4a5a", hair=("short", "#5a3a22"), held=h("book")),
    edwardian("harvey_wiley", "Химик Харви Уайли", coat="#e9e0cc", hair=("receding", "#8a7a6a"), held=h("flask")),
    edwardian("ogden_armour", "Дж. Огден Армор", coat="#2a2a2e", hair=("short", "#8a5a34"), beard=("handlebar", "#8a5a34")),
    edwardian("henry_ford", "Генри Форд", coat="#3b3a38", hair=("short", "#8a7a6a")),
    edwardian("james_couzens", "Джеймс Кузенс", coat="#1e1e22", hair=("receding", "#3b2a20"), glasses={"type": "round", "col": "#3a2a20"},
              held=h("book")),
    worker("charles_sorensen", "Мастер Чарльз Соренсен", shirt="#f4f1ea", pants="#3b3a38", hair=("short", "#d8b070"), held=h("pickaxe")),
    edwardian("samuel_marquis", "Пастор Сэмюэл Маркис", coat="#1e1e22", hair=("receding", "#8a7a6a"), collar={"type": "ruff", "col": "#f4f1ea"}),
    edwardian("du_bois", "У. Э. Б. Дюбуа", skin="african2", coat="#1e1e22", hair=("receding", "#1e1a18"), beard=("goatee", "#1e1a18"), held=h("book")),
    edwardian("ida_wells", "Ида Б. Уэллс", male=False, skin="african2", coat="#1e1e22", hair=("curly", "#1e1a18"), held=h("scroll")),
    edwardian("mary_ovington", "Мэри Уайт Овингтон", male=False, coat="#5a2a6b", hair=("long", "#b8b4c0")),
    edwardian("booker_washington", "Букер Т. Вашингтон", skin="african", coat="#3b3a38", hair=("short", "#1e1a18")),
    edwardian("clara_lemlich", "Клара Лемлих", male=False, coat="#3b4a5a", hair=("curly", "#2a1a12")),
    edwardian("frances_perkins", "Фрэнсис Перкинс", male=False, coat="#2a2a2e", hair=("long", "#3b2a20"), hat={"type": "wide", "col": "#1e1e22", "feather": ""}),
    edwardian("max_blanck", "Фабрикант Макс Бланк", coat="#2a2a2e", hair=("receding", "#2a1a12"), beard=("handlebar", "#2a1a12")),
    edwardian("isaac_harris", "Фабрикант Айзек Харрис", coat="#3b3a38", hair=("short", "#3b2a20"), beard=("walrus", "#3b2a20")),
    R("alice_paul", "Элис Пол", male=False, hair=("long", "#3b2a20"), outfit={"type": "gown", "dress": "#f4f1ea", "trim": "#d8ad3c",
      "mantle": "#5a2a6b", "shoes": "#1e1e22"}, sleeves=sl("#f4f1ea"), held=h("flag")),
    edwardian("lucy_burns", "Люси Бёрнс", male=False, coat="#5a2a6b", hair=("curly", "#b9672e")),
    edwardian("carter_glass", "Конгрессмен Картер Гласс", coat="#2a2a2e", hair=("short", "#b9672e")),
    edwardian("paul_warburg", "Банкир Пол Варбург", coat="#1e1e22", hair=("receding", "#3b2a20"), beard=("handlebar", "#3b2a20")),
    edwardian("louis_brandeis", "Луис Брандейс", coat="#2a2a2e", hair=("curly", "#8a7a6a")),
    R("john_pershing", "Генерал Джон Першинг", hair=("short", "#8a7a6a"), beard=("walrus", "#8a7a6a"), hat={"type": "cap", "col": "#7a7a4a", "fur": ""},
      outfit={"type": "legion_tunic", "col": "#7a7a4a", "belt": "#5a3a22", "button": "#c9a24a"}, sleeves=sl("#7a7a4a"), legs=tr("#7a7a4a"),
      boots=tall("#5a3a22"), held=h("bulawa")),
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
