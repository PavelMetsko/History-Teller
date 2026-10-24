#!/usr/bin/env python3
"""Пачка 7 главы «Польша»: не только короли и битвы — общество, экономика, культура, религия.
14 уровней, каждый встаёт по году между существующими (order).

    python3 tools/batches/poland_7.py [repo_root]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, level, texts, ACT1, ACT2

ACT3 = "Акт III · Ягеллоны"
ACT4 = "Акт IV · Речь Посполитая"
ACT5 = "Акт V · Разделы"
ACT6 = "Акт VI · Без государства"

NEW_CHARS = [
    char("methodius", "Святой Мефодий", ["methodius_pl"], "✝️"),
    char("vistulan_prince", "Князь вислян", ["vistulan_pl"], "🛡️"),
    char("svatopluk", "Святополк Моравский", ["moravian_pl"], "⚔️"),
    char("henry2_hre", "Император Генрих II", ["emperor_h2_pl"], "👑"),
    char("archbishop_gn", "Архиепископ Гнезненский", ["archbishop_pl"], "⛪"),
    char("boleslaw5", "Болеслав Стыдливый", ["boleslaw5_pl"], "👑"),
    char("wojt_dytmar", "Войт Дитмар", ["wojt_pl"], "📜"),
    char("boleslaw_pious", "Болеслав Благочестивый", ["pious_pl"], "👑"),
    char("jewish_elder", "Старейшина общины", ["jew_elder_pl"], "📖"),
    char("skarbimierz", "Ректор Станислав из Скарбимежа", ["rector_pl"], "🎓"),
    char("alexander_jag", "Король Александр Ягеллон", ["alexander_pl"], "👑"),
    char("laski_chancellor", "Канцлер Ян Лаский", ["laski_pl"], "📜"),
    char("szlachcic_pl", "Шляхтич-помещик", ["szlachcic_pl"], "🌾"),
    char("peasant_pl", "Крестьянин", ["peasant_serf_pl"], "🌾"),
    char("flisak_pl", "Флисак", ["flisak_pl"], "🛶"),
    char("dutch_skipper", "Голландский шкипер", ["dutch_pl"], "⛵"),
    char("rej", "Николай Рей", ["rej_pl", "poet_pl"], "✒️"),
    char("kochanowski", "Ян Кохановский", ["kochanowski_pl", "poet_pl"], "✒️"),
    char("printer_pl", "Печатник Виетор", ["printer_pl"], "📚"),
    char("batory", "Стефан Баторий", ["batory_pl"], "👑"),
    char("skarga", "Пётр Скарга", ["skarga_pl"], "✝️"),
    char("wiszowaty", "Анджей Вишоватый", ["arian_pl"], "📖"),
    char("jesuit_pl", "Отец-иезуит", ["jesuit_pl"], "✝️"),
    char("poninski", "Адам Понинский", ["poninski_pl"], "💰"),
    char("mickiewicz", "Адам Мицкевич", ["mickiewicz_pl"], "✒️"),
    char("emigre_pl", "Эмигрант-повстанец", ["emigre_pl"], "🎖️"),
    char("poznanski", "Израиль Познанский", ["factory_pl"], "🏭"),
    char("weaver_pl", "Ткачиха", ["worker_pl"], "🧵"),
    char("dawidowa", "Ядвига Давидова", ["educator_pl"], "📚"),
    char("gendarme_ru", "Жандармский ротмистр", ["gendarme_pl"], "🚨"),
]
NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS = [], [], [], {}

def bait(id, name, tag, slots, donor, roles):
    icon = {"v_battle": "icon_dead", "v_kill": "icon_dead", "v_flee": "icon_ally", "v_prepare": "icon_ally"}.get(tag, "icon_ally")
    act = {"v_battle": "битва", "v_parley": "переговоры", "v_bribe": "подкуп", "v_wed": "свадьба",
           "v_flee": "уход", "v_prepare": "подготовка", "v_kill": "убийство"}[tag]
    emoji = {"v_battle": "⚔️", "v_parley": "🤝", "v_bribe": "💰", "v_wed": "💍", "v_flee": "🚪", "v_prepare": "🛡️", "v_kill": "🗡️"}[tag]
    return scene(id, name, [tag], slots, emoji, act, icon, roles, donor)

PARLEY = ["кто требует", "кто уступает"]

# ================================================================ vistulans_880 (ок. 880) — до Мешко
NEW_SCENES += [
    scene("methodius_warning_pl", "Предостережение Мефодия", ["sig_methodius_warning_pl"], 2, "✝️", "послать слово князю", "icon_ally",
          ["проповедник", "князь"], "cyril_sermon"),
    scene("vistulan_baptism_pl", "Крещение по своей воле", ["sig_vistulan_baptism_pl"], 2, "💧", "креститься на своей земле", "icon_crown",
          ["проповедник", "князь"], "baptism_966_pl"),
    scene("moravian_raid_pl", "Поход Святополка", ["sig_moravian_raid_pl"], 2, "⚔️", "идти войной на вислян", "icon_dead",
          ["нападающий", "князь"], "open_battle"),
    scene("captive_baptism_pl", "Крещение в плену", ["sig_captive_baptism_pl"], 2, "⛓️", "крестить пленника", "icon_plot",
          ["проповедник", "пленник"], "chapel"),
]
NEW_RULES += [
    rule("methodius_warning_pl_sig", "Мефодий передаёт князю вислян: «Крестись добровольно на своей земле, чтобы не крестили тебя пленником на чужой»",
         "sig_methodius_warning_pl",
         [actor("A", 0, tags=["methodius_pl"]), actor("B", 1, tags=["vistulan_pl"])],
         [setf("B", "warned_pl")]),
    rule("vistulan_baptism_pl_sig", "Предупреждённый князь крестится сам, в своей земле, — и остаётся князем",
         "sig_vistulan_baptism_pl",
         [actor("A", 0, tags=["methodius_pl"]), actor("B", 1, tags=["vistulan_pl"], flags=["warned_pl"], notFlags=["captive_pl"])],
         [setf("B", "baptized_free_pl")]),
    rule("moravian_raid_pl_sig", "Святополк Моравский идёт на некрещёного князя-язычника, берёт его в плен и уводит из его земли",
         "sig_moravian_raid_pl",
         [actor("A", 0, tags=["moravian_pl"]), actor("B", 1, tags=["vistulan_pl"], notFlags=["baptized_free_pl"])],
         [setf("B", "captive_pl"), setf("B", "defeated"), setf("A", "victor")]),
    rule("captive_baptism_pl_sig", "Пленного князя крестят на чужой земле — как и было предсказано",
         "sig_captive_baptism_pl",
         [actor("A", 0, tags=["methodius_pl"]), actor("B", 1, tags=["vistulan_pl"], flags=["captive_pl"])],
         [setf("B", "baptized_captive_pl")]),
]
NEW_LEVELS.append(level(
    "vistulans_880", 25, ACT2, "poland_tension", "methodius_warning_pl", 3,
    ["methodius_warning_pl", "vistulan_baptism_pl", "moravian_raid_pl", "captive_baptism_pl"],
    ["methodius", "vistulan_prince", "svatopluk"],
    {"vistulan_prince": ["standing", "reigns"], "svatopluk": ["standing", "strong"]}, [],
    [flag("vistulan_prince", "baptized_captive_pl"), flag("svatopluk", "victor")],
    [("methodius_warning_pl", ["methodius", "vistulan_prince"]), ("moravian_raid_pl", ["svatopluk", "vistulan_prince"]),
     ("captive_baptism_pl", ["methodius", "vistulan_prince"])],
    "simplification"))
TEXTS.update(texts("vistulans_880",
    "Князь вислян",
    "Мефодий предупреждает языческого князя на Висле — тот смеётся, и пророчество сбывается: креститься ему придётся пленником",
    "Совет был дан — но история пошла не по совету. Князь, крестившийся по своей воле, в плен бы не попал; а нам нужно, как было.",
    "Около 880 года. На верхней Висле, там, где потом встанет Краков, правит могучий языческий князь вислян. С юга растёт Великая Моравия князя Святополка, а в ней проповедует славянский учитель Мефодий — тот, что вместе с братом Кириллом дал славянам азбуку.",
    "«Житие Мефодия» рассказывает: языческий князь «на Висле» обижал христиан, и Мефодий послал ему сказать: «Крестись, сынок, по своей воле на своей земле, чтобы не крестили тебя пленённым и насильно на чужой земле — и тогда меня вспомнишь». Князь не послушал. Вскоре Святополк Моравский покорил вислян, а князя, как говорит житие, и вправду крестили в плену. Это первое упоминание о землях будущей Малой Польши в письменных источниках — почти за сто лет до крещения Мешко.",
    "«Житие Мефодия» (Паннонское житие), гл. 11"))

# ================================================================ chrobry_crown_1025
NEW_SCENES += [
    scene("emperor_dies_pl", "Смерть императора", ["sig_emperor_dies_pl"], 1, "⚰️", "встретить смертный час", "icon_dead",
          ["император"], "deathbed"),
    scene("coronation_1025_pl", "Коронация в Гнезно", ["sig_coronation_1025_pl"], 2, "👑", "возложить корону", "icon_crown",
          ["архиепископ", "князь"], "cathedral_altar"),
    scene("ask_crown_pl", "Просить корону у императора", ["sig_ask_crown_pl"], 2, "🙏", "просить разрешения", "icon_ally",
          ["кто просит", "император"], "court_present"),
    bait("chrobry_war_pl", "Новая война с империей", "v_battle", 2, "open_battle_s", ["нападающий", "защитник"]),
]
NEW_RULES += [
    rule("emperor_dies_pl_sig", "Император Генрих II умирает бездетным — трон империи пустеет",
         "sig_emperor_dies_pl",
         [actor("A", 0, tags=["emperor_h2_pl"])],
         [setf("A", "dead")]),
    rule("ask_crown_pl_sig", "Живой император отказывает: польская корона — угроза империи, и дело кончается войной",
         "sig_ask_crown_pl",
         [actor("A", 0, tags=["piast_pl"]), actor("B", 1, tags=["emperor_h2_pl"])],
         [setf("A", "refused_crown_pl"), addr("enemy_of", "B", "A")]),
    rule("coronation_1025_pl_sig", "Архиепископ возлагает корону на Болеслава — Польша становится королевством",
         "sig_coronation_1025_pl",
         [actor("A", 0, tags=["archbishop_pl"]), actor("B", 1, tags=["piast_pl"], notFlags=["refused_crown_pl"]),],
         [setf("B", "first_king_pl"), setf("B", "crowned"), setf("B", "reigns")]),
]
NEW_LEVELS.append(level(
    "chrobry_crown_1025", 55, ACT2, "poland_ceremony", "coronation_1025_pl", 2,
    ["emperor_dies_pl", "coronation_1025_pl", "ask_crown_pl", "chrobry_war_pl"],
    ["chrobry", "henry2_hre", "archbishop_gn"],
    {"chrobry": ["standing", "strong", "reigns"], "henry2_hre": ["standing", "strong", "crowned"]}, [],
    [flag("chrobry", "first_king_pl"), flag("henry2_hre", "dead")],
    [("emperor_dies_pl", ["henry2_hre"]), ("coronation_1025_pl", ["archbishop_gn", "chrobry"])],
    "fact"))
TEXTS.update(texts("chrobry_crown_1025",
    "Первый король",
    "Болеслав Храбрый двадцать пять лет ждёт короны — и надевает её, едва в империи умирает император",
    "Просить у императора бесполезно: он скажет «нет», и это запомнят. Иногда лучший ход — дождаться.",
    "1024 год. Болеслав Храбрый — самый сильный правитель между Эльбой и Днепром: он воевал с императором Генрихом II пятнадцать лет и не проиграл. Королевскую корону ему обещали ещё в 1000 году в Гнезно, но Генрих её не допустит. Болеславу почти шестьдесят.",
    "13 июля 1024 года Генрих II умер, не оставив сына, и в империи начались выборы нового короля. Пока немцам было не до Польши, на Пасху 1025 года архиепископ в Гнезно короновал Болеслава — первого короля Польши. Он прожил королём всего два месяца и умер 17 июня 1025 года. Немецкий хронист с досадой писал, что Болеслав «присвоил» корону; на троне его сменил сын, Мешко II, — тоже коронованный в том же году.",
    "«Анналы Кведлинбургские»; Галл Аноним, «Хроника и деяния князей Польши»"))

# ================================================================ magdeburg_1257
NEW_SCENES += [
    scene("location_charter_pl", "Локационная грамота", ["sig_location_charter_pl"], 2, "📜", "дать городу право", "icon_crown",
          ["князь", "войт"], "council_b"),
    scene("settle_town_pl", "Заселить новый город", ["sig_settle_town_pl"], 2, "🏘️", "принять поселенца", "icon_ally",
          ["войт", "поселенец"], "town_by_town"),
    scene("rynek_pl", "Разметка Рынка", ["sig_rynek_pl"], 2, "📐", "размерить площадь", "icon_crown",
          ["войт", "купец"], "homage_square_pl"),
    bait("buy_wojt_pl", "Выкупить войтовство", "v_bribe", 2, "merchant_deal_pl", ["кто платит", "кого покупают"]),
]
NEW_RULES += [
    rule("location_charter_pl_sig", "Князь даёт войту грамоту: город на магдебургском праве — свой суд, своя рада, свои вольности",
         "sig_location_charter_pl",
         [actor("A", 0, tags=["boleslaw5_pl"]), actor("B", 1, tags=["wojt_pl"])],
         [setf("B", "chartered_pl")]),
    rule("settle_merchant_pl_sig", "Войт зовёт в город купцов и ремесленников — они получают дома и мещанское право",
         "sig_settle_town_pl",
         [actor("A", 0, tags=["wojt_pl"], flags=["chartered_pl"]), actor("B", 1, tags=["merchant_pl"])],
         [setf("B", "settled_pl")]),
    rule("settle_peasant_pl_sig", "Войт сманивает в город княжеского крестьянина — а грамота это прямо запрещает",
         "sig_settle_town_pl",
         [actor("A", 0, tags=["wojt_pl"]), actor("B", 1, tags=["peasant_serf_pl"])],
         [setf("A", "broke_charter_pl")]),
    rule("rynek_pl_sig", "Войт размечает огромную квадратную площадь — Рынок, и вокруг неё ровные кварталы",
         "sig_rynek_pl",
         [actor("A", 0, tags=["wojt_pl"], flags=["chartered_pl"]), actor("B", 1, tags=["merchant_pl"], flags=["settled_pl"])],
         [setf("A", "rynek_pl"), setf("B", "trade_pl")]),
]
NEW_LEVELS.append(level(
    "magdeburg_1257", 101, ACT2, "poland_ceremony", "rynek_pl", 3,
    ["location_charter_pl", "settle_town_pl", "rynek_pl", "buy_wojt_pl"],
    ["boleslaw5", "wojt_dytmar", "merchant_pl", "peasant_pl"],
    {"boleslaw5": ["standing", "reigns"]}, [],
    [flag("wojt_dytmar", "rynek_pl"), flag("merchant_pl", "trade_pl"), nflag("wojt_dytmar", "broke_charter_pl")],
    [("location_charter_pl", ["boleslaw5", "wojt_dytmar"]), ("settle_town_pl", ["wojt_dytmar", "merchant_pl"]),
     ("rynek_pl", ["wojt_dytmar", "merchant_pl"])],
    "fact"))
TEXTS.update(texts("magdeburg_1257",
    "Краков на магдебургском праве",
    "После монгольского пожара Краков строят заново — по немецкому праву, с самоуправлением и огромным Рынком",
    "Город — это люди, но не любые: у князя свои крестьяне, и отдавать их он не собирался. Площадь размечают, когда есть кому торговать.",
    "1257 год. Шестнадцать лет назад монголы сожгли Краков дотла. Князь Болеслав Стыдливый хочет, чтобы столица Малой Польши поднялась быстро и богато, — и зовёт трёх войтов, которые построят город по образцу немецких городов.",
    "5 июня 1257 года Болеслав Стыдливый выдал войтам Гедко, Якубу и Дитмару грамоту: Краков получал магдебургское право — собственный суд, городской совет и вольности для мещан. Посреди города разметили Рынок — около 200 на 200 метров, одну из крупнейших средневековых площадей Европы, а вокруг — сетку прямых улиц, которая сохранилась до сих пор. В грамоте была хитрая оговорка: войтам запрещалось принимать в город княжеских крестьян — князь не хотел терять своих подданных и налоги. Так магдебургское право пошло по всей Польше: к XVI веку на нём жили сотни городов.",
    "Локационная грамота Кракова, 5 июня 1257 года"))

# ================================================================ kalisz_1264
NEW_SCENES += [
    scene("kalisz_statute_pl", "Калишский статут", ["sig_kalisz_statute_pl"], 2, "📜", "даровать привилей", "icon_crown",
          ["князь", "старейшина"], "council"),
    scene("kahal_pl", "Община и синагога", ["sig_kahal_pl"], 1, "🕍", "поселиться общиной", "icon_ally",
          ["старейшина"], "chapel"),
    scene("kalisz_loan_pl", "Заём", ["sig_kalisz_loan_pl"], 2, "💰", "взять в долг", "icon_ally",
          ["заёмщик", "заимодавец"], "bank_loan"),
    scene("blood_libel_pl", "Наветы", ["sig_blood_libel_pl"], 2, "⚖️", "обвинить", "icon_plot",
          ["обвинитель", "обвиняемый"], "court_denounce"),
]
NEW_RULES += [
    rule("kalisz_statute_pl_sig", "Князь берёт евреев под свою защиту: обида еврею — обида князю",
         "sig_kalisz_statute_pl",
         [actor("A", 0, tags=["pious_pl"]), actor("B", 1, tags=["jew_elder_pl"])],
         [setf("B", "protected_pl")]),
    rule("kahal_pl_sig", "Под защитой статута община строит синагогу, школу, своё кладбище",
         "sig_kahal_pl",
         [actor("A", 0, tags=["jew_elder_pl"], flags=["protected_pl"])],
         [setf("A", "community_pl")]),
    rule("kalisz_loan_pl_sig", "Горожанин берёт заём у общины — по закону, под залог и честный процент",
         "sig_kalisz_loan_pl",
         [actor("A", 0, tags=["burgher_pl"]), actor("B", 1, tags=["jew_elder_pl"], flags=["community_pl"])],
         [setf("A", "credit_pl")]),
    rule("blood_libel_protected_pl_sig", "Навет при защите статута: обвинителя, не доказавшего вины, карают как клеветника",
         "sig_blood_libel_pl",
         [actor("A", 0, tags=["burgher_pl"]), actor("B", 1, tags=["jew_elder_pl"], flags=["protected_pl"])],
         [setf("A", "libel_punished_pl")]),
    rule("blood_libel_unprotected_pl_sig", "Навет без защиты закона — и общину изгоняют",
         "sig_blood_libel_pl",
         [actor("A", 0, tags=["burgher_pl"]), actor("B", 1, tags=["jew_elder_pl"], notFlags=["protected_pl"])],
         [setf("B", "expelled_pl"), setf("B", "away")]),
]
NEW_LEVELS.append(level(
    "kalisz_1264", 102, ACT2, "poland_ceremony", "kalisz_statute_pl", 3,
    ["kalisz_statute_pl", "kahal_pl", "kalisz_loan_pl", "blood_libel_pl"],
    ["boleslaw_pious", "jewish_elder", "glogow_burgher"],
    {"boleslaw_pious": ["standing", "reigns"]}, [],
    [flag("jewish_elder", "community_pl"), flag("glogow_burgher", "credit_pl"),
     nflag("glogow_burgher", "libel_punished_pl"), nflag("jewish_elder", "expelled_pl")],
    [("kalisz_statute_pl", ["boleslaw_pious", "jewish_elder"]), ("kahal_pl", ["jewish_elder"]),
     ("kalisz_loan_pl", ["glogow_burgher", "jewish_elder"])],
    "fact"))
TEXTS.update(texts("kalisz_1264",
    "Калишский статут",
    "Князь Великой Польши берёт евреев под защиту закона — и Польша на столетия становится домом крупнейшей еврейской общины мира",
    "Община держится на законе, а не наоборот. Клевета ничего не строит — она только разрушает.",
    "1264 год. По Европе ползут страшные наветы на евреев, их изгоняют из одного города за другим. Князь Великой Польши Болеслав Благочестивый, напротив, зовёт их в свои города: ему нужны торговля, деньги и ремесло.",
    "16 августа 1264 года в Калише Болеслав Благочестивый издал статут: еврей подлежит суду князя, а не толпы; за убийство еврея — казнь и конфискация; нельзя обвинять евреев в использовании христианской крови — а христианин, который поднял такое обвинение и не доказал его, нёс то же наказание. Был в статуте и трогательный пункт: если еврей ночью зовёт на помощь, а соседи-христиане не пришли, они платят штраф. Казимир Великий распространил статут на всё королевство, и за несколько веков в Польшу перебрались сотни тысяч евреев. В 1580 году общины даже получили свой «парламент» — Ваад четырёх земель.",
    "Калишский статут Болеслава Благочестивого, 1264"))

# ================================================================ academy_1400
NEW_SCENES += [
    scene("jadwiga_will_pl", "Завещание Ядвиги", ["sig_jadwiga_will_pl"], 2, "💎", "завещать драгоценности", "icon_dead",
          ["королева", "король"], "deathbed_m"),
    scene("academy_founding_pl", "Возрождение академии", ["sig_academy_founding_pl"], 2, "🎓", "открыть университет", "icon_crown",
          ["король", "ректор"], "krakow_academy_pl"),
    scene("first_lecture_pl", "Первая лекция", ["sig_first_lecture_pl"], 1, "📖", "начать занятия", "icon_ally",
          ["ректор"], "codex_book"),
    scene("jewels_to_war_pl", "Драгоценности — на войну", ["sig_jewels_to_war_pl"], 2, "⚔️", "отдать казну на войско", "icon_plot",
          ["король", "можновладец"], "barons_muster"),
]
NEW_RULES += [
    rule("jadwiga_will_pl_sig", "Умирающая королева завещает свои драгоценности на возрождение Краковской академии",
         "sig_jadwiga_will_pl",
         [actor("A", 0, tags=["jadwiga_pl"]), actor("B", 1, tags=["jagiello_pl"])],
         [setf("A", "dead"), setf("B", "bequest_pl")]),
    rule("jewels_to_war_pl_sig", "Можновладец уговаривает короля пустить завещанное на войско против Ордена",
         "sig_jewels_to_war_pl",
         [actor("A", 0, tags=["jagiello_pl"], flags=["bequest_pl"]), actor("B", 1, tags=["magnate_pl"])],
         [remf("A", "bequest_pl"), setf("A", "spent_jewels_pl")]),
    rule("academy_founding_pl_sig", "Король исполняет волю жены: академия открыта снова, во главе — ректор",
         "sig_academy_founding_pl",
         [actor("A", 0, tags=["jagiello_pl"], flags=["bequest_pl"]), actor("B", 1, tags=["rector_pl"])],
         [setf("B", "rector_named_pl"), setf("A", "founder_univ_pl")]),
    rule("first_lecture_pl_sig", "Ректор открывает занятия: право, богословие, медицина, свободные искусства",
         "sig_first_lecture_pl",
         [actor("A", 0, tags=["rector_pl"], flags=["rector_named_pl"])],
         [setf("A", "lectures_pl")]),
]
NEW_LEVELS.append(level(
    "academy_1400", 145, ACT3, "poland_ceremony", "academy_founding_pl", 3,
    ["jadwiga_will_pl", "academy_founding_pl", "first_lecture_pl", "jewels_to_war_pl"],
    ["jadwiga", "jagiello", "skarbimierz", "magnate_pl"],
    {"jadwiga": ["standing", "crowned"], "jagiello": ["standing", "reigns", "crowned"]}, [],
    [flag("skarbimierz", "lectures_pl"), nflag("jagiello", "spent_jewels_pl")],
    [("jadwiga_will_pl", ["jadwiga", "jagiello"]), ("academy_founding_pl", ["jagiello", "skarbimierz"]),
     ("first_lecture_pl", ["skarbimierz"])],
    "fact"))
TEXTS.update(texts("academy_1400",
    "Драгоценности королевы",
    "Умирающая Ядвига отдаёт свои украшения на университет — и Ягайло возрождает Краковскую академию",
    "Казна у короля одна, а соблазн потратить её на войну с Орденом велик. Без завещания открывать нечего.",
    "1399 год. Университет, основанный Казимиром Великим, после его смерти почти заглох. Королева Ядвига мечтает его возродить — но она тяжело больна после родов. Война с Тевтонским орденом всё ближе, и вельможи считают каждую монету.",
    "Ядвига умерла 17 июля 1399 года и завещала свои драгоценности на возрождение академии. 26 июля 1400 года Ягайло открыл её заново в доме, купленном у мещан Печержей, — сегодня это Collegium Maius; первым ректором стал Станислав из Скарбимежа, а первой речью — проповедь о пользе учёности. Через сто лет здесь будет учиться Николай Коперник. Сегодня это Ягеллонский университет, один из старейших в Европе.",
    "Ян Длугош, «Анналы», под 1399–1400; грамота Ягайло от 26 июля 1400"))

# ================================================================ nihil_novi_1505
NEW_SCENES += [
    scene("sejmik_pl", "Сеймик", ["sig_sejmik_pl"], 1, "🗳️", "выбрать посла", "icon_ally",
          ["шляхтич"], "council_b"),
    scene("radom_sejm_pl", "Сейм в Радоме", ["sig_radom_sejm_pl"], 2, "⚖️", "принять конституцию", "icon_crown",
          ["посол", "король"], "sejm_time_pl"),
    scene("laski_statute_pl", "Статут Лаского", ["sig_laski_statute_pl"], 2, "📚", "напечатать законы", "icon_crown",
          ["канцлер", "король"], "codex_book"),
    scene("mielnik_pl", "Мельницкий привилей", ["sig_mielnik_pl"], 2, "🏰", "отдать власть сенату", "icon_plot",
          ["король", "можновладец"], "secret_council_pl"),
]
NEW_RULES += [
    rule("sejmik_pl_sig", "Шляхта воеводства собирается на сеймик и выбирает посла на вальный сейм",
         "sig_sejmik_pl",
         [actor("A", 0, tags=["szlachcic_pl"])],
         [setf("A", "envoy_pl")]),
    rule("mielnik_pl_sig", "Король подписывает привилей магнатов: вся власть — сенату, то есть горстке вельмож",
         "sig_mielnik_pl",
         [actor("A", 0, tags=["alexander_pl"]), actor("B", 1, tags=["magnate_pl"])],
         [setf("A", "senate_rule_pl")]),
    rule("radom_sejm_pl_sig", "Сейм в Радоме: «ничего нового без общего согласия» — король не издаёт законов без сената и послов",
         "sig_radom_sejm_pl",
         [actor("A", 0, tags=["szlachcic_pl"], flags=["envoy_pl"]), actor("B", 1, tags=["alexander_pl"], notFlags=["senate_rule_pl"])],
         [setf("B", "nihil_novi_pl")]),
    rule("laski_statute_pl_sig", "Канцлер собирает все права королевства в одну книгу и отдаёт её в печать",
         "sig_laski_statute_pl",
         [actor("A", 0, tags=["laski_pl"]), actor("B", 1, tags=["alexander_pl"], flags=["nihil_novi_pl"])],
         [setf("A", "printed_law_pl")]),
]
NEW_LEVELS.append(level(
    "nihil_novi_1505", 175, ACT3, "poland_tension", "radom_sejm_pl", 3,
    ["sejmik_pl", "radom_sejm_pl", "laski_statute_pl", "mielnik_pl"],
    ["alexander_jag", "szlachcic_pl", "laski_chancellor", "magnate_pl"],
    {"alexander_jag": ["standing", "reigns", "crowned"]}, [],
    [flag("laski_chancellor", "printed_law_pl"), flag("alexander_jag", "nihil_novi_pl"), nflag("alexander_jag", "senate_rule_pl")],
    [("sejmik_pl", ["szlachcic_pl"]), ("radom_sejm_pl", ["szlachcic_pl", "alexander_jag"]),
     ("laski_statute_pl", ["laski_chancellor", "alexander_jag"])],
    "fact"))
TEXTS.update(texts("nihil_novi_1505",
    "Nihil novi",
    "Сейм в Радоме решает: король не может ввести ничего нового без согласия шляхты — так рождается шляхетская демократия",
    "Вельможи предложат королю простой путь — власть немногих. Голос шляхты сначала надо выбрать у себя в воеводстве.",
    "1505 год. Король Александр Ягеллон зажат между сильными магнатами и многочисленной шляхтой. Четыре года назад магнаты уже выбили у него Мельницкий привилей: вся власть — сенату. Теперь шляхта, около десятой части населения, требует своей доли.",
    "30 мая 1505 года сейм в Радоме принял конституцию «Nihil novi nisi commune consensu» — «ничего нового без общего согласия»: король не может издавать законы без сената и посольской избы. Мельницкий привилей так и не вступил в силу. В 1506 году канцлер Ян Лаский выпустил первый печатный свод польских законов — «Статут Лаского», с гравюрой короля на сейме. Шляхетская демократия была уникальной для Европы: голосовать могла десятая часть страны — во Франции или Англии того времени таких было в разы меньше. Её тень — крестьянство, которое голоса не имело вовсе.",
    "Конституция Nihil novi (Радом, 1505); «Статут Лаского» (1506)"))

# ================================================================ rej_1562
NEW_SCENES += [
    scene("latin_advice_pl", "«Пиши по-латыни»", ["sig_latin_advice_pl"], 2, "🏛️", "наставить писать по-латыни", "icon_plot",
          ["наставник", "поэт"], "court_whisper"),
    scene("polish_pen_pl", "Перо по-польски", ["sig_polish_pen_pl"], 1, "✒️", "писать на родном языке", "icon_ally",
          ["поэт"], "anekdota_desk"),
    scene("print_shop_pl", "Краковская печатня", ["sig_print_shop_pl"], 2, "📚", "напечатать книгу", "icon_crown",
          ["печатник", "автор"], "codex_book"),
    scene("manor_reading_pl", "Чтение в усадьбе", ["sig_manor_reading_pl"], 2, "🏡", "читать книгу", "icon_ally",
          ["читатель", "автор"], "country_palace"),
]
NEW_RULES += [
    rule("latin_advice_pl_sig", "Учёный прелат убеждает поэта: серьёзные книги пишут только по-латыни",
         "sig_latin_advice_pl",
         [actor("A", 0, tags=["primate_pl"]), actor("B", 1, tags=["poet_pl"])],
         [setf("B", "latin_pl")]),
    rule("polish_pen_pl_sig", "Поэт пишет по-польски — для шляхтича, а не для профессора",
         "sig_polish_pen_pl",
         [actor("A", 0, tags=["poet_pl"], notFlags=["latin_pl"])],
         [setf("A", "polish_book_pl")]),
    rule("print_shop_pl_sig", "Печатник набирает польскую книгу — и её покупают по всей стране",
         "sig_print_shop_pl",
         [actor("A", 0, tags=["printer_pl"]), actor("B", 1, tags=["poet_pl"], flags=["polish_book_pl"])],
         [setf("B", "printed_pl")]),
    rule("manor_reading_pl_sig", "Шляхтич в усадьбе читает книгу на своём языке — и смеётся, и спорит",
         "sig_manor_reading_pl",
         [actor("A", 0, tags=["szlachcic_pl"]), actor("B", 1, tags=["rej_pl"], flags=["printed_pl"])],
         [setf("A", "reads_polish_pl")]),
]
NEW_LEVELS.append(level(
    "rej_1562", 215, ACT3, "poland_ceremony", "polish_pen_pl", 3,
    ["latin_advice_pl", "polish_pen_pl", "print_shop_pl", "manor_reading_pl"],
    ["rej", "kochanowski", "printer_pl", "szlachcic_pl", "primate_uchanski"],
    {"primate_uchanski": ["standing"]}, [],
    [flag("szlachcic_pl", "reads_polish_pl"), nflag("rej", "latin_pl")],
    [("polish_pen_pl", ["rej"]), ("print_shop_pl", ["printer_pl", "rej"]), ("manor_reading_pl", ["szlachcic_pl", "rej"])],
    "fact"))
TEXTS.update(texts("rej_1562",
    "Поляки не гуси",
    "Шляхтич Николай Рей, плохо знавший латынь, начинает писать по-польски — и становится «отцом польской литературы»",
    "Учёные советы не всегда полезны: латынь уведёт книгу от читателя. Читать будет шляхтич — значит, и писать надо для него.",
    "XVI век. Образованная Польша говорит и пишет по-латыни: на ней законы, наука, богословие, стихи. Николай Рей из Нагловиц — шляхтич-самоучка, латынь он так толком и не выучил. Зато знает, как говорят на рынке, в корчме и в усадьбе.",
    "Рей писал только по-польски — сатиры, проповеди, нравоучения, «Жизнь честного человека». В 1562 году в сборнике «Зверинец» он оставил строчку, которую в Польше знает каждый школьник: «пусть все соседние народы знают, что поляки не гуси, — свой язык имеют» (гусиный гогот — намёк на латынь). Рядом с ним работал Ян Кохановский — первый великий поэт польского языка: в 1580 году он выпустил «Трены», плач по умершей двухлетней дочери Урсуле, и личное горе впервые стало в Польше высокой поэзией.",
    "Миколай Рей, «Зверинец» (1562); Ян Кохановский, «Трены» (1580)"))

# ================================================================ grain_gdansk (XVI в.)
NEW_SCENES += [
    scene("panszczyzna_pl", "Барщина", ["sig_panszczyzna_pl"], 2, "🌾", "согнать на барщину", "icon_plot",
          ["пан", "крестьянин"], "plough_field"),
    scene("vistula_raft_pl", "Плоты по Висле", ["sig_vistula_raft_pl"], 2, "🛶", "сплавить зерно", "icon_ally",
          ["флисак", "пан"], "barge"),
    scene("gdansk_sale_pl", "Гданьский порт", ["sig_gdansk_sale_pl"], 2, "⚓", "продать зерно", "icon_crown",
          ["покупатель", "продавец"], "harbor"),
    bait("peasant_run_pl", "Бежать на Украину", "v_flee", 1, "peasant_escape_pl", ["кто бежит"]),
]
NEW_RULES += [
    rule("panszczyzna_pl_sig", "Пан гонит крестьянина на барщину: сначала день в неделю, потом три, потом шесть",
         "sig_panszczyzna_pl",
         [actor("A", 0, tags=["szlachcic_pl"]), actor("B", 1, tags=["peasant_serf_pl"], notFlags=["away"])],
         [setf("B", "serf_pl"), setf("A", "harvest_pl")]),
    rule("vistula_raft_pl_sig", "Флисаки грузят панское зерно на плоты и сплавляют по Висле до Гданьска",
         "sig_vistula_raft_pl",
         [actor("A", 0, tags=["flisak_pl"]), actor("B", 1, tags=["szlachcic_pl"], flags=["harvest_pl"])],
         [setf("B", "grain_shipped_pl")]),
    rule("gdansk_sale_pl_sig", "Голландский шкипер скупает польскую рожь — в Амстердаме её ждут тысячи ртов",
         "sig_gdansk_sale_pl",
         [actor("A", 0, tags=["dutch_pl"]), actor("B", 1, tags=["szlachcic_pl"], flags=["grain_shipped_pl"])],
         [setf("A", "bought_grain_pl"), setf("B", "rich_pl")]),
]
NEW_LEVELS.append(level(
    "grain_gdansk", 225, ACT3, "poland_tension", "gdansk_sale_pl", 3,
    ["panszczyzna_pl", "vistula_raft_pl", "gdansk_sale_pl", "peasant_run_pl"],
    ["szlachcic_pl", "peasant_pl", "flisak_pl", "dutch_skipper"],
    {"szlachcic_pl": ["standing"]}, [],
    [flag("dutch_skipper", "bought_grain_pl"), flag("peasant_pl", "serf_pl")],
    [("panszczyzna_pl", ["szlachcic_pl", "peasant_pl"]), ("vistula_raft_pl", ["flisak_pl", "szlachcic_pl"]),
     ("gdansk_sale_pl", ["dutch_skipper", "szlachcic_pl"])],
    "simplification"))
TEXTS.update(texts("grain_gdansk",
    "Житница Европы",
    "Польская рожь плывёт по Висле в Гданьск и дальше в Амстердам — богатство шляхты держится на крепостном крестьянине",
    "Зерно не растёт само: сначала кто-то должен работать на панском поле. Сбежит крестьянин — продавать будет нечего.",
    "XVI век. Нидерланды и Западная Европа растут, им нужен хлеб. У Польши есть чернозёмы и Висла, которая течёт прямо в Гданьск. Шляхтич понимает: выгоднее не брать с крестьян оброк, а самому сеять на продажу — руками этих же крестьян.",
    "В 1496 году сейм запретил крестьянам свободно уходить из деревни, а Торуньский статут 1520 года ввёл обязательную барщину — день в неделю; к XVII веку она доходила до трёх–шести дней. Панские хозяйства-фольварки отправляли рожь вниз по Висле на плотах и баржах-«шкутах»; сплавщиков-флисаков называли «вислянскими моряками». Гданьск стал крупнейшим портом Балтики, а голландцы называли балтийскую торговлю зерном «матерью всех торговых дел». Шляхта богатела, строила дворцы — а крестьяне бежали от барщины на окраины, в днепровские степи.",
    "Торуньский статут (1520); М. Малович, «Восток и Запад Европы в XIII–XVI вв.»"))

# ================================================================ batory_1579
NEW_SCENES += [
    scene("batory_wedding_pl", "Свадьба с Ягеллонкой", ["sig_batory_wedding_pl"], 2, "💍", "жениться и короноваться", "icon_crown",
          ["избранник", "королева"], "polish_wedding"),
    scene("not_consciences_pl", "«Король людей, не совестей»", ["sig_not_consciences_pl"], 2, "🤝", "защитить иноверца", "icon_ally",
          ["король", "кальвинист"], "council_b"),
    scene("vilnius_academy_pl", "Виленская академия", ["sig_vilnius_academy_pl"], 2, "🎓", "даровать права университета", "icon_crown",
          ["король", "иезуит"], "university_project"),
    scene("skarga_disputation_pl", "Диспут проповедника", ["sig_skarga_disputation_pl"], 2, "🔥", "обличить еретика", "icon_plot",
          ["проповедник", "кальвинист"], "fire_sermon"),
]
NEW_RULES += [
    rule("batory_wedding_pl_sig", "Трансильванский князь женится на Анне Ягеллонке — таково условие элекции — и коронуется в тот же день",
         "sig_batory_wedding_pl",
         [actor("A", 0, tags=["batory_pl"]), actor("B", 1, tags=["infanta_pl"])],
         [setf("A", "king_b_pl"), setf("A", "crowned"), setf("A", "reigns"), setf("B", "married"), setf("A", "married")]),
    rule("not_consciences_pl_sig", "Католик Баторий отказывается преследовать протестантов: «Я король людей, а не совестей»",
         "sig_not_consciences_pl",
         [actor("A", 0, tags=["batory_pl"], flags=["king_b_pl"]), actor("B", 1, tags=["lith_magnate_pl"])],
         [setf("B", "tolerated_pl")]),
    rule("skarga_disputation_pl_sig", "Проповедник требует изгнать ересь — и без королевской защиты кальвиниста гонят",
         "sig_skarga_disputation_pl",
         [actor("A", 0, tags=["skarga_pl"]), actor("B", 1, tags=["lith_magnate_pl"], notFlags=["tolerated_pl"])],
         [setf("B", "persecuted_pl")]),
    rule("vilnius_academy_pl_sig", "Король возводит иезуитскую коллегию в Вильне в академию — первый университет Великого княжества",
         "sig_vilnius_academy_pl",
         [actor("A", 0, tags=["batory_pl"], flags=["king_b_pl"]), actor("B", 1, tags=["skarga_pl"])],
         [setf("B", "rector_v_pl")]),
]
NEW_LEVELS.append(level(
    "batory_1579", 245, ACT4, "poland_ceremony", "vilnius_academy_pl", 3,
    ["batory_wedding_pl", "not_consciences_pl", "vilnius_academy_pl", "skarga_disputation_pl"],
    ["batory", "anna_jag", "skarga", "radziwill_rudy"],
    {"batory": ["standing", "strong"], "anna_jag": ["standing"], "radziwill_rudy": ["standing"]}, [],
    [flag("skarga", "rector_v_pl"), flag("radziwill_rudy", "tolerated_pl"), nflag("radziwill_rudy", "persecuted_pl")],
    [("batory_wedding_pl", ["batory", "anna_jag"]), ("not_consciences_pl", ["batory", "radziwill_rudy"]),
     ("vilnius_academy_pl", ["batory", "skarga"])],
    "fact"))
TEXTS.update(texts("batory_1579",
    "Король людей, не совестей",
    "Стефан Баторий даёт иезуитам университет в Вильне — и при этом не позволяет никого гнать за веру",
    "Король сначала должен стать королём — а условие элекции известно. Ревностный проповедник опасен тому, кого никто не защитил.",
    "1576 год. После бегства Генриха Валуа шляхта избирает трансильванского князя Стефана Батория — с условием жениться на Анне Ягеллонке, сестре последнего Ягеллона. Он католик, ему близки иезуиты, а иезуит Пётр Скарга — лучший проповедник страны. Но вокруг — кальвинисты, лютеране, православные, и все помнят клятву Варшавской конфедерации.",
    "1 мая 1576 года Баторий обвенчался с Анной и был коронован в один день. Он поддерживал иезуитов: 1 апреля 1579 года возвёл их коллегию в Вильне в академию — первый университет Великого княжества Литовского, первым ректором которого стал Пётр Скарга. И при этом твёрдо держал мир вер. Ему приписывают слова: «Я король людей, а не совестей». Кальвинист Николай Радзивилл Рыжий оставался при нём гетманом и канцлером Литвы. Виленская академия — сегодня Вильнюсский университет.",
    "Привилей Стефана Батория для Виленской академии (1579); Р. Гейденштейн, «Записки о Московской войне»"))

# ================================================================ arians_1658
NEW_SCENES += [
    scene("sejm_1658_pl", "Сейм 1658 года", ["sig_sejm_1658_pl"], 2, "⚖️", "изгнать ариан", "icon_dead",
          ["король", "арианин"], "sejm_time_pl"),
    scene("convert_offer_pl", "Перейти в католичество", ["sig_convert_offer_pl"], 2, "⛪", "отречься от веры", "icon_plot",
          ["приор", "арианин"], "cathedral_altar"),
    scene("exile_amsterdam_pl", "Дорога в Амстердам", ["sig_exile_amsterdam_pl"], 1, "🚪", "уйти в изгнание", "icon_ally",
          ["изгнанник"], "exile_road"),
    scene("bibliotheca_pl", "«Библиотека польских братьев»", ["sig_bibliotheca_pl"], 2, "📚", "издать труды", "icon_crown",
          ["печатник", "автор"], "codex_book"),
]
NEW_RULES += [
    rule("sejm_1658_pl_sig", "После шведского «Потопа» сейм обвиняет ариан в измене: перейти в католичество — или покинуть страну",
         "sig_sejm_1658_pl",
         [actor("A", 0, tags=["jk_king_pl"]), actor("B", 1, tags=["arian_pl"])],
         [setf("B", "banished_pl")]),
    rule("convert_offer_pl_sig", "Изгнанник принимает католичество — и остаётся дома, но его вера уходит из Польши",
         "sig_convert_offer_pl",
         [actor("A", 0, tags=["prior_pl"]), actor("B", 1, tags=["arian_pl"], flags=["banished_pl"])],
         [setf("B", "converted_pl")]),
    rule("exile_amsterdam_pl_sig", "Арианин уезжает в веротерпимый Амстердам",
         "sig_exile_amsterdam_pl",
         [actor("A", 0, tags=["arian_pl"], flags=["banished_pl"], notFlags=["converted_pl"])],
         [setf("A", "in_amsterdam_pl")]),
    rule("bibliotheca_pl_sig", "В Амстердаме печатают многотомную «Библиотеку польских братьев» — её будут читать Локк и Вольтер",
         "sig_bibliotheca_pl",
         [actor("A", 0, tags=["printer_pl"]), actor("B", 1, tags=["arian_pl"], flags=["in_amsterdam_pl"])],
         [setf("B", "bibliotheca_done_pl")]),
]
NEW_LEVELS.append(level(
    "arians_1658", 302, ACT4, "poland_tension", "exile_amsterdam_pl", 3,
    ["sejm_1658_pl", "convert_offer_pl", "exile_amsterdam_pl", "bibliotheca_pl"],
    ["jan_kazimierz", "wiszowaty", "kordecki", "printer_pl"],
    {"jan_kazimierz": ["standing", "reigns", "crowned"], "kordecki": ["standing"]}, [],
    [flag("wiszowaty", "bibliotheca_done_pl"), nflag("wiszowaty", "converted_pl")],
    [("sejm_1658_pl", ["jan_kazimierz", "wiszowaty"]), ("exile_amsterdam_pl", ["wiszowaty"]),
     ("bibliotheca_pl", ["printer_pl", "wiszowaty"])],
    "fact"))
TEXTS.update(texts("arians_1658",
    "Изгнание польских братьев",
    "Страна, клявшаяся не гнать за веру, изгоняет ариан — а их книги, изданные в Амстердаме, меняют мысль Европы",
    "Остаться можно, лишь отрекшись, — и тогда книги не будет. Печатать будут там, где за веру не гонят.",
    "1658 год. Польша едва пережила шведский «Потоп». Виноватых ищут, и находят: польских братьев, или ариан, — протестантов, отвергавших Троицу. Их академия в Ракове закрыта ещё двадцать лет назад, теперь сейм решает их судьбу. Среди них — философ Анджей Вишоватый, внук основателя движения Фауста Социна.",
    "Сейм 1658 года приказал арианам за три года перейти в католичество или покинуть страну; потом срок сократили до двух. Около 1660 года несколько тысяч человек ушли в Трансильванию, Пруссию и Нидерланды. Вишоватый поселился в Амстердаме и в 1665–1668 годах издал «Bibliotheca Fratrum Polonorum» — многотомное собрание трудов польских братьев. Их мысль о свободе совести и разуме в вере читали Джон Локк, Пьер Бейль, Вольтер и Ньютон. Так страна, клявшаяся в 1573 году не проливать крови за веру, впервые изгнала целую конфессию.",
    "Конституция сейма 1658 г. «О арианах»; Bibliotheca Fratrum Polonorum (Амстердам, 1665–1668)"))

# ================================================================ ken_1773
NEW_SCENES += [
    scene("jesuit_dissolved_pl", "Папское бреве о роспуске", ["sig_jesuit_dissolved_pl"], 1, "📜", "огласить папское бреве", "icon_dead",
          ["иезуит"], "bull_on_altar"),
    scene("ken_founded_pl", "Комиссия национального образования", ["sig_ken_founded_pl"], 2, "🏫", "учредить комиссию", "icon_crown",
          ["король", "бывший иезуит"], "academy_chancery"),
    scene("distribution_pl", "Распределительная комиссия", ["sig_distribution_pl"], 2, "💰", "распределить имущество", "icon_plot",
          ["маршалок", "король"], "embezzle"),
    scene("academy_reform_pl", "Реформа Краковской академии", ["sig_academy_reform_pl"], 2, "🎓", "реформировать академию", "icon_crown",
          ["реформатор", "король"], "krakow_academy_pl"),
]
NEW_RULES += [
    rule("jesuit_dissolved_pl_sig", "Папа распускает орден иезуитов — сотни их школ в Польше остаются без хозяина",
         "sig_jesuit_dissolved_pl",
         [actor("A", 0, tags=["jesuit_pl"])],
         [setf("A", "dissolved_pl")]),
    rule("ken_founded_pl_sig", "Король и сейм создают Комиссию национального образования — на имущество ордена",
         "sig_ken_founded_pl",
         [actor("A", 0, tags=["sa_king_pl"]), actor("B", 1, tags=["jesuit_pl"], flags=["dissolved_pl"])],
         [setf("A", "ken_pl"), setf("B", "teacher_ken_pl")]),
    rule("distribution_pl_sig", "Маршалок Понинский и его люди «распределяют» имущество иезуитов — себе в карман",
         "sig_distribution_pl",
         [actor("A", 0, tags=["poninski_pl"]), actor("B", 1, tags=["sa_king_pl"], flags=["ken_pl"])],
         [setf("B", "funds_stolen_pl"), setf("A", "rich_pl")]),
    rule("academy_reform_pl_sig", "Коллонтай перестраивает Краковскую академию: вместо схоластики — физика, химия, медицина, на польском языке",
         "sig_academy_reform_pl",
         [actor("A", 0, tags=["reformer_pl"]), actor("B", 1, tags=["sa_king_pl"], flags=["ken_pl"], notFlags=["funds_stolen_pl"])],
         [setf("A", "reformed_academy_pl")]),
]
NEW_LEVELS.append(level(
    "ken_1773", 355, ACT5, "poland_ceremony", "ken_founded_pl", 3,
    ["jesuit_dissolved_pl", "ken_founded_pl", "distribution_pl", "academy_reform_pl"],
    ["poniatowski", "jesuit_pl", "poninski", "kollataj"],
    {"poniatowski": ["standing", "reigns", "crowned"], "poninski": ["standing"]}, [],
    [flag("kollataj", "reformed_academy_pl"), flag("jesuit_pl", "teacher_ken_pl"), nflag("poniatowski", "funds_stolen_pl")],
    [("jesuit_dissolved_pl", ["jesuit_pl"]), ("ken_founded_pl", ["poniatowski", "jesuit_pl"]),
     ("academy_reform_pl", ["kollataj", "poniatowski"])],
    "simplification"))
TEXTS.update(texts("ken_1773",
    "Первое министерство просвещения",
    "Во время первого раздела Польша создаёт Комиссию национального образования — первое министерство просвещения в Европе",
    "Деньги на школы есть — если их не растащат по дороге. Кто громче всех готов «распределять», тот и опаснее всех.",
    "1773 год. Польша только что потеряла треть земель в первом разделе; сейм заседает под надзором русского посла, а маршалок сейма Адам Понинский — платный агент соседей. И вдруг из Рима приходит новость: папа распустил орден иезуитов, который держал почти все школы страны.",
    "14 октября 1773 года сейм учредил Комиссию национального образования — первое в Европе государственное ведомство просвещения. Ей передали имущество иезуитов; бывшие иезуиты часто оставались учителями. Комиссия выпустила новые учебники на польском, ввела физику, природоведение и даже гигиену, а Гуго Коллонтай в 1777–1780 годах реформировал Краковскую академию. Честно говоря, распределительная комиссия Понинского всё-таки разворовала немалую часть иезуитских богатств, — но и оставшегося хватило, чтобы школы пережили сами разделы.",
    "Конституция сейма 14 октября 1773 г.; Т. Мизя, «Комиссия национального образования»"))

# ================================================================ mickiewicz_1834
NEW_SCENES += [
    scene("great_emigration_pl", "Великая эмиграция", ["sig_great_emigration_pl"], 2, "🚪", "уйти за границу", "icon_ally",
          ["поэт", "повстанец"], "exile_road"),
    scene("pan_tadeusz_pl", "«Пан Тадеуш»", ["sig_pan_tadeusz_pl"], 1, "✒️", "писать поэму", "icon_crown",
          ["поэт"], "anekdota_desk"),
    scene("emigre_evening_pl", "Вечер у эмигрантов", ["sig_emigre_evening_pl"], 2, "🕯️", "прочесть вслух", "icon_ally",
          ["поэт", "слушатель"], "salon_c"),
    scene("amnesty_pl", "Царская амнистия", ["sig_amnesty_pl"], 2, "📜", "вернуться по амнистии", "icon_plot",
          ["царь", "повстанец"], "court_pardon"),
]
NEW_RULES += [
    rule("great_emigration_pl_sig", "После разгрома восстания тысячи поляков уходят во Францию — поэт вместе с ними",
         "sig_great_emigration_pl",
         [actor("A", 0, tags=["mickiewicz_pl"]), actor("B", 1, tags=["emigre_pl"], notFlags=["siberia_pl"])],
         [setf("A", "in_paris_pl"), setf("B", "in_paris_pl")]),
    rule("amnesty_pl_sig", "Повстанец верит обещанию прощения и возвращается — а по дороге домой его отправляют в Сибирь",
         "sig_amnesty_pl",
         [actor("A", 0, tags=["tsar_n_pl"]), actor("B", 1, tags=["emigre_pl"], notFlags=["in_paris_pl"])],
         [setf("B", "siberia_pl"), setf("B", "defeated")]),
    rule("pan_tadeusz_pl_sig", "В парижской тоске поэт пишет поэму о старой шляхетской Литве — дом, которого больше нет",
         "sig_pan_tadeusz_pl",
         [actor("A", 0, tags=["mickiewicz_pl"], flags=["in_paris_pl"])],
         [setf("A", "tadeusz_pl")]),
    rule("emigre_evening_pl_sig", "Эмигранты слушают поэму — и плачут: родина у них есть, хотя бы в книге",
         "sig_emigre_evening_pl",
         [actor("A", 0, tags=["mickiewicz_pl"], flags=["tadeusz_pl"]), actor("B", 1, tags=["emigre_pl"], flags=["in_paris_pl"])],
         [setf("B", "consoled_pl")]),
]
NEW_LEVELS.append(level(
    "mickiewicz_1834", 435, ACT6, "poland_romance", "pan_tadeusz_pl", 3,
    ["great_emigration_pl", "pan_tadeusz_pl", "emigre_evening_pl", "amnesty_pl"],
    ["mickiewicz", "emigre_pl", "nicholas1_pl"],
    {"nicholas1_pl": ["standing", "reigns", "crowned"]}, [],
    [flag("emigre_pl", "consoled_pl"), nflag("emigre_pl", "siberia_pl")],
    [("great_emigration_pl", ["mickiewicz", "emigre_pl"]), ("pan_tadeusz_pl", ["mickiewicz"]),
     ("emigre_evening_pl", ["mickiewicz", "emigre_pl"])],
    "simplification"))
TEXTS.update(texts("mickiewicz_1834",
    "Пан Тадеуш",
    "После поражения восстания Мицкевич в Париже пишет «Пана Тадеуша» — книгу, ставшую для поляков домом",
    "Поверить в прощение — значит рискнуть всем. Поэму пишут в изгнании, а слушают её те, кто ушёл вместе с поэтом.",
    "1832 год. Ноябрьское восстание разгромлено. Около десяти тысяч повстанцев, офицеров, поэтов и музыкантов уходят через Германию во Францию — это назовут Великой эмиграцией. Император обещает амнистию тем, кто вернётся. Среди уехавших — Адам Мицкевич, уже самый знаменитый поэт Польши.",
    "Многие поверившие амнистии были арестованы и сосланы. Мицкевич остался в Париже и в 1834 году издал «Пана Тадеуша» — эпопею о шляхетской усадьбе в Литве 1811–1812 годов, о ссорах, охотах, любви и надежде на Наполеона. Поэма начинается строкой «Литва! Отчизна моя! Ты как здоровье», которую в Польше знают наизусть. В Париже тех лет были и Шопен, и Словацкий, и Лелевель: страны на карте не было, а её культура жила в эмиграции. В 2012 году «Пана Тадеуша» вслух читала вся страна — в первом Национальном чтении.",
    "Адам Мицкевич, «Пан Тадеуш» (Париж, 1834)"))

# ================================================================ lodz_1880
NEW_SCENES += [
    scene("customs_lifted_pl", "Таможня на Восток открыта", ["sig_customs_lifted_pl"], 2, "🚂", "открыть рынок империи", "icon_crown",
          ["таможенник", "фабрикант"], "customs_border_pl"),
    scene("village_to_city_pl", "Из деревни — на фабрику", ["sig_village_to_city_pl"], 1, "🧳", "уйти в город", "icon_ally",
          ["кто уходит"], "leave_for_village"),
    scene("factory_floor_pl", "Ткацкий цех", ["sig_factory_floor_pl"], 2, "🏭", "запустить станки", "icon_crown",
          ["фабрикант", "рабочий"], "valmy_mill"),
    scene("lodz_strike_pl", "Забастовка", ["sig_lodz_strike_pl"], 2, "✊", "бросить работу", "icon_plot",
          ["рабочий", "фабрикант"], "bread_riots"),
]
NEW_RULES += [
    rule("customs_lifted_pl_sig", "Граница с Россией открыта для товара — польские ткани едут до самого Тихого океана",
         "sig_customs_lifted_pl",
         [actor("A", 0, tags=["customs_pl"]), actor("B", 1, tags=["factory_pl"])],
         [setf("B", "russian_market_pl")]),
    rule("village_to_city_pl_sig", "Освобождённый крестьянин уходит в Лодзь — и становится рабочим",
         "sig_village_to_city_pl",
         [actor("A", 0, tags=["peasant_serf_pl"])],
         [setf("A", "factory_hand_pl")]),
    rule("factory_floor_peasant_pl_sig", "Фабрикант ставит вчерашнего крестьянина к станку",
         "sig_factory_floor_pl",
         [actor("A", 0, tags=["factory_pl"], flags=["russian_market_pl"]), actor("B", 1, tags=["peasant_serf_pl"], flags=["factory_hand_pl"])],
         [setf("A", "empire_pl")]),
    rule("factory_floor_weaver_pl_sig", "Станки гудят день и ночь — ткачихи работают по двенадцать часов",
         "sig_factory_floor_pl",
         [actor("A", 0, tags=["factory_pl"], flags=["russian_market_pl"]), actor("B", 1, tags=["worker_pl"])],
         [setf("A", "empire_pl")]),
    rule("lodz_strike_pl_sig", "Рабочие бросают станки — фабрика встаёт",
         "sig_lodz_strike_pl",
         [actor("A", 0, tags=["worker_pl"]), actor("B", 1, tags=["factory_pl"])],
         [setf("B", "halted_pl")]),
]
NEW_LEVELS.append(level(
    "lodz_1880", 455, ACT6, "poland_tension", "factory_floor_pl", 2,
    ["customs_lifted_pl", "village_to_city_pl", "factory_floor_pl", "lodz_strike_pl"],
    ["poznanski", "weaver_pl", "peasant_pl", "customs_ru"],
    {"poznanski": ["standing"]}, [],
    [flag("poznanski", "empire_pl"), nflag("poznanski", "halted_pl")],
    [("customs_lifted_pl", ["customs_ru", "poznanski"]), ("factory_floor_pl", ["poznanski", "weaver_pl"])],
    "simplification"))
TEXTS.update(texts("lodz_1880",
    "Земля обетованная",
    "Из деревни вырастает Лодзь — «польский Манчестер», где фабриканты строят дворцы, а ткачихи стоят у станков по двенадцать часов",
    "Ткани нужен покупатель — а самый большой покупатель за восточной таможней. Рабочих руки не хватит, если они бросят работу.",
    "Вторая половина XIX века. Польши нет на карте, но в Царстве Польском дымят трубы. Ещё недавно Лодзь была деревней, а теперь сюда едут поляки, евреи, немцы — строить фабрики и работать на них. Израиль Познанский начинал с лавки, а теперь строит ткацкую империю.",
    "В 1851 году таможенную границу между Царством Польским и Россией сняли, и огромный рынок империи открылся для польских тканей. После отмены крепостного права в 1864 году в Лодзь хлынули крестьяне. Город рос быстрее любого в Европе: несколько сотен жителей в 1820 году — около 300 тысяч к 1900-му. Познанский построил фабрики, рабочие дома и дворец, который называли «лодзинским Лувром». В 1892 году лодзинские рабочие подняли одну из первых массовых забастовок в империи. Владислав Реймонт описал этот город в романе «Земля обетованная», а в 1924 году получил Нобелевскую премию.",
    "Владислав Реймонт, «Земля обетованная» (1899)"))

# ================================================================ flying_university_1885
NEW_SCENES += [
    scene("secret_courses_pl", "Тайные курсы", ["sig_secret_courses_pl"], 1, "🕯️", "собрать курсы на квартире", "icon_ally",
          ["устроительница"], "mothers_school_pl"),
    scene("move_flat_pl", "Переезд на новую квартиру", ["sig_move_flat_pl"], 1, "🧳", "сменить адрес", "icon_ally",
          ["устроительница"], "back_room"),
    scene("secret_lecture_pl", "Лекция по химии", ["sig_secret_lecture_pl"], 2, "⚗️", "учить", "icon_crown",
          ["преподаватель", "слушательница"], "salon_c"),
    scene("gendarme_raid_pl", "Обыск", ["sig_gendarme_raid_pl"], 2, "🚨", "нагрянуть с обыском", "icon_dead",
          ["жандарм", "устроительница"], "cellar_search"),
    bait("go_paris_pl", "Уехать учиться в Париж", "v_flee", 1, "foreign_passport", ["кто уезжает"]),
]
NEW_RULES += [
    rule("secret_courses_pl_sig", "Ядвига Давидова собирает на частной квартире курсы для женщин — университет им закрыт",
         "sig_secret_courses_pl",
         [actor("A", 0, tags=["educator_pl"])],
         [setf("A", "courses_pl")]),
    rule("move_flat_pl_sig", "Курсы каждую неделю кочуют с квартиры на квартиру — полиция не успевает",
         "sig_move_flat_pl",
         [actor("A", 0, tags=["educator_pl"], flags=["courses_pl"])],
         [setf("A", "moving_pl")]),
    rule("gendarme_raid_pl_sig", "Жандарм накрывает курсы, пока они сидят на одном месте",
         "sig_gendarme_raid_pl",
         [actor("A", 0, tags=["gendarme_pl"]), actor("B", 1, tags=["educator_pl"], notFlags=["moving_pl"])],
         [setf("B", "caught_pl")]),
    rule("secret_lecture_pl_sig", "Профессора тайком читают девушкам химию и физику — по-польски",
         "sig_secret_lecture_pl",
         [actor("A", 0, tags=["educator_pl"], flags=["moving_pl"], notFlags=["caught_pl"]),
          actor("B", 1, tags=["scientist_pl"], notFlags=["away"])],
         [setf("B", "educated_pl")]),
]
NEW_LEVELS.append(level(
    "flying_university_1885", 458, ACT6, "poland_tension", "secret_lecture_pl", 3,
    ["secret_courses_pl", "move_flat_pl", "secret_lecture_pl", "gendarme_raid_pl", "go_paris_pl"],
    ["dawidowa", "sklodowska", "gendarme_ru"],
    {"gendarme_ru": ["standing", "strong"]}, [],
    [flag("sklodowska", "educated_pl"), nflag("dawidowa", "caught_pl")],
    [("secret_courses_pl", ["dawidowa"]), ("move_flat_pl", ["dawidowa"]), ("secret_lecture_pl", ["dawidowa", "sklodowska"])],
    "fact"))
TEXTS.update(texts("flying_university_1885",
    "Летучий университет",
    "Женщинам в Варшаве учиться запрещено — и тайный университет кочует по квартирам, где училась юная Мария Склодовская",
    "Тайну хранит не замок, а движение: на одном месте курсы не продержатся. В Париж Мария ещё успеет — сначала здесь.",
    "1885 год. Варшава в Российской империи. В университете преподают только по-русски, а женщин туда не берут вовсе. Учительница Ядвига Давидова решает: если нельзя открыто — будем учить тайно.",
    "С 1885 года Давидова организовала подпольные курсы, которые прозвали «Летучим университетом»: занятия проходили в частных квартирах и каждый раз в новом месте, чтобы не попасться полиции. Читали лучшие варшавские профессора — историю, химию, физику, философию — по-польски. Через курсы прошли тысячи женщин; среди них — Мария Склодовская, которая в 1891 году уехала в Париж и позже стала первой женщиной — лауреатом Нобелевской премии, причём дважды. В 1906 году университет вышел из подполья как Общество научных курсов.",
    "Мария Склодовская-Кюри, «Автобиографические заметки»"))

if __name__ == "__main__":
    P.NEW_CHARS, P.NEW_SCENES, P.NEW_RULES, P.NEW_LEVELS, P.TEXTS = NEW_CHARS, NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS
    P.CHAPTER_TEXTS = {}
    P.main()
