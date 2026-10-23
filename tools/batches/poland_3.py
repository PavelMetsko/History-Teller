#!/usr/bin/env python3
"""Пачка 3 главы «Польша»: Ягеллоны, 1384–1569, 9 уровней.

    python3 tools/batches/poland_3.py [repo_root]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, level, texts

ACT3 = "Акт III · Ягеллоны"

NEW_CHARS = [
    char("jadwiga", "Королева Ядвига", ["jadwiga_pl"], "👑"),
    char("jagiello", "Владислав Ягайло", ["jagiello_pl"], "👑"),
    char("wilhelm_hab", "Вильгельм Габсбург", ["habsburg_pl"], "💔"),
    char("vytautas", "Великий князь Витовт", ["vytautas_pl"], "⚔️"),
    char("jungingen", "Магистр Ульрих фон Юнгинген", ["grandmaster_pl"], "✠"),
    char("zawisza", "Завиша Чёрный", ["knight_pl"], "🛡️"),
    char("wladyslaw3", "Владислав Варненчик", ["varna_king_pl"], "👑"),
    char("hunyadi", "Янош Хуньяди", ["hunyadi_pl"], "⚔️"),
    char("murad2", "Султан Мурад II", ["sultan_pl"], "🌙"),
    char("casimir4", "Казимир Ягеллончик", ["jag_king_pl"], "👑"),
    char("grandmaster_lv", "Магистр Людвиг фон Эрлихсхаузен", ["grandmaster_pl"], "✠"),
    char("czerwonka", "Капитан наёмников Червонка", ["merc_pl"], "💰"),
    char("copernicus", "Николай Коперник", ["canon_pl"], "🔭"),
    char("sigismund1", "Сигизмунд Старый", ["old_king_pl"], "👑"),
    char("albrecht_hz", "Альбрехт Гогенцоллерн", ["albrecht_pl"], "🦅"),
    char("bona", "Королева Бона Сфорца", ["bona_pl"], "👑"),
    char("sigismund2", "Сигизмунд Август", ["august_pl"], "👑"),
    char("barbara", "Барбара Радзивилл", ["barbara_pl"], "💍"),
    char("radziwill_rudy", "Николай Радзивилл Рыжий", ["lith_magnate_pl"], "🏰"),
    char("volhynian_noble", "Волынский шляхтич", ["volhynia_pl"], "🌾"),
    char("philip2_es", "Король Филипп II Испанский", ["spain_pl"], "👑"),
    char("pappacoda", "Придворный Паппакода", ["courtier_pl"], "🗡️"),
]
OLD_CHARS = ["komtur"]   # уже в БД (пачка 2)

NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS = [], [], [], {}

# ================================================================ jadwiga_axe (1384–1386)
NEW_SCENES += [
    scene("wilhelm_sent_pl", "Вильгельма — прочь из Кракова", ["sig_wilhelm_sent_pl"], 2, "🪓", "отказаться от любви", "icon_plot",
          ["королева", "жених"], "flee_castle"),
    scene("krewo_union_pl", "Уния в Креве", ["sig_krewo_union_pl"], 2, "📜", "обещать крещение", "icon_ally",
          ["великий князь", "королева"], "papal_legate"),
    scene("krakow_1386_pl", "Крещение и свадьба в Кракове", ["sig_krakow_1386_pl"], 2, "💒", "креститься и венчаться", "icon_crown",
          ["жених", "королева"], "cathedral_altar"),
    scene("secret_vows_pl", "Тайное венчание с Вильгельмом", ["v_wed"], 2, "💍", "свадьба", "icon_ally",
          ["жених", "невеста"], "polish_wedding"),
]
NEW_RULES += [
    rule("wilhelm_sent_pl_sig", "Паны выставляют жениха из Вавеля; по преданию, королева рвётся к нему с топором — и отступает",
         "sig_wilhelm_sent_pl",
         [actor("A", 0, tags=["jadwiga_pl"], notFlags=["married"]),
          actor("B", 1, tags=["habsburg_pl"])],
         [setf("A", "renounced_pl"), setf("B", "away")]),
    rule("krewo_union_pl_sig", "Великий князь литовский обещает креститься сам, крестить Литву и навечно соединить её с Короной",
         "sig_krewo_union_pl",
         [actor("A", 0, tags=["jagiello_pl"], flags=["pagan"]),
          actor("B", 1, tags=["jadwiga_pl"], flags=["renounced_pl"], notFlags=["married"])],
         [setf("A", "union_pl"), addr("ally_of", "A", "B"), addr("ally_of", "B", "A")]),
    rule("krakow_1386_pl_sig", "Язычник крестится Владиславом, венчается с королевой и коронуется королём Польши",
         "sig_krakow_1386_pl",
         [actor("A", 0, tags=["jagiello_pl"], flags=["union_pl"]),
          actor("B", 1, tags=["jadwiga_pl"])],
         [setf("A", "baptized"), remf("A", "pagan"), setf("A", "crowned"), setf("A", "king_jag_pl"),
          addr("wed", "A", "B"), addr("wed", "B", "A")]),
]
NEW_LEVELS.append(level(
    "jadwiga_axe", 140, ACT3, "poland_romance", "krakow_1386_pl", 3,
    ["wilhelm_sent_pl", "krewo_union_pl", "krakow_1386_pl", "secret_vows_pl"],
    ["jadwiga", "jagiello", "wilhelm_hab"],
    {"jadwiga": ["crowned", "reigns", "standing"], "jagiello": ["pagan", "reigns", "standing"], "wilhelm_hab": ["standing"]},
    [],
    [flag("jagiello", "king_jag_pl"), flag("jagiello", "baptized")],
    [("wilhelm_sent_pl", ["jadwiga", "wilhelm_hab"]), ("krewo_union_pl", ["jagiello", "jadwiga"]),
     ("krakow_1386_pl", ["jagiello", "jadwiga"])],
    "simplification"))
TEXTS.update(texts("jadwiga_axe",
    "Ядвига и Ягайло",
    "Юная королева отказывается от любимого жениха и выходит за литовского князя-язычника — и две страны соединяются на четыре века",
    "Сердце королевы отдано Вильгельму, и тайное венчание кажется таким простым. Но тогда не будет ни унии, ни крещения Литвы. Сначала нужно отказаться — и только потом звать литовца.",
    "1384 год. Польшей правит десятилетняя Ядвига — коронованная «королём», а не королевой, потому что женщина на троне не предусмотрена. С детства она обручена с австрийским княжичем Вильгельмом. Польские паны ищут ей другого мужа: великого князя Литвы Ягайло, язычника, чья страна огромна и окружена врагами.",
    "Ядвигу короновали 16 октября 1384 года. Вильгельм приехал в Краков, но паны выдворили его; по Длугошу, королева хотела прорубить ворота Вавеля топором, и её остановил подканцлер Дмитр из Горая. 14 августа 1385 года в Креве Ягайло обязался креститься, крестить Литву и присоединить её к Короне. 15 февраля 1386 года в Кракове он крестился с именем Владислав, через три дня женился на Ядвиге, а 4 марта был коронован. Так началась уния Польши и Литвы и династия Ягеллонов; Литва стала последней языческой страной Европы, принявшей христианство.",
    "Ян Длугош, «Анналы», X; Кревский акт (1385)"))

# ================================================================ grunwald_1410
NEW_SCENES += [
    scene("two_swords_pl", "Два меча", ["sig_two_swords_pl"], 2, "⚔️", "бросить вызов", "icon_plot",
          ["магистр", "король"], "duel_challenge"),
    scene("lithuanian_retreat_pl", "Отход литовских хоругвей", ["sig_lithuanian_retreat_pl"], 2, "🏇", "отступить", "icon_plot",
          ["великий князь", "погоня"], "hal_retreats"),
    scene("grunwald_charge_pl", "Удар королевских хоругвей", ["sig_grunwald_charge_pl"], 2, "⚔️", "ударить", "icon_dead",
          ["король", "магистр"], "agincourt_field"),
    scene("knight_duel_pl", "Рыцарь против магистра", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "duel_field_b"),
]
NEW_RULES += [
    rule("two_swords_pl_sig", "Герольды магистра привозят королю два обнажённых меча — «в помощь», чтобы тот наконец вышел из леса",
         "sig_two_swords_pl",
         [actor("A", 0, tags=["grandmaster_pl"], flags=["strong"]),
          actor("B", 1, tags=["jagiello_pl"])],
         [setf("A", "challenge_sent_pl"), setf("B", "challenged_pl")]),
    rule("lithuanian_retreat_pl_sig", "Литовские хоругви отходят, и рыцари ордена, решив, что бой выигран, бросаются в погоню",
         "sig_lithuanian_retreat_pl",
         [actor("A", 0, tags=["vytautas_pl"]),
          actor("B", 1, tags=["grandmaster_pl"], flags=["challenge_sent_pl"])],
         [setf("B", "pursuing_pl"), remf("B", "strong")]),
    rule("grunwald_charge_pl_sig", "Король бросает в бой резерв — смешавшееся войско ордена окружено, магистр гибнет",
         "sig_grunwald_charge_pl",
         [actor("A", 0, tags=["jagiello_pl"], flags=["challenged_pl"]),
          actor("B", 1, tags=["grandmaster_pl"], flags=["pursuing_pl"])],
         [setf("B", "dead"), setf("A", "victor")]),
]
NEW_LEVELS.append(level(
    "grunwald_1410", 150, ACT3, "poland_battle", "grunwald_charge_pl", 3,
    ["two_swords_pl", "lithuanian_retreat_pl", "grunwald_charge_pl", "knight_duel_pl"],
    ["jagiello", "vytautas", "jungingen", "zawisza"],
    {"jagiello": ["crowned", "reigns", "standing", "strong"], "vytautas": ["reigns", "standing", "strong"],
     "jungingen": ["standing", "strong"], "zawisza": ["standing"]},
    [("enemy_of", "jungingen", "jagiello"), ("enemy_of", "jagiello", "jungingen"),
     ("enemy_of", "jungingen", "vytautas"), ("enemy_of", "vytautas", "jungingen"),
     ("enemy_of", "zawisza", "jungingen"), ("enemy_of", "jungingen", "zawisza")],
    [flag("jungingen", "dead"), nflag("zawisza", "defeated")],
    [("two_swords_pl", ["jungingen", "jagiello"]), ("lithuanian_retreat_pl", ["vytautas", "jungingen"]),
     ("grunwald_charge_pl", ["jagiello", "jungingen"])],
    "simplification"))
TEXTS.update(texts("grunwald_1410",
    "Грюнвальд",
    "Магистр шлёт королю два меча в насмешку, литовцы отходят, рыцари бросаются в погоню — и король бьёт смешавшееся войско",
    "Орден силён, пока стоит строем, — даже лучший рыцарь в одиночку его не возьмёт. Пусть он сам разорвёт строй в погоне. А король ждёт вызова.",
    "15 июля 1410 года, жара. На поле между Грюнвальдом и Танненбергом сошлись войска Тевтонского ордена и союзные войска Польши и Литвы — одна из крупнейших битв средневековой Европы. Король Ягайло стоит в лесу, слушает мессу и не начинает.",
    "Герольды магистра Ульриха фон Юнгингена привезли Ягайле два обнажённых меча, — эти мечи потом стали символом победы. Литовские хоругви Витовта отступили — бегство это было или притворный манёвр, историки спорят до сих пор, — и часть рыцарей ордена бросилась преследовать их. Ягайло ввёл в бой резервы, войско ордена окружили, магистр погиб вместе с большинством орденских братьев. В бою отличился Завиша Чёрный из Гарбова — с тех пор поляки говорят «положиться как на Завишу». Мальборк после битвы взять не удалось, но могущество ордена было сломлено.",
    "Ян Длугош, «Анналы», XI; «Хроника конфликта Владислава, короля Польши, с крестоносцами»"))

# ================================================================ varna_1444
NEW_SCENES += [
    scene("szeged_peace_pl", "Сегедский мир", ["sig_szeged_peace_pl"], 2, "🤝", "поклясться в мире", "icon_ally",
          ["король", "султан"], "treaty_king"),
    scene("broken_oath_pl", "Клятву снимает легат", ["sig_broken_oath_pl"], 1, "📜", "нарушить клятву", "icon_plot",
          ["король"], "papal_legate"),
    scene("varna_charge_pl", "Атака на янычар", ["sig_varna_charge_pl"], 2, "⚔️", "ударить на султана", "icon_dead",
          ["король", "султан"], "golden_horn_battle"),
    scene("hunyadi_line_pl", "Строй Хуньяди", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "line_of_battle_a"),
]
NEW_RULES += [
    rule("szeged_peace_pl_sig", "Король и султан клянутся на десять лет мира",
         "sig_szeged_peace_pl",
         [actor("A", 0, tags=["varna_king_pl"]),
          actor("B", 1, tags=["sultan_pl"])],
         [setf("A", "sworn_peace_pl"), setf("B", "sworn_peace_pl")]),
    rule("broken_oath_pl_sig", "Папский легат освобождает короля от клятвы неверным — и крестовый поход продолжается",
         "sig_broken_oath_pl",
         [actor("A", 0, tags=["varna_king_pl"], flags=["sworn_peace_pl"])],
         [setf("A", "oathbreaker_pl")]),
    rule("varna_charge_pl_sig", "Двадцатилетний король с гвардией бросается на шатёр султана — и гибнет среди янычар",
         "sig_varna_charge_pl",
         [actor("A", 0, tags=["varna_king_pl"], flags=["oathbreaker_pl"]),
          actor("B", 1, tags=["sultan_pl"])],
         [setf("A", "dead"), setf("B", "victor")]),
]
NEW_LEVELS.append(level(
    "varna_1444", 160, ACT3, "poland_battle", "varna_charge_pl", 3,
    ["szeged_peace_pl", "broken_oath_pl", "varna_charge_pl", "hunyadi_line_pl"],
    ["wladyslaw3", "hunyadi", "murad2"],
    {"wladyslaw3": ["crowned", "reigns", "standing", "strong"], "hunyadi": ["standing", "strong"],
     "murad2": ["crowned", "reigns", "standing", "strong"]},
    [("enemy_of", "murad2", "wladyslaw3"), ("enemy_of", "wladyslaw3", "murad2"),
     ("enemy_of", "murad2", "hunyadi"), ("enemy_of", "hunyadi", "murad2")],
    [flag("wladyslaw3", "dead"), flag("wladyslaw3", "oathbreaker_pl")],
    [("szeged_peace_pl", ["wladyslaw3", "murad2"]), ("broken_oath_pl", ["wladyslaw3"]),
     ("varna_charge_pl", ["wladyslaw3", "murad2"])],
    "simplification"))
TEXTS.update(texts("varna_1444",
    "Варна",
    "Молодой король клянётся султану в мире, нарушает клятву — и гибнет в атаке на шатёр султана",
    "Нарушить можно только данную клятву. Хуньяди держит строй — но поход решает не он. Судьбу битвы решил порыв короля.",
    "1444 год. Владислав III, король Польши и Венгрии, — ему двадцать лет. Летом в Сегеде он клянётся султану Мураду II в десятилетнем мире. Но папа и Венеция обещают флот, кардинал-легат Чезарини говорит, что клятва неверным не обязывает, и крестовый поход продолжается.",
    "10 ноября 1444 года под Варной на черноморском побережье Владислав, вопреки совету Яноша Хуньяди держать строй, с пятью сотнями рыцарей атаковал янычар у ставки султана и погиб; его голову, по преданию, Мурад отправил в Бурсу в банке мёда. Говорят, султан велел поднять на копьё грамоту о нарушенном мире как знамя. Тело короля не нашли — потому долго ходили легенды, что он спасся; одна из них сделала его португальским рыцарем Энрике Немцем на Мадейре. Через девять лет Константинополь пал.",
    "Ян Длугош, «Анналы», XII; Каллимах, «История короля Владислава»"))

# ================================================================ malbork_1457
NEW_SCENES += [
    scene("unpaid_wages_pl", "Жалованье не плачено", ["sig_unpaid_wages_pl"], 2, "💸", "задолжать наёмникам", "icon_plot",
          ["магистр", "наёмник"], "empty_treasury"),
    scene("buy_malbork_pl", "Купить Мальборк", ["sig_buy_malbork_pl"], 2, "🏰", "выкупить замок", "icon_crown",
          ["король", "наёмник"], "gold_for_san_marco"),
    scene("storm_malbork_pl", "Штурм Мальборка", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "breach_wall"),
    scene("early_bribe_pl", "Подкупить заранее", ["v_bribe"], 2, "💰", "подкуп", "icon_ally",
          ["кто платит", "кто берёт"], "bank_loan"),
]
NEW_RULES += [
    rule("unpaid_wages_pl_sig", "Орден не может заплатить наёмникам и отдаёт им в залог свои замки — вместе с Мальборком",
         "sig_unpaid_wages_pl",
         [actor("A", 0, tags=["grandmaster_pl"]),
          actor("B", 1, tags=["merc_pl"], notFlags=["bought"])],
         [setf("B", "holds_castle_pl"), remf("A", "strong")]),
    rule("buy_malbork_pl_sig", "Король платит наёмникам 190 тысяч флоринов — и получает столицу ордена без штурма",
         "sig_buy_malbork_pl",
         [actor("A", 0, tags=["jag_king_pl"], notFlags=["defeated"]),
          actor("B", 1, tags=["merc_pl"], flags=["holds_castle_pl"], notFlags=["bought"])],
         [setf("A", "malbork_pl"), setf("B", "paid_pl")]),
]
NEW_LEVELS.append(level(
    "malbork_1457", 170, ACT3, "poland_tension", "buy_malbork_pl", 2,
    ["unpaid_wages_pl", "buy_malbork_pl", "storm_malbork_pl", "early_bribe_pl"],
    ["casimir4", "grandmaster_lv", "czerwonka"],
    {"casimir4": ["crowned", "reigns", "standing"], "grandmaster_lv": ["standing", "strong"], "czerwonka": ["standing"]},
    [("enemy_of", "casimir4", "grandmaster_lv"), ("enemy_of", "grandmaster_lv", "casimir4")],
    [flag("casimir4", "malbork_pl"), nflag("casimir4", "defeated")],
    [("unpaid_wages_pl", ["grandmaster_lv", "czerwonka"]), ("buy_malbork_pl", ["casimir4", "czerwonka"])],
    "fact"))
TEXTS.update(texts("malbork_1457",
    "Мальборк за деньги",
    "Орден не может заплатить наёмникам — и король покупает у них неприступную столицу ордена",
    "Мальборк не взять штурмом. Но у самой крепкой крепости есть слабое место — гарнизону надо платить. Покупают только то, что уже стало чужим.",
    "1457 год, третий год Тринадцатилетней войны. Прусские города восстали против Тевтонского ордена и позвали польского короля Казимира Ягеллончика. Мальборк, крупнейший кирпичный замок Европы, король взять не может. Но защищают его не рыцари, а наёмники-чехи — и им давно не платят.",
    "Орден задолжал наёмникам огромное жалованье и отдал им в залог свои замки. 6 июня 1457 года чешский капитан Ульрих Червонка передал Мальборк польскому королю за 190 тысяч венгерских флоринов; магистр Людвиг фон Эрлихсхаузен уехал в Кёнигсберг, который с тех пор стал столицей ордена. Горожане Мальборка во главе с бургомистром Бартоломеем Блюме ещё три года держали город за орден — Блюме потом казнили. Война закончилась Вторым Торуньским миром 1466 года: Гданьское Поморье и Вармия перешли к Короне.",
    "Ян Длугош, «Анналы», XII; М. Бискуп, «Тринадцатилетняя война с Тевтонским орденом» (1967)"))

# ================================================================ copernicus_olsztyn
NEW_SCENES += [
    scene("olsztyn_walls_pl", "Стены Ольштына", ["sig_olsztyn_walls_pl"], 2, "🏰", "оборонять замок", "icon_ally",
          ["комендант", "враг"], "camp_walls_m"),
    scene("revolutions_pl", "«О вращениях небесных сфер»", ["sig_revolutions_pl"], 1, "🔭", "издать книгу", "icon_crown",
          ["астроном"], "anekdota_desk"),
    scene("leave_frombork_pl", "Уехать во Фромборк", ["v_flee"], 1, "🚪", "уход", "icon_ally",
          ["кто уходит"], "leave_city"),
]
NEW_RULES += [
    rule("olsztyn_walls_pl_sig", "Каноник-администратор готовит замок к осаде, пишет королю за подмогой — и орден отступает",
         "sig_olsztyn_walls_pl",
         [actor("A", 0, tags=["canon_pl"], notFlags=["away"]),
          actor("B", 1, tags=["order_pl"])],
         [setf("A", "defended_pl"), setf("B", "repelled_pl"), remf("B", "strong")]),
    rule("revolutions_pl_sig", "Когда войны позади, каноник дописывает книгу о том, что Земля вращается вокруг Солнца",
         "sig_revolutions_pl",
         [actor("A", 0, tags=["canon_pl"], flags=["defended_pl"])],
         [setf("A", "heliocentric_pl")]),
]
NEW_LEVELS.append(level(
    "copernicus_olsztyn", 180, ACT3, "poland_ceremony", "revolutions_pl", 2,
    ["olsztyn_walls_pl", "revolutions_pl", "leave_frombork_pl"],
    ["copernicus", "komtur"],
    {"copernicus": ["standing"], "komtur": ["standing", "strong"]},
    [("enemy_of", "komtur", "copernicus"), ("enemy_of", "copernicus", "komtur")],
    [flag("copernicus", "heliocentric_pl"), flag("komtur", "repelled_pl")],
    [("olsztyn_walls_pl", ["copernicus", "komtur"]), ("revolutions_pl", ["copernicus"])],
    "simplification"))
TEXTS.update(texts("copernicus_olsztyn",
    "Коперник держит Ольштын",
    "Астроном-каноник отстаивает замок от рыцарей ордена — а потом сдвигает Землю с центра мира",
    "Сначала стены, потом небо. Уехать от войны можно, но тогда замок падёт.",
    "1520 год, война Польши с Тевтонским орденом. Вармийский каноник Николай Коперник, выпускник Краковской академии, служит администратором владений капитула и живёт в замке Ольштын. Отряды ордена жгут округу и подходят к стенам.",
    "Зимой 1520–1521 годов Коперник руководил обороной Ольштына: укреплял стены, собирал гарнизон и писал королю Сигизмунду, прося подкреплений; орден замок так и не взял. На стене ольштынской галереи до сих пор видна нарисованная им таблица для наблюдения за Солнцем. Книга «О вращениях небесных сфер», где Земля вращается вокруг Солнца, вышла в Нюрнберге в 1543 году; по преданию, Коперник получил первый экземпляр в день своей смерти, 24 мая. Учился он в Кракове в 1491–1495 годах — краковский студент, «жак».",
    "Письма Коперника королю Сигизмунду I (1521); Г. Ретик, «Первое повествование»"))

# ================================================================ prussian_homage (1525)
NEW_SCENES += [
    scene("white_mantle_pl", "Снять белый плащ", ["sig_white_mantle_pl"], 1, "✠", "распустить орден", "icon_plot",
          ["магистр"], "abjuration"),
    scene("homage_square_pl", "Присяга на Рыночной площади", ["sig_homage_square_pl"], 2, "👑", "принести присягу", "icon_crown",
          ["король", "вассал"], "coronation_b"),
    scene("finish_order_pl", "Добить орден", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "battlefield"),
]
NEW_RULES += [
    rule("white_mantle_pl_sig", "Последний магистр по совету Лютера распускает орден и становится светским князем",
         "sig_white_mantle_pl",
         [actor("A", 0, tags=["albrecht_pl"])],
         [setf("A", "secular_pl")]),
    rule("homage_square_pl_sig", "На коленях перед королём на краковской площади бывший магистр получает Пруссию в лен",
         "sig_homage_square_pl",
         [actor("A", 0, tags=["old_king_pl"], notFlags=["defeated"]),
          actor("B", 1, tags=["albrecht_pl"], flags=["secular_pl"])],
         [setf("B", "vassal_pl"), setf("A", "suzerain_pl"), addr("ally_of", "A", "B"), addr("ally_of", "B", "A")]),
]
NEW_LEVELS.append(level(
    "prussian_homage", 190, ACT3, "poland_ceremony", "homage_square_pl", 2,
    ["white_mantle_pl", "homage_square_pl", "finish_order_pl"],
    ["sigismund1", "albrecht_hz"],
    {"sigismund1": ["crowned", "reigns", "standing"], "albrecht_hz": ["standing", "strong"]},
    [("enemy_of", "sigismund1", "albrecht_hz"), ("enemy_of", "albrecht_hz", "sigismund1")],
    [flag("albrecht_hz", "vassal_pl"), nflag("sigismund1", "defeated")],
    [("white_mantle_pl", ["albrecht_hz"]), ("homage_square_pl", ["sigismund1", "albrecht_hz"])],
    "fact"))
TEXTS.update(texts("prussian_homage",
    "Прусская присяга",
    "Последний магистр Тевтонского ордена распускает орден и на краковской площади присягает польскому королю как вассал",
    "Магистр монашеского ордена не может стать ничьим вассалом — сначала ему придётся перестать быть магистром. А добивать его в поле — значит воевать ещё годы.",
    "1525 год. Последняя война с орденом закончилась перемирием. Магистр Альбрехт Гогенцоллерн — племянник польского короля Сигизмунда Старого — съездил к Лютеру, и тот посоветовал ему жениться и превратить орден в светское княжество.",
    "10 апреля 1525 года на Главном рынке Кракова Альбрехт преклонил колени перед Сигизмундом Старым и получил Пруссию в лен как наследственное герцогство. Так появилось первое в Европе протестантское государство — и бывший Тевтонский орден стал польским вассалом. Ирония истории: в 1657 году потомки Альбрехта вышли из вассальной зависимости, а ещё через век Пруссия участвовала в разделах Польши. «Прусскую присягу» Ян Матейко написал в 1882 году, когда Польши на карте не было.",
    "Краковский трактат 1525 г.; «Акты Томициана» (Acta Tomiciana)"))

# ================================================================ barbara_secret (1547–1551)
NEW_SCENES += [
    scene("vilnius_vows_pl", "Тайное венчание в Вильне", ["sig_vilnius_vows_pl"], 2, "💍", "тайно обвенчаться", "icon_ally",
          ["король", "невеста"], "st_james_wed"),
    scene("sejm_divorce_pl", "Сейм требует развода", ["sig_sejm_divorce_pl"], 2, "📜", "требовать развода", "icon_plot",
          ["королева-мать", "король"], "court_denounce"),
    scene("barbara_crown_pl", "Коронация Барбары", ["sig_barbara_crown_pl"], 2, "👑", "короновать жену", "icon_crown",
          ["король", "жена"], "coronation_b"),
    scene("yield_mother_pl", "Уступить матери", ["v_parley"], 2, "🤝", "переговоры", "icon_ally",
          ["кто требует", "кто уступает"], "court_refuse"),
]
NEW_RULES += [
    rule("vilnius_vows_pl_sig", "Молодой король тайно венчается со вдовой литовского магната",
         "sig_vilnius_vows_pl",
         [actor("A", 0, tags=["august_pl"]),
          actor("B", 1, tags=["barbara_pl"])],
         [addr("wed", "A", "B"), addr("wed", "B", "A"), setf("A", "secretly_wed_pl")]),
    rule("sejm_divorce_pl_sig", "Королева-мать и сейм требуют расторгнуть брак — шляхтянка не пара королю",
         "sig_sejm_divorce_pl",
         [actor("A", 0, tags=["bona_pl"]),
          actor("B", 1, tags=["august_pl"], flags=["secretly_wed_pl"])],
         [setf("B", "pressed_pl")]),
    rule("barbara_crown_pl_sig", "Король отвечает: «лучше потерять корону» — и коронует жену вопреки всем",
         "sig_barbara_crown_pl",
         [actor("A", 0, tags=["august_pl"], flags=["pressed_pl"], notFlags=["conceded"]),
          actor("B", 1, tags=["barbara_pl"])],
         [setf("B", "crowned_queen_pl"), setf("B", "crowned")]),
]
NEW_LEVELS.append(level(
    "barbara_secret", 200, ACT3, "poland_romance", "barbara_crown_pl", 3,
    ["vilnius_vows_pl", "sejm_divorce_pl", "barbara_crown_pl", "yield_mother_pl"],
    ["sigismund2", "barbara", "bona"],
    {"sigismund2": ["crowned", "reigns", "standing"], "bona": ["crowned", "standing"]},
    [],
    [flag("barbara", "crowned_queen_pl")],
    [("vilnius_vows_pl", ["sigismund2", "barbara"]), ("sejm_divorce_pl", ["bona", "sigismund2"]),
     ("barbara_crown_pl", ["sigismund2", "barbara"])],
    "simplification"))
TEXTS.update(texts("barbara_secret",
    "Тайный брак короля",
    "Король тайно женится на литовской вдове, выдерживает гнев матери и сейма — и коронует её",
    "Сначала свадьба — тайная. Потом буря: мать и сейм требуют развода. Уступит король — короны у Барбары не будет.",
    "1547 год. Молодой Сигизмунд Август, наследник трона, влюблён в Барбару Радзивилл — вдову литовского магната, красавицу, о которой ходят сплетни. Его мать, королева Бона, ненавидит Радзивиллов. Шляхта считает брак мезальянсом.",
    "Сигизмунд Август тайно обвенчался с Барбарой в Вильне летом 1547 года. Когда в 1548-м он стал королём, королева Бона и сейм потребовали развода; король ответил, что скорее откажется от короны. 7 декабря 1550 года Барбару короновали в Кракове, а 8 мая 1551-го она умерла — молва обвинила в отравлении Бону, хотя доказательств нет. Король шёл за гробом пешком до самой Вильни. По легенде, позже маг пан Твардовский вызвал для него дух Барбары в волшебном зеркале.",
    "Письма Сигизмунда Августа; Лукаш Гурницкий, «Дзеи в короне польской»"))

# ================================================================ bona_sums (1556–1557)
NEW_SCENES += [
    scene("leave_bari_pl", "Отъезд в Бари", ["sig_leave_bari_pl"], 1, "🧳", "уехать с казной", "icon_ally",
          ["королева"], "exile_road"),
    scene("loan_philip_pl", "Заём испанскому королю", ["sig_loan_philip_pl"], 2, "💰", "дать в долг", "icon_ally",
          ["королева", "король"], "bank_loan"),
    scene("forged_will_pl", "Подложное завещание", ["sig_forged_will_pl"], 2, "🧪", "отравить", "icon_dead",
          ["придворный", "королева"], "doctor_letter"),
    scene("buy_courtier_pl", "Подкупить придворного", ["v_bribe"], 2, "💰", "подкуп", "icon_ally",
          ["кто платит", "кто берёт"], "court_purse"),
]
NEW_RULES += [
    rule("leave_bari_pl_sig", "Старая королева уезжает на родину, в Бари, увозя на двадцати четырёх возах свою казну",
         "sig_leave_bari_pl",
         [actor("A", 0, tags=["bona_pl"], notFlags=["away"])],
         [setf("A", "away"), setf("A", "treasure_pl")]),
    rule("loan_philip_pl_sig", "Королева даёт испанскому королю в долг 430 тысяч дукатов",
         "sig_loan_philip_pl",
         [actor("A", 0, tags=["bona_pl"], flags=["treasure_pl"]),
          actor("B", 1, tags=["spain_pl"])],
         [setf("A", "lender_pl"), setf("B", "debtor_pl")]),
    rule("forged_will_pl_sig", "Доверенный придворный травит королеву и предъявляет завещание в пользу Филиппа",
         "sig_forged_will_pl",
         [actor("A", 0, tags=["courtier_pl"], notFlags=["bought"]),
          actor("B", 1, tags=["bona_pl"], flags=["lender_pl"])],
         [setf("B", "dead"), setf("A", "forger_pl")]),
]
NEW_LEVELS.append(level(
    "bona_sums", 210, ACT3, "poland_tension", "forged_will_pl", 3,
    ["leave_bari_pl", "loan_philip_pl", "forged_will_pl", "buy_courtier_pl"],
    ["bona", "philip2_es", "pappacoda"],
    {"bona": ["crowned", "standing"], "philip2_es": ["crowned", "reigns", "standing"]},
    [],
    [flag("philip2_es", "debtor_pl"), flag("bona", "dead")],
    [("leave_bari_pl", ["bona"]), ("loan_philip_pl", ["bona", "philip2_es"]), ("forged_will_pl", ["pappacoda", "bona"])],
    "simplification"))
TEXTS.update(texts("bona_sums",
    "Неаполитанские суммы",
    "Королева уезжает с казной в Италию, даёт в долг испанскому королю — и её травят, а долг Польше так и не возвращают",
    "Деньги можно дать в долг, только если они при тебе. Придворный, которого купила сама королева, её не отравит, — но так не было.",
    "1556 год. Вдовствующая королева Бона Сфорца, итальянка, сорок лет правившая при дворе мужа, — в ссоре с сыном. Она решает вернуться в своё герцогство Бари. С собой — огромная казна. Испанский король Филипп II, владеющий Неаполем, нуждается в деньгах.",
    "В феврале 1556 года Бона уехала в Бари, увезя, по рассказам, казну на двадцати четырёх возах. Филиппу II она одолжила 430 тысяч дукатов. В ноябре 1557 года её отравил доверенный придворный Джан Лоренцо Паппакода — подкупленный, как считали современники, испанцами — и предъявил завещание в пользу Филиппа. Польша двести лет требовала вернуть «неаполитанские суммы» и не получила ничего. От Боны остались итальянские овощи: суповой набор из моркови, петрушки и сельдерея поляки до сих пор зовут «włoszczyzna» — «итальянщина».",
    "В. Поцеха, «Королева Бона» (1949–1958); Лукаш Гурницкий, «Дзеи в короне польской»"))

# ================================================================ lublin_union (1569)
NEW_SCENES += [
    scene("magnates_leave_pl", "Литовские паны покидают сейм", ["sig_magnates_leave_pl"], 2, "🚪", "уехать с сейма", "icon_plot",
          ["магнат", "король"], "leave_city"),
    scene("incorporation_pl", "Земли — Короне", ["sig_incorporation_pl"], 2, "🗺️", "передать земли", "icon_crown",
          ["король", "шляхтич"], "council_b"),
    scene("union_act_pl", "Акт Люблинской унии", ["sig_union_act_pl"], 2, "📜", "подписать унию", "icon_crown",
          ["король", "магнат"], "anonymous_diploma"),
    scene("persuade_pl", "Уговорить панов", ["v_parley"], 2, "🤝", "переговоры", "icon_ally",
          ["кто требует", "кто уступает"], "council"),
]
NEW_RULES += [
    rule("magnates_leave_pl_sig", "Литовские магнаты, не желая растворяться в Короне, ночью уезжают с сейма",
         "sig_magnates_leave_pl",
         [actor("A", 0, tags=["lith_magnate_pl"], notFlags=["conceded"]),
          actor("B", 1, tags=["august_pl"])],
         [setf("A", "left_sejm_pl")]),
    rule("incorporation_pl_sig", "Король переводит в Корону Подляшье, Волынь и Киевщину — и шляхта этих земель присягает Короне",
         "sig_incorporation_pl",
         [actor("A", 0, tags=["august_pl"]),
          actor("B", 1, tags=["volhynia_pl"])],
         [setf("B", "crown_land_pl"), setf("A", "pressure_pl")]),
    rule("union_act_pl_sig", "Ослабленные паны возвращаются: общий король, сейм и монета — Речь Посполитая Обоих Народов",
         "sig_union_act_pl",
         [actor("A", 0, tags=["august_pl"], flags=["pressure_pl"]),
          actor("B", 1, tags=["lith_magnate_pl"], flags=["left_sejm_pl"])],
         [setf("A", "union_pl"), setf("B", "union_pl"), addr("ally_of", "A", "B"), addr("ally_of", "B", "A")]),
]
NEW_LEVELS.append(level(
    "lublin_union", 220, ACT3, "poland_ceremony", "union_act_pl", 3,
    ["magnates_leave_pl", "incorporation_pl", "union_act_pl", "persuade_pl"],
    ["sigismund2", "radziwill_rudy", "volhynian_noble"],
    {"sigismund2": ["crowned", "reigns", "standing"], "radziwill_rudy": ["standing"]},
    [],
    [flag("radziwill_rudy", "union_pl"), flag("volhynian_noble", "crown_land_pl")],
    [("magnates_leave_pl", ["radziwill_rudy", "sigismund2"]), ("incorporation_pl", ["sigismund2", "volhynian_noble"]),
     ("union_act_pl", ["sigismund2", "radziwill_rudy"])],
    "fact"))
TEXTS.update(texts("lublin_union",
    "Люблинская уния",
    "Литовские паны уезжают с сейма, король передаёт часть земель Короне — и две страны становятся одной Речью Посполитой",
    "Уговорами панов не убедить — они уедут всё равно. Давит на них не король, а потеря земель. Подписывают унию те, кто уезжал.",
    "1569 год, сейм в Люблине. У последнего Ягеллона, Сигизмунда Августа, нет детей, и личная уния Польши и Великого княжества Литовского может кончиться с его смертью. Польская шляхта хочет единого государства, литовские магнаты — сохранить своё. Великое княжество воюет с Москвой и нуждается в помощи.",
    "1 марта 1569 года литовские магнаты во главе с Николаем Радзивиллом Рыжим тайно покинули Люблин. Король ответил тем, что перевёл в состав Короны Подляшье, Волынь, а затем Брацлавщину и Киевщину, и местная шляхта присягнула Короне. Литовцы вернулись, и 1 июля 1569 года была подписана уния: общий король, общий сейм и монета, но отдельные войско, казна, должности и законы Великого княжества. Так возникла Речь Посполитая Обоих Народов, просуществовавшая до разделов 1795 года.",
    "Акт Люблинской унии (1569); дневник Люблинского сейма"))

if __name__ == "__main__":
    P.NEW_CHARS, P.NEW_SCENES, P.NEW_RULES, P.NEW_LEVELS, P.TEXTS = NEW_CHARS, NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS
    P.CHAPTER_TEXTS = {"act.poland.3": ACT3}
    P.main()
