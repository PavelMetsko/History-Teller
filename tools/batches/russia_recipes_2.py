#!/usr/bin/env python3
"""Рецепты фабрики для новых персонажей пачки 2 главы «Россия» (удельная Русь, Орда, Новгород, Москва).

    python3 tools/batches/russia_recipes_2.py            записать рецепты (перезаписывает свои id)
    python3 tools/batches/russia_recipes_2.py --ids      только список id (для factory/build.py)
    python3 tools/batches/russia_recipes_2.py --missing  ещё не отрисованные
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_recipes import R, sl, tr, bo, tall, h, BARE, ROOT, OUT  # noqa: F401
from england_recipes_2 import knight, noble, cleric, lady

NASAL = {"type": "nasal", "col": "#a9b0b8", "trim": "#8a6a2a"}
HELM = {"type": "helmet", "col": "#b9bfc6", "trim": "#d4a63c"}


def kolpak(top="#a8312f", fur="#6b4a2a"):
    return {"type": "kolpak", "fur": fur, "top": top}


def prince(id, name, col="#a8312f", top=None, beard=("full", "#5a3a22"), hair=("short", "#5a3a22"), **kw):
    """Русский князь: кафтан с поясом, шапка с меховой опушкой, плащ-корзно."""
    d = dict(hair=hair, beard=beard, hat=kolpak(top or col), outfit={"type": "coat", "col": col, "trim": "#d4a63c", "belt": "#6b4426"},
             sleeves=sl(col), legs=tr("#3b2a20"), boots=bo("#7a3a22"), cape={"type": "cape", "col": "#2f4a7a"})
    d.update(kw)
    return R(id, name, **d)


def druzhina(id, name, surcoat="#a8312f", **kw):
    """Князь-воин в кольчуге и шеломе."""
    d = dict(beard=("full", "#5a3a22"), helm=HELM, cape={"type": "cape", "col": "#a8312f"})
    d.update(kw)
    return knight(id, name, surcoat=surcoat, **d)


def steppe(id, name, col="#7a5232", top="#a8312f", skin="tan", **kw):
    """Степняк — половец или ордынец: кафтан с мехом, монгольская шапка."""
    d = dict(skin=skin, hair=("long", "#1e1a18"), beard=("handlebar", "#1e1a18"), hat={"type": "mongol", "fur": "#6b4a2a", "top": top},
             outfit={"type": "fur_tunic", "col": col, "fur": "#c9b08a", "rope": "#3b2a20"}, sleeves=sl(col),
             legs=tr("#3b2a20"), boots=bo("#3b2a20"))
    d.update(kw)
    return R(id, name, **d)


def khan(id, name, robe="#a8312f", **kw):
    """Хан / царевич: длинный халат, шапка с мехом."""
    d = dict(skin="tan", hair=("long", "#1e1a18"), beard=("goatee", "#1e1a18"), hat={"type": "mongol", "fur": "#8a6a4a", "top": "#d8ad3c"},
             outfit={"type": "emperor", "col": robe, "gold": "#d8ad3c", "mantle": "#2f6a4a"}, sleeves=sl(robe), held=h("bulawa"))
    d.update(kw)
    return R(id, name, **d)


def monk(id, name, col="#2a2a2e", **kw):
    """Православный монах: чёрная ряса, клобук-капюшон, длинная борода."""
    d = dict(age="old", hair=("long", "#b8b4c0"), beard=("long", "#d8d4dc"), hat={"type": "hood", "col": col},
             outfit={"type": "robe", "col": col, "rope": "#5a4434"}, sleeves=sl(col), held=h("cross"))
    d.update(kw)
    return R(id, name, **d)


def townsman(id, name, shirt="#f4f1ea", **kw):
    d = dict(hair=("bowl", "#8a5a34"), beard=("full", "#8a5a34"),
             outfit={"type": "sukmana", "col": shirt, "trim": "#a8312f", "belt": "#a8312f"}, sleeves=sl(shirt),
             legs=tr("#5a4434"), boots=bo("#7a5232"))
    d.update(kw)
    return R(id, name, **d)


RECIPES = [
    # ---------- Игорь
    druzhina("igor_sev_ru", "Князь Игорь Святославич", surcoat="#a8312f", beard=("full", "#3b2a20"), held=h("sword")),
    druzhina("vsevolod_ru", "Буй-тур Всеволод", surcoat="#2f4a7a", beard=("full", "#8a5a34"), bushy=True, held=h("bulawa")),
    steppe("konchak_ru", "Хан Кончак", col="#a8794e", top="#2f6a4a", age="old", beard=("long", "#5a5a5a"), held=h("bulawa")),
    lady("yaroslavna_ru", "Ефросинья Ярославна", dress="#f4f1ea", mantle="#2f4a7a", hair_col="#8a5a34"),
    steppe("ovlur_ru", "Половчанин Овлур", col="#7a6a52", top="#7a5232", beard=None, held=h("spear")),
    # ---------- Калка
    druzhina("mstislav_udatny_ru", "Мстислав Удатный", surcoat="#2f6a4a", beard=("full", "#a8562a"), bushy=True),
    prince("mstislav_kiev_ru", "Мстислав Романович Киевский", col="#5a2a6b", age="old", beard=("long", "#b8b4c0"), hair=("short", "#b8b4c0")),
    steppe("kotyan_ru", "Хан Котян", col="#5a4434", top="#a8312f", age="old", beard=("walrus", "#8a8a8a")),
    steppe("subutai_ru", "Субэдэй", col="#3b3a38", top="#3b3a38", skin="olive", beard=("goatee", "#1e1a18"), held=h("sword")),
    townsman("ploskinya_ru", "Бродник Плоскиня", shirt="#7a6a52", hair=("long", "#3b2a20"), beard=("full", "#3b2a20"), held=h("cross")),
    # ---------- Киев 1240
    khan("batu_ru", "Хан Батый", robe="#a8312f"),
    druzhina("dmitr_ru", "Тысяцкий Дмитр", surcoat="#7a3a22", beard=("full", "#5a3a22"), held=h("spear")),
    prince("daniil_ru", "Князь Даниил Романович", col="#2f4a7a", top="#a8312f", beard=("goatee", "#3b2a20")),
    prince("mikhail_chern_ru", "Михаил Черниговский", col="#5a6b4a", age="old", beard=("long", "#8a7a6a")),
    # ---------- Невский
    druzhina("alexander_nevsky_ru", "Князь Александр Невский", surcoat="#a8312f", beard=("goatee", "#8a5a34"), hair=("shoulder", "#8a5a34"),
             cape={"type": "cape", "col": "#2f4a7a"}),
    druzhina("andrey_yaroslavich_ru", "Князь Андрей Ярославич", surcoat="#2f6a4a", beard=("goatee", "#5a3a22")),
    cleric("hermann_dorpat_ru", "Епископ Герман Дерптский", col="#f1ece2"),
    knight("order_knights_ru", "Рыцари Ордена и дерптцы", surcoat="#f4f1ea", helm={"type": "helmet", "col": "#c6cbd1", "trim": "#1e1e22"},
           cape={"type": "cape", "col": "#f4f1ea"}),
    khan("sartak_ru", "Царевич Сартак", robe="#2f4a7a", beard=("handlebar", "#1e1a18")),
    steppe("nevryuy_ru", "Темник Неврюй", col="#5a2a2a", top="#5a2a2a", held=h("sword")),
    # ---------- Тверь
    prince("alexander_tver_ru", "Князь Александр Тверской", col="#2f6a4a", top="#a8312f", beard=("full", "#8a5a34")),
    prince("ivan_kalita_ru", "Иван Калита", col="#7a5232", top="#5a2a6b", beard=("long", "#5a3a22"), held=h("scroll")),
    steppe("cholkhan_ru", "Чол-хан (Щелкан)", col="#a8312f", top="#d8ad3c", held=h("bulawa")),
    khan("uzbek_ru", "Хан Узбек", robe="#2f6a4a", hat={"type": "turban", "col": "#f4f1ea", "jewel": "#2f9a8a"}),
    townsman("tverites_ru", "Тверичи", shirt="#f4f1ea", held=h("pickaxe")),
    # ---------- Куликово, Тохтамыш
    druzhina("dmitry_donskoy_ru", "Князь Дмитрий Иванович", surcoat="#a8312f", beard=("full", "#2a1a12"), hair=("short", "#2a1a12"),
             cape={"type": "cape", "col": "#d8ad3c"}),
    steppe("mamai_ru", "Беклярибек Мамай", col="#3b3a38", top="#a8312f", age="old", beard=("handlebar", "#5a5a5a"), held=h("bulawa"),
           cape={"type": "cape", "col": "#a8312f"}),
    druzhina("vladimir_serpukhov_ru", "Владимир Серпуховской", surcoat="#2f6a4a", beard=("goatee", "#8a5a34")),
    monk("sergius_ru", "Сергий Радонежский"),
    khan("tokhtamysh_ru", "Хан Тохтамыш", robe="#5a2a6b"),
    prince("oleg_ryazan_ru", "Олег Рязанский", col="#5a4434", top="#2f4a7a", beard=("full", "#5a3a22")),
    knight("ostey_ru", "Литовский князь Остей", surcoat="#2f4a7a", helm=HELM, beard=("goatee", "#d8b070"), hair=("short", "#d8b070")),
    # ---------- Тёмная война, митрополия
    prince("vasily2_ru", "Великий князь Василий II", col="#5a2a6b", top="#a8312f", beard=("full", "#3b2a20")),
    prince("vasily_kosoy_ru", "Василий Косой", col="#2f4a7a", top="#2f4a7a", beard=("goatee", "#3b2a20")),
    druzhina("shemyaka_ru", "Дмитрий Шемяка", surcoat="#3b3a38", beard=("full", "#2a1a12"), bushy=True),
    lady("sofia_vitovtovna_ru", "Софья Витовтовна", dress="#a8312f", mantle="#5a2a6b", hair_col="#8a7a6a", age="old",
         hat={"type": "veil", "col": "#f4f1ea", "band": "#d8ad3c"}),
    cleric("iona_ru", "Епископ Иона", col="#2a2a2e", beard=("long", "#d8d4dc")),
    cleric("isidore_ru", "Митрополит Исидор", col="#a8312f", beard=("long", "#8a7a6a"), skin="olive"),
    # ---------- Новгород, Угра
    prince("ivan3_ru", "Великий князь Иван III", col="#a8312f", top="#d8ad3c", beard=("long", "#5a3a22"), hair=("shoulder", "#5a3a22"),
           cape={"type": "cape", "col": "#d8ad3c"}),
    lady("marfa_boretskaya_ru", "Марфа Борецкая", dress="#2a2a2e", mantle="#5a2a2a", hair_col="#8a7a6a", age="old",
         hat={"type": "veil", "col": "#f4f1ea", "band": ""}),
    cleric("feofil_ru", "Архиепископ Феофил", col="#f1ece2", beard=("long", "#b8b4c0")),
    prince("mikhail_olelkovich_ru", "Князь Михаил Олелькович", col="#2f4a7a", top="#2f6a4a", beard=("goatee", "#8a5a34")),
    khan("akhmat_ru", "Хан Ахмат", robe="#3b3a38", beard=("handlebar", "#5a5a5a"), age="old"),
    druzhina("ivan_molodoy_ru", "Иван Молодой", surcoat="#2f4a7a", beard=None, hair=("shoulder", "#8a5a34")),
    lady("sophia_paleolog_ru", "Софья Палеолог", dress="#5a2a6b", mantle="#d8ad3c", hair_col="#2a1a12",
         hat={"type": "crown", "gold": "#d8ad3c"}),
    khan("mengli_giray_ru", "Хан Менгли-Гирей", robe="#2f6a4a", hat={"type": "turban", "col": "#f4f1ea", "jewel": "#a8312f"}),
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
