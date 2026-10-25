#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 3 главы «Россия» (1535–1863).

    python3 tools/batches/russia_recipes_3.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/russia_recipes_3.py --ids      только список id (для factory/build.py)
    python3 tools/batches/russia_recipes_3.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, colonial, victorian, ROOT, OUT  # noqa: F401


def boyar(id, name, coat="#2f6a4a", fur="#5a3a22", top="#a8312f", beard=("long", "#5a3a22"), age="old", **kw):
    """Московский боярин / дьяк XVI–XVII века: долгополый кафтан, горлатная шапка, борода."""
    d = dict(age=age, hair=("short", beard[1]), beard=beard, bushy=True, hat={"type": "kolpak", "fur": fur, "top": top},
             outfit={"type": "coat", "col": coat, "trim": "#d4a63c", "belt": "#d4a63c"}, sleeves=sl(coat, "#d4a63c"),
             legs=tr(coat), boots=bo("#a8312f"))
    d.update(kw)
    return R(id, name, **d)


def tsar(id, name, robe="#a8312f", mantle="#d8ad3c", beard=("full", "#5a3a22"), **kw):
    d = dict(hair=("short", beard[1] if beard else "#5a3a22"), beard=beard, hat={"type": "crown", "gold": "#d8ad3c"},
             outfit={"type": "emperor", "col": robe, "gold": "#d8ad3c", "mantle": mantle}, sleeves=sl(robe, "#d8ad3c"))
    d.update(kw)
    return R(id, name, **d)


def cleric(id, name, robe="#1e1e22", hood="#1e1e22", beard=("long", "#5a3a22"), **kw):
    d = dict(age="old", hair=("long", beard[1]), beard=beard, hat={"type": "hood", "col": hood},
             outfit={"type": "robe", "col": robe, "rope": "#d8c7a0"}, sleeves=sl(robe), held=h("cross"))
    d.update(kw)
    return R(id, name, **d)


def cossack(id, name, zupan="#e9d8a8", kontusz="#2f4a7a", moustache=("handlebar", "#3b2a20"), **kw):
    d = dict(hair=("short_sides", moustache[1]), beard=moustache, hat={"type": "cap", "col": "#a8312f", "fur": "#3b2a20"},
             outfit={"type": "kontusz", "zupan": zupan, "kontusz": kontusz, "sash": "#a8312f", "sash2": "#d4a63c"},
             sleeves=sl(kontusz), legs=tr("#a8312f"), boots=bo("#a8312f"))
    d.update(kw)
    return R(id, name, **d)


