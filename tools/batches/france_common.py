"""Общие помощники пачек расширения главы «Франция» (epoch revolution) — поверх движка пачек Польши (poland_1).

Реестр сюжетов: docs/countries/france_registry.md (согласован с GPT-5.5, docs/countries/france_gpt_review.md).
Глава уже в проде — гейт не нужен: новые уровни попадают в облако только публикацией.

PLAN — вся хронология главы: id → (order, акт). Существующие уровни перенумеровывает france_reorder.py,
новые пачки берут order/act отсюда же (level() ниже), чтобы порядок был один на всю главу.
"""
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, texts  # noqa: F401

P.LEVELS = P.rp("Content/revolution/levels")
P.CHAPTER = {"id": "revolution", "number": 5, "cover": "guillotine", "icon": "flame.fill", "free": False, "minAppVersion": "1.0"}

ACTS = [
    "Акт I · Легенды",
    "Акт II · Галлия и римское наследие",
    "Акт III · Франки и Каролинги",
    "Акт IV · Феодальная Франция и Капетинги",
    "Акт V · Валуа и Столетняя война",
    "Акт VI · Ренессанс и религиозный раскол",
    "Акт VII · Бурбоны: государство, вера, Атлантика",
    "Акт VIII · Революция",
    "Акт IX · Консульство и Империя",
    "Акт X · Реставрации, революции и Вторая империя",
    "Акт XI · Третья республика и Великая война",
]

# акт → уровни по хронологии; order = 10 × сквозной номер
_PLAN = [
    ["massalia_600bc", "melusine", "soissons_vase", "roland_778"],
    ["gergovia_52bc", "lyon_177"],
    ["syagrius_486", "clovis_496", "tours_732", "pepin_751", "charlemagne_800", "verdun_843"],
    ["rollo_911", "capet_987", "clermont_1095", "eleanor_1152", "gaillard_1204", "beziers_1209", "bouvines",
     "mansurah_1250", "anagni", "templars"],
    ["avignon_plague", "poitiers", "jacquerie_1358", "duguesclin", "joan_reims", "castillon_1453", "spider_king"],
    ["pavia", "villers_1539", "diane", "vassy_1562", "st_bartholomew", "blois", "paris_mass", "nantes_1598"],
    ["la_rochelle", "rocroi_1643", "fronde", "fouquet", "revocation_1685", "encyclopedie_1751", "paris_1763"],
    ["trianon", "necklace", "oath", "mirabeau", "bastille", "rights_1789", "varennes", "valmy", "king_trial",
     "antoinette", "girondins", "marat", "vendee", "jacobins", "danton", "thermidor"],
    ["toulon", "arcole", "egypt", "brumaire", "concordat", "haiti_1804", "civil_code_1804", "sacre", "empress",
     "austerlitz", "jena", "tilsit", "moscow", "marie_louise", "leipzig", "fontainebleau", "vienna_congress",
     "elba", "waterloo", "st_helena"],
    ["july_1830", "algeria_1830", "february_1848", "schoelcher_1848", "coup_1851", "haussmann_1853", "sedan_1870"],
    ["commune_1871", "ferry_1882", "tonkin_1885", "dreyfus_1898", "laicite_1905", "marne_1914", "verdun_1916",
     "mutinies_1917", "compiegne_1918"],
]
PLAN = {}
for _a, _ids in enumerate(_PLAN):
    for _id in _ids:
        assert _id not in PLAN, _id
        PLAN[_id] = (10 * (len(PLAN) + 1), ACTS[_a])

CHAPTER_TEXTS = {
    "chapter.revolution.subtitle": "От легенд до 1918 года",
    **{f"act.revolution.{i}": a for i, a in enumerate(ACTS, 1)},
}

# своей музыки у Франции нет — общие темы (как у существующих 49 уровней)
MUSIC = {"t": "tension", "b": "tension", "c": "theme", "r": "theme"}


def level(id, mood, cover, panels, scenes, chars, flags, rels, goal, solution, accuracy):
    order, act = PLAN[id]
    d = P.level(id, order, act, MUSIC[mood], cover, panels, scenes, chars, flags, rels, goal, solution, accuracy)
    d["epoch"] = "revolution"
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
