"""Общие помощники пачек главы «США» (epoch usa) — поверх движка пачек Польши (poland_1).

Реестр сюжетов: docs/countries/usa_registry.md (согласован с GPT-5.5). Принципы формулировок острых тем —
docs/countries/usa_gpt_review.md, раздел 5.

Пока глава в работе, у неё minAppVersion "99.0": даже случайная публикация в прод её не покажет.
Для теста на телефоне со стендом временно ставь "1.0" (или публикуй стенд с правкой chapters.json).
"""
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, texts  # noqa: F401

P.LEVELS = P.rp("Content/usa/levels")
P.CHAPTER = {"id": "usa", "number": 8, "cover": "boston_tea_us", "icon": "star.fill", "free": False,
             "minAppVersion": "99.0"}

ACT1 = "Акт I · Легенды"
ACT2 = "Акт II · До США: колонии"
ACT3 = "Акт III · Революция"
ACT4 = "Акт IV · Молодая республика"
ACT5 = "Акт V · Реформы и экспансия"
ACT6 = "Акт VI · Раскол и Реконструкция"
ACT7 = "Акт VII · Позолоченный век"
ACT8 = "Акт VIII · Прогрессивная эра"

CHAPTER_TEXTS = {
    "chapter.usa.title": "США",
    "chapter.usa.subtitle": "От колоний до 1918 года",
    "map.usa": "США",
    **{f"act.usa.{i}": a for i, a in enumerate([ACT1, ACT2, ACT3, ACT4, ACT5, ACT6, ACT7, ACT8], 1)},
}

MUSIC = {"t": "usa_tension", "b": "usa_battle", "c": "usa_ceremony", "r": "usa_romance"}


def level(id, order, act, mood, cover, panels, scenes, chars, flags, rels, goal, solution, accuracy):
    d = P.level(id, order, act, MUSIC[mood], cover, panels, scenes, chars, flags, rels, goal, solution, accuracy)
    d["epoch"] = "usa"
    return d


def bait(id, name, tag, slots, donor, roles):
    icon = {"v_battle": "icon_dead", "v_kill": "icon_dead", "v_flee": "icon_ally", "v_prepare": "icon_ally"}.get(tag, "icon_ally")
    act = {"v_battle": "битва", "v_parley": "переговоры", "v_bribe": "подкуп", "v_wed": "свадьба",
           "v_flee": "уход", "v_prepare": "подготовка", "v_kill": "убийство"}[tag]
    emoji = {"v_battle": "⚔️", "v_parley": "🤝", "v_bribe": "💰", "v_wed": "💍", "v_flee": "🚪", "v_prepare": "🛡️", "v_kill": "🗡️"}[tag]
    return scene(id, name, [tag], slots, emoji, act, icon, roles, donor)


PARLEY = ["кто требует", "кто уступает"]
BATTLE = ["нападающий", "защитник"]


def run(chars, scenes, rules, levels, txt):
    P.NEW_CHARS, P.NEW_SCENES, P.NEW_RULES, P.NEW_LEVELS, P.TEXTS = chars, scenes, rules, levels, txt
    P.CHAPTER_TEXTS = CHAPTER_TEXTS
    P.main()