def general_19(id, name, coat="#2f6a4a", **kw):
    d = dict(hair=("short", "#5a3a22"), outfit={"type": "uniform", "col": coat, "facing": "#a8312f", "trim": "#d4a63c",
             "sash": "", "epaulettes": True}, sleeves=sl(coat), legs=tr("#f4f1ea"), boots=tall(), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


def highlander(id, name, coat="#3b3a38", **kw):
    d = dict(hair=("short", "#1e1a18"), beard=("full", "#1e1a18"), bushy=True,
             hat={"type": "cap", "col": "#1e1e22", "fur": "#1e1e22"},
             outfit={"type": "fur_tunic", "col": coat, "fur": "#d8c7a0", "rope": "#a8794e"}, sleeves=sl(coat),
             legs=tr("#3b3a38"), boots=bo("#1e1e22"), held=h("sword"), skin="tan")
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Елена Глинская
    R("elena_glinskaya_ru", "Елена Глинская", male=False, hair=("long", "#3b2a20"),
      hat={"type": "veil", "col": "#f4f1ea", "band": "#d8ad3c"},
      outfit={"type": "gown", "dress": "#a8312f", "trim": "#d4a63c", "mantle": "#5a2a6b", "shoes": "#a8312f"}, sleeves=sl("#a8312f", "#d4a63c")),
    R("ivan_boy_ru", "Малолетний Иван IV", hair=("bowl", "#8a5a34"), hat={"type": "kolpak", "fur": "#5a3a22", "top": "#d8ad3c"},
      outfit={"type": "coat", "col": "#a8312f", "trim": "#d4a63c", "belt": "#d4a63c"}, sleeves=sl("#a8312f"), legs=tr("#a8312f"),
      boots=bo("#d8ad3c")),
    boyar("mikhail_glinsky_ru", "Князь Михаил Глинский", coat="#3b4a5a", beard=("long", "#b8b4c0"), top="#3b4a5a"),
    boyar("ivan_shuisky_ru", "Князь Иван Шуйский", coat="#5a6b4a", beard=("full", "#3b2a20"), age="young", top="#2f6a4a"),
    # ---------- Соляной бунт
    tsar("alexei_mikh_ru", "Царь Алексей Михайлович", beard=("full", "#8a5a34")),
    boyar("morozov_ru", "Боярин Борис Морозов", coat="#2f4a7a", beard=("long", "#d8d4dc"), held=h("scroll")),
    boyar("pleshcheev_ru", "Судья Леонтий Плещеев", coat="#7a5232", beard=("goatee", "#3b2a20"), age="young", top="#5a2a6b",
          held=h("book")),
    boyar("odoevsky_ru", "Князь Никита Одоевский", coat="#5a2a6b", beard=("long", "#8a7a6a"), held=h("scroll")),
    # ---------- Переяслав
    cossack("vyhovsky_ru", "Генеральный писарь Иван Выговский", kontusz="#5a2a6b", held=h("scroll")),
    boyar("buturlin_ru", "Боярин Василий Бутурлин", coat="#a8312f", beard=("long", "#5a3a22"), top="#2f4a7a", held=h("scroll")),
    # ---------- раскол
    cleric("nikon_ru", "Патриарх Никон", robe="#1e1e22", hood="#f4f1ea", beard=("long", "#3b2a20"),
           cape={"type": "cape", "col": "#5a2a6b"}),
    cleric("avvakum_ru", "Протопоп Аввакум", robe="#5a4434", hood="#3b2a20", beard=("long", "#2a1a12"), held=h("book")),
    cleric("paisius_ru", "Патриарх Паисий Александрийский", robe="#1e1e22", hood="#1e1e22", beard=("long", "#e6e0d6"),
           skin="olive", held=h("staff")),
    R("morozova_ru", "Боярыня Феодосия Морозова", male=False, hair=("long", "#2a1a12"), hat={"type": "veil", "col": "#1e1e22", "band": ""},
      outfit={"type": "gown", "dress": "#1e1e22", "trim": "#5a4434", "mantle": "#3b2a20", "shoes": "#1e1e22"}, sleeves=sl("#1e1e22")),
    # ---------- Разин
    cossack("razin_ru", "Атаман Степан Разин", zupan="#f4f1ea", kontusz="#a8312f", moustache=("handlebar", "#2a1a12"), held=h("sword"),
            hat={"type": "cap", "col": "#2f6a4a", "fur": "#2a1a12"}, bushy=True),
    cossack("frol_razin_ru", "Фрол Разин", zupan="#e9d8a8", kontusz="#5a4434", moustache=("full", "#3b2a20"),
            hat={"type": "cap", "col": "#5a4434", "fur": "#3b2a20"}),
    boyar("baryatinsky_ru", "Воевода Юрий Барятинский", coat="#a8312f", beard=("full", "#5a3a22"), age="young",
          hat={"type": "helmet", "col": "#b9bfc6", "trim": "#d4a63c"}, held=h("bulawa")),
    cossack("kornila_ru", "Войсковой атаман Корнила Яковлев", kontusz="#2f4a7a", moustache=("full", "#d8d4dc"), age="old",
            hat={"type": "cap", "col": "#2f4a7a", "fur": "#5a3a22"}, held=h("bulawa")),
    # ---------- Хованщина
    tsar("ivan5_ru", "Царь Иван V", robe="#f4f1ea", mantle="#d8ad3c", beard=None, hair=("long", "#b97a45")),
    boyar("khovansky_ru", "Князь Иван Хованский", coat="#a8312f", beard=("long", "#8a7a6a"), top="#a8312f", held=h("spear")),
    # ---------- Нерчинск
    boyar("golovin_ru", "Посол Фёдор Головин", coat="#2f4a7a", beard=("goatee", "#3b2a20"), age="young", held=h("scroll")),
    R("songgotu_ru", "Князь Сонготу", skin="tan", age="old", hair=("short", "#2a1a12"), beard=("walrus", "#5a5a5a"),
      hat={"type": "mongol", "fur": "#2a1a12", "top": "#a8312f"}, outfit={"type": "robe", "col": "#2f4a7a", "rope": "#d8ad3c"},
      sleeves=sl("#2f4a7a"), held=h("scroll")),
    R("gerbillon_ru", "Иезуит Жан-Франсуа Жербийон", hair=("short", "#8a5a34"), beard=("full", "#8a5a34"),
      outfit={"type": "robe", "col": "#1e1e22", "rope": "#1e1e22"}, sleeves=sl("#1e1e22"), held=h("book")),
    R("kangxi_ru", "Император Канси", skin="tan", hair=("short", "#1e1a18"), beard=("walrus", "#1e1a18"),
      hat={"type": "mongol", "fur": "#1e1a18", "top": "#d8ad3c"}, outfit={"type": "emperor", "col": "#d8ad3c", "gold": "#a8312f", "mantle": "#2f4a7a"},
      sleeves=sl("#d8ad3c")),
    # ---------- конец Сечи
    cossack("kalnyshevsky_ru", "Кошевой атаман Пётр Калнышевский", zupan="#f4f1ea", kontusz="#a8312f", moustache=("walrus", "#e6e0d6"),
            age="old", held=h("bulawa")),
    colonial("tekeli_ru", "Генерал Пётр Текели", coat="#2f6a4a", vest="#a8312f", hat="tricorne", held=h("sword")),
    # ---------- Грузия
    tsar("george12_ru", "Царь Георгий XII", robe="#5a2a6b", mantle="#a8312f", beard=("full", "#3b2a20"), skin="olive"),
    R("darejan_ru", "Царица Дареджан", male=False, age="old", skin="olive", hair=("long", "#8a8a8a"),
      hat={"type": "veil", "col": "#f4f1ea", "band": "#d8ad3c"},
      outfit={"type": "gown", "dress": "#2f6a4a", "trim": "#d4a63c", "mantle": "#5a2a6b", "shoes": "#1e1e22"}, sleeves=sl("#2f6a4a")),
    general_19("tsitsianov_ru", "Генерал Павел Цицианов", skin="olive", hair=("short", "#2a1a12"), beard=("handlebar", "#2a1a12")),
    # ---------- Кавказ
    highlander("shamil_ru", "Имам Шамиль", coat="#f4f1ea", beard=("long", "#5a3a22"), hat={"type": "turban", "col": "#f4f1ea", "jewel": "#2f6a4a"},
               age="old"),
    highlander("hadji_murad_ru", "Наиб Хаджи-Мурат", coat="#5a4434"),
    general_19("baryatinsky_a_ru", "Наместник Александр Барятинский", coat="#1e1e22", beard=("handlebar", "#8a5a34"),
               hair=("short", "#8a5a34"), cape={"type": "cape", "col": "#3b3a38"}),
    general_19("ermolov_ru", "Генерал Алексей Ермолов", coat="#2f6a4a", hair=("curly", "#8a8a8a"), bushy=True, age="old"),
    # ---------- Валуевский циркуляр
    victorian("valuev_ru", "Министр Пётр Валуев", coat="#1e1e22", hair=("receding", "#8a7a6a"), beard=("walrus", "#8a7a6a"),
              held=h("scroll")),
    victorian("kostomarov_ru", "Историк Николай Костомаров", coat="#3b3a38", hair=("receding", "#5a3a22"), beard=("goatee", "#5a3a22"),
              glasses={"type": "round", "col": "#3a2a20"}, held=h("book")),
    victorian("kulish_ru", "Писатель Пантелеймон Кулиш", coat="#5a4434", hair=("short", "#3b2a20"), beard=("full", "#3b2a20"),
              held=h("book")),
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
