#!/usr/bin/env python3
"""Пачка 5 главы «Польша»: разделы и 123 года без государства, 1764–1918, 18 уровней.

    python3 tools/batches/poland_5.py [repo_root]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, level, texts
from poland_4 import bait, PARLEY, BATTLE

ACT5 = "Акт V · Разделы"
ACT6 = "Акт VI · Без государства"

NEW_CHARS = [
    char("catherine2_pl", "Императрица Екатерина II", ["empress_pl"], "👑"),
    char("repnin", "Посол Николай Репнин", ["ambassador_pl"], "📜"),
    char("poniatowski", "Король Станислав Август", ["sa_king_pl"], "👑"),
    char("frederick_great", "Король Фридрих II Прусский", ["prussia_king_pl"], "👑"),
    char("maria_theresa", "Императрица Мария Терезия", ["austria_pl"], "👑"),
    char("rejtan", "Тадеуш Рейтан", ["rejtan_pl"], "🚪"),
    char("kollataj", "Гуго Коллонтай", ["reformer_pl"], "📜"),
    char("malachowski", "Маршалок Станислав Малаховский", ["marshal_g_pl"], "🔔"),
    char("kosciuszko", "Тадеуш Костюшко", ["kosciuszko_pl"], "⚔️"),
    char("glowacki", "Войцех Бартош-Гловацкий", ["scytheman_pl"], "🌾"),
    char("tormasov", "Генерал Александр Тормасов", ["rus_gen_pl"], "⚔️"),
    char("fersen_gen", "Генерал Иван Ферзен", ["rus_gen_f_pl"], "⚔️"),
    char("suvorov_pl", "Генерал Александр Суворов", ["suvorov_pl"], "⚔️"),
    char("dabrowski", "Генерал Ян Генрик Домбровский", ["legion_gen_pl"], "🦅"),
    char("wybicki", "Юзеф Выбицкий", ["poet_pl"], "🎵"),
    char("napoleon_pl", "Наполеон Бонапарт", ["bonaparte_pl"], "👑"),
    char("walewska", "Мария Валевская", ["countess_pl"], "💐"),
    char("jozef_poniatowski", "Князь Юзеф Понятовский", ["prince_j_pl"], "⚔️"),
    char("kozietulski", "Ян Козетульский", ["chevau_pl"], "🐎"),
    char("spanish_gunner", "Испанский артиллерист", ["gunner_es_pl"], "💥"),
    char("wysocki", "Подпоручик Пётр Высоцкий", ["cadet_pl"], "🔥"),
    char("konstantin_pl", "Великий князь Константин", ["grand_duke_pl"], "👑"),
    char("nicholas1_pl", "Император Николай I", ["tsar_n_pl"], "👑"),
    char("chlopicki", "Генерал Юзеф Хлопицкий", ["gen_pl"], "⚔️"),
    char("ordon", "Подпоручик Юлиан Ордон", ["gunner_pl"], "💥"),
    char("diebitsch", "Фельдмаршал Иван Дибич", ["marshal_r_pl"], "⚔️"),
    char("chopin", "Фредерик Шопен", ["composer_pl"], "🎹"),
    char("ludwika", "Людвика Шопен", ["sister_pl"], "🫙"),
    char("customs_ru", "Таможенник", ["customs_pl"], "🛃"),
    char("traugutt", "Ромуальд Траугутт", ["dictator_pl"], "🕯️"),
    char("alexander2_pl", "Император Александр II", ["tsar_a_pl"], "👑"),
    char("sklodowska", "Мария Склодовская-Кюри", ["scientist_pl"], "⚗️"),
    char("pierre_curie", "Пьер Кюри", ["scientist_fr_pl"], "⚗️"),
    char("pupil_wrzesnia", "Школьник из Вжесни", ["pupil_pl"], "🎒"),
    char("mother_wrzesnia", "Мать школьника", ["mother_pl"], "👩"),
    char("teacher_de", "Прусский учитель", ["teacher_pl"], "📏"),
    char("drzymala", "Михал Джимала", ["peasant_d_pl"], "🛞"),
    char("prussian_official", "Прусский чиновник", ["official_pl"], "📋"),
    char("pilsudski", "Юзеф Пилсудский", ["pilsudski_pl"], "🎖️"),
    char("beseler", "Генерал-губернатор Безелер", ["gov_gen_pl"], "🪖"),
    char("paderewski", "Игнаций Падеревский", ["pianist_pl"], "🎹"),
    char("wilson", "Президент Вудро Вильсон", ["president_pl"], "🇺🇸"),
    char("house_col", "Полковник Хаус", ["adviser_pl"], "🎩"),
    char("regent_kakowski", "Регент, архиепископ Каковский", ["regent_pl"], "⛪"),
    char("german_officer", "Немецкий офицер", ["garrison_pl"], "🪖"),
]

NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS = [], [], [], {}

def one(id, name, tag, emoji, action, icon, role, donor):
    return scene(id, name, [tag], 1, emoji, action, icon, [role], donor)

def two(id, name, tag, emoji, action, icon, roles, donor):
    return scene(id, name, [tag], 2, emoji, action, icon, roles, donor)

# ================================================================ poniatowski_1764
NEW_SCENES += [
    two("petersburg_love_pl", "Петербургский роман", "sig_petersburg_love_pl", "💌", "влюбиться", "icon_ally",
        ["великая княгиня", "поляк"], "buduar"),
    two("election_1764_pl", "Элекция при русских войсках", "sig_election_1764_pl", "🗳️", "избрать", "icon_crown",
        ["посол", "кандидат"], "praetorian_camp"),
    two("repnin_dictates_pl", "Посол диктует сейму", "sig_repnin_dictates_pl", "📜", "диктовать", "icon_plot",
        ["посол", "король"], "court_min"),
    bait("marry_empress_pl", "Жениться на императрице", "v_wed", 2, "nea_wedding", ["жених", "невеста"]),
]
NEW_RULES += [
    rule("petersburg_love_pl_sig", "Молодой польский дипломат становится возлюбленным будущей императрицы",
         "sig_petersburg_love_pl",
         [actor("A", 0, tags=["empress_pl"]), actor("B", 1, tags=["sa_king_pl"])],
         [setf("B", "favourite_pl")]),
    rule("election_1764_pl_sig", "Её бывшего возлюбленного избирают королём — под охраной русских войск",
         "sig_election_1764_pl",
         [actor("A", 0, tags=["ambassador_pl"]), actor("B", 1, tags=["sa_king_pl"], flags=["favourite_pl"])],
         [setf("B", "crowned"), setf("B", "reigns"), setf("B", "protege_pl")]),
    rule("repnin_dictates_pl_sig", "Посол императрицы арестует несогласных сенаторов и диктует законы — король лишь подписывает",
         "sig_repnin_dictates_pl",
         [actor("A", 0, tags=["ambassador_pl"]), actor("B", 1, tags=["sa_king_pl"], flags=["protege_pl"])],
         [setf("B", "dictated_pl")]),
]
NEW_LEVELS.append(level(
    "poniatowski_1764", 340, ACT5, "poland_tension", "election_1764_pl", 3,
    ["petersburg_love_pl", "election_1764_pl", "repnin_dictates_pl", "marry_empress_pl"],
    ["catherine2_pl", "poniatowski", "repnin"],
    {"catherine2_pl": ["crowned", "reigns", "standing"], "repnin": ["standing", "strong"]}, [],
    [flag("poniatowski", "dictated_pl"), nflag("poniatowski", "married")],
    [("petersburg_love_pl", ["catherine2_pl", "poniatowski"]), ("election_1764_pl", ["repnin", "poniatowski"]),
     ("repnin_dictates_pl", ["repnin", "poniatowski"])],
    "simplification"))
TEXTS.update(texts("poniatowski_1764",
    "Король по протекции",
    "Бывший возлюбленный императрицы становится королём Польши — и выясняет, что править за него будет её посол",
    "Сначала роман, потом корона. Жениться на императрице он мечтал, но этого не случилось. Король по протекции подписывает то, что ему диктуют.",
    "1755 год, Петербург. Молодой польский аристократ Станислав Понятовский служит секретарём британского посла и влюбляется в великую княгиню Екатерину. Через девять лет она — императрица, а в Польше выбирают короля.",
    "Понятовский был возлюбленным Екатерины в 1755–1758 годах. 7 сентября 1764 года его избрали королём, пока у Варшавы стояли русские войска; Екатерина писала, что «сделала» его королём. В 1767–1768 годах русский посол Николай Репнин арестовал и выслал в Калугу епископов Солтыка и Залуского и гетмана Ржевуского, выступивших против него, и заставил сейм принять законы под гарантией России. Станислав Август был умным, образованным королём-покровителем искусств — и правил в стране, которой всё меньше распоряжалась она сама.",
    "Мемуары Станислава Августа; письма Екатерины II"))

# ================================================================ first_partition_1772
NEW_SCENES += [
    scene("partition_pact_pl", "Договор трёх держав", ["sig_partition_pact_pl"], 3, "✂️", "поделить соседа", "icon_plot",
          ["императрица", "король", "императрица"], "angers_pact"),
    one("rejtan_door_pl", "Рейтан в дверях", "sig_rejtan_door_pl", "🚪", "лечь на пороге", "icon_ally", "посол", "church_door_t"),
    two("ratify_partition_pl", "Сейм утверждает раздел", "sig_ratify_partition_pl", "📜", "утвердить", "icon_dead",
        ["посол", "держава"], "council_b"),
    bait("stop_by_force_pl", "Остановить силой", "v_battle", 2, "battlefield", BATTLE),
]
NEW_RULES += [
    rule("partition_pact_pl_sig", "Россия, Пруссия и Австрия договариваются отрезать от Речи Посполитой по куску",
         "sig_partition_pact_pl",
         [actor("A", 0, tags=["empress_pl"]), actor("B", 1, tags=["prussia_king_pl"]), actor("C", 2, tags=["austria_pl"])],
         [setf("A", "partitioner_pl"), setf("B", "partitioner_pl"), setf("C", "partitioner_pl")]),
    rule("rejtan_door_pl_sig", "Посол ложится на пороге зала, не давая депутатам выйти и утвердить раздел",
         "sig_rejtan_door_pl",
         [actor("A", 0, tags=["rejtan_pl"], notFlags=["defeated"])],
         [setf("A", "protest_pl")]),
    rule("ratify_partition_pl_sig", "Перешагнув через протестующего, сейм под охраной войск утверждает раздел",
         "sig_ratify_partition_pl",
         [actor("A", 0, tags=["rejtan_pl"], flags=["protest_pl"]), actor("B", 1, tags=["empress_pl"], flags=["partitioner_pl"])],
         [setf("B", "ratified_pl")]),
]
NEW_LEVELS.append(level(
    "first_partition_1772", 350, ACT5, "poland_tension", "rejtan_door_pl", 3,
    ["partition_pact_pl", "rejtan_door_pl", "ratify_partition_pl", "stop_by_force_pl"],
    ["catherine2_pl", "frederick_great", "maria_theresa", "rejtan"],
    {"catherine2_pl": ["crowned", "standing"], "frederick_great": ["crowned", "standing", "strong"],
     "maria_theresa": ["crowned", "standing"], "rejtan": ["standing"]},
    [("enemy_of", "rejtan", "frederick_great"), ("enemy_of", "frederick_great", "rejtan")],
    [flag("catherine2_pl", "ratified_pl"), flag("maria_theresa", "partitioner_pl"), flag("rejtan", "protest_pl")],
    [("partition_pact_pl", ["catherine2_pl", "frederick_great", "maria_theresa"]), ("rejtan_door_pl", ["rejtan"]),
     ("ratify_partition_pl", ["rejtan", "catherine2_pl"])],
    "fact"))
TEXTS.update(texts("first_partition_1772",
    "Первый раздел",
    "Три соседа договариваются поделить Речь Посполитую, и одинокий посол ложится на пороге сейма — но раздел всё равно утверждают",
    "Делят трое — и все трое должны договориться. Протест одного человека не остановит раздел, но в истории он остался. Остановить силой? Против прусской армии — нечем.",
    "1772 год. Речь Посполитая ослаблена войной конфедератов и чужими армиями. Россия, Пруссия и Австрия решают взять себе по куску её земель — и заставить сейм это утвердить.",
    "5 августа 1772 года в Петербурге три державы подписали конвенцию: Польша теряла около трети территории и трети населения. В 1773 году сейм под охраной иностранных войск должен был утвердить раздел; посол Тадеуш Рейтан лёг на пороге зала, крича «Убейте меня, но не убивайте Отчизну!», — его перешагнули. Фридрих II сказал о Марии Терезии, долго колебавшейся: «Плакала, но брала». Ян Матейко написал «Рейтана» в 1866 году, и картина висит в Королевском замке в Варшаве.",
    "Петербургская конвенция 1772 г.; дневник сейма 1773 г."))

# ================================================================ may3_1791
NEW_SCENES += [
    two("secret_draft_pl", "Тайный проект", "sig_secret_draft_pl", "✍️", "написать конституцию", "icon_plot",
        ["король", "реформатор"], "anekdota_desk"),
    one("easter_recess_pl", "Пасхальные каникулы", "sig_easter_recess_pl", "🐣", "собрать сторонников", "icon_ally",
        "маршалок", "council"),
    two("vote_may3_pl", "Голосование 3 мая", "sig_vote_may3_pl", "📜", "принять конституцию", "icon_crown",
        ["маршалок", "король"], "council_b"),
    one("full_house_pl", "Ждать полного сейма", "sig_full_house_pl", "⏳", "ждать", "icon_plot", "маршалок", "court_min"),
]
NEW_RULES += [
    rule("secret_draft_pl_sig", "Король с реформаторами тайком пишет новую конституцию",
         "sig_secret_draft_pl",
         [actor("A", 0, tags=["sa_king_pl"]), actor("B", 1, tags=["reformer_pl"])],
         [setf("A", "drafted_pl")]),
    rule("easter_recess_pl_sig", "Голосование назначают на день, когда противники ещё не вернулись с пасхальных каникул",
         "sig_easter_recess_pl",
         [actor("A", 0, tags=["marshal_g_pl"], notFlags=["full_house_pl"])],
         [setf("A", "few_present_pl")]),
    rule("full_house_pl_sig", "Маршалок ждёт, пока соберутся все, — и оппозиция успевает приготовиться",
         "sig_full_house_pl",
         [actor("A", 0, tags=["marshal_g_pl"], notFlags=["few_present_pl"])],
         [setf("A", "full_house_pl")]),
    rule("vote_may3_pl_sig", "Под крики «Виват король, виват конституция!» закон принят",
         "sig_vote_may3_pl",
         [actor("A", 0, tags=["marshal_g_pl"], flags=["few_present_pl"]), actor("B", 1, tags=["sa_king_pl"], flags=["drafted_pl"])],
         [setf("B", "constitution_pl")]),
]
NEW_LEVELS.append(level(
    "may3_1791", 360, ACT5, "poland_ceremony", "vote_may3_pl", 3,
    ["secret_draft_pl", "easter_recess_pl", "vote_may3_pl", "full_house_pl"],
    ["poniatowski", "kollataj", "malachowski"],
    {"poniatowski": ["crowned", "reigns", "standing"], "malachowski": ["standing"]}, [],
    [flag("poniatowski", "constitution_pl")],
    [("secret_draft_pl", ["poniatowski", "kollataj"]), ("easter_recess_pl", ["malachowski"]),
     ("vote_may3_pl", ["malachowski", "poniatowski"])],
    "simplification"))
TEXTS.update(texts("may3_1791",
    "Конституция 3 мая",
    "Король и реформаторы тайком пишут конституцию и проводят её в день, когда противники ещё на пасхальных каникулах",
    "Если ждать, пока соберутся все, конституции не будет. Сначала проект, потом удобный день, потом голосование.",
    "1788–1791 годы, Четырёхлетний сейм. После первого раздела реформаторы хотят спасти государство: отменить liberum veto, сделать трон наследственным, усилить армию. Против — магнаты, которым выгоден старый порядок, и соседи.",
    "3 мая 1791 года в Королевском замке в Варшаве сейм принял Конституцию, подготовленную королём Станиславом Августом, Гуго Коллонтаем, Игнацием Потоцким и маршалком Станиславом Малаховским; заседание назначили, когда многие противники ещё не вернулись с пасхальных каникул. Это первая в Европе и вторая в мире, после американской, писаная конституция современного типа: она отменила liberum veto и вольную элекцию. Прожила она четырнадцать месяцев: противники создали Тарговицкую конфедерацию, позвали русскую армию, и в 1793 году последовал второй раздел. 3 мая — национальный праздник Польши.",
    "Устава правительственная 3 мая 1791 г."))

# ================================================================ kosciuszko_1794
NEW_SCENES += [
    one("krakow_oath_1794_pl", "Присяга на Рынке", "sig_krakow_oath_1794_pl", "✋", "поклясться народу", "icon_crown",
        "начальник", "take_oath"),
    two("scythemen_pl", "Косиньеры", "sig_scythemen_pl", "🌾", "поставить косы торчком", "icon_ally",
        ["начальник", "крестьянин"], "deulino_village"),
    two("raclawice_guns_pl", "Батарея под Рацлавице", "sig_raclawice_guns_pl", "💥", "взять пушки", "icon_dead",
        ["косиньер", "враг"], "open_battle_s"),
    bait("regular_attack_pl", "Лобовая атака регулярного войска", "v_battle", 2, "open_battle", BATTLE),
]
NEW_RULES += [
    rule("krakow_oath_1794_pl_sig", "На краковском Рынке генерал клянётся народу — и становится Начальником восстания",
         "sig_krakow_oath_1794_pl",
         [actor("A", 0, tags=["kosciuszko_pl"], notFlags=["defeated"])],
         [setf("A", "naczelnik_pl"), setf("A", "strong")]),
    rule("scythemen_pl_sig", "Начальник зовёт крестьян; косы, перекованные торчком, становятся пиками",
         "sig_scythemen_pl",
         [actor("A", 0, tags=["kosciuszko_pl"], flags=["naczelnik_pl"]), actor("B", 1, tags=["scytheman_pl"])],
         [setf("B", "kosynier_pl")]),
    rule("raclawice_guns_pl_sig", "Косиньеры бегом бросаются на батарею и берут пушки",
         "sig_raclawice_guns_pl",
         [actor("A", 0, tags=["scytheman_pl"], flags=["kosynier_pl"]), actor("B", 1, tags=["rus_gen_pl"])],
         [setf("B", "defeated"), setf("A", "hero_pl")]),
]
NEW_LEVELS.append(level(
    "kosciuszko_1794", 370, ACT5, "poland_battle", "raclawice_guns_pl", 3,
    ["krakow_oath_1794_pl", "scythemen_pl", "raclawice_guns_pl", "regular_attack_pl"],
    ["kosciuszko", "glowacki", "tormasov"],
    {"kosciuszko": ["standing"], "tormasov": ["standing", "strong"]},
    [("enemy_of", "kosciuszko", "tormasov"), ("enemy_of", "tormasov", "kosciuszko")],
    [flag("tormasov", "defeated"), flag("glowacki", "hero_pl"), nflag("kosciuszko", "defeated")],
    [("krakow_oath_1794_pl", ["kosciuszko"]), ("scythemen_pl", ["kosciuszko", "glowacki"]),
     ("raclawice_guns_pl", ["glowacki", "tormasov"])],
    "simplification"))
TEXTS.update(texts("kosciuszko_1794",
    "Рацлавице",
    "Генерал клянётся народу на краковском Рынке, зовёт крестьян с косами — и косиньеры берут вражескую батарею",
    "Регулярное войско в лоб не взять. Крестьяне пойдут за тем, кто поклялся народу. А пушки берут те, у кого косы.",
    "1794 год. После второго раздела от Речи Посполитой остался обрубок. Генерал Тадеуш Костюшко — герой американской войны за независимость — возвращается в Краков, чтобы поднять восстание. Регулярной армии почти нет.",
    "24 марта 1794 года Костюшко принёс присягу на краковском Рынке и стал Начальником восстания. 4 апреля под Рацлавицами отряды косиньеров — крестьян с косами, насаженными торчком, — бегом взяли русскую батарею генерала Тормасова. Войцех Бартош, по преданию, первым добежал до пушки и загасил фитиль своей шапкой; его произвели в офицеры, а погиб он через два месяца. Костюшко в знак уважения носил крестьянскую сукману. «Рацлавицкая панорама» — огромное круговое полотно 1894 года — сегодня во Вроцлаве.",
    "Реляции Костюшко 1794 г.; Ю. Немцевич, «Записки»"))

# ================================================================ maciejowice_1794
NEW_SCENES += [
    two("maciejowice_field_pl", "Мацеёвице", "sig_maciejowice_field_pl", "⚔️", "разбить", "icon_dead",
        ["генерал", "начальник"], "battlefield"),
    one("praga_storm_pl", "Штурм Праги", "sig_praga_storm_pl", "🔥", "штурмовать предместье", "icon_dead",
        "генерал", "fire_night"),
    one("finis_poloniae_pl", "«Finis Poloniae!»", "sig_finis_poloniae_pl", "💬", "крикнуть", "icon_plot",
        "начальник", "death_in_line"),
    bait("kosciuszko_flee_pl", "Уйти с поля", "v_flee", 1, "exile_road", ["кто уходит"]),
]
NEW_RULES += [
    rule("maciejowice_field_pl_sig", "Войско Начальника разбито, сам он ранен и взят в плен",
         "sig_maciejowice_field_pl",
         [actor("A", 0, tags=["rus_gen_f_pl"]), actor("B", 1, tags=["kosciuszko_pl"], notFlags=["away"])],
         [setf("B", "captured_pl"), setf("B", "defeated")]),
    rule("praga_storm_pl_sig", "Армия штурмует Прагу, предместье Варшавы; через несколько дней столица капитулирует",
         "sig_praga_storm_pl",
         [actor("A", 0, tags=["suvorov_pl"])],
         [setf("A", "praga_pl")]),
    rule("finis_poloniae_pl_sig", "Падая с коня, раненый будто бы кричит «Конец Польши!»",
         "sig_finis_poloniae_pl",
         [actor("A", 0, tags=["kosciuszko_pl"])],
         [setf("A", "finis_said_pl")]),
]
NEW_LEVELS.append(level(
    "maciejowice_1794", 380, ACT5, "poland_tension", "maciejowice_field_pl", 2,
    ["maciejowice_field_pl", "praga_storm_pl", "finis_poloniae_pl", "kosciuszko_flee_pl"],
    ["kosciuszko", "fersen_gen", "suvorov_pl"],
    {"kosciuszko": ["standing"], "fersen_gen": ["standing", "strong"], "suvorov_pl": ["standing", "strong"]}, [],
    [flag("kosciuszko", "captured_pl"), flag("suvorov_pl", "praga_pl"), nflag("kosciuszko", "finis_said_pl")],
    [("maciejowice_field_pl", ["fersen_gen", "kosciuszko"]), ("praga_storm_pl", ["suvorov_pl"])],
    "simplification"))
TEXTS.update(texts("maciejowice_1794",
    "Мацеёвице",
    "Раненый Начальник попадает в плен, Варшава капитулирует — и через год Речь Посполитая исчезает с карты",
    "Начальник не бежал с поля. И знаменитых слов «Finis Poloniae» он, по его собственному письму, не говорил — не повторяйте легенду.",
    "Октябрь 1794 года. Восстание держится полгода. К Варшаве идут армии с востока и запада. Костюшко пытается не дать соединиться русским корпусам Ферзена и Суворова.",
    "10 октября 1794 года под Мацеёвицами войско Костюшко было разбито, сам он, раненый, попал в плен и был увезён в Петербург. Фраза «Finis Poloniae!» — «Конец Польши!», — которую ему приписывали, по его собственному письму 1803 года, им не произносилась. 4 ноября войска Суворова штурмовали Прагу, предместье Варшавы; погибли тысячи жителей, и столица капитулировала. 24 октября 1795 года третий раздел стёр Речь Посполитую с карты. Костюшко, освобождённый в 1796 году, уехал в Америку, а в завещании просил отпустить на волю рабов своего друга Джефферсона — тот волю не исполнил.",
    "Т. Костюшко, письмо к Сегюру (1803); Ю. Немцевич, «Записки»"))

# ================================================================ mazurek_1797
NEW_SCENES += [
    two("legions_italy_pl", "Легионы в Италии", "sig_legions_italy_pl", "🦅", "собрать легионы", "icon_ally",
        ["генерал", "Бонапарт"], "march_on_rome_g"),
    two("reggio_song_pl", "Песня в Реджо-Эмилии", "sig_reggio_song_pl", "🎵", "сочинить песню", "icon_crown",
        ["поэт", "генерал"], "barberini_ode"),
    bait("go_home_pl", "Вернуться домой", "v_flee", 1, "exile_road", ["кто уходит"]),
]
NEW_RULES += [
    rule("legions_italy_pl_sig", "С позволения Бонапарта польский генерал собирает в Италии легионы из пленных и эмигрантов",
         "sig_legions_italy_pl",
         [actor("A", 0, tags=["legion_gen_pl"], notFlags=["away"]), actor("B", 1, tags=["bonaparte_pl"])],
         [setf("A", "legions_pl")]),
    rule("reggio_song_pl_sig", "Для легионеров поэт пишет песню: «Ещё Польша не погибла, пока мы живы»",
         "sig_reggio_song_pl",
         [actor("A", 0, tags=["poet_pl"]), actor("B", 1, tags=["legion_gen_pl"], flags=["legions_pl"])],
         [setf("A", "mazurek_pl")]),
]
NEW_LEVELS.append(level(
    "mazurek_1797", 390, ACT6, "poland_ceremony", "reggio_song_pl", 2,
    ["legions_italy_pl", "reggio_song_pl", "go_home_pl"],
    ["dabrowski", "wybicki", "napoleon_pl"],
    {"dabrowski": ["standing"], "napoleon_pl": ["standing", "strong"]}, [],
    [flag("wybicki", "mazurek_pl")],
    [("legions_italy_pl", ["dabrowski", "napoleon_pl"]), ("reggio_song_pl", ["wybicki", "dabrowski"])],
    "fact"))
TEXTS.update(texts("mazurek_1797",
    "Мазурка Домбровского",
    "Польские легионы собираются в Италии под знамёнами Бонапарта — и для них пишут песню, которая станет гимном",
    "Песня нужна войску — значит, сначала войско. Вернуться домой им некуда: государства больше нет.",
    "1797 год. Польши на карте нет. Генерал Ян Генрик Домбровский едет к молодому генералу Бонапарту, побеждающему австрийцев в Италии, и просит позволения собрать польские легионы — из эмигрантов и пленных поляков, служивших в австрийской армии.",
    "В январе 1797 года в Милане начали формироваться Польские легионы. В июле в Реджо-Эмилии Юзеф Выбицкий написал для них «Песнь польских легионов в Италии»: «Ещё Польша не погибла, пока мы живы… Марш, марш, Домбровский, из земли итальянской в польскую». Песня мгновенно разошлась, а в 1927 году стала государственным гимном — в нём до сих пор упомянут Бонапарт. Часть легионеров позже отправили подавлять восстание на Гаити, и некоторые перешли на сторону гаитян — их потомки живут там до сих пор.",
    "Ю. Выбицкий, «Песнь польских легионов» (1797)"))

# ================================================================ walewska_1807
NEW_SCENES += [
    two("patriots_plea_pl", "Уговоры патриотов", "sig_patriots_plea_pl", "🇵🇱", "просить ради Польши", "icon_plot",
        ["князь", "графиня"], "court_whisper"),
    two("emperor_romance_pl", "Роман с императором", "sig_emperor_romance_pl", "💐", "очаровать", "icon_ally",
        ["графиня", "император"], "buduar"),
    two("duchy_warsaw_pl", "Варшавское герцогство", "sig_duchy_warsaw_pl", "🦅", "создать герцогство", "icon_crown",
        ["император", "князь"], "treaty_king"),
    bait("emperor_wedding_pl", "Свадьба с императором", "v_wed", 2, "louvre_wedding", ["жених", "невеста"]),
]
NEW_RULES += [
    rule("patriots_plea_pl_sig", "Патриоты уговаривают молодую графиню принять ухаживания императора — ради Польши",
         "sig_patriots_plea_pl",
         [actor("A", 0, tags=["prince_j_pl"]), actor("B", 1, tags=["countess_pl"])],
         [setf("B", "for_poland_pl")]),
    rule("emperor_romance_pl_sig", "Император влюблён — и готов слушать о польских делах",
         "sig_emperor_romance_pl",
         [actor("A", 0, tags=["countess_pl"], flags=["for_poland_pl"], notFlags=["married"]),
          actor("B", 1, tags=["bonaparte_pl"])],
         [setf("B", "beloved_pl")]),
    rule("duchy_warsaw_pl_sig", "Император создаёт Варшавское герцогство — не королевство, о котором мечтали",
         "sig_duchy_warsaw_pl",
         [actor("A", 0, tags=["bonaparte_pl"], flags=["beloved_pl"]), actor("B", 1, tags=["prince_j_pl"])],
         [setf("B", "duchy_pl")]),
]
NEW_LEVELS.append(level(
    "walewska_1807", 400, ACT6, "poland_romance", "emperor_romance_pl", 3,
    ["patriots_plea_pl", "emperor_romance_pl", "duchy_warsaw_pl", "emperor_wedding_pl"],
    ["napoleon_pl", "walewska", "jozef_poniatowski"],
    {"napoleon_pl": ["crowned", "standing", "strong"], "jozef_poniatowski": ["standing"]}, [],
    [flag("jozef_poniatowski", "duchy_pl"), nflag("walewska", "married")],
    [("patriots_plea_pl", ["jozef_poniatowski", "walewska"]), ("emperor_romance_pl", ["walewska", "napoleon_pl"]),
     ("duchy_warsaw_pl", ["napoleon_pl", "jozef_poniatowski"])],
    "simplification"))
TEXTS.update(texts("walewska_1807",
    "Пани Валевская",
    "Патриоты уговаривают юную графиню стать возлюбленной Наполеона ради Польши — и император создаёт Варшавское герцогство",
    "Графиня не сама искала этой любви — её просили. Император на ней не женился: жену ему выбрали из Габсбургов. А герцогство получили не за любовь, а через неё.",
    "Январь 1807 года, Варшава. Наполеон разгромил Пруссию, и поляки надеются, что он восстановит их государство. На балу император замечает восемнадцатилетнюю графиню Марию Валевскую, жену пожилого шамбеляна.",
    "По воспоминаниям Валевской, польские патриоты убеждали её, что её благосклонность к императору — долг перед родиной. 7 июля 1807 года по Тильзитскому миру Наполеон создал Варшавское герцогство — с конституцией и армией, но не королевство; военным министром стал князь Юзеф Понятовский. В 1810 году у Валевской родился сын Александр, позже министр иностранных дел Франции. В том же году император женился на Марии-Луизе Австрийской. Валевская навещала его на Эльбе.",
    "Мемуары М. Валевской; Тильзитский мир 1807 г."))

# ================================================================ somosierra_1808
NEW_SCENES += [
    two("emperor_order_pl", "Приказ императора", "sig_emperor_order_pl", "📣", "приказать атаковать", "icon_plot",
        ["император", "эскадрон"], "austerlitz_field"),
    two("somosierra_charge_pl", "Атака в ущелье", "sig_somosierra_charge_pl", "🐎", "взять батареи", "icon_dead",
        ["эскадрон", "батарея"], "devil_bridge"),
    one("mountain_detour_pl", "Обходить по горам", "sig_mountain_detour_pl", "⛰️", "обходить", "icon_plot",
        "император", "alps_pass"),
]
NEW_RULES += [
    rule("emperor_order_pl_sig", "Император, раздражённый задержкой, бросает на батареи польских шеволежеров",
         "sig_emperor_order_pl",
         [actor("A", 0, tags=["bonaparte_pl"], notFlags=["delayed_pl"]), actor("B", 1, tags=["chevau_pl"])],
         [setf("B", "ordered_pl")]),
    rule("somosierra_charge_pl_sig", "За восемь минут эскадрон проносится через четыре батареи в узком ущелье",
         "sig_somosierra_charge_pl",
         [actor("A", 0, tags=["chevau_pl"], flags=["ordered_pl"]), actor("B", 1, tags=["gunner_es_pl"])],
         [setf("B", "defeated"), setf("A", "hero_s_pl")]),
    rule("mountain_detour_pl_sig", "Пехота лезет в обход по горам — и армия теряет день",
         "sig_mountain_detour_pl",
         [actor("A", 0, tags=["bonaparte_pl"])],
         [setf("A", "delayed_pl")]),
]
NEW_LEVELS.append(level(
    "somosierra_1808", 410, ACT6, "poland_battle", "somosierra_charge_pl", 2,
    ["emperor_order_pl", "somosierra_charge_pl", "mountain_detour_pl"],
    ["napoleon_pl", "kozietulski", "spanish_gunner"],
    {"napoleon_pl": ["crowned", "standing", "strong"], "spanish_gunner": ["standing", "strong"]}, [],
    [flag("spanish_gunner", "defeated"), flag("kozietulski", "hero_s_pl")],
    [("emperor_order_pl", ["napoleon_pl", "kozietulski"]), ("somosierra_charge_pl", ["kozietulski", "spanish_gunner"])],
    "fact"))
TEXTS.update(texts("somosierra_1808",
    "Сомосьерра",
    "Польский эскадрон за восемь минут проносится через четыре испанские батареи в горном ущелье — и открывает Наполеону дорогу на Мадрид",
    "Обход по горам кажется разумным — но армия потеряет день. Атака невозможна, пока её не прикажут.",
    "30 ноября 1808 года, Испания. Дорогу на Мадрид перекрывает ущелье Сомосьерра: на серпантине четыре батареи испанской артиллерии. Пехота Наполеона застряла. Рядом с императором — эскадрон польских лёгкоконных шеволежеров гвардии.",
    "По приказу Наполеона третий эскадрон польских шеволежеров под командой Яна Козетульского атаковал вверх по ущелью, длиной около двух с половиной километров, и за семь-восемь минут взял все четыре батареи. Под Козетульским в начале атаки убили коня, последнюю батарею взял раненый поручик Анджей Незголевский. Атаке приписывают клич «Вперёд, собачья кровь, император смотрит!». Дорога на Мадрид была открыта, и Наполеон наградил эскадрон крестами Почётного легиона.",
    "Бюллетени Великой армии 1808 г.; А. Незголевский, «Поляки при Сомосьерре» (1854)"))

# ================================================================ belweder_1830
NEW_SCENES += [
    one("solec_fire_pl", "Пожар на Сольце — сигнал", "sig_solec_fire_pl", "🔥", "подать сигнал", "icon_plot",
        "подпоручик", "fire_night"),
    two("belweder_raid_pl", "Ночь на Бельведере", "sig_belweder_raid_pl", "🌙", "ворваться во дворец", "icon_plot",
        ["заговорщик", "великий князь"], "night_flight"),
    two("dethronement_pl", "«Нет Николая!»", "sig_dethronement_pl", "📜", "низложить императора", "icon_crown",
        ["повстанец", "император"], "abdication_table"),
    bait("kill_duke_pl", "Убить великого князя", "v_kill", 2, "dagger_oath", ["убийца", "жертва"]),
]
NEW_RULES += [
    rule("solec_fire_pl_sig", "Горит пивоварня на Сольце — условный сигнал: подхорунжие школы берут оружие",
         "sig_solec_fire_pl",
         [actor("A", 0, tags=["cadet_pl"])],
         [setf("A", "rising_pl")]),
    rule("belweder_raid_pl_sig", "Повстанцы врываются в Бельведер — великий князь прячется и бежит из Варшавы",
         "sig_belweder_raid_pl",
         [actor("A", 0, tags=["cadet_pl"], flags=["rising_pl"]), actor("B", 1, tags=["grand_duke_pl"])],
         [setf("B", "fled_b_pl"), setf("B", "away")]),
    rule("dethronement_pl_sig", "Сейм объявляет императора низложенным с польского трона",
         "sig_dethronement_pl",
         [actor("A", 0, tags=["cadet_pl"], flags=["rising_pl"]), actor("B", 1, tags=["tsar_n_pl"])],
         [setf("B", "dethroned_pl")]),
]
NEW_LEVELS.append(level(
    "belweder_1830", 420, ACT6, "poland_tension", "belweder_raid_pl", 3,
    ["solec_fire_pl", "belweder_raid_pl", "dethronement_pl", "kill_duke_pl"],
    ["wysocki", "konstantin_pl", "nicholas1_pl"],
    {"konstantin_pl": ["standing"], "nicholas1_pl": ["crowned", "reigns", "standing", "strong"]},
    [("enemy_of", "wysocki", "konstantin_pl"), ("enemy_of", "konstantin_pl", "wysocki")],
    [flag("konstantin_pl", "fled_b_pl"), flag("nicholas1_pl", "dethroned_pl"), nflag("konstantin_pl", "dead")],
    [("solec_fire_pl", ["wysocki"]), ("belweder_raid_pl", ["wysocki", "konstantin_pl"]),
     ("dethronement_pl", ["wysocki", "nicholas1_pl"])],
    "simplification"))
TEXTS.update(texts("belweder_1830",
    "Ноябрьская ночь",
    "Курсанты по сигналу пожара врываются в Бельведер, великий князь бежит — и сейм низлагает императора с польского трона",
    "Без сигнала никто не выйдет. Великий князь в ту ночь не погиб — он спрятался и бежал. А низлагали не кинжалом, а словом.",
    "1830 год. Царство Польское — с конституцией, армией и сеймом, но король его — российский император Николай I, а в Варшаве всем распоряжается его брат, великий князь Константин. В подхорунжевской школе зреет заговор.",
    "Вечером 29 ноября 1830 года подпоручик Пётр Высоцкий поднял курсантов школы подхорунжих; сигналом должен был стать пожар пивоварни на Сольце. Заговорщики ворвались в Бельведер, но великий князь Константин спрятался, а затем покинул Варшаву. Горожане захватили Арсенал. 25 января 1831 года сейм объявил Николая I низложенным с польского трона; началась война, продлившаяся до осени. После поражения Царство Польское лишилось конституции и армии, а тысячи участников ушли в эмиграцию.",
    "Акт о детронизации 25 января 1831 г.; М. Мохнацкий, «Восстание польского народа в 1830–1831 гг.»"))

# ================================================================ olszynka_1831
NEW_SCENES += [
    two("alder_grove_pl", "Ольшинка Гроховская", "sig_alder_grove_pl", "🌳", "удержать рощу", "icon_crown",
        ["генерал", "фельдмаршал"], "forest_ambush"),
    two("ordon_redoubt_pl", "Редут Ордона", "sig_ordon_redoubt_pl", "💥", "держать редут", "icon_dead",
        ["артиллерист", "враг"], "breach_wall"),
    bait("open_field_1831_pl", "Наступать в поле", "v_battle", 2, "open_battle", BATTLE),
]
NEW_RULES += [
    rule("alder_grove_pl_sig", "Целый день польские полки держат ольховую рощу — фельдмаршал не может взять Варшаву с ходу",
         "sig_alder_grove_pl",
         [actor("A", 0, tags=["gen_pl"], notFlags=["defeated"]), actor("B", 1, tags=["marshal_r_pl"], flags=["strong"])],
         [setf("B", "stalled_pl"), remf("B", "strong")]),
    rule("ordon_redoubt_pl_sig", "Редут стоит до последнего — и в легенде взлетает на воздух вместе с защитниками",
         "sig_ordon_redoubt_pl",
         [actor("A", 0, tags=["gunner_pl"]), actor("B", 1, tags=["marshal_r_pl"])],
         [setf("A", "legend_ordon_pl")]),
]
NEW_LEVELS.append(level(
    "olszynka_1831", 430, ACT6, "poland_battle", "alder_grove_pl", 2,
    ["alder_grove_pl", "ordon_redoubt_pl", "open_field_1831_pl"],
    ["chlopicki", "ordon", "diebitsch"],
    {"chlopicki": ["standing"], "diebitsch": ["standing", "strong"]},
    [("enemy_of", "chlopicki", "diebitsch"), ("enemy_of", "diebitsch", "chlopicki")],
    [flag("diebitsch", "stalled_pl"), flag("ordon", "legend_ordon_pl")],
    [("alder_grove_pl", ["chlopicki", "diebitsch"]), ("ordon_redoubt_pl", ["ordon", "diebitsch"])],
    "simplification"))
TEXTS.update(texts("olszynka_1831",
    "Ольшинка и редут Ордона",
    "Польская армия весь день держит ольховую рощу под Варшавой, а артиллерист Ордон становится легендой обороны",
    "В открытом поле армия фельдмаршала сильнее — держитесь за рощу. А редут Ордона стоит до конца, что бы о нём потом ни рассказывали.",
    "Февраль 1831 года. Армия фельдмаршала Дибича идёт на Варшаву, чтобы одним ударом закончить войну. Перед столицей, у Грохова, есть ольховая роща — Ольшинка.",
    "25 февраля 1831 года у Ольшинки Гроховской польские войска под командованием генерала Хлопицкого, тяжело раненного в бою, весь день удерживали рощу, и Дибич отказался от штурма Варшавы — война продлилась ещё полгода. В сентябре, при штурме Варшавы, пал редут № 54 на Воле; Адам Мицкевич написал балладу «Редут Ордона», где артиллерист Юлиан Ордон взрывает его вместе с собой. На самом деле Ордон выжил, эмигрировал и умер в 1887 году — говорят, он сам читал балладу о своей гибели.",
    "А. Мицкевич, «Редут Ордона» (1832); И. Прондзинский, «Мемуары»"))

# ================================================================ chopin_heart_1849
NEW_SCENES += [
    two("last_wish_pl", "Последняя воля", "sig_last_wish_pl", "🕯️", "завещать сердце", "icon_dead",
        ["композитор", "сестра"], "deathbed"),
    one("cognac_jar_pl", "Сердце в банке с коньяком", "sig_cognac_jar_pl", "🫙", "спрятать", "icon_plot",
        "сестра", "cellar_search"),
    two("customs_border_pl", "Таможня", "sig_customs_border_pl", "🛃", "пройти досмотр", "icon_ally",
        ["сестра", "таможенник"], "citadel_gate_t"),
]
NEW_RULES += [
    rule("last_wish_pl_sig", "Умирающий композитор просит сестру отвезти его сердце на родину",
         "sig_last_wish_pl",
         [actor("A", 0, tags=["composer_pl"]), actor("B", 1, tags=["sister_pl"])],
         [setf("A", "dead"), setf("B", "carries_heart_pl")]),
    rule("cognac_jar_pl_sig", "Сестра прячет сердце в сосуд с коньяком и укрывает его под платьем",
         "sig_cognac_jar_pl",
         [actor("A", 0, tags=["sister_pl"], flags=["carries_heart_pl"])],
         [setf("A", "hidden_pl")]),
    rule("customs_border_hidden_pl", "Таможня ничего не находит — сердце едет в Варшаву",
         "sig_customs_border_pl",
         [actor("A", 0, tags=["sister_pl"], flags=["carries_heart_pl", "hidden_pl"]), actor("B", 1, tags=["customs_pl"])],
         [setf("A", "home_heart_pl")]),
    rule("customs_border_open_pl", "Сосуд везут открыто — таможня его забирает",
         "sig_customs_border_pl",
         [actor("A", 0, tags=["sister_pl"], flags=["carries_heart_pl"], notFlags=["hidden_pl"]), actor("B", 1, tags=["customs_pl"])],
         [setf("A", "confiscated_pl")]),
]
NEW_LEVELS.append(level(
    "chopin_heart_1849", 440, ACT6, "poland_romance", "cognac_jar_pl", 3,
    ["last_wish_pl", "cognac_jar_pl", "customs_border_pl"],
    ["chopin", "ludwika", "customs_ru"],
    {"customs_ru": ["standing"]}, [],
    [flag("ludwika", "home_heart_pl"), nflag("ludwika", "confiscated_pl")],
    [("last_wish_pl", ["chopin", "ludwika"]), ("cognac_jar_pl", ["ludwika"]), ("customs_border_pl", ["ludwika", "customs_ru"])],
    "fact"))
TEXTS.update(texts("chopin_heart_1849",
    "Сердце Шопена",
    "Шопен умирает в Париже, и сестра тайно провозит его сердце через границу в банке с коньяком",
    "Через таможню открыто ничего не провезти. Сначала завещание, потом тайник.",
    "1849 год, Париж. Фредерик Шопен, покинувший Польшу в 1830-м, умирает от болезни лёгких в тридцать девять лет. Вернуться на родину он так и не смог. Рядом с ним — сестра Людвика.",
    "Шопен умер 17 октября 1849 года и был похоронен на кладбище Пер-Лашез, но перед смертью просил, чтобы его сердце отвезли на родину. Людвика в начале 1850 года тайно провезла его через границу в сосуде с коньяком — по преданию, спрятав под юбкой. Сердце замуровано в колонне костёла Святого Креста в Варшаве. В 2014 году сосуд тайно осмотрели учёные и подтвердили: Шопен умер от осложнений туберкулёза.",
    "Письма семьи Шопен; заключение исследования 2014 г."))

# ================================================================ january_1863
NEW_SCENES += [
    one("secret_seal_pl", "Тайная печать", "sig_secret_seal_pl", "🕯️", "создать правительство", "icon_plot",
        "диктатор", "back_room"),
    one("secret_state_pl", "Подпольные налоги и почта", "sig_secret_state_pl", "📮", "собирать налоги", "icon_ally",
        "диктатор", "anonymous_diploma"),
    two("peasant_ukaz_pl", "Указ о крестьянах", "sig_peasant_ukaz_pl", "📜", "дать крестьянам землю", "icon_crown",
        ["император", "повстанец"], "abolition_act"),
    bait("open_battle_1863_pl", "Открытый бой", "v_battle", 2, "forest_ambush", BATTLE),
]
NEW_RULES += [
    rule("secret_seal_pl_sig", "Повстанцы создают Национальное правительство: печать есть, имён членов не знает никто",
         "sig_secret_seal_pl",
         [actor("A", 0, tags=["dictator_pl"], notFlags=["defeated"])],
         [setf("A", "underground_gov_pl")]),
    rule("secret_state_pl_sig", "Тайное государство собирает налоги, держит почту и свою полицию",
         "sig_secret_state_pl",
         [actor("A", 0, tags=["dictator_pl"], flags=["underground_gov_pl"])],
         [setf("A", "state_pl")]),
    rule("peasant_ukaz_pl_sig", "Чтобы оторвать крестьян от восстания, император наделяет их землёй",
         "sig_peasant_ukaz_pl",
         [actor("A", 0, tags=["tsar_a_pl"]), actor("B", 1, tags=["dictator_pl"], flags=["state_pl"])],
         [setf("A", "emancipation_pl")]),
]
NEW_LEVELS.append(level(
    "january_1863", 450, ACT6, "poland_tension", "secret_seal_pl", 3,
    ["secret_seal_pl", "secret_state_pl", "peasant_ukaz_pl", "open_battle_1863_pl"],
    ["traugutt", "alexander2_pl"],
    {"traugutt": ["standing"], "alexander2_pl": ["crowned", "reigns", "standing", "strong"]},
    [("enemy_of", "traugutt", "alexander2_pl"), ("enemy_of", "alexander2_pl", "traugutt")],
    [flag("traugutt", "state_pl"), flag("alexander2_pl", "emancipation_pl")],
    [("secret_seal_pl", ["traugutt"]), ("secret_state_pl", ["traugutt"]), ("peasant_ukaz_pl", ["alexander2_pl", "traugutt"])],
    "simplification"))
TEXTS.update(texts("january_1863",
    "Тайное государство",
    "Повстанцы создают подпольное государство с налогами и почтой — а император отвечает тем, что даёт крестьянам землю",
    "В открытом бою с армией империи не выстоять. Государство строится тайно: сначала правительство, потом всё остальное. Император отвечает не только войсками.",
    "1863 год. В Царстве Польском начинается восстание — партизанская война в лесах, без армии и крепостей. Чтобы продержаться, повстанцам нужно невидимое государство. Осенью его возглавляет бывший офицер Ромуальд Траугутт.",
    "Январское восстание началось 22 января 1863 года. Национальное правительство действовало подпольно: печать, налоги, почта, свои суды и полиция — и почти никто не знал, кто в него входит. 2 марта 1864 года указом Александра II крестьяне Царства Польского получили землю в собственность на более выгодных условиях, чем в России, — во многом чтобы отвратить их от восстания. Траугутта арестовали в апреле 1864 года и 5 августа казнили на склонах Варшавской цитадели вместе с четырьмя членами правительства. Тысячи участников сослали в Сибирь.",
    "Документы Национального правительства 1863–1864 гг.; указ 2 марта 1864 г."))

# ================================================================ polonium_1898
NEW_SCENES += [
    one("flying_univ_pl", "Летучий университет", "sig_flying_univ_pl", "📚", "учиться тайно", "icon_ally",
        "студентка", "academy_chancery"),
    two("shed_lab_pl", "Сарай-лаборатория", "sig_shed_lab_pl", "⚗️", "искать излучение", "icon_crown",
        ["исследовательница", "муж"], "anekdota_desk"),
    one("name_polonium_pl", "Назвать полонием", "sig_name_polonium_pl", "🇵🇱", "назвать элемент", "icon_crown",
        "исследовательница", "council"),
    one("name_radium_pl", "Объявить сначала радий", "sig_name_radium_pl", "✨", "назвать элемент", "icon_ally",
        "исследовательница", "court_present"),
]
NEW_RULES += [
    rule("flying_univ_pl_sig", "Женщин в Варшавский университет не берут — она учится в подпольном «летучем университете»",
         "sig_flying_univ_pl",
         [actor("A", 0, tags=["scientist_pl"])],
         [setf("A", "educated_pl")]),
    rule("shed_lab_pl_sig", "В холодном сарае муж и жена перерабатывают тонны руды и находят новый элемент",
         "sig_shed_lab_pl",
         [actor("A", 0, tags=["scientist_pl"], flags=["educated_pl"]), actor("B", 1, tags=["scientist_fr_pl"])],
         [setf("A", "new_element_pl")]),
    rule("name_polonium_pl_sig", "Первый открытый элемент она называет в честь страны, которой нет на карте",
         "sig_name_polonium_pl",
         [actor("A", 0, tags=["scientist_pl"], flags=["new_element_pl"], notFlags=["named_pl"])],
         [setf("A", "polonium_pl"), setf("A", "named_pl")]),
    rule("name_radium_pl_sig", "Первым объявлен радий — и газеты пишут о французской науке",
         "sig_name_radium_pl",
         [actor("A", 0, tags=["scientist_pl"], flags=["new_element_pl"], notFlags=["named_pl"])],
         [setf("A", "radium_first_pl"), setf("A", "named_pl")]),
]
NEW_LEVELS.append(level(
    "polonium_1898", 460, ACT6, "poland_ceremony", "shed_lab_pl", 3,
    ["flying_univ_pl", "shed_lab_pl", "name_polonium_pl", "name_radium_pl"],
    ["sklodowska", "pierre_curie"],
    {}, [],
    [flag("sklodowska", "polonium_pl")],
    [("flying_univ_pl", ["sklodowska"]), ("shed_lab_pl", ["sklodowska", "pierre_curie"]), ("name_polonium_pl", ["sklodowska"])],
    "fact"))
TEXTS.update(texts("polonium_1898",
    "Полоний",
    "Учившаяся тайком варшавянка открывает в Париже новый элемент и называет его в честь страны, которой нет на карте",
    "В Париж она приезжает уже ученицей подпольного университета. Первым был объявлен не радий — имя первого элемента было политическим жестом.",
    "1891 год. Марии Склодовской двадцать четыре. В Варшаве, под властью империи, женщинам закрыта дорога в университет, и она учится в подпольном «летучем университете», переходящем из квартиры в квартиру. Теперь она едет в Париж, в Сорбонну.",
    "В Париже Мария вышла замуж за физика Пьера Кюри, и в 1898 году в холодном сарае на улице Ломон они открыли два новых элемента. Первый, объявленный в июле 1898 года, она назвала полонием — «в честь страны одного из нас». Радий объявили в декабре. В 1903 году Склодовская-Кюри получила Нобелевскую премию по физике, в 1911-м — по химии: она первый человек с двумя Нобелевскими премиями. Её лабораторные тетради до сих пор радиоактивны и хранятся в свинцовых ящиках.",
    "М. и П. Кюри, сообщение Академии наук, июль 1898 г."))

# ================================================================ wrzesnia_1901
NEW_SCENES += [
    two("german_prayer_pl", "Молитва по-немецки", "sig_german_prayer_pl", "📖", "отказаться", "icon_plot",
        ["учитель", "ученик"], "censor_cuts"),
    two("rods_pl", "Розги", "sig_rods_pl", "📏", "наказать", "icon_dead",
        ["учитель", "ученик"], "court_dis"),
    two("mothers_school_pl", "Матери у школы", "sig_mothers_school_pl", "📰", "встать за детей", "icon_crown",
        ["мать", "учитель"], "bread_riots"),
    bait("persuade_child_pl", "Уговорить ребёнка уступить", "v_parley", 2, "court_whisper", PARLEY),
]
NEW_RULES += [
    rule("german_prayer_pl_sig", "Дети отказываются отвечать на уроке закона Божьего по-немецки",
         "sig_german_prayer_pl",
         [actor("A", 0, tags=["teacher_pl"]), actor("B", 1, tags=["pupil_pl"])],
         [setf("B", "refused_pl")]),
    rule("rods_pl_sig", "Упрямых детей секут розгами",
         "sig_rods_pl",
         [actor("A", 0, tags=["teacher_pl"]), actor("B", 1, tags=["pupil_pl"], flags=["refused_pl"], notFlags=["conceded"])],
         [setf("B", "flogged_pl"), setf("A", "flogger_pl")]),
    rule("mothers_school_pl_sig", "Родители врываются в школу; суд над ними слышит вся Европа",
         "sig_mothers_school_pl",
         [actor("A", 0, tags=["mother_pl"]), actor("B", 1, tags=["teacher_pl"], flags=["flogger_pl"])],
         [setf("A", "protest_w_pl")]),
]
NEW_LEVELS.append(level(
    "wrzesnia_1901", 470, ACT6, "poland_tension", "mothers_school_pl", 3,
    ["german_prayer_pl", "rods_pl", "mothers_school_pl", "persuade_child_pl"],
    ["pupil_wrzesnia", "teacher_de", "mother_wrzesnia"],
    {"teacher_de": ["standing"], "mother_wrzesnia": ["standing"]}, [],
    [flag("mother_wrzesnia", "protest_w_pl"), flag("pupil_wrzesnia", "refused_pl")],
    [("german_prayer_pl", ["teacher_de", "pupil_wrzesnia"]), ("rods_pl", ["teacher_de", "pupil_wrzesnia"]),
     ("mothers_school_pl", ["mother_wrzesnia", "teacher_de"])],
    "fact"))
TEXTS.update(texts("wrzesnia_1901",
    "Дети из Вжесни",
    "Школьники отказываются молиться по-немецки, их секут, — и протест их матерей облетает всю Европу",
    "Если мать уговорит сына уступить, ничего не случится — а случилось. Протест родителей начался с розог.",
    "1901 год, город Вжесня в Великой Польше, часть Пруссии. Польский язык выдавливают из школ; теперь даже закон Божий дети должны учить и отвечать по-немецки, по немецким катехизисам.",
    "Весной 1901 года школьники Вжесни отказались отвечать на уроке религии по-немецки; их наказали розгами. 20 мая родители ворвались в школу; осенью суд в Гнезно приговорил десятки взрослых к тюрьме, мать одного из учеников — к двум с половиной годам. О Вжесне писали газеты всей Европы, Генрик Сенкевич и Мария Конопницкая выступили в защиту детей. В 1906–1907 годах школьная забастовка охватила, по разным оценкам, до семидесяти пяти тысяч детей в прусской части Польши.",
    "Материалы гнезненского процесса 1901 г.; М. Конопницкая, «Рота»"))

# ================================================================ drzymala_1904
NEW_SCENES += [
    one("land_purchase_pl", "Купить землю", "sig_land_purchase_pl", "🌾", "купить участок", "icon_ally",
        "крестьянин", "leave_for_village"),
    two("permit_denied_pl", "Разрешения не будет", "sig_permit_denied_pl", "📋", "отказать в постройке", "icon_plot",
        ["чиновник", "крестьянин"], "court_min"),
    one("circus_wagon_pl", "Цирковой фургон", "sig_circus_wagon_pl", "🛞", "жить в фургоне", "icon_crown",
        "крестьянин", "deulino_village"),
    one("build_house_pl", "Построить дом без разрешения", "sig_build_house_pl", "🏠", "строить", "icon_dead",
        "крестьянин", "burnt_fields"),
]
NEW_RULES += [
    rule("land_purchase_pl_sig", "Крестьянин-поляк покупает клочок земли",
         "sig_land_purchase_pl",
         [actor("A", 0, tags=["peasant_d_pl"])],
         [setf("A", "landowner_pl")]),
    rule("permit_denied_pl_sig", "По новому закону поляку отказывают в разрешении построить дом на своей земле",
         "sig_permit_denied_pl",
         [actor("A", 0, tags=["official_pl"]), actor("B", 1, tags=["peasant_d_pl"], flags=["landowner_pl"])],
         [setf("B", "no_permit_pl")]),
    rule("circus_wagon_pl_sig", "Фургон не дом — если каждый день его передвигать; крестьянин живёт в цирковом фургоне",
         "sig_circus_wagon_pl",
         [actor("A", 0, tags=["peasant_d_pl"], flags=["no_permit_pl"], notFlags=["house_demolished_pl"])],
         [setf("A", "wagon_pl")]),
    rule("build_house_pl_sig", "Дом без разрешения сносят, а хозяина штрафуют",
         "sig_build_house_pl",
         [actor("A", 0, tags=["peasant_d_pl"], flags=["no_permit_pl"])],
         [setf("A", "house_demolished_pl")]),
]
NEW_LEVELS.append(level(
    "drzymala_1904", 480, ACT6, "poland_romance", "circus_wagon_pl", 3,
    ["land_purchase_pl", "permit_denied_pl", "circus_wagon_pl", "build_house_pl"],
    ["drzymala", "prussian_official"],
    {"prussian_official": ["standing"]}, [],
    [flag("drzymala", "wagon_pl")],
    [("land_purchase_pl", ["drzymala"]), ("permit_denied_pl", ["prussian_official", "drzymala"]), ("circus_wagon_pl", ["drzymala"])],
    "fact"))
TEXTS.update(texts("drzymala_1904",
    "Фургон Джималы",
    "Поляку запрещают построить дом на своей земле — и он пять лет живёт в цирковом фургоне, каждый день передвигая его",
    "Без земли не о чем и спорить. Строить дом без разрешения — значит потерять его. Закон говорит о домах, а не о фургонах.",
    "1904 год, Пруссия. Новый закон запрещает строить жилые дома на только что купленной земле без разрешения властей — а полякам разрешения не дают. Так власти мешают полякам покупать землю. Крестьянин Михал Джимала купил участок в Подградовицах.",
    "Получив отказ, Михал Джимала купил цирковой фургон и поселился в нём: по закону фургон не считался домом, если его каждый сутки передвигать, — и он передвигал. Власти годами штрафовали его и судились с ним, о «фургоне Джималы» писали газеты, а сам он стал символом упрямого сопротивления германизации. В 1909 году фургон всё же конфисковали; Джимала вырыл землянку. Сегодня в Подградовицах стоит памятный фургон.",
    "Прусский колонизационный закон 1904 г.; пресса 1904–1909 гг."))

# ================================================================ oath_crisis_1917
NEW_SCENES += [
    one("cadre_company_pl", "Первая кадровая рота", "sig_cadre_company_pl", "🎖️", "выступить", "icon_ally",
        "комендант", "march_on_rome_g"),
    two("oath_demand_pl", "Присяга на «братство по оружию»", "sig_oath_demand_pl", "✋", "потребовать присяги", "icon_plot",
        ["генерал-губернатор", "комендант"], "take_oath"),
    two("magdeburg_pl", "Магдебург", "sig_magdeburg_pl", "🏰", "арестовать", "icon_dead",
        ["генерал-губернатор", "узник"], "tower_cell"),
    two("swear_kaiser_pl", "Присягнуть", "sig_swear_kaiser_pl", "📜", "присягнуть", "icon_ally",
        ["генерал-губернатор", "комендант"], "reoath"),
]
NEW_RULES += [
    rule("cadre_company_pl_sig", "Из Кракова выходит Первая кадровая рота — начало польских легионов",
         "sig_cadre_company_pl",
         [actor("A", 0, tags=["pilsudski_pl"])],
         [setf("A", "legions_cmd_pl")]),
    rule("oath_demand_pl_sig", "Легионеры должны присягнуть на верность германскому императору — комендант отказывается",
         "sig_oath_demand_pl",
         [actor("A", 0, tags=["gov_gen_pl"]), actor("B", 1, tags=["pilsudski_pl"], flags=["legions_cmd_pl"], notFlags=["sworn_k_pl"])],
         [setf("B", "refused_oath_pl")]),
    rule("swear_kaiser_pl_sig", "Комендант присягает — и становится офицером чужой армии",
         "sig_swear_kaiser_pl",
         [actor("A", 0, tags=["gov_gen_pl"]), actor("B", 1, tags=["pilsudski_pl"], notFlags=["refused_oath_pl"])],
         [setf("B", "sworn_k_pl")]),
    rule("magdeburg_pl_sig", "Отказавшегося коменданта арестовывают и увозят в крепость Магдебург",
         "sig_magdeburg_pl",
         [actor("A", 0, tags=["gov_gen_pl"]), actor("B", 1, tags=["pilsudski_pl"], flags=["refused_oath_pl"])],
         [setf("B", "prisoner_pl"), setf("B", "away")]),
]
NEW_LEVELS.append(level(
    "oath_crisis_1917", 490, ACT6, "poland_tension", "magdeburg_pl", 3,
    ["cadre_company_pl", "oath_demand_pl", "magdeburg_pl", "swear_kaiser_pl"],
    ["pilsudski", "beseler"],
    {"beseler": ["standing", "strong"]}, [],
    [flag("pilsudski", "prisoner_pl")],
    [("cadre_company_pl", ["pilsudski"]), ("oath_demand_pl", ["beseler", "pilsudski"]), ("magdeburg_pl", ["beseler", "pilsudski"])],
    "fact"))
TEXTS.update(texts("oath_crisis_1917",
    "Кризис присяги",
    "Командир легионов отказывается присягать германскому императору — и из узника Магдебурга становится героем",
    "Сначала нужны легионы. Присягнув, он стал бы офицером чужой армии — а стал узником.",
    "Первая мировая война. Юзеф Пилсудский в 1914 году вывел из Кракова Первую кадровую роту и создал польские легионы, воюющие на стороне Австрии и Германии против России. В 1916 году Германия и Австрия провозгласили «Королевство Польское» — без короля и границ. Теперь легионеры должны присягнуть на «братство по оружию» с армиями центральных держав.",
    "6 августа 1914 года Первая кадровая рота вышла из Кракова. В июле 1917 года большинство легионеров Первой и Третьей бригад, следуя за Пилсудским, отказалось от присяги; 22 июля генерал-губернатор Ганс фон Безелер приказал арестовать Пилсудского, и тот провёл больше года в крепости Магдебург. Арест сделал его в глазах поляков символом независимости — не служившим ни одной из держав.",
    "Документы кризиса присяги 1917 г.; Ю. Пилсудский, «Мои первые бои»"))

# ================================================================ paderewski_1918
NEW_SCENES += [
    one("concerts_us_pl", "Концерты в Америке", "sig_concerts_us_pl", "🎹", "играть ради Польши", "icon_ally",
        "пианист", "globe_opens"),
    two("house_friend_pl", "Дружба с полковником", "sig_house_friend_pl", "🤝", "убедить советника", "icon_ally",
        ["пианист", "советник"], "court_whisper"),
    two("point13_pl", "Тринадцатый пункт", "sig_point13_pl", "📜", "включить пункт", "icon_crown",
        ["советник", "президент"], "council_b"),
    two("demand_borders_pl", "Сразу требовать границ", "sig_demand_borders_pl", "🗺️", "требовать", "icon_plot",
        ["пианист", "президент"], "court_refuse"),
]
NEW_RULES += [
    rule("concerts_us_pl_sig", "Знаменитый пианист даёт концерты по всей Америке и собирает деньги для голодающей Польши",
         "sig_concerts_us_pl",
         [actor("A", 0, tags=["pianist_pl"])],
         [setf("A", "famous_pl")]),
    rule("house_friend_pl_sig", "Пианист становится другом ближайшего советника президента",
         "sig_house_friend_pl",
         [actor("A", 0, tags=["pianist_pl"], flags=["famous_pl"]), actor("B", 1, tags=["adviser_pl"])],
         [setf("B", "convinced_pl")]),
    rule("point13_pl_sig", "В программу мира включают пункт о независимой Польше с выходом к морю",
         "sig_point13_pl",
         [actor("A", 0, tags=["adviser_pl"], flags=["convinced_pl"]), actor("B", 1, tags=["president_pl"], notFlags=["annoyed_pl"])],
         [setf("B", "point13_pl")]),
    rule("demand_borders_pl_sig", "Требовать у президента конкретных границ — значит раздражить его",
         "sig_demand_borders_pl",
         [actor("A", 0, tags=["pianist_pl"]), actor("B", 1, tags=["president_pl"])],
         [setf("B", "annoyed_pl")]),
]
NEW_LEVELS.append(level(
    "paderewski_1918", 500, ACT6, "poland_ceremony", "point13_pl", 3,
    ["concerts_us_pl", "house_friend_pl", "point13_pl", "demand_borders_pl"],
    ["paderewski", "wilson", "house_col"],
    {"wilson": ["standing"]}, [],
    [flag("wilson", "point13_pl")],
    [("concerts_us_pl", ["paderewski"]), ("house_friend_pl", ["paderewski", "house_col"]), ("point13_pl", ["house_col", "wilson"])],
    "simplification"))
TEXTS.update(texts("paderewski_1918",
    "Тринадцатый пункт",
    "Знаменитый пианист своими концертами и дружбой с советником президента добивается, чтобы независимая Польша вошла в программу мира",
    "Без славы его бы не слушали. К президенту идут не напрямую, а через того, кому он доверяет. И просить сразу границ — значит всё испортить.",
    "1915–1917 годы. Игнаций Падеревский — самый знаменитый пианист мира. Он ездит по Америке с концертами, собирая деньги для голодающей Польши, и в каждом выступлении говорит о польской независимости. Президент Вудро Вильсон готовит программу послевоенного мира.",
    "Падеревский дал в Америке сотни концертов и выступлений в пользу Польши и подружился с полковником Эдвардом Хаусом, ближайшим советником Вильсона. 8 января 1918 года в «Четырнадцати пунктах» Вильсона тринадцатый гласил: должно быть создано независимое польское государство со свободным и надёжным доступом к морю. В 1919 году Падеревский стал премьер-министром и подписал Версальский договор.",
    "В. Вильсон, «Четырнадцать пунктов» (1918); дневник Э. Хауса"))

# ================================================================ november_11_1918
NEW_SCENES += [
    one("train_magdeburg_pl", "Поезд из Магдебурга", "sig_train_magdeburg_pl", "🚂", "вернуться в Варшаву", "icon_ally",
        "узник", "golden_gate_return"),
    two("regency_hands_pl", "Регентский совет передаёт власть", "sig_regency_hands_pl", "📜", "передать власть", "icon_crown",
        ["регент", "комендант"], "abdication_table"),
    two("disarm_garrison_pl", "Разоружить гарнизон", "sig_disarm_garrison_pl", "🏳️", "разоружить", "icon_crown",
        ["комендант", "офицер"], "arms_at_feet"),
    bait("storm_barracks_pl", "Штурм казарм", "v_battle", 2, "breach_wall", BATTLE),
]
NEW_RULES += [
    rule("train_magdeburg_pl_sig", "Освобождённый узник поездом возвращается в Варшаву",
         "sig_train_magdeburg_pl",
         [actor("A", 0, tags=["pilsudski_pl"], flags=["prisoner_pl"])],
         [setf("A", "returned_w_pl"), remf("A", "away"), setf("A", "standing")]),
    rule("regency_hands_pl_sig", "Регентский совет передаёт вернувшемуся коменданту командование армией",
         "sig_regency_hands_pl",
         [actor("A", 0, tags=["regent_pl"]), actor("B", 1, tags=["pilsudski_pl"], flags=["returned_w_pl"])],
         [setf("B", "commander_pl")]),
    rule("disarm_garrison_pl_sig", "Немецкие солдаты сдают оружие и уезжают домой — почти без выстрелов",
         "sig_disarm_garrison_pl",
         [actor("A", 0, tags=["pilsudski_pl"], flags=["commander_pl"], notFlags=["at_war"]), actor("B", 1, tags=["garrison_pl"])],
         [setf("B", "disarmed_pl")]),
]
NEW_LEVELS.append(level(
    "november_11_1918", 510, ACT6, "poland_ceremony", "disarm_garrison_pl", 3,
    ["train_magdeburg_pl", "regency_hands_pl", "disarm_garrison_pl", "storm_barracks_pl"],
    ["pilsudski", "regent_kakowski", "german_officer"],
    {"pilsudski": ["prisoner_pl", "away"], "regent_kakowski": ["standing"], "german_officer": ["standing", "strong"]},
    [("enemy_of", "pilsudski", "german_officer"), ("enemy_of", "german_officer", "pilsudski")],
    [flag("german_officer", "disarmed_pl"), nflag("pilsudski", "at_war")],
    [("train_magdeburg_pl", ["pilsudski"]), ("regency_hands_pl", ["regent_kakowski", "pilsudski"]),
     ("disarm_garrison_pl", ["pilsudski", "german_officer"])],
    "fact"))
TEXTS.update(texts("november_11_1918",
    "11 ноября",
    "Узник Магдебурга возвращается в Варшаву, Регентский совет передаёт ему власть — и немецкий гарнизон уходит почти без выстрела",
    "Командовать можно, только вернувшись. Власть не берут штурмом — её передают. И немцев не штурмуют: их разоружают, и они уходят домой.",
    "Ноябрь 1918 года. Германия проигрывает войну, в Берлине революция. В Варшаве правит Регентский совет, созданный немцами, а в городе стоит немецкий гарнизон. В Магдебурге освобождают Пилсудского.",
    "10 ноября 1918 года Пилсудский приехал поездом в Варшаву. 11 ноября — в день перемирия на Западном фронте — Регентский совет передал ему верховное командование армией, а 14 ноября распустился, передав всю власть. Немецкие гарнизоны разоружали отряды Польской военной организации и добровольцы, но в основном без боя: солдатский совет гарнизона согласился уехать домой. Так после 123 лет Польша вернулась на карту; 11 ноября — День независимости. Впереди были годы войн за границы — но это уже другая история.",
    "Документы Регентского совета, ноябрь 1918 г.; А. Гарлицкий, «Юзеф Пилсудский»"))

if __name__ == "__main__":
    P.NEW_CHARS, P.NEW_SCENES, P.NEW_RULES, P.NEW_LEVELS, P.TEXTS = NEW_CHARS, NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS
    P.CHAPTER_TEXTS = {"act.poland.5": ACT5, "act.poland.6": ACT6}
    P.main()
