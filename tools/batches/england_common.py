"""Общие помощники пачек расширения главы «Англия» (epoch tudor) — поверх движка пачек Польши (poland_1).

Реестр сюжетов: docs/countries/england_registry.md (согласован с GPT-5.5, docs/countries/england_gpt_review.md).
Глава уже в проде — гейт не нужен: новые уровни попадают в облако только публикацией.

PLAN — вся хронология главы: id → (order, акт). Существующие уровни перенумеровывает england_reorder.py,
новые пачки берут order/act отсюда же (level() ниже), чтобы порядок был один на всю главу.
"""
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, texts  # noqa: F401

P.LEVELS = P.rp("Content/tudor/levels")
P.CHAPTER = {"id": "tudor", "number": 3, "cover": "tower", "icon": "crown.fill", "free": False, "minAppVersion": "1.0"}

ACTS = [
    "Акт I · Легенды",
    "Акт II · Римляне, саксы и викинги",
    "Акт III · Нормандцы и Плантагенеты",
    "Акт IV · Ланкастеры и Йорки",
    "Акт V · Восхождение Тюдоров",
    "Акт VI · Шесть жён",
    "Акт VII · Наследники Генриха",
    "Акт VIII · Стюарты и революция",
    "Акт IX · Великобритания",
    "Акт X · Век реформ и империи",
    "Акт XI · Война и голоса",
]

# акт → уровни по хронологии; order = 10 × сквозной номер
_PLAN = [
    ["arthur_sword", "godiva", "robin_hood", "whittington"],
    ["claudius_43", "boudica_60", "augustine_597", "edington_878", "cnut_1016", "witan_1066"],
    ["hastings", "domesday_1086", "matilda_1142", "becket", "lionheart", "magna_carta", "montfort_1265",
     "llywelyn_1282", "wallace", "bannockburn_1314", "isabella", "crecy", "black_death_1348", "wat_tyler", "wycliffe_1382"],
    ["bolingbroke", "hotspur", "agincourt", "joan_stake", "henry6", "kingmaker", "princes"],
    ["bosworth", "union", "simnel", "stanley_fall"],
    ["aragon_divorce", "wolsey", "anne_boleyn", "thomas_more", "jane_seymour", "pilgrimage", "anne_cleves",
     "cromwell_fall", "howard", "parr"],
    ["jane_grey", "wyatt", "elizabeth_tower", "bloody_mary", "cranmer_hand", "elizabeth", "dudley_courtship",
     "drake_knight", "babington", "mary_stuart", "armada", "globe", "essex"],
    ["gunpowder", "raleigh", "felton_1628", "strafford", "naseby_1645", "putney_1647", "charles_execution",
     "drogheda_1649", "restoration", "great_fire", "titus_oates", "monmouth", "principia_1687", "glorious", "blenheim"],
    ["union_1707", "south_sea", "culloden", "plassey", "quebec", "cromford_1771", "cook", "yorktown", "zong_1781",
     "wilberforce", "united_irishmen_1798", "trafalgar", "luddites_1812", "waterloo_1815"],
    ["peterloo_1819", "reform_act", "victoria_albert", "famine_1845", "chartists_1848", "light_brigade", "india_1857",
     "darwin_1859", "livingstone", "suez", "home_rule_1886", "boer_1900"],
    ["davison_1913", "lamps_1914", "easter_1916", "somme_1916", "two_bells_1918"],
]
PLAN = {}
for _a, _ids in enumerate(_PLAN):
    for _id in _ids:
        assert _id not in PLAN, _id
        PLAN[_id] = (10 * (len(PLAN) + 1), ACTS[_a])

CHAPTER_TEXTS = {
    "chapter.tudor.subtitle": "От легенд до 1918 года",
    **{f"act.tudor.{i}": a for i, a in enumerate(ACTS, 1)},
}

# своя музыка главы (ElevenLabs, tools/gen_audio_11labs.py): england_{tension,battle,ceremony,romance}
MUSIC = {"t": "england_tension", "b": "england_battle", "c": "england_ceremony", "r": "england_romance"}


def level(id, mood, cover, panels, scenes, chars, flags, rels, goal, solution, accuracy):
    order, act = PLAN[id]
    d = P.level(id, order, act, MUSIC[mood], cover, panels, scenes, chars, flags, rels, goal, solution, accuracy)
    d["epoch"] = "tudor"
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
