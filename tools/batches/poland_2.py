#!/usr/bin/env python3
"""Пачка 2 главы «Польша»: ещё две легенды и Пясты до 1370 года, 9 уровней.

Применение — тот же код, что у пачки 1 (poland_1.main), с подменёнными списками.
    python3 tools/batches/poland_2.py [repo_root]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poland_1 as P
from poland_1 import char, scene, actor, setf, remf, addr, rule, flag, nflag, level, texts, ACT1, ACT2

NEW_CHARS = [
    char("wanda", "Королевна Ванда", ["princess_pl"], "👸"),
    char("rytygier", "Князь Ритигер", ["german_prince_pl"], "⚔️"),
    char("syrenka", "Варшавская Сирена", ["mermaid_pl"], "🧜‍♀️"),
    char("wars_fisher", "Рыбак Варс", ["fisher_pl"], "🎣"),
    char("merchant_pl", "Богатый купец", ["merchant_pl"], "💰"),
    char("boleslaw2", "Болеслав Смелый", ["king_pl"], "👑"),
    char("stanislaw_bp", "Епископ Станислав", ["bishop_kr_pl"], "⛪"),
    char("magnate_pl", "Можновладец", ["magnate_pl"], "🏰"),
    char("wladyslaw_herman", "Владислав Герман", ["herman_pl"], "🛡️"),
    char("konrad_maz", "Конрад Мазовецкий", ["mazovia_pl"], "🛡️"),
    char("salza", "Магистр Герман фон Зальца", ["order_pl"], "✠"),
    char("henry_pious", "Генрих Благочестивый", ["silesia_pl"], "🛡️"),
    char("mongol_pl", "Монгольский нойон", ["mongol_pl"], "🏹"),
    char("trumpeter_pl", "Трубач с Мариацкой башни", ["trumpeter_pl"], "🎺"),
    char("kinga", "Княжна Кинга", ["princess_hu_pl"], "💍"),
    char("bela4", "Король Бела IV", ["king_hu_pl"], "👑"),
    char("miner_pl", "Рудокоп из Велички", ["miner_pl"], "⛏️"),
    char("lokietek", "Владислав Локетек", ["lokietek_pl"], "👑"),
    char("czech_knight", "Рыцарь Вацлава", ["czech_knight_pl"], "⚔️"),
    char("janislaw", "Архиепископ Янислав", ["archbishop_pl"], "⛪"),
    char("young_casimir", "Королевич Казимир", ["heir_pl"], "🗡️"),
    char("komtur", "Комтур ордена", ["order_pl"], "✠"),
    char("casimir3", "Казимир Великий", ["casimir_great_pl"], "🏛️"),
    char("charles4_hre", "Император Карл IV", ["guest_king_pl"], "👑"),
    char("louis_hu", "Людовик Венгерский", ["guest_king_pl"], "👑"),
    char("wierzynek", "Купец Вежинек", ["host_pl"], "🍷"),
]

NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS = [], [], [], {}

# ================================================================ wanda (легенда)
NEW_SCENES += [
    scene("wanda_refusal_pl", "Сватовство Ритигера", ["sig_wanda_refusal_pl"], 2, "💔", "отказать жениху", "icon_plot",
          ["жених", "королевна"], "court_refuse"),
    scene("wanda_armies_pl", "Войска сошлись", ["sig_wanda_armies_pl"], 2, "🛡️", "выйти к войску", "icon_crown",
          ["королевна", "враг"], "line_of_battle_a"),
    scene("rytygier_sword_pl", "Меч на себя", ["sig_rytygier_sword_pl"], 1, "🗡️", "броситься на меч", "icon_dead",
          ["князь"], "death_in_line"),
    scene("wanda_wedding_pl", "Свадьба", ["v_wed"], 2, "💍", "свадьба", "icon_ally",
          ["жених", "невеста"], "louvre_wedding"),
    scene("wanda_battle_pl", "Битва", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "battlefield"),
]
NEW_RULES += [
    rule("wanda_refusal_pl_sig", "Немецкий князь сватается к королевне — она отказывает: «Не за немца»",
         "sig_wanda_refusal_pl",
         [actor("A", 0, tags=["german_prince_pl"]),
          actor("B", 1, tags=["princess_pl"], notFlags=["married"])],
         [setf("B", "refused_pl"), setf("A", "rejected_pl")]),
    rule("wanda_armies_pl_sig", "Королевна выходит к войскам — и воины отвергнутого жениха, увидев её, отказываются поднять на неё оружие",
         "sig_wanda_armies_pl",
         [actor("A", 0, tags=["princess_pl"], flags=["refused_pl"], notFlags=["defeated", "married"]),
          actor("B", 1, tags=["german_prince_pl"], flags=["rejected_pl"])],
         [setf("B", "deserted_pl"), remf("B", "strong")]),
    rule("rytygier_sword_pl_sig", "Покинутый своим войском князь бросается на собственный меч",
         "sig_rytygier_sword_pl",
         [actor("A", 0, tags=["german_prince_pl"], flags=["deserted_pl"])],
         [setf("A", "dead")]),
]
NEW_LEVELS.append(level(
    "wanda", 13, ACT1, "poland_romance", "wanda_armies_pl", 3,
    ["wanda_refusal_pl", "wanda_armies_pl", "rytygier_sword_pl", "wanda_wedding_pl", "wanda_battle_pl"],
    ["wanda", "rytygier"],
    {"wanda": ["reigns", "standing"], "rytygier": ["strong", "standing"]},
    [("enemy_of", "rytygier", "wanda"), ("enemy_of", "wanda", "rytygier")],
    [flag("rytygier", "dead"), nflag("wanda", "married"), nflag("wanda", "defeated")],
    [("wanda_refusal_pl", ["rytygier", "wanda"]), ("wanda_armies_pl", ["wanda", "rytygier"]),
     ("rytygier_sword_pl", ["rytygier"])],
    "legend"))
TEXTS.update(texts("wanda",
    "Ванда, что не хотела немца",
    "Королевна отказывает чужеземному жениху и выходит к его войску — и войско отказывается с ней сражаться",
    "Свадьба — это не про Ванду, а в поле её армия слабее. Её оружие — она сама: сначала отказ, потом выйти к чужому войску лицом к лицу.",
    "После смерти основателя Кракова, князя Крака, на престол села его дочь Ванда — такая красивая и мудрая, что слава о ней дошла до немецких земель. Князь алеманнов Ритигер прислал сватов. А когда получил отказ — привёл войско.",
    "Легенду о Ванде записал около 1200 года Винцентий Кадлубек: воины Ритигера, увидев королевну, «будто поражённые лучом солнца», отказались биться, и князь в отчаянии пронзил себя мечом. Через три столетия Ян Длугош переписал конец: Ванда, чтобы не выходить за чужеземца, сама бросилась в Вислу — эта версия и стала самой известной. Её именем назван курган Ванды на окраине Кракова, насыпанный, вероятно, ещё в VII–VIII веках; на его вершине стоит памятник с белым орлом работы Яна Матейко.",
    "Винцентий Кадлубек, «Хроника», I, 7; Ян Длугош, «Анналы», I"))

# ================================================================ warsaw_mermaid (легенда)
NEW_SCENES += [
    scene("merchant_net_pl", "Сети купца", ["sig_merchant_net_pl"], 2, "🕸️", "поймать сирену", "icon_plot",
          ["купец", "сирена"], "pirate_crosses"),
    scene("night_rescue_pl", "Ночью у сарая", ["sig_night_rescue_pl"], 2, "🌙", "освободить пленницу", "icon_ally",
          ["рыбак", "пленница"], "wall_passage"),
    scene("mermaid_oath_pl", "Клятва сирены", ["sig_mermaid_oath_pl"], 2, "🛡️", "поклясться защищать", "icon_crown",
          ["сирена", "рыбак"], "black_river"),
    scene("merchant_deal_pl", "Сделка с купцом", ["v_bribe"], 2, "💰", "подкуп", "icon_ally",
          ["кто платит", "кто берёт"], "bank_loan"),
]
NEW_RULES += [
    rule("merchant_net_pl_sig", "Купец слышит, как поёт сирена, и ловит её в сети — показывать на ярмарках за деньги",
         "sig_merchant_net_pl",
         [actor("A", 0, tags=["merchant_pl"]),
          actor("B", 1, tags=["mermaid_pl"], notFlags=["freed_pl", "captured_pl"])],
         [setf("B", "captured_pl")]),
    rule("night_rescue_pl_sig", "Рыбак, не взявший купеческих денег, ночью освобождает сирену и отпускает в Вислу",
         "sig_night_rescue_pl",
         [actor("A", 0, tags=["fisher_pl"], notFlags=["bought"]),
          actor("B", 1, tags=["mermaid_pl"], flags=["captured_pl"])],
         [setf("B", "freed_pl"), remf("B", "captured_pl"), addr("ally_of", "B", "A")]),
    rule("mermaid_oath_pl_sig", "Освобождённая сирена берёт меч и щит и клянётся защищать рыбацкий посёлок — будущую Варшаву",
         "sig_mermaid_oath_pl",
         [actor("A", 0, tags=["mermaid_pl"], flags=["freed_pl"]),
          actor("B", 1, tags=["fisher_pl"])],
         [setf("A", "protector_pl"), setf("A", "standing")]),
]
NEW_LEVELS.append(level(
    "warsaw_mermaid", 16, ACT1, "poland_romance", "mermaid_oath_pl", 3,
    ["merchant_net_pl", "night_rescue_pl", "mermaid_oath_pl", "merchant_deal_pl"],
    ["syrenka", "wars_fisher", "merchant_pl"],
    {}, [],
    [flag("syrenka", "protector_pl"), nflag("wars_fisher", "bought")],
    [("merchant_net_pl", ["merchant_pl", "syrenka"]), ("night_rescue_pl", ["wars_fisher", "syrenka"]),
     ("mermaid_oath_pl", ["syrenka", "wars_fisher"])],
    "legend"))
TEXTS.update(texts("warsaw_mermaid",
    "Варшавская Сирена",
    "Жадный купец ловит сирену, бедный рыбак её освобождает — и сирена с мечом встаёт на защиту города",
    "Чтобы сирену спасти, её сначала должны поймать. Освободит её только тот, кто не взял денег. А клятву она даёт своему спасителю.",
    "На берегу Вислы стоит маленький рыбацкий посёлок. По ночам рыбаки слышат над рекой чудесное пение — и видят, как кто-то рвёт им сети. Однажды песню слышит и проезжий богатый купец.",
    "По варшавскому преданию, сирена приплыла в Вислу из Балтики — её сестра осталась у Копенгагена, где теперь сидит на камне Русалочка. Сирена с мечом и щитом появилась на гербе Варшавы ещё в XIV–XV веках, но поначалу была похожа скорее на крылатое чудовище с птичьими ногами; женщиной с рыбьим хвостом она стала лишь к XVII веку. Сама сказка о купце и рыбаке сложилась поздно, в XIX веке, а бронзовая Сирена Константы Хегеля стоит на Рынке Старого города с 1855 года.",
    "Варшавские городские предания; Артур Оппман (Ор-От), «Варшавские легенды» (1925)"))

# ================================================================ stanislaus_1079
NEW_SCENES += [
    scene("skalka_pl", "Костёл на Скалке", ["sig_skalka_pl"], 2, "⛪", "покарать епископа", "icon_dead",
          ["король", "епископ"], "church_door_t"),
    scene("magnates_revolt_pl", "Бунт можновладцев", ["sig_magnates_revolt_pl"], 2, "🔥", "изгнать короля", "icon_plot",
          ["можновладец", "король"], "court_depose"),
    scene("herman_power_pl", "Власть — брату", ["sig_herman_power_pl"], 2, "🛡️", "посадить на стол", "icon_crown",
          ["можновладец", "брат короля"], "throne"),
    scene("bishop_peace_pl", "Примирение с епископом", ["v_parley"], 2, "🤝", "переговоры", "icon_ally",
          ["кто требует", "кто уступает"], "council"),
    scene("crush_revolt_pl", "Подавить бунт", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "battlefield"),
]
NEW_RULES += [
    rule("skalka_pl_sig", "Король обвиняет епископа в измене и велит казнить — по преданию, рубит его сам, у алтаря на Скалке",
         "sig_skalka_pl",
         [actor("A", 0, tags=["king_pl"], notFlags=["exiled_pl"]),
          actor("B", 1, tags=["bishop_kr_pl"], notFlags=["conceded"])],
         [setf("B", "dead"), setf("B", "martyr_pl"), setf("A", "bishop_slayer_pl")]),
    rule("magnates_revolt_pl_sig", "Убийство епископа поднимает знать — король бежит в Венгрию",
         "sig_magnates_revolt_pl",
         [actor("A", 0, tags=["magnate_pl"], notFlags=["defeated"]),
          actor("B", 1, tags=["king_pl"], flags=["bishop_slayer_pl"])],
         [setf("B", "exiled_pl"), setf("B", "away"), remf("B", "reigns"), setf("A", "rebel_pl")]),
    rule("herman_power_pl_sig", "Знать сажает на престол младшего брата — без короны, князем",
         "sig_herman_power_pl",
         [actor("A", 0, tags=["magnate_pl"], flags=["rebel_pl"]),
          actor("B", 1, tags=["herman_pl"])],
         [setf("B", "reigns"), setf("B", "standing")]),
]
NEW_LEVELS.append(level(
    "stanislaus_1079", 65, ACT2, "poland_tension", "skalka_pl", 3,
    ["skalka_pl", "magnates_revolt_pl", "herman_power_pl", "bishop_peace_pl", "crush_revolt_pl"],
    ["boleslaw2", "stanislaw_bp", "magnate_pl", "wladyslaw_herman"],
    {"boleslaw2": ["crowned", "reigns", "standing", "strong"], "stanislaw_bp": ["standing"], "magnate_pl": ["standing"]},
    [("enemy_of", "boleslaw2", "magnate_pl"), ("enemy_of", "magnate_pl", "boleslaw2")],
    [flag("stanislaw_bp", "martyr_pl"), flag("boleslaw2", "exiled_pl"), flag("wladyslaw_herman", "reigns")],
    [("skalka_pl", ["boleslaw2", "stanislaw_bp"]), ("magnates_revolt_pl", ["magnate_pl", "boleslaw2"]),
     ("herman_power_pl", ["magnate_pl", "wladyslaw_herman"])],
    "simplification"))
TEXTS.update(texts("stanislaus_1079",
    "Епископ на Скалке",
    "Король казнит епископа — и убитый епископ свергает короля: знать изгоняет его и сажает на престол брата",
    "Мириться король не станет — тогда не было бы ни мученика, ни бунта. Бунт не подавить: короля свергают не мечом, а тем, что он сделал. И брата сажают на трон не сами братья.",
    "1079 год. Болеслав Смелый — король, воевавший от Киева до Праги, — правит жёстко. Краковский епископ Станислав выступает против него, и король обвиняет его в измене. Знать затаила обиду: король слишком самовластен.",
    "Епископ Станислав был казнён 11 апреля 1079 года по приговору короля — Галл Аноним называет его «изменником», не объясняя, в чём была измена. По позднему житию, король сам зарубил епископа у алтаря костёла на Скалке и велел разрубить тело на части. Убийство подняло знать: Болеслав бежал в Венгрию и умер в изгнании около 1081 года, а правил его брат Владислав Герман — уже князем, без короны. В 1253 году Станислава канонизировали, и по легенде разрубленное тело чудесно срослось — это стали считать знаком того, что и раздробленная Польша снова станет единой. Он — покровитель Польши, а к его гробнице в Вавеле короли совершали покаянное паломничество перед коронацией.",
    "Галл Аноним, I, 27; Винцентий из Кельчи, «Житие святого Станислава» (XIII в.)"))

# ================================================================ teutonic_call (1226)
NEW_SCENES += [
    scene("prussian_raids_pl", "Набеги на Мазовию", ["sig_prussian_raids_pl"], 2, "🔥", "грабить пограничье", "icon_dead",
          ["язычник", "князь"], "burnt_fields"),
    scene("call_order_pl", "Хелминская земля — ордену", ["sig_call_order_pl"], 2, "📜", "позвать рыцарей", "icon_ally",
          ["князь", "магистр"], "papal_legate"),
    scene("order_crusade_pl", "Крестовый поход на пруссов", ["sig_order_crusade_pl"], 2, "✠", "покорить язычников", "icon_crown",
          ["рыцарь", "язычник"], "forest_ambush"),
    scene("konrad_alone_pl", "Идти самому", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "open_battle"),
]
NEW_RULES += [
    rule("prussian_raids_pl_sig", "Пруссы раз за разом жгут мазовецкое пограничье — князь не может его удержать",
         "sig_prussian_raids_pl",
         [actor("A", 0, tags=["prussian_pl"], flags=["strong"]),
          actor("B", 1, tags=["mazovia_pl"], notFlags=["raided_pl"])],
         [setf("B", "raided_pl")]),
    rule("call_order_pl_sig", "Разорённый князь зовёт немецких рыцарей и даёт им Хелминскую землю на войну с пруссами",
         "sig_call_order_pl",
         [actor("A", 0, tags=["mazovia_pl"], flags=["raided_pl"], notFlags=["defeated"]),
          actor("B", 1, tags=["order_pl"])],
         [setf("B", "order_land_pl"), addr("ally_of", "A", "B"), addr("ally_of", "B", "A")]),
    rule("order_crusade_pl_sig", "За полвека орден покоряет пруссов — и строит на их земле своё государство",
         "sig_order_crusade_pl",
         [actor("A", 0, tags=["order_pl"], flags=["order_land_pl"]),
          actor("B", 1, tags=["prussian_pl"])],
         [setf("B", "defeated"), setf("A", "order_state_pl"), setf("A", "strong")]),
]
NEW_LEVELS.append(level(
    "teutonic_call", 90, ACT2, "poland_tension", "call_order_pl", 3,
    ["prussian_raids_pl", "call_order_pl", "order_crusade_pl", "konrad_alone_pl"],
    ["konrad_maz", "salza", "prussian_pl"],
    {"konrad_maz": ["reigns", "standing"], "salza": ["standing"], "prussian_pl": ["strong", "standing"]},
    [("enemy_of", "konrad_maz", "prussian_pl"), ("enemy_of", "prussian_pl", "konrad_maz"),
     ("enemy_of", "salza", "prussian_pl"), ("enemy_of", "prussian_pl", "salza")],
    [flag("prussian_pl", "defeated"), flag("salza", "order_state_pl"), nflag("konrad_maz", "defeated")],
    [("prussian_raids_pl", ["prussian_pl", "konrad_maz"]), ("call_order_pl", ["konrad_maz", "salza"]),
     ("order_crusade_pl", ["salza", "prussian_pl"])],
    "simplification"))
TEXTS.update(texts("teutonic_call",
    "Позвать орден",
    "Князь, не справляясь с набегами пруссов, зовёт немецких рыцарей — и они, покорив пруссов, строят на их земле своё государство",
    "Сам князь пруссов не одолеет. Рыцари приходят не даром — им нужна земля, а землю дают тому, кто разорён набегами.",
    "XIII век. Польша раздроблена на уделы. Мазовецкий князь Конрад год за годом отбивается от язычников-пруссов, жгущих его пограничье, — и проигрывает. Свой рыцарский орден, Добжинских братьев, он уже основал, но тот не справился. На юге, в Венгрии, только что остался без земли другой орден — немецкий, Тевтонский.",
    "В 1226 году Конрад Мазовецкий пригласил Тевтонский орден и отдал ему Хелминскую землю. Магистр Герман фон Зальца, искусный дипломат, в том же году получил от императора Фридриха II Золотую буллу из Римини, признававшую за орденом все будущие завоевания в Пруссии, — Конрад об этом, вероятно, не знал. Рыцари пришли в 1230 году и за полвека, к 1283-му, покорили пруссов, построив на их земле собственное государство с замками от Торуни до Кёнигсберга. Двести лет оно будет главным врагом Польши — до Грюнвальда и Тринадцатилетней войны, — а в 1525 году превратится в герцогство Пруссию, из которого вырастет Прусское королевство.",
    "Золотая булла из Римини (1226); Пётр из Дусбурга, «Хроника земли Прусской»"))

# ================================================================ legnica_1241
NEW_SCENES += [
    scene("mongol_feint_pl", "Ложное бегство", ["sig_mongol_feint_pl"], 2, "🏇", "притворно бежать", "icon_plot",
          ["отступающий", "преследователь"], "feign_flight_h"),
    scene("legnica_field_pl", "Поле под Легницей", ["sig_legnica_field_pl"], 2, "⚔️", "окружить", "icon_dead",
          ["нападающий", "рыцарь"], "kleidion_battle"),
    scene("hejnal_tower_pl", "Мариацкая башня", ["sig_hejnal_tower_pl"], 2, "🎺", "трубить тревогу", "icon_dead",
          ["трубач", "враг"], "two_sisters_tower"),
    scene("legnica_front_pl", "Лобовой удар", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "open_battle"),
]
NEW_RULES += [
    rule("mongol_feint_pl_sig", "Монголы будто бы бегут — рыцарская конница бросается в погоню и ломает строй",
         "sig_mongol_feint_pl",
         [actor("A", 0, tags=["mongol_pl"]),
          actor("B", 1, tags=["silesia_pl"], flags=["strong"])],
         [setf("B", "pursuing_pl"), remf("B", "strong")]),
    rule("legnica_field_pl_sig", "Растянутых рыцарей окружают и расстреливают из луков; князь гибнет",
         "sig_legnica_field_pl",
         [actor("A", 0, tags=["mongol_pl"]),
          actor("B", 1, tags=["silesia_pl"], flags=["pursuing_pl"])],
         [setf("B", "dead"), setf("A", "victor")]),
    rule("hejnal_tower_pl_sig", "Трубач с башни видит врага и трубит тревогу — стрела обрывает мелодию, но город успевает закрыть ворота",
         "sig_hejnal_tower_pl",
         [actor("A", 0, tags=["trumpeter_pl"]),
          actor("B", 1, tags=["mongol_pl"])],
         [setf("A", "dead"), setf("A", "hejnal_pl")]),
]
NEW_LEVELS.append(level(
    "legnica_1241", 100, ACT2, "poland_battle", "hejnal_tower_pl", 3,
    ["mongol_feint_pl", "legnica_field_pl", "hejnal_tower_pl", "legnica_front_pl"],
    ["henry_pious", "mongol_pl", "trumpeter_pl"],
    {"henry_pious": ["reigns", "standing", "strong"], "mongol_pl": ["strong", "standing"]},
    [("enemy_of", "henry_pious", "mongol_pl"), ("enemy_of", "mongol_pl", "henry_pious")],
    [flag("henry_pious", "dead"), flag("trumpeter_pl", "hejnal_pl")],
    [("mongol_feint_pl", ["mongol_pl", "henry_pious"]), ("legnica_field_pl", ["mongol_pl", "henry_pious"]),
     ("hejnal_tower_pl", ["trumpeter_pl", "mongol_pl"])],
    "simplification"))
TEXTS.update(texts("legnica_1241",
    "Легница и хейнал",
    "Монголы притворным бегством ломают строй рыцарей и убивают князя, а трубач на башне Кракова трубит тревогу, пока стрела не обрывает мелодию",
    "В лоб рыцарей не взять — они сильны, пока держат строй. Пусть строй сломает погоня. А тревогу трубят, глядя врагу в лицо.",
    "1241 год. Монгольское войско Батыя идёт на Венгрию, а один из его отрядов, под началом Байдара и Орды, проходит Польшу: сожжён Сандомир, сожжён Краков. Под Легницей монголов ждёт силезский князь Генрих Благочестивый — с польскими рыцарями, немецкими добровольцами и братьями рыцарских орденов.",
    "9 апреля 1241 года под Легницей монголы, по Длугошу, притворным бегством и дымовой завесой разорвали рыцарский строй и перебили его стрелами; Генрих Благочестивый погиб, его голову на копье пронесли под стенами Легницы. Хейнал — сигнал с башни Мариацкого костёла в Кракове — звучит каждый час и обрывается на полуноте; по преданию, так стрела оборвала трубача, заметившего врага. Легенду широко разнёс американец Эрик Келли в книге «Трубач из Кракова» (1928), а с 1927 года хейнал в полдень передаёт Польское радио.",
    "Ян Длугош, «Анналы», VII; «Силезская хроника»; Э. Келли, «Трубач из Кракова» (1928)"))

# ================================================================ kinga_salt (легенда)
NEW_SCENES += [
    scene("dowry_salt_pl", "Приданое — соль", ["sig_dowry_salt_pl"], 2, "🧂", "попросить соли", "icon_ally",
          ["отец", "дочь"], "court_present"),
    scene("dowry_gold_pl", "Приданое — золото", ["sig_dowry_gold_pl"], 2, "🪙", "взять золото", "icon_ally",
          ["отец", "дочь"], "gold_scales"),
    scene("ring_mine_pl", "Перстень в шахту", ["sig_ring_mine_pl"], 1, "💍", "бросить перстень", "icon_plot",
          ["княжна"], "cellar_search"),
    scene("wieliczka_pl", "Шахта в Величке", ["sig_wieliczka_pl"], 2, "⛏️", "копать", "icon_crown",
          ["рудокоп", "княгиня"], "tower_cell"),
]
NEW_RULES += [
    rule("dowry_salt_pl_sig", "Королевна просит у отца в приданое не золото, а соль — то, чего нет в её новой земле",
         "sig_dowry_salt_pl",
         [actor("A", 0, tags=["king_hu_pl"]),
          actor("B", 1, tags=["princess_hu_pl"], notFlags=["dowry_salt_pl", "dowry_gold_pl"])],
         [setf("B", "dowry_salt_pl")]),
    rule("dowry_gold_pl_sig", "Королевна берёт в приданое золото — как все",
         "sig_dowry_gold_pl",
         [actor("A", 0, tags=["king_hu_pl"]),
          actor("B", 1, tags=["princess_hu_pl"], notFlags=["dowry_salt_pl", "dowry_gold_pl"])],
         [setf("B", "dowry_gold_pl")]),
    rule("ring_mine_pl_sig", "В венгерской соляной шахте королевна бросает в ствол свой обручальный перстень",
         "sig_ring_mine_pl",
         [actor("A", 0, tags=["princess_hu_pl"], flags=["dowry_salt_pl"], notFlags=["ring_thrown_pl"])],
         [setf("A", "ring_thrown_pl")]),
    rule("wieliczka_pl_sig", "В Польше она велит копать в Величке — и в первой глыбе соли рудокопы находят её перстень",
         "sig_wieliczka_pl",
         [actor("A", 0, tags=["miner_pl"]),
          actor("B", 1, tags=["princess_hu_pl"], flags=["ring_thrown_pl"])],
         [setf("A", "found_salt_pl"), setf("B", "salt_queen_pl")]),
]
NEW_LEVELS.append(level(
    "kinga_salt", 105, ACT2, "poland_romance", "wieliczka_pl", 3,
    ["dowry_salt_pl", "dowry_gold_pl", "ring_mine_pl", "wieliczka_pl"],
    ["kinga", "bela4", "miner_pl"],
    {"bela4": ["crowned", "reigns", "standing"]}, [],
    [flag("miner_pl", "found_salt_pl"), nflag("kinga", "dowry_gold_pl")],
    [("dowry_salt_pl", ["bela4", "kinga"]), ("ring_mine_pl", ["kinga"]), ("wieliczka_pl", ["miner_pl", "kinga"])],
    "legend"))
TEXTS.update(texts("kinga_salt",
    "Перстень святой Кинги",
    "Королевна просит в приданое соль, бросает перстень в венгерскую шахту — и его находят в первой глыбе соли в Величке",
    "Золото есть у всех — Польше нужно другое. Перстень бросают там, откуда хотят забрать соль. А найдут его те, кто копает.",
    "1246 год. Венгерская королевна Кинга, дочь Белы IV, едет в Краков — женой князя Болеслава Стыдливого. Отец спрашивает, что дать ей в приданое. Венгрия богата солью, а в Малой Польше соль — дорогой привозной товар.",
    "По житию, Кинга попросила у отца в приданое соль и бросила свой перстень в соляную шахту Марамуреша, а в Польше велела рыть под Величкой — в первой же глыбе соли рудокопы нашли её перстень. На деле соль из рассолов под Величкой добывали задолго до неё, но шахты начали бить именно в XIII веке, и копи стали опорой королевской казны: в XIV веке они давали до трети её доходов. Кинга — покровительница горняков, канонизирована в 1999 году; на глубине 101 метра в Величке есть её часовня, целиком вырезанная из соли за 1896–1963 годы.",
    "Житие блаженной Кинги (XIV в.); Ян Длугош, «Анналы»"))

# ================================================================ lokietek_cave (1300–1320)
NEW_SCENES += [
    scene("ojcow_cave_pl", "Пещера у Ойцова", ["sig_ojcow_cave_pl"], 2, "🕷️", "спрятаться", "icon_ally",
          ["беглец", "погоня"], "cellar_search"),
    scene("lokietek_muster_pl", "Собрать сторонников", ["v_prepare"], 1, "🛡️", "подготовка", "icon_ally",
          ["кто вооружается"], "barons_muster"),
    scene("wawel_1320_pl", "Коронация на Вавеле", ["sig_wawel_1320_pl"], 2, "👑", "короновать", "icon_crown",
          ["князь", "архиепископ"], "coronation_b"),
    scene("lokietek_fight_pl", "Бой с погоней", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "forest_ambush"),
]
NEW_RULES += [
    rule("ojcow_cave_pl_sig", "Беглый князь прячется в пещере; паук затягивает вход паутиной, и погоня проходит мимо",
         "sig_ojcow_cave_pl",
         [actor("A", 0, tags=["lokietek_pl"], flags=["hunted_pl"]),
          actor("B", 1, tags=["czech_knight_pl"])],
         [setf("A", "survived_pl"), remf("A", "hunted_pl")]),
    rule("wawel_1320_pl_sig", "Объединивший земли князь коронуется в Краковском соборе — первым из польских королей на Вавеле",
         "sig_wawel_1320_pl",
         [actor("A", 0, tags=["lokietek_pl"], flags=["survived_pl", "strong"], notFlags=["defeated"]),
          actor("B", 1, tags=["archbishop_pl"])],
         [setf("A", "crowned_1320"), setf("A", "crowned"), setf("A", "reigns")]),
]
NEW_LEVELS.append(level(
    "lokietek_cave", 110, ACT2, "poland_ceremony", "wawel_1320_pl", 3,
    ["ojcow_cave_pl", "lokietek_muster_pl", "wawel_1320_pl", "lokietek_fight_pl"],
    ["lokietek", "czech_knight", "janislaw"],
    {"lokietek": ["hunted_pl"], "czech_knight": ["strong", "standing"], "janislaw": ["standing"]},
    [("enemy_of", "lokietek", "czech_knight"), ("enemy_of", "czech_knight", "lokietek")],
    [flag("lokietek", "crowned_1320")],
    [("ojcow_cave_pl", ["lokietek", "czech_knight"]), ("lokietek_muster_pl", ["lokietek"]),
     ("wawel_1320_pl", ["lokietek", "janislaw"])],
    "simplification"))
TEXTS.update(texts("lokietek_cave",
    "Локетек в пещере",
    "Маленький князь прячется от погони в пещере, собирает сторонников — и коронуется в Кракове, вновь собрав Польшу",
    "С погоней один на один не биться — сначала выжить. Корону не дают беглецу: нужны и силы, и тот, кто её возложит.",
    "Начало XIV века. Чешский король Вацлав II стал и польским королём, а куявский князь Владислав, прозванный Локетком за малый рост — «ростом с локоть», — изгнан. По Малой Польше за ним рыщут чешские отряды.",
    "Владислав Локетек провёл в изгнании 1300–1304 годы; по местному преданию, он укрывался в пещере у Ойцова, и паук затянул вход паутиной так, что погоня решила: внутри никого нет, — теперь это «Пещера Локетка». Вернувшись с венгерской помощью, он двадцать лет собирал земли и 20 января 1320 года был коронован в Краковском соборе архиепископом Яниславом — впервые не в Гнезно, а на Вавеле, где с тех пор короновались почти все короли Польши. Это конец раздробленности, начавшейся с завещания Кривоустого.",
    "Ян Длугош, «Анналы», IX; «Великопольская хроника»"))

# ================================================================ plowce_1331
NEW_SCENES += [
    scene("order_split_pl", "Орден делит войско", ["sig_order_split_pl"], 2, "🔭", "выследить врага", "icon_plot",
          ["разведчик", "враг"], "gifford_intercept"),
    scene("plowce_strike_pl", "Удар у Пловцев", ["sig_plowce_strike_pl"], 2, "⚔️", "ударить по отряду", "icon_dead",
          ["король", "враг"], "open_battle_s"),
    scene("heir_charge_pl", "Королевич — в бой", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "battlefield"),
]
NEW_RULES += [
    rule("order_split_pl_sig", "Разъезд видит: орден разделил войско на колонны, и одна отстала",
         "sig_order_split_pl",
         [actor("A", 0, tags=["lokietek_pl"]),
          actor("B", 1, tags=["order_pl"], flags=["strong"])],
         [setf("B", "split_pl"), remf("B", "strong")]),
    rule("order_split_heir_pl", "Разведку ведёт сам королевич — и видит отставшую колонну",
         "sig_order_split_pl",
         [actor("A", 0, tags=["heir_pl"]),
          actor("B", 1, tags=["order_pl"], flags=["strong"])],
         [setf("B", "split_pl"), remf("B", "strong")]),
    rule("plowce_strike_pl_sig", "Король бьёт отставшую колонну раньше, чем подойдут остальные",
         "sig_plowce_strike_pl",
         [actor("A", 0, tags=["lokietek_pl"], flags=["crowned"]),
          actor("B", 1, tags=["order_pl"], flags=["split_pl"])],
         [setf("B", "defeated"), setf("A", "victor")]),
]
NEW_LEVELS.append(level(
    "plowce_1331", 120, ACT2, "poland_battle", "plowce_strike_pl", 2,
    ["order_split_pl", "plowce_strike_pl", "heir_charge_pl"],
    ["lokietek", "young_casimir", "komtur"],
    {"lokietek": ["crowned", "reigns", "standing"], "young_casimir": ["standing"], "komtur": ["strong", "standing"]},
    [("enemy_of", "lokietek", "komtur"), ("enemy_of", "komtur", "lokietek"),
     ("enemy_of", "young_casimir", "komtur"), ("enemy_of", "komtur", "young_casimir")],
    [flag("komtur", "defeated"), nflag("young_casimir", "defeated")],
    [("order_split_pl", ["lokietek", "komtur"]), ("plowce_strike_pl", ["lokietek", "komtur"])],
    "simplification"))
TEXTS.update(texts("plowce_1331",
    "Пловцы",
    "Старый король бьёт отставшую колонну рыцарей ордена, а наследника уводят с поля",
    "Орден силён, пока идёт одним войском. Сначала найдите, где оно разделилось. Наследника в рубку не пускать — ему ещё править.",
    "1331 год. Тевтонский орден, захвативший Гданьское Поморье, огнём идёт по Куявии. Королю Владиславу Локетку за семьдесят, его сын Казимир — единственный наследник. Войско ордена больше польского.",
    "27 сентября 1331 года под Пловцами Локетек напал на отставший в тумане отряд ордена и разбил его; когда подошли главные силы, бой стал ничейным, но для Польши это была первая полевая победа над крестоносцами. Королевича Казимира, по хронистам, перед битвой отослали с поля, чтобы не рисковать наследником. С Пловцами связана легенда о рыцаре Флориане Шаром: король увидел его с тремя копьями в теле, придерживающего выпавшие внутренности, — и будто бы отсюда пошёл герб Елита с тремя копьями.",
    "Ян Длугош, «Анналы», IX; Виганд Марбургский, «Хроника»"))

# ================================================================ wierzynek_1364
NEW_SCENES += [
    scene("krakow_academy_pl", "Краковская академия", ["sig_krakow_academy_pl"], 1, "🎓", "основать университет", "icon_crown",
          ["король"], "academy_chancery"),
    scene("wierzynek_feast_pl", "Пир у Вежинка", ["sig_wierzynek_feast_pl"], 2, "🍷", "дать пир", "icon_crown",
          ["хозяин", "король"], "feast_pd"),
    scene("krakow_congress_pl", "Краковский съезд", ["sig_krakow_congress_pl"], 3, "🤝", "помирить королей", "icon_ally",
          ["посредник", "гость", "гость"], "council_b"),
    scene("silesia_quarrel_pl", "Спор за Силезию", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "open_battle"),
]
NEW_RULES += [
    rule("krakow_academy_pl_sig", "Король основывает в Кракове университет — второй в Центральной Европе после Праги",
         "sig_krakow_academy_pl",
         [actor("A", 0, tags=["casimir_great_pl"], notFlags=["university_pl", "feast_given_pl"])],
         [setf("A", "university_pl")]),
    rule("wierzynek_feast_pl_sig", "Краковский купец Вежинек даёт пир, на котором король угощает монархов Европы",
         "sig_wierzynek_feast_pl",
         [actor("A", 0, tags=["host_pl"]),
          actor("B", 1, tags=["casimir_great_pl"])],
         [setf("B", "feast_given_pl"), setf("B", "standing")]),
    rule("krakow_congress_pl_sig", "За столом король мирит императора с венгерским королём",
         "sig_krakow_congress_pl",
         [actor("A", 0, tags=["casimir_great_pl"], flags=["feast_given_pl"]),
          actor("B", 1, tags=["guest_king_pl"], notFlags=["at_war"]),
          actor("C", 2, tags=["guest_king_pl"], notFlags=["at_war"])],
         [{"type": "removeRelation", "rel": "enemy_of", "from": "B", "to": "C"},
          {"type": "removeRelation", "rel": "enemy_of", "from": "C", "to": "B"},
          setf("B", "reconciled_pl"), setf("C", "reconciled_pl"),
          addr("ally_of", "B", "C"), addr("ally_of", "C", "B")]),
]
NEW_LEVELS.append(level(
    "wierzynek_1364", 130, ACT2, "poland_ceremony", "wierzynek_feast_pl", 3,
    ["krakow_academy_pl", "wierzynek_feast_pl", "krakow_congress_pl", "silesia_quarrel_pl"],
    ["casimir3", "charles4_hre", "louis_hu", "wierzynek"],
    {"casimir3": ["crowned", "reigns", "standing"], "charles4_hre": ["crowned", "standing"],
     "louis_hu": ["crowned", "standing"]},
    [("enemy_of", "charles4_hre", "louis_hu"), ("enemy_of", "louis_hu", "charles4_hre")],
    [flag("charles4_hre", "reconciled_pl"), flag("louis_hu", "reconciled_pl"), flag("casimir3", "university_pl")],
    [("krakow_academy_pl", ["casimir3"]), ("wierzynek_feast_pl", ["wierzynek", "casimir3"]),
     ("krakow_congress_pl", ["casimir3", "charles4_hre", "louis_hu"])],
    "simplification"))
TEXTS.update(texts("wierzynek_1364",
    "Пир у Вежинка",
    "Король основывает университет, а на пиру у краковского купца мирит императора с венгерским королём",
    "Университет король основал весной, ещё до съезда. Мирить гостей проще за столом, чем в поле, — но сначала нужен стол. И не дайте гостям схватиться раньше, чем сядут.",
    "1364 год. Казимир Великий, последний из Пястов, превратил разорённую страну в державу, с которой считаются. Император Карл IV и венгерский король Людовик в ссоре: император оскорбил мать Людовика — сестру Казимира. В Краков съезжаются короли.",
    "12 мая 1364 года Казимир основал в Кракове университет — будущий Ягеллонский, второй в Центральной Европе после Праги. В сентябре на Краковском съезде собрались император Карл IV, Людовик Венгерский, Пётр Кипрский, Вальдемар Датский и немецкие князья; Казимир помирил Карла с Людовиком. По Длугошу, гостей угощал богатый краковский купец Вежинек, — и ресторан «Вежинек» на Главном рынке до сих пор ведёт отсчёт от 1364 года. О Казимире Длугош скажет: «застал Польшу деревянной, а оставил каменной».",
    "Ян Длугош, «Анналы», IX; Ян из Чарнкова, «Хроника»"))

if __name__ == "__main__":
    P.NEW_CHARS, P.NEW_SCENES, P.NEW_RULES, P.NEW_LEVELS, P.TEXTS = NEW_CHARS, NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS
    P.CHAPTER_TEXTS = {}
    P.main()
