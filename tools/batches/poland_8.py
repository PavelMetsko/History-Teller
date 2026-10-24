#!/usr/bin/env python3
"""Пачка 8 главы «Польша»: закрываем хронологию от Пшемысла II до Акта 5 ноября, 19 уровней.

    python3 tools/batches/poland_8.py [repo_root]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, level, texts, ACT2
from poland_7 import bait, ACT3, ACT4, ACT5, ACT6

NEW_CHARS = [
    char("przemysl2", "Пшемысл II", ["przemysl_pl"], "👑"),
    char("brandenburg_knight", "Бранденбургский рыцарь", ["brand_pl"], "⚔️"),
    char("wit_stwosz", "Вит Ствош", ["carver_pl"], "🪵"),
    char("berrecci", "Бартоломео Берреччи", ["architect_pl"], "🏛️"),
    char("khmelnytsky", "Богдан Хмельницкий", ["khmel_pl"], "🐎"),
    char("czaplinski", "Подстароста Чаплинский", ["starosta_pl"], "🗡️"),
    char("potocki_hetman", "Гетман Николай Потоцкий", ["crown_hetman_pl"], "🪽"),
    char("islam_giray", "Хан Ислам Герай", ["khan_pl"], "🏹"),
    char("august2", "Август II Сильный", ["saxon2_pl"], "💪"),
    char("conti", "Принц де Конти", ["conti_pl"], "⛵"),
    char("pulaski", "Казимир Пулаский", ["pulaski_pl"], "⚔️"),
    char("soltyk", "Епископ Каетан Солтык", ["bishop_k_pl"], "⛪"),
    char("potocki_sz", "Щенсны Потоцкий", ["targowica_pl"], "📜"),
    char("sievers", "Посол Сиверс", ["ambassador_s_pl"], "🎩"),
    char("archduke_ferdinand", "Эрцгерцог Фердинанд д’Эсте", ["austrian_pl"], "⚔️"),
    char("alexander1_pl", "Император Александр I", ["tsar_a1_pl"], "👑"),
    char("czartoryski", "Князь Адам Чарторыйский", ["czartoryski_pl"], "📜"),
    char("dembowski", "Эдвард Дембовский", ["dembowski_pl"], "✝️"),
    char("szela", "Якуб Шеля", ["szela_pl"], "🌾"),
    char("mieroslawski", "Людвик Мерославский", ["mieroslawski_pl"], "⚔️"),
    char("gymnasist_pl", "Гимназист", ["gymnasist_pl"], "🎒"),
    char("strzelec_pl", "Стрелец Первой кадровой", ["strzelec_pl"], "🎖️"),
]
NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS = [], [], [], {}
BATTLE = ["нападающий", "защитник"]
PARLEY = ["кто требует", "кто уступает"]

# ================================================================ przemysl_1295
NEW_SCENES += [
    scene("mestwin_will_pl", "Завещание Мстивоя", ["sig_mestwin_will_pl"], 1, "📜", "унаследовать Поморье", "icon_crown",
          ["князь"], "deathbed"),
    scene("coronation_1295_pl", "Коронация в Гнезно", ["sig_coronation_1295_pl"], 2, "👑", "короновать", "icon_crown",
          ["архиепископ", "князь"], "cathedral_altar"),
    scene("rogozno_pl", "Масленица в Рогозьно", ["sig_rogozno_pl"], 2, "🗡️", "напасть на рассвете", "icon_dead",
          ["нападающий", "жертва"], "night_flight"),
    bait("brand_talks_pl", "Мир с Бранденбургом", "v_parley", 2, "court_whisper", PARLEY),
]
NEW_RULES += [
    rule("mestwin_will_pl_sig", "Умирающий князь Гданьского Поморья завещает свои земли Пшемыслу — Польша снова выходит к морю",
         "sig_mestwin_will_pl",
         [actor("A", 0, tags=["przemysl_pl"])],
         [setf("A", "pomerania_pl")]),
    rule("coronation_1295_pl_sig", "Архиепископ Якуб Свинка возлагает корону — впервые за двести с лишним лет у Польши король",
         "sig_coronation_1295_pl",
         [actor("A", 0, tags=["archbishop_pl"]), actor("B", 1, tags=["przemysl_pl"], flags=["pomerania_pl"])],
         [setf("B", "crowned_1295_pl"), setf("B", "crowned"), setf("B", "reigns")]),
    rule("rogozno_crowned_pl_sig", "Люди бранденбургских маркграфов нападают на короля — короны Польше они не простят",
         "sig_rogozno_pl",
         [actor("A", 0, tags=["brand_pl"]), actor("B", 1, tags=["przemysl_pl"], flags=["crowned_1295_pl"])],
         [setf("B", "dead")]),
    rule("rogozno_prince_pl_sig", "Нападение на князя без короны — его просто уводят в плен ради выкупа",
         "sig_rogozno_pl",
         [actor("A", 0, tags=["brand_pl"]), actor("B", 1, tags=["przemysl_pl"], notFlags=["crowned_1295_pl"])],
         [setf("B", "captive_pl")]),
]
NEW_LEVELS.append(level(
    "przemysl_1295", 107, ACT2, "poland_tension", "coronation_1295_pl", 3,
    ["mestwin_will_pl", "coronation_1295_pl", "rogozno_pl", "brand_talks_pl"],
    ["przemysl2", "archbishop_gn", "brandenburg_knight"],
    {"przemysl2": ["standing"], "brandenburg_knight": ["standing", "strong"]}, [],
    [flag("przemysl2", "crowned_1295_pl"), flag("przemysl2", "dead"), nflag("przemysl2", "captive_pl")],
    [("mestwin_will_pl", ["przemysl2"]), ("coronation_1295_pl", ["archbishop_gn", "przemysl2"]),
     ("rogozno_pl", ["brandenburg_knight", "przemysl2"])],
    "fact"))
TEXTS.update(texts("przemysl_1295",
    "Король на семь месяцев",
    "Пшемысл II объединяет Великую Польшу с Поморьем и коронуется — а через семь месяцев его убивают",
    "Корону дают тому, у кого есть земли: сначала наследство. Убить хотят именно короля — князя без короны просто держали бы ради выкупа.",
    "1294 год. Польша уже полтора века раздроблена между князьями. Князь Великой Польши Пшемысл II мечтает о большем — и ему везёт: бездетный князь Гданьского Поморья Мстивой обещает ему свои земли у моря. Соседи-маркграфы Бранденбурга смотрят на это с ненавистью.",
    "Мстивой II умер в декабре 1294 года, и Пшемысл получил Гданьское Поморье. 26 июня 1295 года в Гнезно архиепископ Якуб Свинка короновал его — это была первая королевская коронация в Польше с 1076 года. Пшемысл взял на печать белого орла в короне — с тех пор это герб Польши. Королём он пробыл семь месяцев: 8 февраля 1296 года, в последние дни масленицы, в Рогозьно на него напали и убили. Убийц, по общему мнению хронистов, наняли бранденбургские маркграфы.",
    "«Великопольская хроника»; Ян Длугош, «Анналы», под 1295–1296"))

# ================================================================ gdansk_1308
NEW_SCENES += [
    scene("brand_siege_pl", "Бранденбуржцы у Гданьска", ["sig_brand_siege_pl"], 2, "🏰", "осадить город", "icon_dead",
          ["осаждающий", "горожанин"], "breach_wall"),
    scene("call_knights_pl", "Позвать крестоносцев на помощь", ["sig_call_knights_pl"], 2, "✉️", "просить помощи", "icon_ally",
          ["князь", "комтур"], "court_present"),
    scene("gdansk_night_pl", "Ночь 13 ноября", ["sig_gdansk_night_pl"], 3, "🗡️", "войти в город", "icon_dead",
          ["комтур", "осаждающий", "горожанин"], "dawn_storm_pl"),
    bait("pay_order_pl", "Заплатить ордену", "v_bribe", 2, "merchant_deal_pl", ["кто платит", "кого покупают"]),
]
NEW_RULES += [
    rule("brand_siege_pl_sig", "Маркграфы Бранденбурга осаждают Гданьск — горожане открывают им ворота, замок держится",
         "sig_brand_siege_pl",
         [actor("A", 0, tags=["brand_pl"]), actor("B", 1, tags=["merchant_pl"])],
         [setf("B", "besieged_pl")]),
    rule("call_knights_pl_sig", "Князь, у которого нет сил, зовёт на помощь Тевтонский орден — за плату",
         "sig_call_knights_pl",
         [actor("A", 0, tags=["lokietek_pl"]), actor("B", 1, tags=["order_pl"])],
         [setf("B", "called_pl")]),
    rule("gdansk_night_pl_sig", "Рыцари выгоняют бранденбуржцев, а потом вырезают город и оставляют Гданьск себе",
         "sig_gdansk_night_pl",
         [actor("A", 0, tags=["order_pl"], flags=["called_pl"]), actor("B", 1, tags=["brand_pl"]),
          actor("C", 2, tags=["merchant_pl"], flags=["besieged_pl"])],
         [setf("B", "away"), setf("C", "dead"), setf("A", "holds_gdansk_pl")]),
]
NEW_LEVELS.append(level(
    "gdansk_1308", 112, ACT2, "poland_tension", "gdansk_night_pl", 3,
    ["brand_siege_pl", "call_knights_pl", "gdansk_night_pl", "pay_order_pl"],
    ["lokietek", "komtur", "brandenburg_knight", "merchant_pl"],
    {"lokietek": ["standing", "reigns"], "komtur": ["standing", "strong"], "brandenburg_knight": ["standing", "strong"]}, [],
    [flag("komtur", "holds_gdansk_pl"), flag("brandenburg_knight", "away")],
    [("brand_siege_pl", ["brandenburg_knight", "merchant_pl"]), ("call_knights_pl", ["lokietek", "komtur"]),
     ("gdansk_night_pl", ["komtur", "brandenburg_knight", "merchant_pl"])],
    "fact"))
TEXTS.update(texts("gdansk_1308",
    "Гданьская резня",
    "Локетек зовёт крестоносцев спасти Гданьск от Бранденбурга — и теряет Поморье на полтора века",
    "Помощь позвали, когда стало нечем защищаться. Орден приходит не к князю — к городу, который уже в беде.",
    "1308 год. Владислав Локетек едва собрал Польшу и ещё не король. На Гданьск идут бранденбургские маркграфы, город открывает им ворота, держится только замок. Своих войск у Локетка нет, и его наместник делает роковой шаг — просит помощи у соседей, рыцарей Тевтонского ордена.",
    "Крестоносцы пришли, выбили бранденбуржцев, а затем в ночь на 14 ноября 1308 года вошли в город и устроили резню; число жертв спорно, но папа потом разбирал жалобу на «десять тысяч убитых». Локетку выставили счёт за помощь, которого он не мог оплатить, и орден оставил Гданьск и всё Поморье себе. Польша вернула их только по Торуньскому миру 1466 года — через 158 лет. Отсюда и Пловцы, и Грюнвальд.",
    "Процесс польского короля с орденом, 1320–1321 и 1339 гг.; Ян Длугош, «Анналы», под 1308"))

# ================================================================ koszyce_1374
NEW_SCENES += [
    scene("koszyce_pl", "Кошице", ["sig_koszyce_pl"], 2, "📜", "даровать привилей", "icon_crown",
          ["король", "шляхтич"], "council_b"),
    scene("daughter_heir_pl", "Наследница", ["sig_daughter_heir_pl"], 2, "👸", "назначить наследницей", "icon_crown",
          ["король", "дочь"], "throne"),
    scene("raise_tax_pl", "Новый налог", ["sig_raise_tax_pl"], 2, "💰", "поднять налог", "icon_plot",
          ["король", "шляхтич"], "empty_treasury"),
    bait("magnates_deal_pl", "Сговор с вельможами", "v_parley", 2, "secret_council_pl", PARLEY),
]
NEW_RULES += [
    rule("raise_tax_pl_sig", "Король требует денег — шляхта отказывается признавать его дочерей",
         "sig_raise_tax_pl",
         [actor("A", 0, tags=["guest_king_pl"]), actor("B", 1, tags=["szlachcic_pl"])],
         [setf("B", "rebels_pl")]),
    rule("koszyce_pl_sig", "Король освобождает шляхту почти от всех налогов — в обмен на трон для дочери",
         "sig_koszyce_pl",
         [actor("A", 0, tags=["guest_king_pl"]), actor("B", 1, tags=["szlachcic_pl"], notFlags=["rebels_pl"])],
         [setf("B", "privileged_pl"), setf("A", "succession_pl")]),
    rule("daughter_heir_pl_sig", "Шляхта признаёт дочь короля будущей правительницей Польши",
         "sig_daughter_heir_pl",
         [actor("A", 0, tags=["guest_king_pl"], flags=["succession_pl"]), actor("B", 1, tags=["jadwiga_pl"])],
         [setf("B", "heir_pl")]),
]
NEW_LEVELS.append(level(
    "koszyce_1374", 135, ACT2, "poland_ceremony", "koszyce_pl", 2,
    ["koszyce_pl", "daughter_heir_pl", "raise_tax_pl", "magnates_deal_pl"],
    ["louis_hu", "szlachcic_pl", "jadwiga", "magnate_pl"],
    {"louis_hu": ["standing", "reigns", "crowned"]}, [],
    [flag("jadwiga", "heir_pl"), flag("szlachcic_pl", "privileged_pl")],
    [("koszyce_pl", ["louis_hu", "szlachcic_pl"]), ("daughter_heir_pl", ["louis_hu", "jadwiga"])],
    "fact"))
TEXTS.update(texts("koszyce_1374",
    "Кошицкий привилей",
    "У короля только дочери — и он покупает для них польский трон, освободив шляхту от налогов",
    "Требовать с шляхты — значит её потерять. Корону для дочери не завоюешь, её покупают.",
    "1374 год. Казимир Великий, последний Пяст на троне, умер, и Польшей правит его племянник — венгерский король Людовик. Сыновей у него нет, только дочери, а польский обычай не знает королев. Чтобы трон достался одной из них, нужна воля шляхты.",
    "17 сентября 1374 года в Кошице Людовик выдал привилей: шляхта освобождалась от всех податей, кроме двух грошей с лана земли, а король обещал не назначать чужеземцев на должности. Взамен шляхта признала право его дочери на трон. Это был первый общий шляхетский привилей — и пример на века: каждый следующий король покупал власть новыми вольностями. А дочерью оказалась Ядвига: в 1384 году её короновали — не королевой, а «королём» Польши.",
    "Кошицкий привилей, 17 сентября 1374"))

# ================================================================ stwosz_1489
NEW_SCENES += [
    scene("commission_altar_pl", "Заказ мещан", ["sig_commission_altar_pl"], 2, "💰", "заказать алтарь", "icon_ally",
          ["мещанин", "мастер"], "guildhall_speech"),
    scene("carve_linden_pl", "Двенадцать лет резьбы", ["sig_carve_linden_pl"], 1, "🪵", "резать липу", "icon_ally",
          ["мастер"], "theatre_timbers"),
    scene("altar_consecration_pl", "Освящение алтаря", ["sig_altar_consecration_pl"], 2, "⛪", "освятить алтарь", "icon_crown",
          ["мастер", "король"], "cathedral_altar"),
    scene("nuremberg_bill_pl", "Нюрнбергский вексель", ["sig_nuremberg_bill_pl"], 2, "✒️", "подделать подпись", "icon_plot",
          ["мастер", "купец"], "bank_loan"),
]
NEW_RULES += [
    rule("commission_altar_pl_sig", "Краковские мещане собирают деньги и заказывают мастеру алтарь для Мариацкого костёла",
         "sig_commission_altar_pl",
         [actor("A", 0, tags=["merchant_pl"]), actor("B", 1, tags=["carver_pl"])],
         [setf("B", "commissioned_pl")]),
    rule("carve_linden_pl_sig", "Мастер двенадцать лет режет из липы двести фигур — апостолы ростом почти в три метра",
         "sig_carve_linden_pl",
         [actor("A", 0, tags=["carver_pl"], flags=["commissioned_pl"], notFlags=["branded_pl"])],
         [setf("A", "carved_pl")]),
    rule("altar_consecration_pl_sig", "Алтарь открыт — и Краков видит величайшее готическое резное чудо Европы",
         "sig_altar_consecration_pl",
         [actor("A", 0, tags=["carver_pl"], flags=["carved_pl"]), actor("B", 1, tags=["jag_king_pl"])],
         [setf("A", "altar_done_pl")]),
    rule("nuremberg_bill_pl_sig", "Мастер подделывает подпись на векселе — и палач клеймит его в обе щеки",
         "sig_nuremberg_bill_pl",
         [actor("A", 0, tags=["carver_pl"]), actor("B", 1, tags=["merchant_pl"])],
         [setf("A", "branded_pl")]),
]
NEW_LEVELS.append(level(
    "stwosz_1489", 172, ACT3, "poland_ceremony", "altar_consecration_pl", 3,
    ["commission_altar_pl", "carve_linden_pl", "altar_consecration_pl", "nuremberg_bill_pl"],
    ["wit_stwosz", "merchant_pl", "casimir4"],
    {"casimir4": ["standing", "reigns", "crowned"]}, [],
    [flag("wit_stwosz", "altar_done_pl"), nflag("wit_stwosz", "branded_pl")],
    [("commission_altar_pl", ["merchant_pl", "wit_stwosz"]), ("carve_linden_pl", ["wit_stwosz"]),
     ("altar_consecration_pl", ["wit_stwosz", "casimir4"])],
    "fact"))
TEXTS.update(texts("stwosz_1489",
    "Алтарь Вита Ствоша",
    "Нюрнбергский резчик двенадцать лет режет в Кракове алтарь — величайший готический алтарь Европы",
    "Шедевр начинается с заказчика и с терпения. Деньги и подписи — опасная тема для мастера.",
    "1477 год. Краков богат: через него идут пути от Балтики к Венгрии и от Германии к Руси. Мещане хотят, чтобы их Мариацкий костёл на Рынке затмил всех. Они зовут из Нюрнберга резчика Файта Штосса — в Польше его будут звать Вит Ствош.",
    "Алтарь освятили в 1489 году. Он высотой около 13 метров, фигуры апостолов — до 2,7 метра, вырезаны из цельных стволов липы, и всего на нём около двухсот фигур. Говорят, лица святых Ствош резал с краковских мещан. Вернувшись в Нюрнберг богачом, он в 1503 году подделал подпись на векселе — и его заклеймили раскалённым железом в обе щеки. Во Вторую мировую нацисты вывезли алтарь в Нюрнберг, но после войны его нашли и вернули в Краков. Каждый день его створки торжественно открывают.",
    "Договор краковских мещан с Файтом Штоссом (1477); акты нюрнбергского суда (1503)"))

# ================================================================ wawel_1520
NEW_SCENES += [
    scene("bona_italians_pl", "Итальянцы при дворе", ["sig_bona_italians_pl"], 2, "🎨", "позвать мастеров", "icon_ally",
          ["королева", "зодчий"], "buildings_praise"),
    scene("sigismund_chapel_pl", "Сигизмундова капелла", ["sig_sigismund_chapel_pl"], 2, "⛪", "строить капеллу", "icon_crown",
          ["король", "зодчий"], "palace_chapel"),
    scene("bell_1520_pl", "Колокол «Зыгмунт»", ["sig_bell_1520_pl"], 1, "🔔", "отлить колокол", "icon_crown",
          ["король"], "bells_cannons"),
    scene("rival_quarrel_pl", "Ссора с соперником", ["sig_rival_quarrel_pl"], 2, "🗡️", "затеять ссору", "icon_dead",
          ["зодчий", "соперник"], "inn_rome_pl"),
]
NEW_RULES += [
    rule("bona_italians_pl_sig", "Королева из Милана зовёт в Краков итальянских мастеров — Ренессанс приходит на Вавель",
         "sig_bona_italians_pl",
         [actor("A", 0, tags=["bona_pl"]), actor("B", 1, tags=["architect_pl"])],
         [setf("B", "at_court_pl")]),
    rule("sigismund_chapel_pl_sig", "Флорентиец строит королю усыпальницу с золотым куполом — жемчужину Ренессанса к северу от Альп",
         "sig_sigismund_chapel_pl",
         [actor("A", 0, tags=["old_king_pl"]), actor("B", 1, tags=["architect_pl"], flags=["at_court_pl"])],
         [setf("B", "chapel_pl")]),
    rule("bell_1520_pl_sig", "На Вавеле отливают огромный колокол — он звонит только в великие дни",
         "sig_bell_1520_pl",
         [actor("A", 0, tags=["old_king_pl"])],
         [setf("A", "bell_pl")]),
    rule("rival_quarrel_pl_sig", "Зодчий ссорится с завистником — и получает удар ножом",
         "sig_rival_quarrel_pl",
         [actor("A", 0, tags=["architect_pl"], notFlags=["chapel_pl"]), actor("B", 1)],
         [setf("A", "dead")]),
]
NEW_LEVELS.append(level(
    "wawel_1520", 185, ACT3, "poland_ceremony", "sigismund_chapel_pl", 3,
    ["bona_italians_pl", "sigismund_chapel_pl", "bell_1520_pl", "rival_quarrel_pl"],
    ["sigismund1", "bona", "berrecci", "magnate_pl"],
    {"sigismund1": ["standing", "reigns", "crowned"], "bona": ["standing", "crowned"]}, [],
    [flag("berrecci", "chapel_pl"), flag("sigismund1", "bell_pl")],
    [("bona_italians_pl", ["bona", "berrecci"]), ("sigismund_chapel_pl", ["sigismund1", "berrecci"]),
     ("bell_1520_pl", ["sigismund1"])],
    "simplification"))
TEXTS.update(texts("wawel_1520",
    "Золотой купол Вавеля",
    "Сигизмунд Старый и Бона Сфорца превращают готический Вавель в ренессансный дворец — с капеллой и колоколом «Зыгмунт»",
    "Мастер должен сначала оказаться при дворе. Ссоры с завистниками не строят капелл.",
    "1518 год. Король Сигизмунд Старый женится на миланской принцессе Боне Сфорца. С ней в Краков едут итальянские вкусы, овощи, музыка — и мастера. Флорентийский зодчий Бартоломео Берреччи уже перестраивает Вавель.",
    "Берреччи строил Сигизмундову капеллу в 1519–1533 годах; её позолоченный купол называют самым красивым ренессансным памятником к северу от Альп. Он же перестроил Вавель в итальянский дворец с аркадами. В 1520 году для короля отлили колокол «Зыгмунт» — почти 13 тонн; он звонит только в самые важные дни, и говорят, если коснуться его сердца левой рукой, найдёшь любовь. С Боной в Польшу пришли и «итальянские» овощи: салат, капуста, порей — и по-польски суповой набор до сих пор называют «włoszczyzna», «итальянщина». Берреччи погиб в 1537 году — его зарезали в краковской ссоре.",
    "Надпись в куполе Сигизмундовой капеллы; Ю. Л. Децюш, «О временах короля Сигизмунда»"))

# ================================================================ warsaw_capital_1596
NEW_SCENES += [
    scene("wawel_fire_pl", "Пожар на Вавеле", ["sig_wawel_fire_pl"], 1, "🔥", "возиться с алхимией", "icon_dead",
          ["король"], "fire_sermon"),
    scene("move_warsaw_pl", "Двор едет в Варшаву", ["sig_move_warsaw_pl"], 1, "🐎", "перенести двор", "icon_crown",
          ["король"], "liege_ride"),
    scene("rebuild_wawel_pl", "Отстроить Вавель", ["sig_rebuild_wawel_pl"], 1, "🏰", "остаться в Кракове", "icon_ally",
          ["король"], "build_house_pl"),
    scene("column_pl", "Колонна Сигизмунда", ["sig_column_pl"], 2, "🗿", "поставить колонну", "icon_crown",
          ["сын", "отец"], "palace_square"),
]
NEW_RULES += [
    rule("wawel_fire_pl_sig", "В королевских покоях загорается — молва винит алхимические опыты короля",
         "sig_wawel_fire_pl",
         [actor("A", 0, tags=["vasa_pl"])],
         [setf("A", "wawel_burnt_pl")]),
    rule("rebuild_wawel_pl_sig", "Король решает остаться в Кракове и отстраивать сгоревший замок",
         "sig_rebuild_wawel_pl",
         [actor("A", 0, tags=["vasa_pl"])],
         [setf("A", "stays_krakow_pl")]),
    rule("move_warsaw_pl_sig", "Король переносит двор в Варшаву — ближе к Литве, к сейму и к его родной Швеции",
         "sig_move_warsaw_pl",
         [actor("A", 0, tags=["vasa_pl"], flags=["wawel_burnt_pl"], notFlags=["stays_krakow_pl"])],
         [setf("A", "in_warsaw_pl")]),
    rule("column_pl_sig", "Сын ставит отцу колонну перед новым Королевским замком",
         "sig_column_pl",
         [actor("A", 0, tags=["prince_w_pl"]), actor("B", 1, tags=["vasa_pl"], flags=["in_warsaw_pl"])],
         [setf("A", "column_pl")]),
]
NEW_LEVELS.append(level(
    "warsaw_capital_1596", 255, ACT4, "poland_ceremony", "column_pl", 3,
    ["wawel_fire_pl", "move_warsaw_pl", "rebuild_wawel_pl", "column_pl"],
    ["sigismund3", "wladyslaw4", "zamoyski"],
    {"sigismund3": ["standing", "reigns", "crowned"]}, [],
    [flag("wladyslaw4", "column_pl"), nflag("sigismund3", "stays_krakow_pl")],
    [("wawel_fire_pl", ["sigismund3"]), ("move_warsaw_pl", ["sigismund3"]), ("column_pl", ["wladyslaw4", "sigismund3"])],
    "simplification"))
TEXTS.update(texts("warsaw_capital_1596",
    "Столица переезжает в Варшаву",
    "После пожара на Вавеле Сигизмунд III переносит двор в Варшаву — и город становится столицей",
    "Повод нужен — и он вспыхнул в королевских покоях. Решив отстраивать Краков, король в Варшаву уже не поедет.",
    "1595 год. Сигизмунд III Ваза — король Польши и наследник шведского трона. Краков стоит на южном краю огромной Речи Посполитой, далеко от Литвы и от моря. Король увлекается алхимией, и в его покоях на Вавеле стоят печи и колбы.",
    "В 1595 году на Вавеле случился пожар, сгорело северо-восточное крыло; молва упорно винила алхимические опыты короля. Сигизмунд отстроил покои, но всё чаще жил в Варшаве, где собирался сейм, а около 1596–1611 годов двор окончательно переехал туда. Официального указа о переносе столицы так и не было, а короновались короли по-прежнему в Кракове. В 1644 году его сын Владислав IV поставил отцу в Варшаве колонну — один из старейших светских памятников Европы. «Сигизмунд» с саблей и крестом до сих пор стоит на Замковой площади.",
    "Надпись на колонне Сигизмунда (1644)"))

# ================================================================ khmelnytsky_1648
NEW_SCENES += [
    scene("subotiv_raid_pl", "Наезд на Суботов", ["sig_subotiv_raid_pl"], 2, "🔥", "отнять хутор", "icon_plot",
          ["подстароста", "сотник"], "burnt_fields"),
    scene("sabre_advice_pl", "Жалоба королю", ["sig_sabre_advice_pl"], 2, "⚖️", "искать правды в суде", "icon_ally",
          ["сотник", "подстароста"], "court"),
    scene("khan_alliance_pl", "Союз с ханом", ["sig_khan_alliance_pl"], 2, "🤝", "позвать орду", "icon_ally",
          ["гетман", "хан"], "hostage_chief"),
    scene("korsun_pl", "Корсунь", ["sig_korsun_pl"], 2, "⚔️", "ударить по коронному войску", "icon_dead",
          ["гетман", "коронный гетман"], "open_battle"),
]
NEW_RULES += [
    rule("subotiv_raid_pl_sig", "Подстароста отнимает у сотника хутор, а сына его велит высечь",
         "sig_subotiv_raid_pl",
         [actor("A", 0, tags=["starosta_pl"]), actor("B", 1, tags=["khmel_pl"])],
         [setf("B", "wronged_pl")]),
    rule("sabre_advice_pl_sig", "Суд ничего не возвращает, а король, говорят, бросает: «У вас же есть сабли»",
         "sig_sabre_advice_pl",
         [actor("A", 0, tags=["khmel_pl"]), actor("B", 1, tags=["starosta_pl"])],
         [setf("A", "sabre_advice_pl")]),
    rule("khan_alliance_pl_sig", "Обиженный сотник бежит на Сечь, становится гетманом и зовёт в союзники крымского хана",
         "sig_khan_alliance_pl",
         [actor("A", 0, tags=["khmel_pl"], flags=["wronged_pl"]), actor("B", 1, tags=["khan_pl"])],
         [setf("A", "allied_khan_pl"), setf("A", "strong")]),
    rule("korsun_allied_pl_sig", "Казаки и орда разбивают коронное войско — оба гетмана Речи Посполитой в плену",
         "sig_korsun_pl",
         [actor("A", 0, tags=["khmel_pl"], flags=["allied_khan_pl"]), actor("B", 1, tags=["crown_hetman_pl"])],
         [setf("B", "captive_pl"), setf("B", "defeated"), setf("A", "victor")]),
    rule("korsun_alone_pl_sig", "Без татарской конницы казаков опрокидывают крылатые гусары",
         "sig_korsun_pl",
         [actor("A", 0, tags=["khmel_pl"], notFlags=["allied_khan_pl"]), actor("B", 1, tags=["crown_hetman_pl"])],
         [setf("A", "defeated")]),
]
NEW_LEVELS.append(level(
    "khmelnytsky_1648", 285, ACT4, "poland_battle", "korsun_pl", 3,
    ["subotiv_raid_pl", "sabre_advice_pl", "khan_alliance_pl", "korsun_pl"],
    ["khmelnytsky", "czaplinski", "islam_giray", "potocki_hetman"],
    {"potocki_hetman": ["standing", "strong"], "islam_giray": ["standing", "strong"]}, [],
    [flag("potocki_hetman", "captive_pl"), nflag("khmelnytsky", "defeated")],
    [("subotiv_raid_pl", ["czaplinski", "khmelnytsky"]), ("khan_alliance_pl", ["khmelnytsky", "islam_giray"]),
     ("korsun_pl", ["khmelnytsky", "potocki_hetman"])],
    "fact"))
TEXTS.update(texts("khmelnytsky_1648",
    "Восстание Хмельницкого",
    "Личная обида чигиринского сотника перерастает в войну, которая потрясёт Речь Посполитую до основания",
    "Восстание начинается с обиды, а не с суда. Против гусарии казакам нужна конница, и взять её можно только у соседа.",
    "1647 год. На Поднепровье магнаты и их люди забирают землю у казаков, а казачий реестр урезан. Чигиринский сотник Богдан Хмельницкий — шляхтич, человек учёный и уважаемый. Подстароста Даниэль Чаплинский положил глаз на его хутор Суботов.",
    "Чаплинский захватил Суботов, сына Хмельницкого жестоко высекли. Жалобы в суд и королю Владиславу IV ничего не дали; по преданию, король ответил, что у казаков есть сабли. Хмельницкий бежал на Запорожскую Сечь, был избран гетманом и заключил союз с крымским ханом Ислам Гераем. В мае 1648 года под Жёлтыми Водами и Корсунем коронное войско было разбито, гетманы Николай Потоцкий и Мартин Калиновский попали в татарский плен. Война шла годами и стала одной из самых кровавых в истории этих земель: гибли шляхтичи, казаки, крестьяне, сотни еврейских общин. В Польше её помнят как начало упадка Речи Посполитой, в Украине — как рождение казацкого государства.",
    "Самуил Твардовский, «Война домашняя»; казацкие летописи Самовидца и Грабянки"))

# ================================================================ august2_1697
NEW_SCENES += [
    scene("secret_conversion_pl", "Тайное обращение", ["sig_secret_conversion_pl"], 1, "⛪", "принять католичество", "icon_ally",
          ["курфюрст"], "chapel"),
    scene("saxon_dash_pl", "Бросок саксонского войска", ["sig_saxon_dash_pl"], 2, "🐎", "успеть первым", "icon_crown",
          ["курфюрст", "соперник"], "liege_ride"),
    scene("oliwa_roads_pl", "Рейд у Оливы", ["sig_oliwa_roads_pl"], 1, "⛵", "повернуть корабли", "icon_ally",
          ["принц"], "harbor"),
    bait("buy_votes_pl", "Скупить голоса", "v_bribe", 2, "court_purse", ["кто платит", "кого покупают"]),
]
NEW_RULES += [
    rule("secret_conversion_pl_sig", "Лютеранин-курфюрст Саксонии тайно переходит в католичество — иначе польской короны не видать",
         "sig_secret_conversion_pl",
         [actor("A", 0, tags=["saxon2_pl"])],
         [setf("A", "catholic_pl")]),
    rule("saxon_dash_pl_sig", "Саксонец с войском первым входит в Краков и коронуется, пока француз ещё в море",
         "sig_saxon_dash_pl",
         [actor("A", 0, tags=["saxon2_pl"], flags=["catholic_pl"]), actor("B", 1, tags=["conti_pl"])],
         [setf("A", "crowned_aug_pl"), setf("A", "crowned"), setf("A", "reigns"), setf("B", "outrun_pl")]),
    rule("oliwa_roads_pl_sig", "Французский принц видит, что страна уже за соперником, и уплывает домой",
         "sig_oliwa_roads_pl",
         [actor("A", 0, tags=["conti_pl"], flags=["outrun_pl"])],
         [setf("A", "away")]),
]
NEW_LEVELS.append(level(
    "august2_1697", 325, ACT4, "poland_ceremony", "saxon_dash_pl", 3,
    ["secret_conversion_pl", "saxon_dash_pl", "oliwa_roads_pl", "buy_votes_pl"],
    ["august2", "conti", "archbishop_gn"],
    {"august2": ["standing", "strong"], "conti": ["standing"]}, [],
    [flag("august2", "crowned_aug_pl"), flag("conti", "away")],
    [("secret_conversion_pl", ["august2"]), ("saxon_dash_pl", ["august2", "conti"]), ("oliwa_roads_pl", ["conti"])],
    "fact"))
TEXTS.update(texts("august2_1697",
    "Август Сильный",
    "Саксонский курфюрст меняет веру, обгоняет избранного француза и садится на польский трон",
    "Католический трон требует католика — это первое. Кто быстрее с войском, тот и король; соперник поймёт сам.",
    "1697 год. Умер Ян Собеский. Самый богатый кандидат — французский принц де Конти, за него примас и большинство голосов. Но у саксонского курфюрста Фридриха Августа есть деньги, войско по соседству и железные руки: говорят, он ломает подковы пальцами. Беда одна — он лютеранин.",
    "1 июня 1697 года курфюрст тайно принял католичество. 27 июня примас провозгласил королём Конти, но часть шляхты — Августа, и саксонец с войском двинулся в Польшу первым. 15 сентября его короновали в Вавельском соборе — правда, не примас, а куявский епископ. Конти доплыл с французской эскадрой до Гданьского залива только в сентябре, увидел, что всё решено, и вернулся во Францию. Так началась «саксонская эпоха»: Август втянул страну в Северную войну, а в 1717 году «Немой сейм» под присмотром русских войск урезал армию Речи Посполитой до 24 тысяч — и почти никто на нём не говорил.",
    "Дневники элекции 1697 г.; Казимеж Яроховский, «История правления Августа II»"))

# ================================================================ bar_1768
NEW_SCENES += [
    scene("bishops_kidnap_pl", "Арест епископов", ["sig_bishops_kidnap_pl"], 2, "⛓️", "увезти в Калугу", "icon_plot",
          ["посол", "епископ"], "arrest_d"),
    scene("bar_oath_pl", "Конфедерация в Баре", ["sig_bar_oath_pl"], 2, "⚔️", "поклясться за веру и вольность", "icon_ally",
          ["конфедерат", "епископ"], "dagger_oath"),
    scene("jasna_defense_pl", "Оборона Ясной Горы", ["sig_jasna_defense_pl"], 2, "🏰", "держать монастырь", "icon_crown",
          ["конфедерат", "посол"], "breach_wall"),
    scene("king_kidnap_pl", "Похищение короля", ["sig_king_kidnap_pl"], 2, "🌙", "похитить короля", "icon_plot",
          ["конфедерат", "король"], "night_flight"),
]
NEW_RULES += [
    rule("bishops_kidnap_pl_sig", "Посол Репнин велит схватить епископов, выступивших против него на сейме, и вывезти в Россию",
         "sig_bishops_kidnap_pl",
         [actor("A", 0, tags=["ambassador_pl"]), actor("B", 1, tags=["bishop_k_pl"])],
         [setf("B", "exiled_kaluga_pl"), setf("B", "away")]),
    rule("bar_oath_pl_sig", "Шляхта в Баре клянётся сражаться за веру и вольность — против посла и короля-ставленника",
         "sig_bar_oath_pl",
         [actor("A", 0, tags=["pulaski_pl"]), actor("B", 1, tags=["bishop_k_pl"], flags=["exiled_kaluga_pl"])],
         [setf("A", "confederate_pl")]),
    rule("jasna_defense_pl_sig", "Пулаский удерживает Ясногорский монастырь, отбивая осаду за осадой",
         "sig_jasna_defense_pl",
         [actor("A", 0, tags=["pulaski_pl"], flags=["confederate_pl"], notFlags=["outlaw_pl"]), actor("B", 1, tags=["ambassador_pl"])],
         [setf("A", "held_jasna_pl")]),
    rule("king_kidnap_pl_sig", "Конфедераты ночью похищают короля — и вся Европа объявляет их цареубийцами",
         "sig_king_kidnap_pl",
         [actor("A", 0, tags=["pulaski_pl"]), actor("B", 1, tags=["sa_king_pl"])],
         [setf("A", "outlaw_pl")]),
]
NEW_LEVELS.append(level(
    "bar_1768", 345, ACT5, "poland_tension", "jasna_defense_pl", 3,
    ["bishops_kidnap_pl", "bar_oath_pl", "jasna_defense_pl", "king_kidnap_pl"],
    ["repnin", "soltyk", "pulaski", "poniatowski"],
    {"repnin": ["standing", "strong"], "poniatowski": ["standing", "reigns", "crowned"], "soltyk": ["standing"]}, [],
    [flag("pulaski", "held_jasna_pl"), nflag("pulaski", "outlaw_pl")],
    [("bishops_kidnap_pl", ["repnin", "soltyk"]), ("bar_oath_pl", ["pulaski", "soltyk"]),
     ("jasna_defense_pl", ["pulaski", "repnin"])],
    "simplification"))
TEXTS.update(texts("bar_1768",
    "Барская конфедерация",
    "Посол арестует епископов, шляхта поднимается в Баре, а молодой Пулаский держит Ясную Гору",
    "Восстанию нужен повод — и посол его даст. Не всякая дерзость — подвиг: тронешь короля, и тебя проклянёт вся Европа.",
    "1767 год. В Варшаве всем распоряжается российский посол Николай Репнин. Сейм под его давлением должен утвердить права иноверцев и гарантии императрицы. Против выступают краковский епископ Каетан Солтык и ещё несколько сенаторов.",
    "В ночь на 14 октября 1767 года Репнин велел арестовать Солтыка, ещё одного епископа и двух сенаторов и вывезти в Калугу, где они провели пять лет. 29 февраля 1768 года в Баре на Подолье шляхта создала конфедерацию «за веру и вольность». Война шла четыре года; Казимир Пулаский прославился обороной Ясной Горы в 1770–1771 годах. Но в 1771 году конфедераты похитили короля Станислава Августа — тот сбежал той же ночью, а Пулаского объявили цареубийцей. Он уехал в Америку, стал «отцом американской кавалерии» и погиб в 1779 году под Саванной. Конфедерацию разгромили, а в 1772 году случился первый раздел.",
    "Акт Барской конфедерации (1768); Владислав Конопчинский, «Барская конфедерация»"))

# ================================================================ targowica_1792
NEW_SCENES += [
    scene("targowica_act_pl", "Акт Тарговицкой конфедерации", ["sig_targowica_act_pl"], 2, "📜", "подписать акт", "icon_plot",
          ["магнат", "императрица"], "court_present"),
    scene("zielence_pl", "Зеленцы", ["sig_zielence_pl"], 2, "⚔️", "дать бой", "icon_crown",
          ["князь", "магнат"], "open_battle_s"),
    scene("king_joins_pl", "Король примыкает к Тарговице", ["sig_king_joins_pl"], 2, "✍️", "подписать акцессию", "icon_dead",
          ["король", "магнат"], "abdication_table"),
    bait("king_to_army_pl", "Король идёт к войску", "v_battle", 2, "open_battle", BATTLE),
]
NEW_RULES += [
    rule("targowica_act_pl_sig", "Магнаты подписывают в Петербурге акт против Конституции 3 мая и зовут русскую армию",
         "sig_targowica_act_pl",
         [actor("A", 0, tags=["targowica_pl"]), actor("B", 1, tags=["empress_pl"])],
         [setf("A", "confederation_t_pl"), setf("A", "strong")]),
    rule("zielence_pl_sig", "Князь Юзеф разбивает наступающих под Зеленцами — король учреждает орден Virtuti Militari",
         "sig_zielence_pl",
         [actor("A", 0, tags=["prince_j_pl"]), actor("B", 1, tags=["targowica_pl"], flags=["confederation_t_pl"])],
         [setf("A", "virtuti_pl")]),
    rule("king_joins_pl_sig", "Король, надеясь спасти хоть что-то, присоединяется к Тарговице — и армия складывает оружие",
         "sig_king_joins_pl",
         [actor("A", 0, tags=["sa_king_pl"]), actor("B", 1, tags=["targowica_pl"], flags=["confederation_t_pl"])],
         [setf("A", "joined_targowica_pl")]),
]
NEW_LEVELS.append(level(
    "targowica_1792", 365, ACT5, "poland_battle", "zielence_pl", 3,
    ["targowica_act_pl", "zielence_pl", "king_joins_pl", "king_to_army_pl"],
    ["potocki_sz", "catherine2_pl", "jozef_poniatowski", "poniatowski"],
    {"catherine2_pl": ["standing", "reigns", "crowned"], "poniatowski": ["standing", "reigns", "crowned"],
     "jozef_poniatowski": ["standing", "strong"]}, [],
    [flag("jozef_poniatowski", "virtuti_pl"), flag("poniatowski", "joined_targowica_pl")],
    [("targowica_act_pl", ["potocki_sz", "catherine2_pl"]), ("zielence_pl", ["jozef_poniatowski", "potocki_sz"]),
     ("king_joins_pl", ["poniatowski", "potocki_sz"])],
    "fact"))
TEXTS.update(texts("targowica_1792",
    "Тарговица",
    "Магнаты зовут чужую армию против Конституции 3 мая; князь Юзеф побеждает под Зеленцами, а король сдаётся",
    "Враг без союзницы не придёт. Победа в поле ещё не победа: решать будет король.",
    "1792 год. Год назад Польша приняла Конституцию 3 мая. Магнаты, потерявшие власть, — Щенсны Потоцкий, Ксаверий Браницкий, Северин Ржевуский — едут в Петербург к императрице Екатерине II.",
    "Акт конфедерации подписали в Петербурге 27 апреля 1792 года, а провозгласили в местечке Тарговица; в мае в страну вошла стотысячная русская армия. 18 июня под Зеленцами князь Юзеф Понятовский разбил русский корпус, и в честь этой победы король учредил орден Virtuti Militari — высшую военную награду Польши по сей день; первыми её получили Понятовский и Костюшко. Но 24 июля король присоединился к Тарговице, армия сложила оружие, а Понятовский и Костюшко ушли в отставку. Через год случился второй раздел. Слово «тарговичанин» в польском языке до сих пор означает предателя.",
    "Акт Тарговицкой конфедерации (1792); Эмануэль Ростворовский, «Последний король Речи Посполитой»"))

# ================================================================ grodno_1795
NEW_SCENES += [
    scene("deputy_protest_pl", "Протест депутата", ["sig_deputy_protest_pl"], 1, "📢", "протестовать", "icon_plot",
          ["депутат"], "sejm_time_pl"),
    scene("silent_sejm_pl", "Немое заседание", ["sig_silent_sejm_pl"], 2, "🤐", "промолчать", "icon_ally",
          ["посол", "депутат"], "sejm_divorce_pl"),
    scene("partition_treaty_pl", "Договор о втором разделе", ["sig_partition_treaty_pl"], 3, "✍️", "утвердить договор", "icon_dead",
          ["посол", "депутат", "король"], "abdication_table"),
    scene("abdication_1795_pl", "Отречение в Гродно", ["sig_abdication_1795_pl"], 2, "📜", "отречься от короны", "icon_dead",
          ["императрица", "король"], "abdicate_d"),
]
NEW_RULES += [
    rule("deputy_protest_pl_sig", "Депутат громко протестует — его хватают солдаты и выводят из зала",
         "sig_deputy_protest_pl",
         [actor("A", 0, tags=["szlachcic_pl"])],
         [setf("A", "arrested_pl"), setf("A", "away")]),
    rule("silent_sejm_pl_sig", "Зал окружён пушками, депутаты молчат — и маршалок объявляет: молчание есть согласие",
         "sig_silent_sejm_pl",
         [actor("A", 0, tags=["ambassador_s_pl"]), actor("B", 1, tags=["szlachcic_pl"], notFlags=["arrested_pl"])],
         [setf("B", "silent_pl")]),
    rule("partition_treaty_pl_sig", "Договор о втором разделе утверждён — Речь Посполитая теряет больше половины земель",
         "sig_partition_treaty_pl",
         [actor("A", 0, tags=["ambassador_s_pl"]), actor("B", 1, tags=["szlachcic_pl"], flags=["silent_pl"]),
          actor("C", 2, tags=["sa_king_pl"])],
         [setf("C", "treaty_pl")]),
    rule("abdication_1795_pl_sig", "После третьего раздела последний король подписывает отречение — в день именин императрицы",
         "sig_abdication_1795_pl",
         [actor("A", 0, tags=["empress_pl"]), actor("B", 1, tags=["sa_king_pl"], flags=["treaty_pl"])],
         [setf("B", "abdicated_pl"), remf("B", "reigns")]),
]
NEW_LEVELS.append(level(
    "grodno_1795", 385, ACT5, "poland_tension", "abdication_1795_pl", 3,
    ["deputy_protest_pl", "silent_sejm_pl", "partition_treaty_pl", "abdication_1795_pl"],
    ["sievers", "szlachcic_pl", "poniatowski", "catherine2_pl"],
    {"poniatowski": ["standing", "reigns", "crowned"], "catherine2_pl": ["standing", "reigns", "crowned"],
     "sievers": ["standing", "strong"]}, [],
    [flag("poniatowski", "abdicated_pl")],
    [("silent_sejm_pl", ["sievers", "szlachcic_pl"]), ("partition_treaty_pl", ["sievers", "szlachcic_pl", "poniatowski"]),
     ("abdication_1795_pl", ["catherine2_pl", "poniatowski"])],
    "fact"))
TEXTS.update(texts("grodno_1795",
    "Немой сейм и последний король",
    "В Гродно сейм под пушками «соглашается» молчанием на второй раздел, а через два года король отрекается",
    "Протест здесь не останавливает — он просто убирает человека из зала. Отречение подписывают, когда государства уже нет.",
    "1793 год. После Тарговицы в Гродно созван последний сейм Речи Посполитой. Российский посол Якоб Сиверс подкупил часть депутатов, остальных окружили войска; в зал наведены пушки. Нужно утвердить второй раздел.",
    "23 сентября 1793 года, после многочасового молчания депутатов, маршалок объявил, что «молчание есть знак согласия», и договор о втором разделе был утверждён. Протестовавших депутатов арестовывали. Через год вспыхнуло восстание Костюшко, а после его разгрома, в 1795 году, Россия, Пруссия и Австрия поделили остаток страны. 25 ноября 1795 года, в день именин Екатерины II, Станислав Август подписал в Гродно отречение. Он умер в Петербурге в 1798 году. Польши не будет на карте 123 года.",
    "Дневник Гродненского сейма 1793 г.; акт отречения Станислава Августа (1795)"))

# ================================================================ raszyn_1809
NEW_SCENES += [
    scene("raszyn_pl", "Рашин", ["sig_raszyn_pl"], 2, "⚔️", "встретить австрийцев", "icon_dead",
          ["князь", "эрцгерцог"], "open_field_1831_pl"),
    scene("yield_warsaw_pl", "Сдать Варшаву без боя", ["sig_yield_warsaw_pl"], 2, "🤝", "уступить столицу", "icon_ally",
          ["эрцгерцог", "князь"], "empty_city"),
    scene("galicia_march_pl", "Поход в Галицию", ["sig_galicia_march_pl"], 1, "🐎", "идти на юг", "icon_crown",
          ["князь"], "danube_march"),
    scene("last_stand_pl", "Стоять насмерть у стен", ["sig_last_stand_pl"], 2, "🏰", "держать Варшаву", "icon_dead",
          ["князь", "эрцгерцог"], "breach_wall"),
]
NEW_RULES += [
    rule("raszyn_pl_sig", "Под Рашином маленькая польская армия весь день держит втрое большие силы австрийцев",
         "sig_raszyn_pl",
         [actor("A", 0, tags=["prince_j_pl"]), actor("B", 1, tags=["austrian_pl"])],
         [setf("A", "held_raszyn_pl")]),
    rule("last_stand_pl_sig", "Князь запирается в Варшаве — армию осаждают и связывают по рукам",
         "sig_last_stand_pl",
         [actor("A", 0, tags=["prince_j_pl"]), actor("B", 1, tags=["austrian_pl"])],
         [setf("A", "trapped_pl")]),
    rule("yield_warsaw_pl_sig", "Князь отдаёт Варшаву по договору — и уводит армию целой",
         "sig_yield_warsaw_pl",
         [actor("A", 0, tags=["austrian_pl"]), actor("B", 1, tags=["prince_j_pl"], flags=["held_raszyn_pl"], notFlags=["trapped_pl"])],
         [setf("A", "in_warsaw_pl"), setf("B", "free_hand_pl")]),
    rule("galicia_march_pl_sig", "Пока австрийцы сидят в Варшаве, поляки идут в их Галицию: Люблин, Сандомир, Краков",
         "sig_galicia_march_pl",
         [actor("A", 0, tags=["prince_j_pl"], flags=["free_hand_pl"])],
         [setf("A", "galicia_pl")]),
]
NEW_LEVELS.append(level(
    "raszyn_1809", 412, ACT6, "poland_battle", "galicia_march_pl", 3,
    ["raszyn_pl", "yield_warsaw_pl", "galicia_march_pl", "last_stand_pl"],
    ["jozef_poniatowski", "archduke_ferdinand", "napoleon_pl"],
    {"jozef_poniatowski": ["standing"], "archduke_ferdinand": ["standing", "strong"], "napoleon_pl": ["standing", "reigns", "crowned"]}, [],
    [flag("jozef_poniatowski", "galicia_pl"), flag("archduke_ferdinand", "in_warsaw_pl")],
    [("raszyn_pl", ["jozef_poniatowski", "archduke_ferdinand"]), ("yield_warsaw_pl", ["archduke_ferdinand", "jozef_poniatowski"]),
     ("galicia_march_pl", ["jozef_poniatowski"])],
    "fact"))
TEXTS.update(texts("raszyn_1809",
    "Рашин: отдать столицу, чтобы выиграть войну",
    "Князь Юзеф уступает Варшаву австрийцам — и, пока они сидят в ней, забирает у Австрии пол-Галиции",
    "Держаться за столицу — значит в ней и погибнуть. Пусть враг сидит в Варшаве, а армия пойдёт туда, где её не ждут.",
    "1809 год. Наполеон воюет с Австрией, а на маленькое Варшавское герцогство идёт 30-тысячная австрийская армия эрцгерцога Фердинанда. У князя Юзефа Понятовского вдвое-втрое меньше солдат.",
    "19 апреля 1809 года под Рашином поляки весь день сдерживали австрийцев, потом отошли. Понятовский заключил соглашение, сдал Варшаву без боя и вывел армию на правый берег Вислы — а затем двинулся на юг, в австрийскую Галицию: взял Люблин, Сандомир, Замостье, а 15 июля вошёл в Краков. Австрийцы, оставшись без тыла, ушли из Варшавы. По Шёнбруннскому миру герцогство получило Краков и Западную Галицию и выросло почти в полтора раза.",
    "Шёнбруннский мир (1809); Шимон Аскенази, «Князь Юзеф Понятовский»"))

# ================================================================ leipzig_1813
NEW_SCENES += [
    scene("marshal_baton_pl", "Маршальский жезл", ["sig_marshal_baton_pl"], 2, "🎖️", "вручить жезл", "icon_crown",
          ["император", "князь"], "court_favour"),
    scene("rear_guard_pl", "Прикрыть отступление", ["sig_rear_guard_pl"], 2, "🛡️", "держать арьергард", "icon_ally",
          ["князь", "император"], "leipzig_field"),
    scene("elster_crossing_pl", "Эльстер", ["sig_elster_crossing_pl"], 1, "🌊", "броситься в реку", "icon_dead",
          ["князь"], "elster_bridge"),
    scene("switch_sides_pl", "Предложение царя", ["sig_switch_sides_pl"], 2, "🤝", "перейти к союзникам", "icon_plot",
          ["император", "князь"], "court_whisper"),
]
NEW_RULES += [
    rule("marshal_baton_pl_sig", "Посреди Битвы народов Наполеон делает князя Юзефа маршалом Франции",
         "sig_marshal_baton_pl",
         [actor("A", 0, tags=["bonaparte_pl"]), actor("B", 1, tags=["prince_j_pl"], notFlags=["switched_pl"])],
         [setf("B", "marshal_pl")]),
    rule("switch_sides_pl_sig", "Князь принимает предложение Александра — и армия Варшавского герцогства переходит к союзникам",
         "sig_switch_sides_pl",
         [actor("A", 0, tags=["tsar_a1_pl"]), actor("B", 1, tags=["prince_j_pl"])],
         [setf("B", "switched_pl")]),
    rule("rear_guard_pl_sig", "Маршал с поляками прикрывает отход армии через Лейпциг",
         "sig_rear_guard_pl",
         [actor("A", 0, tags=["prince_j_pl"], flags=["marshal_pl"]), actor("B", 1, tags=["bonaparte_pl"])],
         [setf("A", "rearguard_pl")]),
    rule("elster_crossing_pl_sig", "Мост взорван раньше времени; раненый князь бросается на коне в Эльстер и тонет",
         "sig_elster_crossing_pl",
         [actor("A", 0, tags=["prince_j_pl"], flags=["rearguard_pl"])],
         [setf("A", "honor_pl"), setf("A", "dead")]),
]
NEW_LEVELS.append(level(
    "leipzig_1813", 415, ACT6, "poland_tension", "elster_crossing_pl", 3,
    ["marshal_baton_pl", "rear_guard_pl", "elster_crossing_pl", "switch_sides_pl"],
    ["jozef_poniatowski", "napoleon_pl", "alexander1_pl"],
    {"napoleon_pl": ["standing", "reigns", "crowned"], "alexander1_pl": ["standing", "reigns", "crowned"],
     "jozef_poniatowski": ["standing"]}, [],
    [flag("jozef_poniatowski", "honor_pl"), nflag("jozef_poniatowski", "switched_pl")],
    [("marshal_baton_pl", ["napoleon_pl", "jozef_poniatowski"]), ("rear_guard_pl", ["jozef_poniatowski", "napoleon_pl"]),
     ("elster_crossing_pl", ["jozef_poniatowski"])],
    "fact"))
TEXTS.update(texts("leipzig_1813",
    "Честь поляков",
    "Князь Юзеф получает маршальский жезл в Битве народов и через три дня гибнет в Эльстере, прикрывая отход",
    "Ему предлагали спасение — у другого императора. Жезл даётся тому, кто остался верен.",
    "1813 год. Великая армия погибла в России, Варшавское герцогство занято русскими. Царь Александр через посредников предлагает князю Юзефу Понятовскому перейти на сторону союзников. Князь ведёт остатки польской армии к Наполеону в Саксонию.",
    "Понятовский ответил на предложения, что ему поручена честь поляков. 16 октября 1813 года, в первый день Битвы народов под Лейпцигом, Наполеон сделал его маршалом Франции — единственным иностранцем среди своих маршалов. 19 октября князь с поляками прикрывал отступление; мост через Эльстер взорвали слишком рано, и раненый Понятовский бросился с конём в реку и утонул. Ему приписывают последние слова: «Бог вверил мне честь поляков, Богу её и отдам». Его прах покоится на Вавеле рядом с королями.",
    "Бюллетени Великой армии (1813); Шимон Аскенази, «Князь Юзеф Понятовский»"))

# ================================================================ kingdom_1815
NEW_SCENES += [
    scene("vienna_congress_pl", "Венский конгресс", ["sig_vienna_congress_pl"], 2, "🗺️", "договориться о Польше", "icon_crown",
          ["император", "советник"], "coalition_oath"),
    scene("constitution_1815_pl", "Конституция Царства", ["sig_constitution_1815_pl"], 2, "📜", "даровать конституцию", "icon_crown",
          ["император", "советник"], "council"),
    scene("namiestnik_pl", "Назначить наместника", ["sig_namiestnik_pl"], 2, "👔", "сделать наместником", "icon_plot",
          ["император", "советник"], "court_favour"),
    scene("army_command_pl", "Командующий армией", ["sig_army_command_pl"], 2, "⚔️", "отдать армию брату", "icon_ally",
          ["император", "брат"], "palace_square"),
]
NEW_RULES += [
    rule("vienna_congress_pl_sig", "На конгрессе царь добивается польского королевства под своей короной",
         "sig_vienna_congress_pl",
         [actor("A", 0, tags=["tsar_a1_pl"]), actor("B", 1, tags=["czartoryski_pl"])],
         [setf("A", "kingdom_pl")]),
    rule("constitution_1815_pl_sig", "Царь дарует Царству одну из самых либеральных конституций Европы — свой сейм, своя армия, польский язык",
         "sig_constitution_1815_pl",
         [actor("A", 0, tags=["tsar_a1_pl"], flags=["kingdom_pl"]), actor("B", 1, tags=["czartoryski_pl"])],
         [setf("A", "constitution_pl")]),
    rule("namiestnik_pl_sig", "Царь назначает друга молодости наместником — и тот вместо советника становится исполнителем",
         "sig_namiestnik_pl",
         [actor("A", 0, tags=["tsar_a1_pl"]), actor("B", 1, tags=["czartoryski_pl"])],
         [setf("B", "viceroy_pl")]),
    rule("army_command_pl_sig", "Командование польской армией получает брат царя, великий князь Константин",
         "sig_army_command_pl",
         [actor("A", 0, tags=["tsar_a1_pl"], flags=["kingdom_pl"]), actor("B", 1, tags=["grand_duke_pl"])],
         [setf("B", "commander_pl")]),
]
NEW_LEVELS.append(level(
    "kingdom_1815", 418, ACT6, "poland_ceremony", "constitution_1815_pl", 3,
    ["vienna_congress_pl", "constitution_1815_pl", "namiestnik_pl", "army_command_pl"],
    ["alexander1_pl", "czartoryski", "konstantin_pl"],
    {"alexander1_pl": ["standing", "reigns", "crowned"], "konstantin_pl": ["standing", "strong"]}, [],
    [flag("alexander1_pl", "constitution_pl"), flag("konstantin_pl", "commander_pl"), nflag("czartoryski", "viceroy_pl")],
    [("vienna_congress_pl", ["alexander1_pl", "czartoryski"]), ("constitution_1815_pl", ["alexander1_pl", "czartoryski"]),
     ("army_command_pl", ["alexander1_pl", "konstantin_pl"])],
    "simplification"))
TEXTS.update(texts("kingdom_1815",
    "Царство Польское",
    "Венский конгресс создаёт Царство Польское с царём-королём и либеральной конституцией — и с братом царя во главе армии",
    "Конституцию дают королевству, а королевство ещё надо выторговать. Наместником друга царь так и не сделал.",
    "1815 год. Наполеон разбит. В Вене монархи перекраивают Европу, и судьба польских земель — один из самых острых вопросов. Рядом с царём Александром I — князь Адам Ежи Чарторыйский, его друг юности и бывший министр иностранных дел России.",
    "Венский конгресс создал Царство Польское в унии с Россией: царь стал польским королём. 27 ноября 1815 года Александр I даровал ему конституцию — одну из самых либеральных в тогдашней Европе: свой сейм, армия, суды, польский язык в делах. Чарторыйский надеялся стать наместником, но им назначили старого генерала Юзефа Зайончека, а армию возглавил великий князь Константин. Конституцию постепенно перестали соблюдать — и через пятнадцать лет вспыхнула Ноябрьская ночь.",
    "Заключительный акт Венского конгресса (1815); Конституционная хартия Царства Польского"))

# ================================================================ krakow_1846
NEW_SCENES += [
    scene("krakow_rising_pl", "Краковское восстание", ["sig_krakow_rising_pl"], 1, "🚩", "поднять восстание", "icon_ally",
          ["революционер"], "barons_muster"),
    scene("promise_land_pl", "Обещать землю крестьянам", ["sig_promise_land_pl"], 2, "🌾", "пообещать землю", "icon_ally",
          ["революционер", "крестьянин"], "peasant_ukaz_pl"),
    scene("rabacja_pl", "Галицийская резня", ["sig_rabacja_pl"], 2, "🔥", "пойти на усадьбы", "icon_dead",
          ["крестьянин", "шляхтич"], "burnt_fields"),
    scene("podgorze_procession_pl", "Крестный ход в Подгуже", ["sig_podgorze_procession_pl"], 1, "✝️", "выйти к крестьянам с крестом", "icon_dead",
          ["революционер"], "cathedral_procession"),
]
NEW_RULES += [
    rule("krakow_rising_pl_sig", "В Вольном городе Кракове объявлено национальное правительство и отмена барщины",
         "sig_krakow_rising_pl",
         [actor("A", 0, tags=["dembowski_pl"])],
         [setf("A", "rising_pl")]),
    rule("promise_land_pl_sig", "Крестьянин слушает агитатора — но не верит панам, которые вчера гнали его на барщину",
         "sig_promise_land_pl",
         [actor("A", 0, tags=["dembowski_pl"]), actor("B", 1, tags=["szela_pl"])],
         [setf("B", "distrusts_pl")]),
    rule("rabacja_pl_sig", "Крестьяне, подогретые австрийскими чиновниками, громят усадьбы и убивают шляхтичей",
         "sig_rabacja_pl",
         [actor("A", 0, tags=["szela_pl"]), actor("B", 1, tags=["szlachcic_pl"])],
         [setf("B", "dead"), setf("A", "rabacja_pl")]),
    rule("podgorze_procession_pl_sig", "Революционер выходит к крестьянам с крестным ходом — австрийские солдаты стреляют",
         "sig_podgorze_procession_pl",
         [actor("A", 0, tags=["dembowski_pl"], flags=["rising_pl"])],
         [setf("A", "martyr_pl"), setf("A", "dead")]),
]
NEW_LEVELS.append(level(
    "krakow_1846", 437, ACT6, "poland_tension", "krakow_rising_pl", 3,
    ["krakow_rising_pl", "promise_land_pl", "rabacja_pl", "podgorze_procession_pl"],
    ["dembowski", "szela", "szlachcic_pl"],
    {"szlachcic_pl": ["standing"]}, [],
    [flag("dembowski", "martyr_pl"), flag("szela", "rabacja_pl")],
    [("krakow_rising_pl", ["dembowski"]), ("rabacja_pl", ["szela", "szlachcic_pl"]), ("podgorze_procession_pl", ["dembowski"])],
    "fact"))
TEXTS.update(texts("krakow_1846",
    "1846: восстание и резня",
    "Шляхта поднимает восстание за свободу — а крестьяне Галиции, помня барщину, идут не за ней, а против неё",
    "Обещание опоздало: верит не тот, кому обещают, а тот, кто помнит барщину. Восстание кончится крестным ходом.",
    "Февраль 1846 года. Готовится всепольское восстание, центр — Вольный город Краков, крошечная республика под надзором трёх держав. В австрийской Галиции крестьяне по-прежнему отбывают барщину, и паны для них — не братья по нации, а господа.",
    "22 февраля в Кракове объявили Национальное правительство, отмену барщины и наделение крестьян землёй. Но в Галиции крестьяне во главе с Якубом Шелей, подогреваемые австрийскими чиновниками, которые платили за «бунтовщиков», разгромили сотни усадеб и убили около тысячи человек — шляхтичей, управляющих, ксендзов. 27 февраля философ-революционер Эдвард Дембовский вышел к крестьянам у Подгуже с крестным ходом, и его застрелили австрийские солдаты. Восстание пало, Краков присоединили к Австрии. Шеля получил от властей землю на Буковине, а в 1848 году барщину в Галиции всё-таки отменили — уже сами австрийцы.",
    "Стефан Кеневич, «Крестьянское движение в Галиции в 1846 году»"))

# ================================================================ poznan_1848
NEW_SCENES += [
    scene("moabit_release_pl", "Ворота Моабита", ["sig_moabit_release_pl"], 1, "🔓", "выйти из тюрьмы", "icon_ally",
          ["узник"], "bastille_storm"),
    scene("kosynierzy_pl", "Косиньеры", ["sig_kosynierzy_pl"], 2, "🌾", "поставить косы торчком", "icon_ally",
          ["командир", "крестьянин"], "communes_muster"),
    scene("miloslaw_pl", "Милослав", ["sig_miloslaw_pl"], 2, "⚔️", "ударить по пруссакам", "icon_crown",
          ["командир", "противник"], "open_field_1831_pl"),
    scene("jaroslawiec_pl", "Ярославецкое соглашение", ["sig_jaroslawiec_pl"], 2, "🤝", "распустить отряды", "icon_plot",
          ["командир", "чиновник"], "court_present"),
]
NEW_RULES += [
    rule("moabit_release_pl_sig", "Революция в Берлине: толпа освобождает польских узников, и их везут по городу как героев",
         "sig_moabit_release_pl",
         [actor("A", 0, tags=["mieroslawski_pl"])],
         [setf("A", "free_pl")]),
    rule("jaroslawiec_pl_sig", "Командир соглашается распустить большую часть отрядов в обмен на обещание реформ",
         "sig_jaroslawiec_pl",
         [actor("A", 0, tags=["mieroslawski_pl"]), actor("B", 1, tags=["official_pl"])],
         [setf("A", "disarmed_pl")]),
    rule("kosynierzy_pl_sig", "Крестьяне Великой Польши идут в отряды с косами, выпрямленными, как пики",
         "sig_kosynierzy_pl",
         [actor("A", 0, tags=["mieroslawski_pl"], flags=["free_pl"], notFlags=["disarmed_pl"]), actor("B", 1, tags=["peasant_serf_pl"])],
         [setf("A", "army_pl"), setf("B", "kosynier_pl")]),
    rule("miloslaw_pl_sig", "Под Милославом повстанцы отбрасывают прусские войска",
         "sig_miloslaw_pl",
         [actor("A", 0, tags=["mieroslawski_pl"], flags=["army_pl"]), actor("B", 1, tags=["official_pl"])],
         [setf("A", "won_miloslaw_pl")]),
]
NEW_LEVELS.append(level(
    "poznan_1848", 439, ACT6, "poland_battle", "miloslaw_pl", 3,
    ["moabit_release_pl", "kosynierzy_pl", "miloslaw_pl", "jaroslawiec_pl"],
    ["mieroslawski", "peasant_pl", "prussian_official"],
    {"prussian_official": ["standing", "strong"]}, [],
    [flag("mieroslawski", "won_miloslaw_pl"), flag("peasant_pl", "kosynier_pl")],
    [("moabit_release_pl", ["mieroslawski"]), ("kosynierzy_pl", ["mieroslawski", "peasant_pl"]),
     ("miloslaw_pl", ["mieroslawski", "prussian_official"])],
    "fact"))
TEXTS.update(texts("poznan_1848",
    "Весна народов в Познани",
    "Берлинская революция выпускает поляков из тюрьмы, и в Великой Польше поднимается восстание косиньеров",
    "Сначала узник должен выйти на свободу. Распустишь отряды ради обещаний — драться будет некем.",
    "Март 1848 года. По Европе катится Весна народов. В берлинской тюрьме Моабит сидит Людвик Мерославский — его приговорили к смерти за подготовку восстания 1846 года. В Познани поляки создают Национальный комитет и ждут, что прусский король даст им самоуправление.",
    "20 марта 1848 года берлинская толпа освободила польских узников, и Мерославского с товарищами провезли по Берлину в открытой коляске под крики «Да здравствует Польша!». В Великой Польше собрались отряды, куда шли и крестьяне-косиньеры. 11 апреля по Ярославецкому соглашению большую часть отрядов распустили в обмен на обещанную «национальную реорганизацию», но пруссаки обещание не сдержали. 30 апреля под Милославом повстанцы победили, а уже 9 мая капитулировали. В Великой Польше после этого начали бороться не оружием, а «органической работой»: школами, банками, кооперативами.",
    "Людвик Мерославский, «Рассказ о великопольской кампании 1848 г.»"))

# ================================================================ school_strike_1905
NEW_SCENES += [
    scene("revolution_1905_pl", "Революция 1905 года", ["sig_revolution_1905_pl"], 1, "🚩", "услышать о забастовках", "icon_ally",
          ["гимназист"], "bread_riots"),
    scene("school_strike_pl", "Школьная забастовка", ["sig_school_strike_pl"], 2, "📚", "отказаться учиться по-русски", "icon_plot",
          ["гимназист", "жандарм"], "eighth_class"),
    scene("polish_school_pl", "Польская школа", ["sig_polish_school_pl"], 2, "🏫", "учить по-польски", "icon_crown",
          ["учительница", "ученик"], "mothers_school_pl"),
    scene("back_to_desk_pl", "Вернуться за парту", ["sig_back_to_desk_pl"], 1, "🪑", "смириться", "icon_ally",
          ["гимназист"], "fourteen_classes"),
]
NEW_RULES += [
    rule("revolution_1905_pl_sig", "По империи идут забастовки — и в Варшаве встают даже школы",
         "sig_revolution_1905_pl",
         [actor("A", 0, tags=["gymnasist_pl"], notFlags=["obeys_pl"])],
         [setf("A", "inspired_pl")]),
    rule("back_to_desk_pl_sig", "Гимназист возвращается за парту и учит историю России по-русски",
         "sig_back_to_desk_pl",
         [actor("A", 0, tags=["gymnasist_pl"])],
         [setf("A", "obeys_pl")]),
    rule("school_strike_pl_sig", "Гимназисты бросают казённые школы с требованием: польский язык и польская школа",
         "sig_school_strike_pl",
         [actor("A", 0, tags=["gymnasist_pl"], flags=["inspired_pl"]), actor("B", 1, tags=["gendarme_pl"])],
         [setf("A", "striking_pl")]),
    rule("polish_school_pl_sig", "Власти уступают: открываются частные польские школы, и бастующие идут туда",
         "sig_polish_school_pl",
         [actor("A", 0, tags=["educator_pl"]), actor("B", 1, tags=["gymnasist_pl"], flags=["striking_pl"])],
         [setf("B", "polish_school_pl")]),
]
NEW_LEVELS.append(level(
    "school_strike_1905", 485, ACT6, "poland_tension", "school_strike_pl", 3,
    ["revolution_1905_pl", "school_strike_pl", "polish_school_pl", "back_to_desk_pl"],
    ["gymnasist_pl", "gendarme_ru", "dawidowa"],
    {"gendarme_ru": ["standing", "strong"]}, [],
    [flag("gymnasist_pl", "polish_school_pl")],
    [("revolution_1905_pl", ["gymnasist_pl"]), ("school_strike_pl", ["gymnasist_pl", "gendarme_ru"]),
     ("polish_school_pl", ["dawidowa", "gymnasist_pl"])],
    "fact"))
TEXTS.update(texts("school_strike_1905",
    "Школьная забастовка",
    "В революцию 1905 года варшавские гимназисты бросают русские школы — и добиваются польских",
    "Смирение здесь — проигрыш. Сначала нужен пример взрослых, потом смелость, потом новая школа.",
    "1905 год. Царство Польское. В гимназиях всё преподают по-русски, даже польский язык; за польское слово на перемене могут наказать. В январе в Петербурге стреляют в рабочих, и по всей империи начинаются забастовки.",
    "В январе–феврале 1905 года ученики гимназий Варшавы и других городов объявили бойкот казённой школы: они требовали польского языка обучения и польских учителей. Бойкот держался годами, тысячи учеников ушли из государственных школ. Власти уступили: разрешили частные школы с польским языком, и в 1905 году возникло общество «Польская школьная матица», открывшее сотни школ и читален. Многие бастовавшие гимназисты через десять лет ушли в легионы.",
    "Устав Польской школьной матицы (1905)"))

# ================================================================ kadrowka_1914
NEW_SCENES += [
    scene("oleandry_pl", "Олеандры", ["sig_oleandry_pl"], 2, "🎖️", "построить кадровую роту", "icon_ally",
          ["комендант", "стрелец"], "cadre_company_pl"),
    scene("border_posts_pl", "Пограничные столбы", ["sig_border_posts_pl"], 2, "🪓", "повалить столбы", "icon_crown",
          ["стрелец", "страж"], "customs_border_pl"),
    scene("kielce_pl", "Вход в Кельце", ["sig_kielce_pl"], 2, "🏘️", "войти в город", "icon_ally",
          ["стрелец", "горожанин"], "homage_square_pl"),
    bait("kielce_battle_pl", "Бой за Кельце", "v_battle", 2, "open_field_1831_pl", BATTLE),
]
NEW_RULES += [
    rule("oleandry_pl_sig", "В Кракове комендант строит первую кадровую роту стрелков",
         "sig_oleandry_pl",
         [actor("A", 0, tags=["pilsudski_pl"]), actor("B", 1, tags=["strzelec_pl"])],
         [setf("B", "cadre_pl")]),
    rule("border_posts_pl_sig", "Стрелки валят пограничные столбы трёх империй — граница разделов падает",
         "sig_border_posts_pl",
         [actor("A", 0, tags=["strzelec_pl"], flags=["cadre_pl"]), actor("B", 1, tags=["gendarme_pl"])],
         [setf("A", "crossed_pl"), setf("B", "away")]),
    rule("kielce_pl_sig", "Стрелки входят в Кельце — город встречает их закрытыми ставнями",
         "sig_kielce_pl",
         [actor("A", 0, tags=["strzelec_pl"], flags=["crossed_pl"]), actor("B", 1, tags=["merchant_pl"])],
         [setf("A", "in_kielce_pl")]),
]
NEW_LEVELS.append(level(
    "kadrowka_1914", 486, ACT6, "poland_battle", "border_posts_pl", 3,
    ["oleandry_pl", "border_posts_pl", "kielce_pl", "kielce_battle_pl"],
    ["pilsudski", "strzelec_pl", "gendarme_ru", "merchant_pl"],
    {"pilsudski": ["standing", "strong"], "gendarme_ru": ["standing"]}, [],
    [flag("strzelec_pl", "in_kielce_pl")],
    [("oleandry_pl", ["pilsudski", "strzelec_pl"]), ("border_posts_pl", ["strzelec_pl", "gendarme_ru"]),
     ("kielce_pl", ["strzelec_pl", "merchant_pl"])],
    "fact"))
TEXTS.update(texts("kadrowka_1914",
    "Первая кадровая",
    "В первые дни Великой войны стрелки Пилсудского валят пограничные столбы разделов и идут на Кельце",
    "Сначала роту надо построить. Город не обязательно брать боем — в него просто входят.",
    "Август 1914 года. Три державы-раздельщицы впервые воюют между собой: Австро-Венгрия и Германия против России. Поляки служат во всех трёх армиях. Юзеф Пилсудский в австрийском Кракове годами готовил стрелковые союзы и ждёт этого часа.",
    "6 августа 1914 года из краковских Олеандров вышла Первая кадровая рота — около 150 стрелков. У Михаловиц они повалили пограничные столбы между Австрией и Россией и пошли на север. 12 августа рота вошла в Кельце, но город встретил её холодно: жители боялись русской мести и не верили в успех. Из этих стрелков выросли Польские легионы, а песня «Мы, Первая бригада» стала одной из главных польских солдатских песен.",
    "Приказ Пилсудского от 6 августа 1914 г.; Вацлав Липиньский, «Борьба за независимость»"))

# ================================================================ act_1916
NEW_SCENES += [
    scene("act_5_nov_pl", "Акт 5 ноября", ["sig_act_5_nov_pl"], 1, "📜", "провозгласить королевство", "icon_crown",
          ["генерал-губернатор"], "palace_square"),
    scene("call_recruits_pl", "Набор добровольцев", ["sig_call_recruits_pl"], 2, "📯", "звать в армию", "icon_plot",
          ["генерал-губернатор", "комендант"], "barons_muster"),
    scene("state_council_pl", "Временный Государственный совет", ["sig_state_council_pl"], 2, "🏛️", "войти в совет", "icon_crown",
          ["генерал-губернатор", "комендант"], "council_b"),
    bait("pilsudski_resign_pl", "Подать в отставку", "v_flee", 1, "exile_road", ["кто уходит"]),
]
NEW_RULES += [
    rule("act_5_nov_pl_sig", "Два императора объявляют «самостоятельное» Королевство Польское — без короля и без границ",
         "sig_act_5_nov_pl",
         [actor("A", 0, tags=["gov_gen_pl"])],
         [setf("A", "kingdom_proclaimed_pl")]),
    rule("call_recruits_pl_sig", "Генерал зовёт добровольцев раньше, чем есть польское правительство, — приходят единицы",
         "sig_call_recruits_pl",
         [actor("A", 0, tags=["gov_gen_pl"], flags=["kingdom_proclaimed_pl"]), actor("B", 1, tags=["pilsudski_pl"])],
         [setf("A", "recruit_failed_pl")]),
    rule("state_council_pl_sig", "Создан Временный Государственный совет — Пилсудский берёт военный отдел",
         "sig_state_council_pl",
         [actor("A", 0, tags=["gov_gen_pl"], flags=["kingdom_proclaimed_pl", "recruit_failed_pl"]), actor("B", 1, tags=["pilsudski_pl"], notFlags=["away"])],
         [setf("B", "council_pl")]),
]
NEW_LEVELS.append(level(
    "act_1916", 488, ACT6, "poland_ceremony", "act_5_nov_pl", 3,
    ["act_5_nov_pl", "call_recruits_pl", "state_council_pl", "pilsudski_resign_pl"],
    ["beseler", "pilsudski", "regent_kakowski"],
    {"beseler": ["standing", "strong"], "pilsudski": ["standing", "strong"]}, [],
    [flag("pilsudski", "council_pl")],
    [("act_5_nov_pl", ["beseler"]), ("call_recruits_pl", ["beseler", "pilsudski"]), ("state_council_pl", ["beseler", "pilsudski"])],
    "simplification"))
TEXTS.update(texts("act_1916",
    "Акт 5 ноября",
    "Германия и Австрия провозглашают Королевство Польское, чтобы набрать солдат, — а Пилсудский требует сначала правительство",
    "Обещание без власти солдат не приведёт — но только провал заставит немцев уступить. Уходить пока рано.",
    "1916 год. Германские и австрийские войска заняли русскую часть Польши. Под Верденом и на Сомме гибнут сотни тысяч, и Берлину нужны новые солдаты. Генерал-губернатор Варшавы Ханс фон Безелер предлагает: пообещаем полякам государство, и они пойдут в армию.",
    "5 ноября 1916 года в Варшаве и Люблине огласили акт двух императоров о создании «самостоятельного Королевства Польского» — без короля, без правительства и без определённых границ. Через неделю призвали добровольцев, но пришли лишь единицы: поляки, по словам Пилсудского, не собирались давать солдат без собственного правительства. В январе 1917 года создали Временный Государственный совет, и Пилсудский возглавил его военную комиссию. Впервые со времён разделов о польском государстве заговорили державы — и уже не смогли взять слова назад.",
    "Акт 5 ноября 1916 г.; Анджей Гарлицкий, «Юзеф Пилсудский»"))

if __name__ == "__main__":
    P.NEW_CHARS, P.NEW_SCENES, P.NEW_RULES, P.NEW_LEVELS, P.TEXTS = NEW_CHARS, NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS
    P.CHAPTER_TEXTS = {}
    P.main()
