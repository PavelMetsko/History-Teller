"""Общие помощники пачек расширения главы «Россия» (epoch empire) — поверх движка пачек Польши (poland_1).

Реестр сюжетов: docs/countries/russia_registry.md (согласован с GPT-5.5, docs/countries/russia_gpt_review.md).
Глава уже в проде — гейт не нужен: новые уровни попадают в облако только публикацией.

PLAN — вся хронология главы: id → (order, акт). Существующие уровни перенумеровывает russia_reorder.py,
новые пачки берут order/act отсюда же (level() ниже), чтобы порядок был один на всю главу.
"""
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, texts  # noqa: F401

P.LEVELS = P.rp("Content/empire/levels")
P.CHAPTER = {"id": "empire", "number": 6, "cover": "sobor", "icon": "seal.fill", "free": False, "minAppVersion": "1.0"}

ACTS = [
    "Акт I · Легенды и былины",
    "Акт II · Ранняя Русь",
    "Акт III · Удельная Русь и степь",
    "Акт IV · Орда, Новгород и Москва",
    "Акт V · Иван Грозный",
    "Акт VI · Смута",
    "Акт VII · XVII век: закон, раскол, казаки",
    "Акт VIII · Пётр Великий",
    "Акт IX · Перевороты и Екатерина",
    "Акт X · От Павла до Николая I",
    "Акт XI · Реформы, общество и окраины",
    "Акт XII · Закат империи и революции",
]

# акт → уровни по хронологии; order = 10 × сквозной номер
_PLAN = [
    ["rurik_862", "oleg_horse", "ilya_muromets", "sadko"],
    ["kyiv_882", "olga_945", "svyatoslav_965", "baptism_988", "yaroslav_1015"],
    ["lyubech_1097", "kyiv_sack_1169", "igor_1185", "kalka_1223", "batu_1240"],
    ["ice_1242", "yarlyk_1252", "tver_1327", "kulikovo_1380", "tokhtamysh_1382", "dark_war_1446", "metropolitan_1448",
     "novgorod_1478", "ugra_1480", "elena_1535"],
    ["coronation", "sudebnik", "kazan", "sloboda", "oprichnina", "philip", "wrath", "ermak"],
    ["godunov", "false_dmitry", "shuisky_tsar", "bolotnikov", "tushino", "militia", "romanov", "deulino"],
    ["salt_riot_1648", "pereyaslav_1654", "raskol_1666", "razin_1670", "khovanshchina_1682", "nerchinsk_1689"],
    ["embassy", "streltsy", "narva", "petersburg", "poltava", "alexei", "emperor", "tabel"],
    ["menshikov", "menshikov_fall", "lomonosov", "biron", "elizabeth_coup", "coup", "reform", "pugachev", "execution",
     "sech_1775", "potemkin", "crimea", "izmail"],
    ["alps", "paul_murder", "georgia_1801", "speransky", "fili", "poselenia", "decembrists", "censor", "pushkin"],
    ["sevastopol", "shamil_1859", "emancipation", "valuev_1863", "court_reform", "alaska_1867", "shipka_1877",
     "geok_tepe_1881", "narodnaya_volya", "pogroms_1882"],
    ["khodynka_1896", "witte", "revolution_1905", "duma_1906", "war_1914", "rasputin", "february", "october_1917",
     "brest_1918", "ekaterinburg_1918"],
]
PLAN = {}
for _a, _ids in enumerate(_PLAN):
    for _id in _ids:
        assert _id not in PLAN, _id
        PLAN[_id] = (10 * (len(PLAN) + 1), ACTS[_a])

CHAPTER_TEXTS = {
    "chapter.empire.subtitle": "От легенд до 1918 года",
    **{f"act.empire.{i}": a for i, a in enumerate(ACTS, 1)},
}

# своей музыки у России нет — общие темы (как у существующих 51 уровня)
MUSIC = {"t": "tension", "b": "tension", "c": "theme", "r": "theme"}


def level(id, mood, cover, panels, scenes, chars, flags, rels, goal, solution, accuracy):
    order, act = PLAN[id]
    d = P.level(id, order, act, MUSIC[mood], cover, panels, scenes, chars, flags, rels, goal, solution, accuracy)
    d["epoch"] = "empire"
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
