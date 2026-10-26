"""Общие помощники пачек расширения главы «Италия» (epoch borgia) — поверх движка пачек Польши (poland_1).

Реестр сюжетов: docs/countries/italy_registry.md (согласован с GPT-5.5, docs/countries/italy_gpt_review.md).
Глава уже в проде — гейт не нужен: новые уровни попадают в облако только публикацией.

PLAN — вся хронология главы: id → (order, акт). Существующие уровни перенумеровывает italy_reorder.py,
новые пачки берут order/act отсюда же (level() ниже), чтобы порядок был один на всю главу.
"""
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, texts  # noqa: F401

P.LEVELS = P.rp("Content/borgia/levels")
P.CHAPTER = {"id": "borgia", "number": 7, "cover": "curia", "icon": "flame.fill", "free": False, "minAppVersion": "1.0"}

ACTS = [
    "Акт I · Легенды",
    "Акт II · После Империи: короли Италии",
    "Акт III · Папы, императоры и коммуны",
    "Акт IV · Купцы, города и кризисы",
    "Акт V · Равновесие Ренессанса",
    "Акт VI · Борджиа и Итальянские войны",
    "Акт VII · Высокое Возрождение",
    "Акт VIII · Контрреформация и барокко",
    "Акт IX · Савойя, Бурбоны и Просвещение",
    "Акт X · Революции, Наполеон и Реставрация",
    "Акт XI · Рисорджименто",
    "Акт XII · Либеральная Италия и Великая война",
]

# акт → уровни по хронологии; order = 10 × сквозной номер
_PLAN = [
    ["galgano", "colapesce", "pontida", "loreto"],
    ["odoacer_476", "theodoric_493", "lombards_568", "pavia_774", "sicily_827"],
    ["otto_962", "melfi_1059", "canossa_1077", "roger_1130", "legnano_1176", "francis", "francis_sultan", "frederick2"],
    ["marco_polo", "vespers", "bordeaux_duel", "meloria_1284", "dante", "cola", "black_death", "cola_death",
     "ciompi_1378", "chioggia_1380"],
    ["cosimo", "lodi_1454", "pazzi", "lorenzo_naples", "lorenzo_deathbed", "leonardo"],
    ["conclave", "nepotism", "giulia", "charles8_1494", "juan", "fratricide", "excommunicate", "bonfire", "lucrezia",
     "prince", "imola_1502", "senigallia", "poison", "poison_death", "julius", "downfall"],
    ["michelangelo_flight", "sistine", "machiavelli", "ghetto_1516", "sack_rome", "florence_1530", "castel_escape"],
    ["trent_1563", "lepanto", "cenci", "bruno", "bellarmine_1616", "plague_1630", "galileo", "masaniello"],
    ["turin_1706", "sardinia_1720", "naples_1734", "casanova", "beccaria_1764"],
    ["venice_1797", "parthenopean_1799", "kingdom_1805", "vienna_1815", "carbonari_1820", "young_italy_1831"],
    ["statuto_1848", "five_days_1848", "roman_republic_1849", "cavour", "verdi", "garibaldi", "brigands_1861",
     "aspromonte", "venice_1866", "porta_pia", "guarantees_1871"],
    ["dogali_1887", "fasci_1893", "adwa_1896", "bava_1898", "emigration_1901", "libya_1911", "intervention_1915",
     "caporetto_1917", "vittorio_1918"],
]
PLAN = {}
for _a, _ids in enumerate(_PLAN):
    for _id in _ids:
        assert _id not in PLAN, _id
        PLAN[_id] = (10 * (len(PLAN) + 1), ACTS[_a])

CHAPTER_TEXTS = {
    "chapter.borgia.subtitle": "От легенд до 1918 года",
    **{f"act.borgia.{i}": a for i, a in enumerate(ACTS, 1)},
}

# своей музыки у Италии нет — общие темы (как у существующих 47 уровней)
MUSIC = {"t": "tension", "b": "tension", "c": "theme", "r": "theme"}


def level(id, mood, cover, panels, scenes, chars, flags, rels, goal, solution, accuracy):
    order, act = PLAN[id]
    d = P.level(id, order, act, MUSIC[mood], cover, panels, scenes, chars, flags, rels, goal, solution, accuracy)
    d["epoch"] = "borgia"
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
