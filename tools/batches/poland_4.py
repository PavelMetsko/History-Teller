#!/usr/bin/env python3
"""Пачка 4 главы «Польша»: Речь Посполитая, 1573–1734, 12 уровней.

    python3 tools/batches/poland_4.py [repo_root]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, level, texts

ACT4 = "Акт IV · Речь Посполитая"

NEW_CHARS = [
    char("primate_uchanski", "Примас Уханский", ["primate_pl"], "⛪"),
    char("firlej", "Ян Фирлей", ["calvinist_pl"], "📜"),
    char("henri_valois", "Генрих Валуа", ["valois_pl"], "👑"),
    char("anna_jag", "Анна Ягеллонка", ["infanta_pl"], "👸"),
    char("tenczynski", "Подкоморий Тенчинский", ["chamberlain_pl"], "🐎"),
    char("zamoyski", "Ян Замойский", ["zamoyski_pl"], "🏰"),
    char("maximilian3", "Эрцгерцог Максимилиан", ["claimant_pl"], "👑"),
    char("sigismund3", "Сигизмунд III Ваза", ["vasa_pl"], "👑"),
    char("chodkiewicz", "Гетман Ян Кароль Ходкевич", ["hussar_hetman_pl"], "🪽"),
    char("charles9_sw", "Король Карл IX Шведский", ["swede_king_pl"], "👑"),
    char("zolkiewski", "Гетман Станислав Жолкевский", ["hetman_z_pl"], "🪽"),
    char("wladyslaw4", "Королевич Владислав Ваза", ["prince_w_pl"], "👑"),
    char("shuisky_pl", "Царь Василий Шуйский", ["tsar_pl"], "👑"),
    char("lubomirski", "Станислав Любомирский", ["lubomirski_pl"], "⚔️"),
    char("sahaidachny", "Гетман Пётр Сагайдачный", ["cossack_pl"], "⚔️"),
    char("osman2", "Султан Осман II", ["sultan2_pl"], "🌙"),
    char("sicinski", "Посол Сицинский", ["envoy_pl"], "✋"),
    char("fredro_marshal", "Маршалок сейма Фредро", ["marshal_pl"], "🔔"),
    char("jan_kazimierz", "Ян Казимир", ["jk_king_pl"], "👑"),
    char("kordecki", "Приор Августин Кордецкий", ["prior_pl"], "⛪"),
    char("muller_sw", "Генерал Бурхард Мюллер", ["swede_gen_pl"], "⚔️"),
    char("twardowski", "Пан Твардовский", ["sorcerer_pl"], "🌙"),
    char("devil_pl", "Чёрт", ["devil_pl"], "😈"),
    char("sobieski", "Ян Собеский", ["sobieski_pl"], "🪽"),
    char("husein_pasha", "Гусейн-паша", ["pasha_pl"], "🌙"),
    char("kara_mustafa", "Великий визирь Кара-Мустафа", ["vizier_pl"], "🌙"),
    char("leopold1", "Император Леопольд I", ["emperor_l_pl"], "👑"),
    char("kulczycki", "Ежи Кульчицкий", ["spy_pl"], "☕"),
    char("leszczynski", "Станислав Лещинский", ["leszczynski_pl"], "👑"),
    char("august3", "Август III Саксонский", ["saxon_pl"], "👑"),
    char("munnich", "Фельдмаршал Миних", ["field_marshal_pl"], "⚔️"),
]

NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS = [], [], [], {}

def bait(id, name, tag, slots, donor, roles):
    icon = {"v_battle": "icon_dead", "v_kill": "icon_dead", "v_flee": "icon_ally", "v_prepare": "icon_ally"}.get(tag, "icon_ally")
    act = {"v_battle": "битва", "v_parley": "переговоры", "v_bribe": "подкуп", "v_wed": "свадьба",
           "v_flee": "уход", "v_prepare": "подготовка", "v_kill": "убийство"}[tag]
    emoji = {"v_battle": "⚔️", "v_parley": "🤝", "v_bribe": "💰", "v_wed": "💍", "v_flee": "🚪", "v_prepare": "🛡️", "v_kill": "🗡️"}[tag]
    return scene(id, name, [tag], slots, emoji, act, icon, roles, donor)

PARLEY = ["кто требует", "кто уступает"]
BATTLE = ["нападающий", "защитник"]

# ================================================================ warsaw_confederation (1573)
NEW_SCENES += [
    scene("confederation_pl", "Варшавская конфедерация", ["sig_confederation_pl"], 1, "🤝", "поклясться в мире вер", "icon_ally",
          ["маршалок"], "council_b"),
    scene("election_1573_pl", "Вольная элекция", ["sig_election_1573_pl"], 2, "🗳️", "избрать короля", "icon_crown",
          ["маршалок", "кандидат"], "council"),
    scene("si_non_iurabis_pl", "«Если не присягнёшь…»", ["sig_si_non_iurabis_pl"], 2, "✋", "привести к присяге", "icon_crown",
          ["маршалок", "король"], "cathedral_altar"),
    bait("primate_talks_pl", "Уговоры примаса", "v_parley", 2, "court_whisper", PARLEY),
]
NEW_RULES += [
    rule("confederation_pl_sig", "Шляхта клянётся: мы, различные в вере, сохраним мир между собой и не прольём крови за веру",
         "sig_confederation_pl",
         [actor("A", 0, tags=["calvinist_pl"], notFlags=["conceded"])],
         [setf("A", "confederation_pl")]),
    rule("election_1573_pl_sig", "На поле под Варшавой шляхта избирает королём французского принца",
         "sig_election_1573_pl",
         [actor("A", 0, tags=["calvinist_pl"], flags=["confederation_pl"]),
          actor("B", 1, tags=["valois_pl"])],
         [setf("B", "elected_pl")]),
    rule("si_non_iurabis_pl_sig", "Избранник медлит с присягой на мир вер — и слышит: «Не присягнёшь — не будешь царствовать»",
         "sig_si_non_iurabis_pl",
         [actor("A", 0, tags=["calvinist_pl"], flags=["confederation_pl"]),
          actor("B", 1, tags=["valois_pl"], flags=["elected_pl"])],
         [setf("B", "sworn_articles_pl"), setf("B", "crowned")]),
]
NEW_LEVELS.append(level(
    "warsaw_confederation", 230, ACT4, "poland_ceremony", "confederation_pl", 3,
    ["confederation_pl", "election_1573_pl", "si_non_iurabis_pl", "primate_talks_pl"],
    ["firlej", "primate_uchanski", "henri_valois"],
    {"primate_uchanski": ["standing"], "firlej": ["standing"]}, [],
    [flag("henri_valois", "sworn_articles_pl"), flag("firlej", "confederation_pl")],
    [("confederation_pl", ["firlej"]), ("election_1573_pl", ["firlej", "henri_valois"]),
     ("si_non_iurabis_pl", ["firlej", "henri_valois"])],
    "simplification"))
TEXTS.update(texts("warsaw_confederation",
    "Варшавская конфедерация",
    "Шляхта клянётся не воевать за веру и заставляет нового короля, брата устроителя Варфоломеевской ночи, присягнуть на этот мир",
    "Сначала мир между верами — потом выборы, иначе выберут того, кто его нарушит. Примас уговорит маршалка отступить; не поддавайтесь.",
    "1573 год. Умер последний Ягеллон, и впервые короля будет избирать вся шляхта. Среди католиков, лютеран, кальвинистов и православных страшно вспоминать, что полгода назад в Париже, в Варфоломеевскую ночь, католики перебили тысячи протестантов. Главный кандидат — французский принц Генрих Валуа, брат короля, устроившего ту ночь.",
    "28 января 1573 года Варшавская конфедерация провозгласила: «мы, различные в вере, будем хранить мир между собой» — впервые в Европе свобода вероисповедания для знати была закреплена законом; из епископов акт подписал лишь один. В мае королём избрали Генриха Валуа. Когда в соборе Парижской Богоматери он медлил с присягой на мир вер, польский посол бросил ему: «Si non iurabis, non regnabis» — «Не присягнёшь — не будешь царствовать». Акт конфедерации внесён ЮНЕСКО в реестр «Память мира».",
    "Акт Варшавской конфедерации (1573); Генриховы артикулы"))

# ================================================================ henri_flight (1574)
NEW_SCENES += [
    scene("news_paris_pl", "Гонец из Парижа", ["sig_news_paris_pl"], 1, "🐎", "узнать о смерти брата", "icon_crown",
          ["король"], "liege_ride"),
    scene("night_escape_pl", "Ночной побег из Вавеля", ["sig_night_escape_pl"], 1, "🌙", "бежать ночью", "icon_plot",
          ["король"], "flee_castle"),
    scene("chase_pszczyna_pl", "Погоня до Пщины", ["sig_chase_pszczyna_pl"], 2, "🏇", "догнать короля", "icon_ally",
          ["подкоморий", "беглец"], "liege_ride"),
    bait("anna_wedding_pl", "Свадьба с Анной Ягеллонкой", "v_wed", 2, "polish_wedding", ["жених", "невеста"]),
]
NEW_RULES += [
    rule("news_paris_pl_sig", "Гонец привозит весть: французский король умер, корона Франции ждёт брата",
         "sig_news_paris_pl",
         [actor("A", 0, tags=["valois_pl"])],
         [setf("A", "heir_france_pl")]),
    rule("night_escape_pl_sig", "Ночью, после пира, король тайком выходит из Вавеля и скачет к границе",
         "sig_night_escape_pl",
         [actor("A", 0, tags=["valois_pl"], flags=["heir_france_pl"], notFlags=["married"])],
         [setf("A", "fled_pl"), setf("A", "away")]),
    rule("chase_pszczyna_pl_sig", "Подкоморий догоняет беглеца у границы — тот дарит перстень и обещает вернуться",
         "sig_chase_pszczyna_pl",
         [actor("A", 0, tags=["chamberlain_pl"]),
          actor("B", 1, tags=["valois_pl"], flags=["fled_pl"])],
         [setf("A", "caught_up_pl"), setf("B", "promised_return_pl")]),
]
NEW_LEVELS.append(level(
    "henri_flight", 240, ACT4, "poland_tension", "night_escape_pl", 3,
    ["news_paris_pl", "night_escape_pl", "chase_pszczyna_pl", "anna_wedding_pl"],
    ["henri_valois", "anna_jag", "tenczynski"],
    {"henri_valois": ["crowned", "reigns", "standing"], "anna_jag": ["standing"]}, [],
    [flag("henri_valois", "fled_pl"), flag("tenczynski", "caught_up_pl"), nflag("anna_jag", "married")],
    [("news_paris_pl", ["henri_valois"]), ("night_escape_pl", ["henri_valois"]),
     ("chase_pszczyna_pl", ["tenczynski", "henri_valois"])],
    "fact"))
TEXTS.update(texts("henri_flight",
    "Побег Генриха Валуа",
    "Французский принц, всего полгода король Польши, узнаёт о смерти брата и ночью бежит из Вавеля — его догоняют уже у границы",
    "Бежать без причины он не стал бы — сначала весть из Парижа. Женатому на Ягеллонке бежать было бы куда труднее; свадьбы так и не случилось.",
    "1574 год. Генрих Валуа коронован в Кракове, но ему скучно: чужой язык, бесконечные сеймы, обещанный брак с немолодой Анной Ягеллонкой. Во Франции болен его брат, король Карл IX.",
    "30 мая 1574 года Карл IX умер; весть дошла до Кракова 14 июня. В ночь на 19 июня Генрих после пира тайком вышел из Вавеля и поскакал к границе империи. Подкоморий Ян Тенчинский догнал его у Пщины; король, по рассказам, подарил ему перстень и обещал вернуться. Не вернулся: в Париже он стал Генрихом III, а в 1589 году его убил монах Жак Клеман. Через год Польша объявила трон свободным, и королём выбрали Стефана Батория — вместе с той самой Анной Ягеллонкой.",
    "Ян Дмитр Соликовский, «Краткие записки о польских делах»; Ф. Депорт, «Прощание с Польшей»"))

# ================================================================ byczyna_1588
NEW_SCENES += [
    scene("double_election_pl", "Двойная элекция", ["sig_double_election_pl"], 2, "🗳️", "избрать двоих", "icon_plot",
          ["кандидат", "кандидат"], "council"),
    scene("byczyna_field_pl", "Бычина", ["sig_byczyna_field_pl"], 2, "⚔️", "разбить претендента", "icon_dead",
          ["гетман", "эрцгерцог"], "open_battle_s"),
    scene("renounce_crown_pl", "Отказ от короны", ["sig_renounce_crown_pl"], 2, "📜", "отречься в плену", "icon_crown",
          ["пленник", "король"], "abdication_table"),
    bait("vasa_sweden_pl", "Уехать в Швецию", "v_flee", 1, "exile_road", ["кто уходит"]),
]
NEW_RULES += [
    rule("double_election_pl_sig", "Шляхта раскалывается: одни кричат шведского королевича, другие — австрийского эрцгерцога",
         "sig_double_election_pl",
         [actor("A", 0, tags=["vasa_pl"]),
          actor("B", 1, tags=["claimant_pl"])],
         [setf("A", "elected_pl"), setf("B", "elected_pl"),
          addr("enemy_of", "A", "B"), addr("enemy_of", "B", "A")]),
    rule("byczyna_field_pl_sig", "Гетман бьёт войско претендента и берёт его самого в плен",
         "sig_byczyna_field_pl",
         [actor("A", 0, tags=["zamoyski_pl"], flags=["strong"]),
          actor("B", 1, tags=["claimant_pl"], flags=["elected_pl"])],
         [setf("B", "captured_pl"), setf("B", "defeated"), setf("A", "victor")]),
    rule("renounce_crown_pl_sig", "Пленный эрцгерцог отказывается от притязаний — и трон остаётся за Вазой",
         "sig_renounce_crown_pl",
         [actor("A", 0, tags=["claimant_pl"], flags=["captured_pl"]),
          actor("B", 1, tags=["vasa_pl"], flags=["elected_pl"], notFlags=["away"])],
         [setf("B", "crowned_vasa_pl"), setf("B", "crowned"), setf("B", "reigns")]),
]
NEW_LEVELS.append(level(
    "byczyna_1588", 250, ACT4, "poland_battle", "byczyna_field_pl", 3,
    ["double_election_pl", "byczyna_field_pl", "renounce_crown_pl", "vasa_sweden_pl"],
    ["zamoyski", "maximilian3", "sigismund3"],
    {"zamoyski": ["standing", "strong"], "maximilian3": ["standing"], "sigismund3": ["standing"]}, [],
    [flag("sigismund3", "crowned_vasa_pl"), flag("maximilian3", "captured_pl")],
    [("double_election_pl", ["sigismund3", "maximilian3"]), ("byczyna_field_pl", ["zamoyski", "maximilian3"]),
     ("renounce_crown_pl", ["maximilian3", "sigismund3"])],
    "fact"))
TEXTS.update(texts("byczyna_1588",
    "Бычина",
    "Шляхта избирает двух королей сразу — и гетман Замойский решает спор в поле, взяв в плен австрийского эрцгерцога",
    "Сражаться можно, только когда претендент уже избран. Пленник отрекается в пользу того, кто остался в стране, — уедет Ваза в Швецию, и трон опустеет.",
    "1587 год. Умер король Стефан Баторий. На элекции шляхта раскололась: канцлер и гетман Ян Замойский поддержал шведского королевича Сигизмунда Вазу, его враги Зборовские — австрийского эрцгерцога Максимилиана Габсбурга. Обоих объявили королями.",
    "Максимилиан осадил Краков, но взять не смог и отступил в Силезию. 24 января 1588 года под Бычиной Замойский разбил его войско и взял эрцгерцога в плен; тринадцать месяцев тот просидел в Красныставе и в 1589 году отказался от польской короны. Замойский — канцлер, гетман и основатель Замостья, «идеального города» Ренессанса, внесённого в список ЮНЕСКО. Ему приписывают слова: «Такими будут Речи Посполитые, каким будет воспитание их молодёжи».",
    "Рейнгольд Гейденштейн, «История Польши от смерти Сигизмунда Августа»"))

# ================================================================ kircholm_1605
NEW_SCENES += [
    scene("kircholm_feint_pl", "Притворный отход", ["sig_kircholm_feint_pl"], 2, "🏇", "выманить с холмов", "icon_plot",
          ["гетман", "враг"], "hal_retreats"),
    scene("hussar_charge_pl", "Атака крылатых гусар", ["sig_hussar_charge_pl"], 2, "🪽", "ударить гусарией", "icon_dead",
          ["гетман", "враг"], "open_battle_s"),
    bait("kircholm_hill_pl", "Атака на холм", "v_battle", 2, "open_battle", BATTLE),
    bait("kircholm_muster_pl", "Подтянуть пехоту", "v_prepare", 1, "barons_muster", ["кто вооружается"]),
]
NEW_RULES += [
    rule("kircholm_feint_pl_sig", "Гетман делает вид, что отходит, — шведы спускаются с холмов в погоню и рвут строй",
         "sig_kircholm_feint_pl",
         [actor("A", 0, tags=["hussar_hetman_pl"], notFlags=["defeated"]),
          actor("B", 1, tags=["swede_king_pl"], flags=["strong"])],
         [setf("B", "descended_pl"), remf("B", "strong")]),
    rule("hussar_charge_pl_sig", "Крылатые гусары бьют по растянутому войску — за двадцать минут армия втрое больше разбита",
         "sig_hussar_charge_pl",
         [actor("A", 0, tags=["hussar_hetman_pl"], notFlags=["defeated"]),
          actor("B", 1, tags=["swede_king_pl"], flags=["descended_pl"])],
         [setf("B", "defeated"), setf("A", "victor")]),
]
NEW_LEVELS.append(level(
    "kircholm_1605", 260, ACT4, "poland_battle", "hussar_charge_pl", 2,
    ["kircholm_feint_pl", "hussar_charge_pl", "kircholm_hill_pl", "kircholm_muster_pl"],
    ["chodkiewicz", "charles9_sw"],
    {"chodkiewicz": ["standing"], "charles9_sw": ["crowned", "standing", "strong"]},
    [("enemy_of", "chodkiewicz", "charles9_sw"), ("enemy_of", "charles9_sw", "chodkiewicz")],
    [flag("charles9_sw", "defeated"), nflag("chodkiewicz", "defeated")],
    [("kircholm_feint_pl", ["chodkiewicz", "charles9_sw"]), ("hussar_charge_pl", ["chodkiewicz", "charles9_sw"])],
    "fact"))
TEXTS.update(texts("kircholm_1605",
    "Кирхгольм",
    "Гетман притворным отходом выманивает шведов с холмов — и крылатые гусары громят армию втрое больше",
    "На холмах шведы неуязвимы — и в лоб, и с подкреплением. Пусть сами спустятся. Гусары бьют только по растянутому строю.",
    "1605 год. Шведский король Карл IX ведёт на Ригу армию почти в одиннадцать тысяч человек. Литовский гетман Ян Кароль Ходкевич может выставить против неё меньше четырёх. Шведы стоят на холмах у местечка Кирхгольм.",
    "27 сентября 1605 года Ходкевич притворным отходом выманил шведов с холмов, и гусария в одной атаке опрокинула растянувшееся войско; шведы потеряли, по разным оценкам, от половины до двух третей армии. Сам Карл IX спасся лишь потому, что рыцарь Генрик Вреде отдал ему своего коня и погиб. Поздравления пришли от папы, императора и даже от персидского шаха. Кирхгольм — образец того, что умела польская гусария, а её крылья — деревянные рамы с перьями — стали символом эпохи.",
    "Ш. Старовольский; Я. Ходкевич, донесение королю (1605)"))

# ================================================================ klushino_1610
NEW_SCENES += [
    scene("klushino_field_pl", "Клушино", ["sig_klushino_field_pl"], 2, "🪽", "разбить войско", "icon_dead",
          ["гетман", "царь"], "open_battle_s"),
    scene("tsar_tonsured_pl", "Царя постригают в монахи", ["sig_tsar_tonsured_pl"], 1, "⛪", "свести с престола", "icon_dead",
          ["царь"], "abdicate_d"),
    scene("boyars_invite_pl", "Бояре зовут королевича", ["sig_boyars_invite_pl"], 2, "📜", "заключить договор", "icon_crown",
          ["гетман", "королевич"], "treaty_king"),
    scene("king_claims_pl", "Король хочет трон себе", ["sig_king_claims_pl"], 2, "👑", "потребовать трон", "icon_plot",
          ["гетман", "король"], "court_refuse"),
]
NEW_RULES += [
    rule("klushino_field_pl_sig", "Гусария гетмана разбивает войско вчетверо больше; наёмники противника переходят на его сторону",
         "sig_klushino_field_pl",
         [actor("A", 0, tags=["hetman_z_pl"]),
          actor("B", 1, tags=["tsar_pl"])],
         [setf("B", "army_lost_pl"), remf("B", "strong"), setf("A", "victor")]),
    rule("tsar_tonsured_pl_sig", "Оставшегося без войска царя сводят с престола и насильно постригают",
         "sig_tsar_tonsured_pl",
         [actor("A", 0, tags=["tsar_pl"], flags=["army_lost_pl"])],
         [setf("A", "deposed_pl"), remf("A", "reigns"), setf("A", "away")]),
    rule("boyars_invite_pl_sig", "Победитель заключает с боярами договор: царём станет королевич — если примет православие",
         "sig_boyars_invite_pl",
         [actor("A", 0, tags=["hetman_z_pl"], flags=["victor"]),
          actor("B", 1, tags=["prince_w_pl"])],
         [setf("B", "tsar_elect_pl")]),
    rule("king_claims_pl_sig", "Король не отпускает сына в православие и требует трон для себя — договор рушится",
         "sig_king_claims_pl",
         [actor("A", 0, tags=["hetman_z_pl"]),
          actor("B", 1, tags=["vasa_pl"])],
         [setf("B", "claims_throne_pl")]),
]
NEW_LEVELS.append(level(
    "klushino_1610", 270, ACT4, "poland_battle", "klushino_field_pl", 3,
    ["klushino_field_pl", "tsar_tonsured_pl", "boyars_invite_pl", "king_claims_pl"],
    ["zolkiewski", "shuisky_pl", "wladyslaw4", "sigismund3"],
    {"zolkiewski": ["standing", "strong"], "shuisky_pl": ["crowned", "reigns", "standing", "strong"],
     "wladyslaw4": ["standing"], "sigismund3": ["crowned", "reigns", "standing"]},
    [("enemy_of", "zolkiewski", "shuisky_pl"), ("enemy_of", "shuisky_pl", "zolkiewski")],
    [flag("wladyslaw4", "tsar_elect_pl"), flag("shuisky_pl", "deposed_pl"), nflag("sigismund3", "claims_throne_pl")],
    [("klushino_field_pl", ["zolkiewski", "shuisky_pl"]), ("tsar_tonsured_pl", ["shuisky_pl"]),
     ("boyars_invite_pl", ["zolkiewski", "wladyslaw4"])],
    "simplification"))
TEXTS.update(texts("klushino_1610",
    "Клушино",
    "Гетман разбивает царское войско, царя сводят с престола — и бояре соглашаются звать на трон польского королевича",
    "Договор подписывает победитель — значит, сначала битва. А король Сигизмунд хотел трон для себя, и этого в нашей истории быть не должно.",
    "1610 год, Смутное время. Польский король Сигизмунд III осаждает Смоленск. Гетман Станислав Жолкевский с небольшим войском выходит навстречу армии, которую ведёт брат царя Василия Шуйского вместе со шведскими наёмниками.",
    "4 июля 1610 года под Клушином Жолкевский разбил войско, в несколько раз превосходившее его собственное; часть иноземных наёмников перешла на его сторону. Через две недели в Москве свели с престола царя Василия Шуйского и насильно постригли в монахи. Боярское правительство, «семибоярщина», 17 августа заключило с гетманом договор: царём станет королевич Владислав — при условии, что примет православие. Король Сигизмунд не отпустил сына и потребовал трон себе; договор рухнул, а польский гарнизон в Кремле в ноябре 1612 года сдался ополчению Минина и Пожарского. Шуйского увезли в Польшу, где он и умер.",
    "С. Жолкевский, «Начало и успех Московской войны»; «Новый летописец»"))

# ================================================================ chocim_1621
NEW_SCENES += [
    scene("cossacks_join_pl", "Казаки приходят в лагерь", ["sig_cossacks_join_pl"], 2, "⚔️", "соединиться", "icon_ally",
          ["гетман", "атаман"], "camp_walls_m"),
    scene("hetman_deathbed_pl", "Смерть гетмана в лагере", ["sig_hetman_deathbed_pl"], 2, "🕯️", "передать булаву", "icon_dead",
          ["умирающий", "преемник"], "deathbed_m"),
    scene("camp_holds_pl", "Лагерь держится", ["sig_camp_holds_pl"], 2, "🛡️", "отбить штурмы", "icon_crown",
          ["командующий", "султан"], "rescue_camp_c"),
    bait("chocim_field_pl", "Выйти в поле", "v_battle", 2, "open_battle", BATTLE),
]
NEW_RULES += [
    rule("cossacks_join_pl_sig", "К укреплённому лагерю под Хотином подходят запорожские казаки — войско почти удваивается",
         "sig_cossacks_join_pl",
         [actor("A", 0, tags=["hussar_hetman_pl"], notFlags=["defeated"]),
          actor("B", 1, tags=["cossack_pl"])],
         [setf("A", "fortified_pl"), setf("B", "allied_kh_pl"), addr("ally_of", "A", "B"), addr("ally_of", "B", "A")]),
    rule("hetman_deathbed_pl_sig", "Старый гетман умирает в лагере посреди осады, передав булаву",
         "sig_hetman_deathbed_pl",
         [actor("A", 0, tags=["hussar_hetman_pl"], flags=["fortified_pl"]),
          actor("B", 1, tags=["lubomirski_pl"])],
         [setf("A", "dead"), setf("B", "command_pl")]),
    rule("camp_holds_pl_sig", "Месяц штурмов — лагерь стоит, и султан уводит армию, согласившись на мир",
         "sig_camp_holds_pl",
         [actor("A", 0, tags=["lubomirski_pl"], flags=["command_pl"]),
          actor("B", 1, tags=["sultan2_pl"])],
         [setf("B", "withdrew_pl"), remf("B", "strong"), setf("A", "victor")]),
]
NEW_LEVELS.append(level(
    "chocim_1621", 280, ACT4, "poland_battle", "camp_holds_pl", 3,
    ["cossacks_join_pl", "hetman_deathbed_pl", "camp_holds_pl", "chocim_field_pl"],
    ["chodkiewicz", "lubomirski", "sahaidachny", "osman2"],
    {"chodkiewicz": ["standing"], "lubomirski": ["standing"], "sahaidachny": ["standing"],
     "osman2": ["crowned", "reigns", "standing", "strong"]},
    [("enemy_of", "chodkiewicz", "osman2"), ("enemy_of", "osman2", "chodkiewicz")],
    [flag("osman2", "withdrew_pl"), flag("sahaidachny", "allied_kh_pl")],
    [("cossacks_join_pl", ["chodkiewicz", "sahaidachny"]), ("hetman_deathbed_pl", ["chodkiewicz", "lubomirski"]),
     ("camp_holds_pl", ["lubomirski", "osman2"])],
    "simplification"))
TEXTS.update(texts("chocim_1621",
    "Хотин",
    "Укреплённый лагерь с подошедшими казаками месяц выдерживает штурмы огромной армии султана; гетман умирает, но лагерь стоит",
    "В поле с такой армией не выйти. Сила — в лагере и в тех, кто в него пришёл. И булаву гетман передаёт, уже умирая.",
    "1621 год. Молодой султан Осман II ведёт на Речь Посполитую огромную армию. На Днестре, у хотинской крепости, её ждёт укреплённый лагерь гетмана Яна Кароля Ходкевича — ему за шестьдесят, он болен. На помощь идут запорожские казаки гетмана Петра Сагайдачного.",
    "Со 2 сентября по 9 октября 1621 года лагерь под Хотином отбил все штурмы войска, в несколько раз большего. Ходкевич умер в лагере 24 сентября, командование принял Станислав Любомирский. Казаки Сагайдачного, раненого в бою, составляли едва ли не половину защитников. Султан согласился на мир. Вернувшись, Осман II обвинил в неудаче янычар, задумал их распустить — и в 1622 году был ими убит; это первое цареубийство в истории Османской империи.",
    "Якуб Собеский (отец короля), «Комментарии о Хотинской войне»"))

# ================================================================ veto_1652
NEW_SCENES += [
    scene("magnate_money_pl", "Деньги магната", ["sig_magnate_money_pl"], 1, "💰", "получить подкуп", "icon_plot",
          ["посол"], "court_purse"),
    scene("sejm_time_pl", "Срок сейма истёк", ["sig_sejm_time_pl"], 1, "⏳", "продлить сейм", "icon_ally",
          ["маршалок"], "council"),
    scene("nie_pozwalam_pl", "«Не позволяю!»", ["sig_nie_pozwalam_pl"], 2, "✋", "сорвать сейм", "icon_dead",
          ["посол", "маршалок"], "council_b"),
    bait("king_persuades_pl", "Король уговаривает посла", "v_parley", 2, "court_whisper", PARLEY),
]
NEW_RULES += [
    rule("magnate_money_pl_sig", "Посол из глухого повета получает деньги от могущественного магната",
         "sig_magnate_money_pl",
         [actor("A", 0, tags=["envoy_pl"])],
         [setf("A", "bribed_pl")]),
    rule("sejm_time_pl_sig", "Шесть недель сейма истекают; чтобы продлить работу, нужно согласие всех",
         "sig_sejm_time_pl",
         [actor("A", 0, tags=["marshal_pl"])],
         [setf("A", "time_up_pl")]),
    rule("nie_pozwalam_pl_sig", "Один посол кричит «не позволяю» и уходит — маршалок признаёт сейм сорванным",
         "sig_nie_pozwalam_pl",
         [actor("A", 0, tags=["envoy_pl"], flags=["bribed_pl"], notFlags=["conceded"]),
          actor("B", 1, tags=["marshal_pl"], flags=["time_up_pl"])],
         [setf("B", "sejm_broken_pl"), setf("A", "away")]),
]
NEW_LEVELS.append(level(
    "veto_1652", 290, ACT4, "poland_tension", "nie_pozwalam_pl", 3,
    ["magnate_money_pl", "sejm_time_pl", "nie_pozwalam_pl", "king_persuades_pl"],
    ["sicinski", "fredro_marshal", "jan_kazimierz"],
    {"jan_kazimierz": ["crowned", "reigns", "standing"], "fredro_marshal": ["standing"], "sicinski": ["standing"]}, [],
    [flag("fredro_marshal", "sejm_broken_pl")],
    [("magnate_money_pl", ["sicinski"]), ("sejm_time_pl", ["fredro_marshal"]),
     ("nie_pozwalam_pl", ["sicinski", "fredro_marshal"])],
    "simplification"))
TEXTS.update(texts("veto_1652",
    "Liberum veto",
    "Один посол кричит «не позволяю!» — и весь сейм Речи Посполитой распущен без единого решения",
    "Сорвать можно только сейм, срок которого истёк и который надо продлевать единогласно. И кричит «не позволяю» не просто так — за ним стоят деньги. Если король уговорит посла, ничего не случится — а случилось.",
    "1652 год. В Речи Посполитой решения сейма принимаются единогласно: каждый шляхтич равен другому. До сих пор несогласных уговаривали — или перекрикивали. Сейм в Варшаве идёт шесть недель, срок истекает.",
    "9 марта 1652 года посол из Упиты Владислав Сицинский заявил протест против продления сейма и уехал; маршалок Анджей Максимилиан Фредро признал, что без согласия всех сейм продолжаться не может. Говорили, что Сицинского подкупил литовский магнат Януш Радзивилл. Это был первый сейм, сорванный одним голосом, — liberum veto. В следующие сто с лишним лет так закончилась едва ли не половина сеймов, и государство почти потеряло способность принимать решения. По легенде, тело Сицинского после смерти не истлевало, и его, «проклятого», долго показывали в костёле в Упите.",
    "Дневник сейма 1652 г.; В. Конопчинский, «Liberum veto»"))

# ================================================================ jasna_gora_1655
NEW_SCENES += [
    scene("jasna_siege_pl", "Осада Ясной Горы", ["sig_jasna_siege_pl"], 2, "⛪", "держать оборону", "icon_crown",
          ["приор", "генерал"], "mock_walls"),
    scene("king_returns_pl", "Король возвращается из Силезии", ["sig_king_returns_pl"], 1, "🐎", "вернуться", "icon_ally",
          ["король"], "golden_gate_return"),
    scene("lwow_vows_pl", "Львовские обеты", ["sig_lwow_vows_pl"], 2, "🙏", "дать обет", "icon_crown",
          ["король", "приор"], "cathedral_altar"),
    bait("honourable_surrender_pl", "Почётная сдача", "v_parley", 2, "court_present", PARLEY),
]
NEW_RULES += [
    rule("jasna_siege_pl_sig", "Монахи и горстка шляхты отбивают штурмы шведов — генерал снимает осаду",
         "sig_jasna_siege_pl",
         [actor("A", 0, tags=["prior_pl"], notFlags=["conceded"]),
          actor("B", 1, tags=["swede_gen_pl"])],
         [setf("A", "held_pl"), setf("B", "lifted_pl"), remf("B", "strong")]),
    rule("king_returns_pl_sig", "Король, бежавший от шведов в Силезию, возвращается в страну",
         "sig_king_returns_pl",
         [actor("A", 0, tags=["jk_king_pl"], flags=["away"])],
         [setf("A", "returned_pl"), remf("A", "away")]),
    rule("lwow_vows_pl_sig", "Во Львове король провозглашает Богородицу королевой Польши и клянётся облегчить долю крестьян",
         "sig_lwow_vows_pl",
         [actor("A", 0, tags=["jk_king_pl"], flags=["returned_pl"]),
          actor("B", 1, tags=["prior_pl"], flags=["held_pl"])],
         [setf("A", "vows_pl")]),
]
NEW_LEVELS.append(level(
    "jasna_gora_1655", 300, ACT4, "poland_ceremony", "jasna_siege_pl", 3,
    ["jasna_siege_pl", "king_returns_pl", "lwow_vows_pl", "honourable_surrender_pl"],
    ["kordecki", "muller_sw", "jan_kazimierz"],
    {"kordecki": ["standing"], "muller_sw": ["standing", "strong"], "jan_kazimierz": ["crowned", "away"]},
    [("enemy_of", "muller_sw", "kordecki"), ("enemy_of", "kordecki", "muller_sw")],
    [flag("jan_kazimierz", "vows_pl"), flag("muller_sw", "lifted_pl")],
    [("jasna_siege_pl", ["kordecki", "muller_sw"]), ("king_returns_pl", ["jan_kazimierz"]),
     ("lwow_vows_pl", ["jan_kazimierz", "kordecki"])],
    "simplification"))
TEXTS.update(texts("jasna_gora_1655",
    "Ясная Гора",
    "Монастырь, который защищают монахи и горстка шляхты, отбивает шведов — и вся страна поднимается против захватчиков",
    "Генерал предложит сдаться с честью; приор не уступил. Король не может давать обеты из Силезии — сначала ему нужно вернуться. А обет он дал, когда монастырь уже выстоял.",
    "1655 год, «Потоп». Шведская армия заняла почти всю Речь Посполитую, магнаты переходят на сторону шведского короля, Ян Казимир бежал в Силезию. Шведский генерал Бурхард Мюллер подходит к монастырю паулинов на Ясной Горе в Ченстохове — святыне с иконой Богоматери.",
    "С 18 ноября по 27 декабря 1655 года около трёх тысяч шведов осаждали Ясную Гору, которую обороняли около семидесяти монахов и пара сотен солдат и шляхты под началом приора Августина Кордецкого; монастырь устоял. Весть об обороне разошлась по стране и помогла поднять восстание против шведов. 1 апреля 1656 года во Львове Ян Казимир провозгласил Богородицу королевой Польши и обещал облегчить долю крестьян — обещание так и не выполнили. Генрик Сенкевич сделал эту осаду центром романа «Потоп», добавив вымышленного Кмицица, взорвавшего шведскую пушку.",
    "А. Кордецкий, «Новая гигантомахия» (1658); Самуэль Пуфендорф, «О деяниях Карла Густава»"))

# ================================================================ twardowski (легенда)
NEW_SCENES += [
    scene("pact_krzemionki_pl", "Договор на Кшемёнках", ["sig_pact_krzemionki_pl"], 2, "📜", "продать душу", "icon_plot",
          ["шляхтич", "чёрт"], "devil_bridge"),
    scene("inn_rome_pl", "Корчма «Рим»", ["sig_inn_rome_pl"], 2, "🍺", "зайти в корчму", "icon_dead",
          ["шляхтич", "чёрт"], "feast"),
    scene("marian_hymn_pl", "Песнь Богородице", ["sig_marian_hymn_pl"], 1, "🌙", "запеть", "icon_crown",
          ["пленник чёрта"], "night_flight"),
    scene("real_rome_pl", "Ехать в Рим", ["sig_real_rome_pl"], 1, "🏛️", "отправиться в Рим", "icon_ally",
          ["путник"], "rome_walls"),
]
NEW_RULES += [
    rule("pact_krzemionki_pl_sig", "Шляхтич подписывает кровью договор: чёрт служит ему, а душу заберёт — но только в Риме",
         "sig_pact_krzemionki_pl",
         [actor("A", 0, tags=["sorcerer_pl"], notFlags=["pact_pl"]),
          actor("B", 1, tags=["devil_pl"])],
         [setf("A", "pact_pl")]),
    rule("inn_rome_pl_sig", "Чёрт ловит его в корчме, которая называется «Рим», — и уносит в небо",
         "sig_inn_rome_pl",
         [actor("A", 0, tags=["sorcerer_pl"], flags=["pact_pl"]),
          actor("B", 1, tags=["devil_pl"])],
         [setf("A", "seized_pl")]),
    rule("marian_hymn_pl_sig", "Летя над землёй, пленник запевает песнь Богородице — чёрт роняет его, и он повисает на Луне",
         "sig_marian_hymn_pl",
         [actor("A", 0, tags=["sorcerer_pl"], flags=["seized_pl"])],
         [setf("A", "on_moon_pl")]),
    rule("real_rome_pl_sig", "Шляхтич, помня договор, за версту обходит настоящий Рим — и думает, что спасён",
         "sig_real_rome_pl",
         [actor("A", 0, tags=["sorcerer_pl"], flags=["pact_pl"])],
         [setf("A", "avoids_rome_pl")]),
]
NEW_LEVELS.append(level(
    "twardowski", 305, ACT4, "poland_romance", "inn_rome_pl", 3,
    ["pact_krzemionki_pl", "inn_rome_pl", "marian_hymn_pl", "real_rome_pl"],
    ["twardowski", "devil_pl"],
    {}, [],
    [flag("twardowski", "on_moon_pl")],
    [("pact_krzemionki_pl", ["twardowski", "devil_pl"]), ("inn_rome_pl", ["twardowski", "devil_pl"]),
     ("marian_hymn_pl", ["twardowski"])],
    "legend"))
TEXTS.update(texts("twardowski",
    "Пан Твардовский",
    "Краковский шляхтич продаёт душу чёрту с условием, что тот заберёт её только в Риме, — и попадается в корчме под названием «Рим»",
    "Без договора чёрту нечего забирать. В настоящий Рим Твардовский не поедет — его ловят там, где он не ждёт. А спасает его песня, а не хитрость.",
    "XVI век, Краков. Учёный шляхтич Твардовский хочет знаний и власти над природой. Ночью на Кшемёнках, известняковых холмах за Вислой, он вызывает чёрта.",
    "Шляхтич Твардовский хотел знать всё, что скрыто от людей. Однажды ночью на Кшемёнках за Вислой он вызвал чёрта и подписал кровью договор: чёрт будет служить ему во всём, а душу заберёт только тогда, когда Твардовский окажется в Риме. Твардовский летал на петухе, скакал на нарисованном коне, показывал королю в волшебном зеркале его умершую жену — и много лет обходил Рим стороной. Но однажды он зашёл в придорожную корчму, не зная, что она называется «Рим». Чёрт явился, схватил его и понёс в небо. Тогда Твардовский запел песнь Богородице, которую пел ещё мальчиком, — и чёрт выпустил его из когтей. Твардовский повис на Луне и сидит там до сих пор, а его единственный друг, паучок, спускается на землю на ниточке и приносит ему новости.",
    "Польские народные предания; А. Мицкевич, «Пани Твардовская» (1822)"))

# ================================================================ chocim_1673
NEW_SCENES += [
    scene("frost_night_pl", "Ночь на морозе", ["sig_frost_night_pl"], 2, "❄️", "держать врага в напряжении", "icon_plot",
          ["гетман", "паша"], "danube_winter"),
    scene("dawn_storm_pl", "Штурм лагеря на рассвете", ["sig_dawn_storm_pl"], 2, "🌅", "штурмовать", "icon_dead",
          ["гетман", "паша"], "breach_wall"),
    scene("election_1674_pl", "Элекция 1674 года", ["sig_election_1674_pl"], 1, "👑", "быть избранным", "icon_crown",
          ["победитель"], "coronation_b"),
    bait("chocim_headon_pl", "Атаковать сразу", "v_battle", 2, "open_battle", BATTLE),
]
NEW_RULES += [
    rule("frost_night_pl_sig", "Всю ледяную ночь гетман держит турок в ожидании атаки — к утру они окоченели в доспехах",
         "sig_frost_night_pl",
         [actor("A", 0, tags=["sobieski_pl"]),
          actor("B", 1, tags=["pasha_pl"], flags=["strong"])],
         [setf("B", "frozen_pl"), remf("B", "strong")]),
    rule("dawn_storm_pl_sig", "На рассвете пехота взламывает вал, гусария врывается в лагерь — армия паши разбита",
         "sig_dawn_storm_pl",
         [actor("A", 0, tags=["sobieski_pl"], notFlags=["defeated"]),
          actor("B", 1, tags=["pasha_pl"], flags=["frozen_pl"])],
         [setf("B", "defeated"), setf("A", "victor")]),
    rule("election_1674_pl_sig", "Слава победителя приводит его на трон — шляхта выбирает гетмана королём",
         "sig_election_1674_pl",
         [actor("A", 0, tags=["sobieski_pl"], flags=["victor"])],
         [setf("A", "king_sob_pl"), setf("A", "crowned"), setf("A", "reigns")]),
]
NEW_LEVELS.append(level(
    "chocim_1673", 310, ACT4, "poland_battle", "dawn_storm_pl", 3,
    ["frost_night_pl", "dawn_storm_pl", "election_1674_pl", "chocim_headon_pl"],
    ["sobieski", "husein_pasha"],
    {"sobieski": ["standing"], "husein_pasha": ["standing", "strong"]},
    [("enemy_of", "sobieski", "husein_pasha"), ("enemy_of", "husein_pasha", "sobieski")],
    [flag("sobieski", "king_sob_pl")],
    [("frost_night_pl", ["sobieski", "husein_pasha"]), ("dawn_storm_pl", ["sobieski", "husein_pasha"]),
     ("election_1674_pl", ["sobieski"])],
    "fact"))
TEXTS.update(texts("chocim_1673",
    "Хотин-1673",
    "Гетман всю ночь держит турок на морозе в ожидании атаки, на рассвете берёт их лагерь — и становится королём",
    "Укреплённый лагерь в лоб не взять. Пусть враг устанет раньше, чем начнётся бой. Короной за победу награждает шляхта — но только победителя.",
    "Ноябрь 1673 года. Под Хотином на Днестре стоит укреплённый лагерь турецкого войска Гусейн-паши. Его осаждает войско Речи Посполитой под командованием великого коронного гетмана Яна Собеского. Холод, ледяной дождь.",
    "В ночь на 11 ноября 1673 года Собеский держал войско в боевой готовности, и турки, ждавшие штурма, провели ночь в доспехах на морозе. На рассвете пехота взломала вал, гусария ворвалась в лагерь; армия Гусейн-паши была почти уничтожена, многие погибли при обрушении моста через Днестр. Накануне битвы, 10 ноября, умер король Михаил Корибут Вишневецкий — в войске об этом ещё не знали. 21 мая 1674 года Собеского избрали королём.",
    "Я. Собеский, письма к Марысеньке; В. Коховский, «Климактеры»"))

# ================================================================ vienna_1683
NEW_SCENES += [
    scene("spy_lines_pl", "Через турецкий лагерь", ["sig_spy_lines_pl"], 2, "🥷", "пробраться с письмом", "icon_ally",
          ["лазутчик", "кому весть"], "cross_the_lines"),
    scene("relief_march_pl", "Король идёт на выручку", ["sig_relief_march_pl"], 2, "🐎", "выступить", "icon_ally",
          ["король", "лазутчик"], "road_to_vienna"),
    scene("kahlenberg_charge_pl", "Атака с Каленберга", ["sig_kahlenberg_charge_pl"], 2, "🪽", "ударить с холма", "icon_dead",
          ["король", "визирь"], "line_of_battle_a"),
    bait("emperor_sortie_pl", "Вылазка императора", "v_battle", 2, "attila_walls", BATTLE),
]
NEW_RULES += [
    rule("spy_lines_pl_sig", "Переодетый турком лазутчик проходит через лагерь осаждающих с письмом о помощи",
         "sig_spy_lines_pl",
         [actor("A", 0, tags=["spy_pl"]),
          actor("B", 1, tags=["emperor_l_pl"])],
         [setf("A", "delivered_pl")]),
    rule("relief_march_pl_sig", "Получив весть, король ведёт войско на выручку осаждённой столицы империи",
         "sig_relief_march_pl",
         [actor("A", 0, tags=["sobieski_pl"]),
          actor("B", 1, tags=["spy_pl"], flags=["delivered_pl"])],
         [setf("A", "relief_pl"), setf("A", "strong")]),
    rule("kahlenberg_charge_pl_sig", "С холмов Каленберга король ведёт крупнейшую кавалерийскую атаку в истории — лагерь визиря бежит",
         "sig_kahlenberg_charge_pl",
         [actor("A", 0, tags=["sobieski_pl"], flags=["relief_pl"]),
          actor("B", 1, tags=["vizier_pl"])],
         [setf("B", "defeated"), setf("A", "savior_pl"), setf("A", "victor")]),
]
NEW_LEVELS.append(level(
    "vienna_1683", 320, ACT4, "poland_battle", "kahlenberg_charge_pl", 3,
    ["spy_lines_pl", "relief_march_pl", "kahlenberg_charge_pl", "emperor_sortie_pl"],
    ["sobieski", "kara_mustafa", "leopold1", "kulczycki"],
    {"sobieski": ["crowned", "reigns", "standing"], "kara_mustafa": ["standing", "strong"],
     "leopold1": ["crowned", "standing"], "kulczycki": ["standing"]},
    [("enemy_of", "kara_mustafa", "leopold1"), ("enemy_of", "leopold1", "kara_mustafa"),
     ("enemy_of", "kara_mustafa", "sobieski"), ("enemy_of", "sobieski", "kara_mustafa")],
    [flag("sobieski", "savior_pl"), flag("kara_mustafa", "defeated"), nflag("leopold1", "defeated")],
    [("spy_lines_pl", ["kulczycki", "leopold1"]), ("relief_march_pl", ["sobieski", "kulczycki"]),
     ("kahlenberg_charge_pl", ["sobieski", "kara_mustafa"])],
    "simplification"))
TEXTS.update(texts("vienna_1683",
    "Вена",
    "Лазутчик проносит весть через турецкий лагерь, король Ян III ведёт войско на выручку — и крылатые гусары с холма спасают Вену",
    "Король не придёт, пока не узнает. Император из Вены уехал, и вылазка ему не по силам. Решает атака с холма.",
    "Лето 1683 года. Великий визирь Кара-Мустафа с огромной османской армией осаждает Вену, столицу империи Габсбургов. Император Леопольд I уехал в Пассау. Город держится из последних сил. На помощь обещал прийти польский король Ян III Собеский — но для этого кто-то должен пройти через турецкий лагерь.",
    "В августе Ежи Кульчицкий, знавший турецкий язык, в турецкой одежде прошёл через лагерь осаждающих и обратно с письмами. 12 сентября 1683 года Собеский повёл объединённую армию с холмов Каленберга; атака около восемнадцати тысяч всадников, среди них несколько тысяч крылатых гусар, считается крупнейшей кавалерийской атакой в истории. Визирь бежал, бросив лагерь; в декабре его по приказу султана задушили в Белграде. Собеский написал папе: «Venimus, vidimus, Deus vicit» — «Пришли, увидели, Бог победил». Легенда приписывает Кульчицкому первую венскую кофейню на трофейных зёрнах; на деле первую открыл армянин Иоганнес Диодато в 1685 году.",
    "Ян III Собеский, письма к Марысеньке (1683); Дж. Стойе, «Осада Вены» (1964)"))

# ================================================================ leszczynski_1734
NEW_SCENES += [
    scene("minority_election_pl", "Выборы под охраной войск", ["sig_minority_election_pl"], 2, "🗳️", "посадить своего", "icon_crown",
          ["фельдмаршал", "саксонец"], "praetorian_camp"),
    scene("gdansk_siege_pl", "Осада Гданьска", ["sig_gdansk_siege_pl"], 2, "🏰", "осадить город", "icon_dead",
          ["фельдмаршал", "король"], "siege"),
    scene("peasant_escape_pl", "Бегство в крестьянской одежде", ["sig_peasant_escape_pl"], 1, "🧥", "уйти переодетым", "icon_ally",
          ["король"], "beggar_disguise"),
    bait("hold_gdansk_pl", "Держаться до конца", "v_battle", 2, "breach_wall", BATTLE),
]
NEW_RULES += [
    rule("minority_election_pl_sig", "Под охраной иностранных войск горстка выборщиков избирает саксонского курфюрста",
         "sig_minority_election_pl",
         [actor("A", 0, tags=["field_marshal_pl"]),
          actor("B", 1, tags=["saxon_pl"])],
         [setf("B", "crowned_saxon_pl"), setf("B", "crowned"), setf("A", "strong")]),
    rule("gdansk_siege_pl_sig", "Избранного большинством короля осаждают в Гданьске",
         "sig_gdansk_siege_pl",
         [actor("A", 0, tags=["field_marshal_pl"]),
          actor("B", 1, tags=["leszczynski_pl"], flags=["elected_pl"])],
         [setf("B", "besieged_pl")]),
    rule("peasant_escape_pl_sig", "Король переодевается крестьянином и уходит из осаждённого города через болота",
         "sig_peasant_escape_pl",
         [actor("A", 0, tags=["leszczynski_pl"], flags=["besieged_pl"], notFlags=["defeated"])],
         [setf("A", "escaped_pl"), setf("A", "away")]),
]
NEW_LEVELS.append(level(
    "leszczynski_1734", 330, ACT4, "poland_tension", "peasant_escape_pl", 3,
    ["minority_election_pl", "gdansk_siege_pl", "peasant_escape_pl", "hold_gdansk_pl"],
    ["leszczynski", "august3", "munnich"],
    {"leszczynski": ["elected_pl", "crowned", "standing"], "munnich": ["standing", "strong"], "august3": ["standing"]},
    [("enemy_of", "munnich", "leszczynski"), ("enemy_of", "leszczynski", "munnich")],
    [flag("leszczynski", "escaped_pl"), flag("august3", "crowned_saxon_pl")],
    [("minority_election_pl", ["munnich", "august3"]), ("gdansk_siege_pl", ["munnich", "leszczynski"]),
     ("peasant_escape_pl", ["leszczynski"])],
    "fact"))
TEXTS.update(texts("leszczynski_1734",
    "Король в крестьянской одежде",
    "Шляхта избирает короля огромным большинством, но иностранные войска сажают на трон другого — и избранник бежит из Гданьска переодетым крестьянином",
    "Бежать можно только из осады. Держаться до конца — значит попасть в плен. Пока одного осаждают, на трон уже сажают другого.",
    "1733 год. Шляхта огромным большинством избрала королём Станислава Лещинского — поляка, тестя французского короля Людовика XV. Но соседи хотят на троне саксонского курфюрста Августа. В страну входит русская армия, и выборы проводят ещё раз — для другого кандидата.",
    "В сентябре 1733 года за Лещинского голосовали около тринадцати тысяч шляхтичей; под охраной русских войск небольшая группа выборщиков избрала Августа III. Лещинский укрылся в Гданьске, который в 1734 году осадила русская армия фельдмаршала Миниха; 27 июня он бежал из города, переодевшись крестьянином. Началась война за польское наследство. В 1736 году Лещинский отрёкся и получил в пожизненное владение Лотарингию — площадь Станислава в Нанси, построенная при нём, теперь в списке ЮНЕСКО. Он умер в 1766 году, когда от камина вспыхнул его халат.",
    "Ст. Лещинский, «Глас вольный, вольность обеспечивающий» (1749)"))

if __name__ == "__main__":
    P.NEW_CHARS, P.NEW_SCENES, P.NEW_RULES, P.NEW_LEVELS, P.TEXTS = NEW_CHARS, NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS
    P.CHAPTER_TEXTS = {"act.poland.4": ACT4}
    P.main()
