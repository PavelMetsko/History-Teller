#!/usr/bin/env python3
"""Рецепты фабрики для персонажей пачки 4 главы «Россия» (1867–1918).

    python3 tools/batches/russia_recipes_4.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/russia_recipes_4.py --ids      только список id (для factory/build.py)
    python3 tools/batches/russia_recipes_4.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, victorian, edwardian, worker, ROOT, OUT

RU_GREEN, KHAKI, OTTOMAN_BLUE, FEZ = "#2f4a3a", "#7a7a4a", "#2f3f6a", "#a8312f"


def ru_general(id, name, coat=RU_GREEN, cap="#f4f1ea", **kw):
    """Русский генерал второй половины XIX века: тёмно-зелёный мундир, белая фуражка."""
    d = dict(hair=("short", "#8a7a6a"), hat={"type": "cap", "col": cap, "fur": ""},
             outfit={"type": "uniform", "col": coat, "facing": "#a8312f", "trim": "#d4a63c", "sash": "", "epaulettes": True},
             sleeves=sl(coat), legs=tr("#1e1e22"), boots=tall(), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


def khaki(id, name, **kw):
    """Русский генерал Первой мировой: защитный китель, фуражка."""
    d = dict(hair=("short", "#b8b4c0"), hat={"type": "cap", "col": KHAKI, "fur": ""},
             outfit={"type": "legion_tunic", "col": KHAKI, "belt": "#5a3a22", "button": "#d4a63c"},
             sleeves=sl(KHAKI), legs=tr(KHAKI), boots=tall("#3b2a20"))
    d.update(kw)
    return R(id, name, **d)


def ottoman(id, name, **kw):
    """Османский паша: тёмно-синий мундир, красная феска."""
    d = dict(skin="olive", hair=("short", "#2a1a12"), hat={"type": "cap", "col": FEZ, "fur": ""},
             outfit={"type": "uniform", "col": OTTOMAN_BLUE, "facing": FEZ, "trim": "#d4a63c", "sash": "", "epaulettes": True},
             sleeves=sl(OTTOMAN_BLUE), legs=tr(OTTOMAN_BLUE), boots=tall(), held=h("sword"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Аляска
    ru_general("konstantin_nik_ru", "Великий князь Константин Николаевич", coat="#1e2a44", cap="#1e2a44",
               hair=("receding", "#8a5a34"), beard=("full", "#8a5a34"), held=h("scroll")),
    victorian("stoeckl_ru", "Посланник Эдуард Стекль", hair=("receding", "#3b2a20"), beard=("walrus", "#3b2a20"), held=h("scroll")),
    victorian("seward_ru", "Госсекретарь Уильям Сьюард", hair=("curly", "#b8b4c0"), age="old", held=h("book")),
    # ---------- Шипка
    ru_general("stoletov_ru", "Генерал Николай Столетов", hair=("short", "#3b2a20"), beard=("full", "#3b2a20")),
    R("opalchentsi_ru", "Болгарские ополченцы", hair=("short", "#2a1a12"), beard=("handlebar", "#2a1a12"),
      hat={"type": "cap", "col": "#3b2a20", "fur": "#3b2a20"},
      outfit={"type": "coat", "col": "#2f3a2a", "trim": "#a8312f", "belt": "#5a3a22"}, sleeves=sl("#2f3a2a"),
      legs=tr("#2f3a2a"), boots=bo("#3b2a20"), held=h("flag")),
    ottoman("suleiman_ru", "Сулейман-паша", beard=("full", "#2a1a12")),
    ottoman("osman_pasha_ru", "Осман-паша", hair=("short", "#8a7a6a"), beard=("full", "#8a7a6a"), age="old"),
    ru_general("radetzky_ru", "Генерал Фёдор Радецкий", hair=("receding", "#d8d4dc"), beard=("walrus", "#d8d4dc"), age="old"),
    # ---------- Геок-Тепе
    ru_general("skobelev_ru", "Генерал Михаил Скобелев", coat="#f4f1ea", hair=("short", "#b9672e"), beard=("full", "#b9672e")),
    R("tykma_ru", "Тыкма-сердар", skin="tan", hair=("short", "#1e1a18"), beard=("full", "#1e1a18"),
      hat={"type": "cap", "col": "#f4f1ea", "fur": "#e6e0d6"},
      outfit={"type": "robe", "col": "#a8312f", "rope": "#d4a63c"}, sleeves=sl("#a8312f"), held=h("sword")),
    ru_general("grodekov_ru", "Полковник Николай Гродеков", hair=("short", "#5a3a22"), beard=("goatee", "#5a3a22"), held=h("scroll")),
    # ---------- погромы
    victorian("ignatyev_ru", "Министр Николай Игнатьев", hair=("receding", "#8a7a6a"), beard=("walrus", "#8a7a6a"), held=h("scroll")),
    victorian("pinsker_ru", "Доктор Лев Пинскер", hair=("receding", "#b8b4c0"), beard=("full", "#b8b4c0"), age="old",
              glasses={"type": "round", "col": "#3a2a20"}, held=h("book")),
    # ---------- Ходынка
    ru_general("sergei_ru", "Великий князь Сергей Александрович", coat="#1e2a44", cap="#1e2a44",
               hair=("short", "#8a5a34"), beard=("goatee", "#8a5a34")),
    worker("gilyarovsky_ru", "Репортёр Владимир Гиляровский", shirt="#f4f1ea", pants="#3b3a38", hair=("short", "#8a7a6a"),
           beard=("walrus", "#8a7a6a"), bushy=True, hat={"type": "cap", "col": "#3b3a38", "fur": ""}, held=h("book")),
    # ---------- 1905
    R("gapon_ru", "Священник Георгий Гапон", hair=("long", "#2a1a12"), beard=("full", "#2a1a12"),
      outfit={"type": "robe", "col": "#1e1e22", "rope": "#1e1e22"}, sleeves=sl("#1e1e22"), held=h("cross")),
    ru_general("trepov_ru", "Генерал Дмитрий Трепов", hair=("receding", "#8a7a6a"), beard=("walrus", "#8a7a6a")),
    # ---------- Дума
    edwardian("stolypin_ru", "Пётр Столыпин", coat="#1e1e22", hair=("receding", "#3b2a20"), beard=("full", "#3b2a20")),
    edwardian("milyukov_ru", "Павел Милюков", coat="#2a2a2e", hair=("short", "#d8d4dc"), beard=("walrus", "#d8d4dc"),
              glasses={"type": "pince", "col": "#3a2a20"}, held=h("book")),
    worker("khutor_peasant_ru", "Хуторянин", shirt="#e9e0cc", pants="#3b4a6a", hair=("bowl", "#8a5a34"), beard=("full", "#8a5a34"),
           held=h("scythe")),
    # ---------- 1914
    edwardian("sazonov_ru", "Министр Сергей Сазонов", coat="#1e1e22", hair=("receding", "#5a3a22"), beard=("goatee", "#5a3a22")),
    khaki("brusilov_ru", "Генерал Алексей Брусилов", beard=("walrus", "#d8d4dc"), held=h("sword")),
    # ---------- 1917–1918
    worker("lenin_ru", "Владимир Ленин", shirt="#2a2a2e", pants="#2a2a2e", hair=("receding", "#8a5a34"), beard=("goatee", "#8a5a34"),
           hat={"type": "cap", "col": "#2a2a2e", "fur": ""}),
    edwardian("trotsky_ru", "Лев Троцкий", coat="#2a2a2e", hair=("curly", "#1e1a18"), beard=("goatee", "#1e1a18"),
              glasses={"type": "pince", "col": "#3a2a20"}),
    khaki("kerensky_ru", "Министр-председатель Александр Керенский", hat={"type": "none"}, hair=("short", "#3b2a20")),
    edwardian("kamenev_ru", "Лев Каменев", coat="#3b3a38", hair=("receding", "#8a5a34"), beard=("full", "#8a5a34"),
              glasses={"type": "pince", "col": "#3a2a20"}, held=h("book")),
    edwardian("chernov_ru", "Виктор Чернов", coat="#3b3a38", hair=("curly", "#8a7a6a"), beard=("full", "#8a7a6a")),
    R("hoffmann_ru", "Генерал Макс Гофман", hair=("receding", "#d8b070"), glasses={"type": "round", "col": "#3a2a20"},
      hat={"type": "cap", "col": "#6e7468", "fur": ""},
      outfit={"type": "legion_tunic", "col": "#6e7468", "belt": "#3b2a20", "button": "#d4a63c"}, sleeves=sl("#6e7468"),
      legs=tr("#6e7468"), boots=tall()),
    R("yurovsky_ru", "Комендант Яков Юровский", hair=("curly", "#1e1a18"), beard=("goatee", "#1e1a18"),
      outfit={"type": "coat", "col": "#1e1e22", "trim": "#1e1e22", "belt": "#3b2a20"}, sleeves=sl("#1e1e22"),
      legs=tr("#1e1e22"), boots=tall()),
    edwardian("sverdlov_ru", "Яков Свердлов", coat="#1e1e22", hair=("curly", "#1e1a18"), beard=("goatee", "#1e1a18"),
              glasses={"type": "pince", "col": "#3a2a20"}, held=h("scroll")),
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
