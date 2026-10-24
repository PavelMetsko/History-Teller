#!/usr/bin/env python3
"""Глава «США», пачка 1: шесть легенд + начало акта «До США» (Кахокия … Плимут), 15 уровней.

    python3 tools/batches/usa_1.py [repo_root]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usa_common import (char, scene, actor, setf, remf, addr, rule, flag, nflag, texts, level, bait, run,
                        PARLEY, BATTLE, ACT1, ACT2)

def C(id, name, emoji, tags=None):
    return char(id, name, tags or [id], emoji)

CH, SC, RU, LV, TX = [], [], [], [], {}

# ======================================================================= Акт I · Легенды
# ---------------------------------------------------------------- betsy_ross (легенда)
CH += [C("betsy_ross", "Бетси Росс", "🧵"), C("robert_morris", "Роберт Моррис", "💰")]
SC += [
    scene("flag_committee_us", "Комитет приходит к швее", ["sig_flag_committee_us"], 2, "🚪", "заказать флаг", "icon_ally",
          ["генерал", "швея"], "court_present"),
    scene("one_snip_us", "Один взмах ножниц", ["sig_one_snip_us"], 1, "✂️", "вырезать звезду", "icon_crown",
          ["швея"], "anekdota_desk"),
    scene("six_star_us", "Шестиконечные звёзды", ["sig_six_star_us"], 1, "✡️", "шить как на эскизе", "icon_plot",
          ["швея"], "anekdota_desk"),
    scene("sew_flag_us", "Первый флаг", ["sig_sew_flag_us"], 2, "🇺🇸", "сшить флаг", "icon_crown",
          ["швея", "заказчик"], "palace_chapel"),
]
RU += [
    rule("flag_committee_us_sig", "Вашингтон с комитетом приносят швее эскиз флага с шестиконечными звёздами",
         "sig_flag_committee_us", [actor("A", 0, tags=["american"]), actor("B", 1, tags=["betsy_ross"])],
         [setf("B", "commissioned_us")]),
    rule("six_star_us_sig", "Швея шьёт звёзды как на эскизе — по шесть лучей, долго и криво",
         "sig_six_star_us", [actor("A", 0, tags=["betsy_ross"], flags=["commissioned_us"])],
         [setf("A", "six_star_us")]),
    rule("one_snip_us_sig", "Швея складывает ткань и одним взмахом ножниц вырезает ровную пятиконечную звезду",
         "sig_one_snip_us", [actor("A", 0, tags=["betsy_ross"], flags=["commissioned_us"], notFlags=["six_star_us"])],
         [setf("A", "five_star_us")]),
    rule("sew_flag_us_sig", "Тринадцать полос и тринадцать звёзд по кругу — флаг готов",
         "sig_sew_flag_us", [actor("A", 0, tags=["betsy_ross"], flags=["five_star_us"]), actor("B", 1, tags=["robert_morris"])],
         [setf("A", "flag_us")]),
]
LV.append(level("betsy_ross", 10, ACT1, "c", "sew_flag_us", 3,
    ["flag_committee_us", "one_snip_us", "six_star_us", "sew_flag_us"], ["betsy_ross", "washington", "robert_morris"],
    {"washington": ["standing", "strong"]}, [],
    [flag("betsy_ross", "flag_us"), nflag("betsy_ross", "six_star_us")],
    [("flag_committee_us", ["washington", "betsy_ross"]), ("one_snip_us", ["betsy_ross"]), ("sew_flag_us", ["betsy_ross", "robert_morris"])],
    "legend"))
TX.update(texts("betsy_ross", "Звезда одним взмахом",
    "Филадельфийская швея показывает генералу Вашингтону, как вырезать звезду одним взмахом ножниц — и шьёт первый флаг",
    "Эскиз — не приказ: шестиконечные звёзды шить долго. Покажи заказчикам, как сделать проще.",
    "Филадельфия, 1776 год. По семейному преданию, в мастерскую вдовы-обойщицы Бетси Росс входят трое: генерал Джордж Вашингтон, финансист Роберт Моррис и дядя её покойного мужа Джордж Росс. У них эскиз флага новой страны — тринадцать полос и тринадцать шестиконечных звёзд.",
    "По семейному преданию, Бетси сказала генералу, что звезда должна быть пятиконечной, сложила лоскут ткани и одним щелчком ножниц вырезала ровную звезду. Комитет был поражён, и она сшила флаг с тринадцатью звёздами по кругу. 14 июня 1777 года Конгресс утвердил флаг из 13 полос и 13 звёзд, не указав, как их расположить, — этот день до сих пор празднуют как День флага. Рассказ о Бетси впервые обнародовал её внук в 1870 году, и документов о нём нет, но дом Бетси Росс в Филадельфии — один из самых посещаемых музеев города.",
    "Уильям Кэнби, доклад Пенсильванскому историческому обществу (1870); резолюция Конгресса о флаге (1777)"))

# ---------------------------------------------------------------- rip_van_winkle (легенда)
CH += [C("rip_van_winkle", "Рип ван Винкль", "😴"), C("dame_van_winkle", "Дама ван Винкль", "🧹"),
       C("hudson_ghost", "Призрак Хендрика Гудзона", "👻"), C("vedder", "Трактирщик Веддер", "🍺")]
SC += [
    scene("henpecked_us", "Ворчливая жена", ["sig_henpecked_us"], 2, "🧹", "сбежать от жены", "icon_ally",
          ["жена", "муж"], "deulino_village"),
    scene("ninepins_us", "Кегли в горах Кэтскилл", ["sig_ninepins_us"], 2, "🎳", "выпить с призраками", "icon_plot",
          ["призрак", "гость"], "forest_ambush"),
    scene("return_village_us", "Возвращение в деревню", ["sig_return_village_us"], 2, "🏘️", "узнать новости", "icon_crown",
          ["странник", "трактирщик"], "vienna_inn"),
    scene("toast_king_us", "Тост за короля Георга", ["sig_toast_king_us"], 1, "🍻", "поднять кружку", "icon_dead",
          ["кто пьёт"], "vienna_inn"),
]
RU += [
    rule("henpecked_us_sig", "Жена пилит бездельника — он берёт ружьё и уходит в горы",
         "sig_henpecked_us", [actor("A", 0, tags=["dame_van_winkle"]), actor("B", 1, tags=["rip_van_winkle"])],
         [setf("B", "in_mountains_us")]),
    rule("ninepins_us_sig", "Молчаливые призраки играют в кегли; Рип пробует их настойку и засыпает на двадцать лет",
         "sig_ninepins_us", [actor("A", 0, tags=["hudson_ghost"]), actor("B", 1, tags=["rip_van_winkle"], flags=["in_mountains_us"])],
         [setf("B", "slept_us")]),
    rule("toast_king_us_sig", "Старик поднимает кружку за короля Георга — толпа кричит «Тори! Шпион!»",
         "sig_toast_king_us", [actor("A", 0, tags=["rip_van_winkle"], flags=["slept_us"])],
         [setf("A", "mobbed_us")]),
    rule("return_village_us_sig", "Трактирщик рассказывает: была революция, король больше не правит, теперь тут республика",
         "sig_return_village_us", [actor("A", 0, tags=["rip_van_winkle"], flags=["slept_us"], notFlags=["mobbed_us"]),
                                   actor("B", 1, tags=["vedder"])],
         [setf("A", "citizen_us")]),
]
LV.append(level("rip_van_winkle", 20, ACT1, "r", "ninepins_us", 3,
    ["henpecked_us", "ninepins_us", "return_village_us", "toast_king_us"], ["rip_van_winkle", "dame_van_winkle", "hudson_ghost", "vedder"],
    {}, [],
    [flag("rip_van_winkle", "citizen_us"), nflag("rip_van_winkle", "mobbed_us")],
    [("henpecked_us", ["dame_van_winkle", "rip_van_winkle"]), ("ninepins_us", ["hudson_ghost", "rip_van_winkle"]),
     ("return_village_us", ["rip_van_winkle", "vedder"])],
    "legend"))
TX.update(texts("rip_van_winkle", "Рип ван Винкль",
    "Добродушный лентяй засыпает в горах подданным британского короля — и просыпается гражданином республики",
    "Сначала надо уйти из дома — без этого в горы не попасть. Проснувшись, сперва расспроси, что изменилось, прежде чем пить за кого-то.",
    "Деревня у гор Кэтскилл, долина Гудзона, задолго до революции. Рип ван Винкль — всеобщий любимец, готов помочь любому соседу, только не собственной жене. Однажды, спасаясь от её ворчания, он уходит с ружьём и собакой в горы.",
    "В горах Рип встречает странных молчаливых людей в старинной голландской одежде — призраков команды Генри Гудзона, — которые играют в кегли, и пробует их настойку. Он засыпает, а просыпается с седой бородой до пояса. В деревне всё чужое: на трактире вместо портрета короля Георга — генерал Вашингтон, вокруг кричат о выборах и правах граждан. Рип по привычке объявляет себя верным подданным короля — и его едва не принимают за шпиона. Оказывается, он проспал двадцать лет и всю революцию. Ворчливая жена за это время умерла — «единственное, о чём он не жалел». Рассказ Вашингтона Ирвинга 1819 года стал одним из первых американских литературных мифов.",
    "Вашингтон Ирвинг, «Рип ван Винкль» (1819)"))

# ---------------------------------------------------------------- sleepy_hollow (легенда)
CH += [C("ichabod_crane", "Икабод Крейн", "📚"), C("katrina", "Катрина ван Тассел", "🌸"),
       C("brom_bones", "Бром Бонс", "💪"), C("headless_horseman", "Всадник без головы", "🎃")]
SC += [
    scene("tassel_party_us", "Праздник у ван Тасселов", ["sig_tassel_party_us"], 2, "💃", "ухаживать", "icon_ally",
          ["кавалер", "невеста"], "hofburg_ball"),
    scene("ghost_tales_us", "Страшные истории у камина", ["sig_ghost_tales_us"], 2, "🕯️", "рассказать о призраке", "icon_plot",
          ["рассказчик", "слушатель"], "vienna_inn"),
    scene("bridge_chase_us", "Погоня у церковного моста", ["sig_bridge_chase_us"], 2, "🐎", "гнаться в ночи", "icon_dead",
          ["всадник", "путник"], "night_flight"),
    bait("hollow_duel_us", "Вызвать соперника на бой", "v_battle", 2, "duel_challenge", BATTLE),
]
RU += [
    rule("tassel_party_us_sig", "Учитель пляшет с первой красавицей Сонной Лощины и уже видит себя хозяином её ферм",
         "sig_tassel_party_us", [actor("A", 0, tags=["ichabod_crane"]), actor("B", 1, tags=["katrina"])],
         [setf("A", "smitten_us")]),
    rule("ghost_tales_us_sig", "Соперник рассказывает о Всаднике без головы — и суеверный учитель уходит домой дрожа",
         "sig_ghost_tales_us", [actor("A", 0, tags=["brom_bones"]), actor("B", 1, tags=["ichabod_crane"], flags=["smitten_us"])],
         [setf("B", "frightened_us")]),
    rule("bridge_chase_us_sig", "Безголовый всадник гонится за перепуганным учителем и швыряет в него свою голову",
         "sig_bridge_chase_us", [actor("A", 0, tags=["headless_horseman"]), actor("B", 1, tags=["ichabod_crane"], flags=["frightened_us"])],
         [setf("B", "fled_hollow_us"), setf("B", "away")]),
]
LV.append(level("sleepy_hollow", 30, ACT1, "t", "bridge_chase_us", 3,
    ["tassel_party_us", "ghost_tales_us", "bridge_chase_us", "hollow_duel_us"], ["ichabod_crane", "katrina", "brom_bones", "headless_horseman"],
    {"brom_bones": ["standing", "strong"]}, [],
    [flag("ichabod_crane", "fled_hollow_us")],
    [("tassel_party_us", ["ichabod_crane", "katrina"]), ("ghost_tales_us", ["brom_bones", "ichabod_crane"]),
     ("bridge_chase_us", ["headless_horseman", "ichabod_crane"])],
    "legend"))
TX.update(texts("sleepy_hollow", "Легенда Сонной Лощины",
    "Сельский учитель сватается к богатой невесте, наслушается историй о Всаднике без головы — и исчезает навсегда",
    "Силачу драка не нужна: страх сделает всё за него. Но испугать можно только того, кто остался на праздник допоздна.",
    "Сонная Лощина, голландская деревушка у Гудзона. Тощий и суеверный учитель Икабод Крейн мечтает жениться на Катрине ван Тассел — и на её отцовских фермах. У Катрины есть и другой поклонник: здоровяк-шутник Бром Бонс.",
    "Осенним вечером на празднике у ван Тасселов гости рассказывали страшные истории — о гессенском кавалеристе, которому ядро оторвало голову, и который ночами скачет искать её. Возвращаясь домой за полночь, Икабод услышал позади топот: за ним гнался безголовый всадник. У церковного моста всадник швырнул в учителя свою голову — и Икабод исчез. Утром нашли лошадь, шляпу и разбитую тыкву. Бром Бонс вскоре женился на Катрине и всякий раз, когда при нём вспоминали ту ночь, подозрительно усмехался. Повесть Вашингтона Ирвинга 1820 года стала первой американской готической легендой, а тыква на дороге — её символом.",
    "Вашингтон Ирвинг, «Легенда о Сонной Лощине» (1820)"))

# ---------------------------------------------------------------- johnny_appleseed (легенда)
CH += [C("chapman", "Джонни Эплсид", "🍎"), C("cider_miller", "Мельник-сидродел", "🍶"), C("settler_us", "Переселенец", "🪓")]
SC += [
    scene("cider_seeds_us", "Семечки из сидровой мельницы", ["sig_cider_seeds_us"], 2, "🌰", "собрать семечки", "icon_ally",
          ["мельник", "странник"], "valmy_mill"),
    scene("nursery_us", "Питомник на краю леса", ["sig_nursery_us"], 1, "🌱", "посадить питомник", "icon_ally",
          ["садовник"], "plough_field"),
    scene("orchard_claim_us", "Пятьдесят яблонь — и земля твоя", ["sig_orchard_claim_us"], 2, "🏡", "продать саженцы", "icon_crown",
          ["переселенец", "садовник"], "deulino_village"),
    scene("graft_us", "Привить сладкий сорт", ["sig_graft_us"], 1, "🔪", "сделать прививку", "icon_plot",
          ["садовник"], "plough_field"),
]
RU += [
    rule("cider_seeds_us_sig", "Странник выбирает семечки из жмыха сидровой мельницы",
         "sig_cider_seeds_us", [actor("A", 0, tags=["cider_miller"]), actor("B", 1, tags=["chapman"])], [setf("B", "seeds_us")]),
    rule("graft_us_sig", "Садовник режет и прививает деревья — сам он считал это жестокостью к дереву",
         "sig_graft_us", [actor("A", 0, tags=["chapman"])], [setf("A", "grafted_us")]),
    rule("nursery_us_sig", "Питомник из семечек вырастает там, куда переселенцы придут только через несколько лет",
         "sig_nursery_us", [actor("A", 0, tags=["chapman"], flags=["seeds_us"], notFlags=["grafted_us"])], [setf("A", "nursery_us")]),
    rule("orchard_claim_us_sig", "Переселенец покупает саженцы: по закону компании участок дают тому, кто посадил 50 яблонь",
         "sig_orchard_claim_us", [actor("A", 0, tags=["settler_us"]), actor("B", 1, tags=["chapman"], flags=["nursery_us"])],
         [setf("A", "claim_us")]),
]
LV.append(level("johnny_appleseed", 40, ACT1, "r", "orchard_claim_us", 3,
    ["cider_seeds_us", "nursery_us", "orchard_claim_us", "graft_us"], ["chapman", "cider_miller", "settler_us"], {}, [],
    [flag("settler_us", "claim_us"), nflag("chapman", "grafted_us")],
    [("cider_seeds_us", ["cider_miller", "chapman"]), ("nursery_us", ["chapman"]), ("orchard_claim_us", ["settler_us", "chapman"])],
    "legend"))
TX.update(texts("johnny_appleseed", "Джонни Эплсид",
    "Босой странник с котелком на голове сажает яблоневые питомники на пути переселенцев на Запад",
    "Семечки берут там, где давят яблоки. Сладкие сорта прививкой — это чужой метод: наш садовник считал, что дереву так больно.",
    "Начало XIX века. Через Пенсильванию, Огайо и Индиану на Запад движутся переселенцы. Впереди них, босиком, в мешковине и, по рассказам, с котелком вместо шляпы, идёт Джон Чепмен — его прозвали Джонни Эплсид, «Джонни Яблочное Семечко».",
    "Чепмен собирал семечки на сидровых мельницах Пенсильвании и сажал питомники там, куда переселенцы должны были прийти через несколько лет, — а потом продавал им саженцы. Ему было выгодно: по правилам земельных компаний Огайо, чтобы закрепить за собой участок, поселенец должен был посадить на нём 50 яблонь. Чепмен не прививал деревья — считал, что резать их жестоко, — поэтому из его семечек росли кислые дикие яблоки. Ели их мало: из них делали сидр и яблочный бренди. Он был проповедником-сведенборгианином, вегетарианцем и умер в 1845 году владельцем больших земель. Последнее его дерево, по преданию, до сих пор растёт в Огайо.",
    "Майкл Поллан, «Ботаника желаний» (2001); У. Хейли, «Джонни Эплсид» (1871)"))

# ---------------------------------------------------------------- john_henry (легенда)
CH += [C("john_henry", "Джон Генри", "🔨"), C("polly_ann", "Полли Энн", "👩"),
       C("rail_captain", "Капитан бригады", "🎩"), C("drill_salesman", "Продавец паровой дрели", "⚙️")]
SC += [
    scene("captain_bet_us", "Спор капитана", ["sig_captain_bet_us"], 2, "🤝", "поспорить", "icon_ally",
          ["капитан", "продавец"], "merchant_deal_pl"),
    scene("tunnel_race_us", "Человек против машины", ["sig_tunnel_race_us"], 2, "⚒️", "бить быстрее машины", "icon_dead",
          ["молотобоец", "машина"], "cellar_search"),
    scene("hammer_passes_us", "Молот переходит к Полли", ["sig_hammer_passes_us"], 2, "💪", "поднять молот", "icon_crown",
          ["кто поднимает", "проигравший"], "ring_mine_pl"),
    scene("buy_drill_us", "Купить машину без спора", ["sig_buy_drill_us"], 2, "💵", "купить дрель", "icon_plot",
          ["капитан", "продавец"], "merchant_deal_pl"),
]
RU += [
    rule("captain_bet_us_sig", "Капитан ставит деньги: его человек пробьёт скалу быстрее паровой дрели",
         "sig_captain_bet_us", [actor("A", 0, tags=["rail_captain"]), actor("B", 1, tags=["drill_salesman"])], [setf("B", "contest_us")]),
    rule("buy_drill_us_sig", "Капитан молча покупает дрель — молотобойцы больше не нужны",
         "sig_buy_drill_us", [actor("A", 0, tags=["rail_captain"]), actor("B", 1, tags=["drill_salesman"], notFlags=["contest_us"])],
         [setf("A", "drill_bought_us")]),
    rule("tunnel_race_us_sig", "Джон Генри с двумя молотами пробивает больше машины — и падает замертво с молотом в руке",
         "sig_tunnel_race_us", [actor("A", 0, tags=["john_henry"]), actor("B", 1, tags=["drill_salesman"], flags=["contest_us"])],
         [setf("A", "beat_machine_us"), setf("A", "dead"), setf("B", "lost_race_us")]),
    rule("hammer_passes_us_sig", "Полли Энн берёт молот и бьёт «как мужчина» — песня о Джоне Генри идёт дальше",
         "sig_hammer_passes_us", [actor("A", 0, tags=["polly_ann"]), actor("B", 1, tags=["drill_salesman"], flags=["lost_race_us"])],
         [setf("A", "legend_lives_us")]),
]
LV.append(level("john_henry", 50, ACT1, "b", "tunnel_race_us", 3,
    ["captain_bet_us", "tunnel_race_us", "hammer_passes_us", "buy_drill_us"], ["john_henry", "polly_ann", "rail_captain", "drill_salesman"],
    {"john_henry": ["standing", "strong"]}, [],
    [flag("john_henry", "beat_machine_us"), flag("polly_ann", "legend_lives_us"), nflag("rail_captain", "drill_bought_us")],
    [("captain_bet_us", ["rail_captain", "drill_salesman"]), ("tunnel_race_us", ["john_henry", "drill_salesman"]),
     ("hammer_passes_us", ["polly_ann", "drill_salesman"])],
    "legend"))
TX.update(texts("john_henry", "Джон Генри",
    "Чернокожий молотобоец соревнуется с паровой дрелью в тоннеле — выигрывает и умирает с молотом в руке",
    "Без спора нет состязания — а купленная без спора машина просто заменит людей. Молот после героя не падает на землю.",
    "Горы Западной Вирджинии, 1870-е годы. Железная дорога пробивает тоннель сквозь скалу Биг-Бенд. Молотобойцы, многие из них вчерашние рабы, вручную вбивают стальные бурики в камень. Сильнее всех — Джон Генри. Однажды в лагерь привозят паровую дрель.",
    "По балладе, Джон Генри сказал капитану: «Человек — всего лишь человек, но прежде чем меня победит паровая дрель, я умру с молотом в руке». Взяв по молоту в каждую руку, он пробил за день больше, чем машина, — и упал замертво. Его жена Полли Энн подняла молот и «работала как мужчина». Существовал ли Джон Генри, спорят до сих пор: историк Скотт Нельсон нашёл узника Джона Уильяма Генри, которого тюрьма Вирджинии «сдавала в аренду» на строительство тоннелей. Баллада стала гимном рабочих и одной из самых записываемых песен Америки.",
    "Скотт Р. Нельсон, «Человек со стальным молотом» (2006); баллада «John Henry» (XIX в.)"))

# ---------------------------------------------------------------- paul_bunyan (легенда)
CH += [C("paul_bunyan", "Пол Баньян", "🪓"), C("inkslinger", "Джонни Инкслингер", "🖋️"), C("sourdough_sam", "Повар Саурдо Сэм", "🥞")]
SC += [
    scene("blue_snow_us", "Зима синего снега", ["sig_blue_snow_us"], 1, "❄️", "найти синего телёнка", "icon_ally",
          ["лесоруб"], "nancy_snow"),
    scene("crooked_river_us", "Выпрямить реку", ["sig_crooked_river_us"], 1, "🐂", "тянуть реку быком", "icon_crown",
          ["лесоруб"], "black_river"),
    scene("pancake_griddle_us", "Сковорода на акр", ["sig_pancake_griddle_us"], 2, "🥞", "испечь блины на весь лагерь", "icon_ally",
          ["повар", "лесоруб"], "royal_kitchen"),
    scene("ledger_us", "Счётная книга лагеря", ["sig_ledger_us"], 2, "📒", "свести счета", "icon_plot",
          ["счетовод", "лесоруб"], "codex_book"),
]
RU += [
    rule("blue_snow_us_sig", "В зиму синего снега великан находит замёрзшего телёнка, отогревает — и получает синего быка Бейба",
         "sig_blue_snow_us", [actor("A", 0, tags=["paul_bunyan"])], [setf("A", "babe_us")]),
    rule("crooked_river_us_sig", "Бейб тянет кривую реку за конец, как верёвку, пока та не выпрямится",
         "sig_crooked_river_us", [actor("A", 0, tags=["paul_bunyan"], flags=["babe_us", "fed_us"])], [setf("A", "river_straight_us")]),
    rule("pancake_griddle_us_sig", "Повар печёт блины на сковороде размером с акр — поварята катаются по ней на свиных окороках",
         "sig_pancake_griddle_us", [actor("A", 0, tags=["sourdough_sam"]), actor("B", 1, tags=["paul_bunyan"])], [setf("B", "fed_us")]),
    rule("ledger_us_sig", "Счетовод тратит на учёт лагеря столько чернил, что сэкономил девять бочек, перестав ставить точки над i",
         "sig_ledger_us", [actor("A", 0, tags=["inkslinger"]), actor("B", 1, tags=["paul_bunyan"])], [setf("A", "ledger_us")]),
]
LV.append(level("paul_bunyan", 60, ACT1, "c", "crooked_river_us", 3,
    ["blue_snow_us", "pancake_griddle_us", "crooked_river_us", "ledger_us"], ["paul_bunyan", "inkslinger", "sourdough_sam"], {}, [],
    [flag("paul_bunyan", "river_straight_us")],
    [("blue_snow_us", ["paul_bunyan"]), ("pancake_griddle_us", ["sourdough_sam", "paul_bunyan"]), ("crooked_river_us", ["paul_bunyan"])],
    "legend"))
TX.update(texts("paul_bunyan", "Пол Баньян и синий бык",
    "Великан-лесоруб находит в синем снегу телёнка, выкармливает лагерь блинами и выпрямляет реку",
    "Без быка реку не выпрямить, а голодный великан ничего не потянет. Счета подождут.",
    "Северные леса Мичигана, Висконсина и Миннесоты, конец XIX века. В лесорубных лагерях долгими вечерами рассказывают небылицы — и главный их герой Пол Баньян, лесоруб такого роста, что его шаг — семь миль.",
    "В Зиму синего снега, когда даже снег шёл синим, Пол нашёл замёрзшего телёнка, отогрел его, и тот навсегда остался синим — так появился бык Бейб, между рогами которого умещалось 42 топорища. Повар Саурдо Сэм пёк для лагеря блины на сковороде в акр, по которой поварята катались, привязав к ногам свиные окорока вместо масла. Бейб тянул за конец кривую реку, пока та не стала прямой, а следы Пола и Бейба, говорят, стали десятью тысячами озёр Миннесоты. Эти «tall tales» — устный фольклор лесорубов; в 1910-х их подхватила реклама лесопромышленной компании Red River Lumber, и Пол стал национальным героем. Его гигантские статуи стоят в десятках городов Северной Америки.",
    "Джеймс Макгилливрей, «Сплав по Круглой реке» (Detroit News-Tribune, 1910); У. Лохид, рекламные буклеты Red River Lumber (1914)"))

# ======================================================================= Акт II · До США: колонии
# ---------------------------------------------------------------- cahokia (~1050–1350)
CH += [C("cahokia_elder", "Старейшина Кахокии", "🛕"), C("sun_priestess", "Жрица Солнца", "☀️"),
       C("shell_master", "Мастер раковин", "🐚"), C("aztalan_envoy", "Посланник из Азталана", "🛶")]
SC += [
    scene("monks_mound_us", "Великий курган", ["sig_monks_mound_us"], 2, "⛰️", "насыпать курган", "icon_crown",
          ["старейшина", "жрица"], "pyramids"),
    scene("shell_trade_us", "Раковины с Мексиканского залива", ["sig_shell_trade_us"], 2, "🐚", "обменять раковины", "icon_ally",
          ["мастер", "посланник"], "harbor"),
    scene("woodhenge_us", "Деревянный круг солнца", ["sig_woodhenge_us"], 1, "🌅", "отметить солнцестояние", "icon_crown",
          ["жрица"], "royal_oak"),
    scene("palisade_us", "Частокол из всего леса", ["sig_palisade_us"], 1, "🪵", "вырубить лес на стены", "icon_plot",
          ["старейшина"], "burnt_fields"),
]
RU += [
    rule("woodhenge_us_sig", "Жрица по кругу из столбов отмечает солнцестояние — по нему живёт весь город",
         "sig_woodhenge_us", [actor("A", 0, tags=["sun_priestess"])], [setf("A", "calendar_us")]),
    rule("monks_mound_us_sig", "Тысячи людей корзинами насыпают земляной холм выше любого здания до XIX века",
         "sig_monks_mound_us", [actor("A", 0, tags=["cahokia_elder"]), actor("B", 1, tags=["sun_priestess"], flags=["calendar_us"])],
         [setf("A", "mound_us")]),
    rule("palisade_us_sig", "Город обносят частоколом из двадцати тысяч брёвен — леса вокруг больше нет",
         "sig_palisade_us", [actor("A", 0, tags=["cahokia_elder"])], [setf("A", "forest_gone_us")]),
    rule("shell_trade_us_sig", "Морские раковины, медь Великих озёр и кремень с юга сходятся на рынках Кахокии",
         "sig_shell_trade_us", [actor("A", 0, tags=["shell_master"]), actor("B", 1, tags=["aztalan_envoy"])],
         [setf("A", "trade_us")]),
]
LV.append(level("cahokia", 100, ACT2, "c", "monks_mound_us", 3,
    ["woodhenge_us", "monks_mound_us", "shell_trade_us", "palisade_us"], ["cahokia_elder", "sun_priestess", "shell_master", "aztalan_envoy"],
    {"cahokia_elder": ["standing", "reigns"]}, [],
    [flag("cahokia_elder", "mound_us"), flag("shell_master", "trade_us"), nflag("cahokia_elder", "forest_gone_us")],
    [("woodhenge_us", ["sun_priestess"]), ("monks_mound_us", ["cahokia_elder", "sun_priestess"]),
     ("shell_trade_us", ["shell_master", "aztalan_envoy"])],
    "simplification"))
TX.update(texts("cahokia", "Город курганов",
    "За пятьсот лет до европейцев на Миссисипи стоит город больше тогдашнего Лондона — с курганами, солнечным календарём и торговлей на полконтинента",
    "Город живёт по солнцу — сначала календарь, потом стройка. Защищаться частоколом соблазнительно, но лес не бесконечен.",
    "Около 1050 года, берег Миссисипи напротив нынешнего Сент-Луиса. Здесь вырастает Кахокия — крупнейший город к северу от Мексики. Имён его жителей мы не знаем: письменности не было, и всё, что известно, рассказала археология. Мы назовём их по ролям.",
    "В расцвете, около 1100 года, в Кахокии жило 10–20 тысяч человек — больше, чем в тогдашнем Лондоне. Главный курган, Монкс-Маунд, насыпан вручную корзинами земли: он выше 30 метров и по площади основания больше египетской пирамиды Хеопса. Круг из деревянных столбов — его прозвали «Вудхендж» — отмечал солнцестояния и равноденствия. Сюда везли раковины с Мексиканского залива, медь с Великих озёр и слюду из Аппалачей. Около 1350 года город опустел: учёные спорят о причинах — засухи, наводнения, вырубка лесов, войны. Кахокия внесена в список Всемирного наследия ЮНЕСКО. Наша история США начинается не с кораблей, а с неё.",
    "Тимоти Покетат, «Древний город Америки — Кахокия на Миссисипи» (2009); ЮНЕСКО, «Исторический памятник Кахокия-Маундс»"))

# ---------------------------------------------------------------- haudenosaunee (XV–XVI вв.)
CH += [C("deganawida", "Деганавида, Миротворец", "🕊️"), C("hiawatha", "Хайавата", "📿"),
       C("jigonsaseh", "Джигонсаси, мать кланов", "🌽"), C("tadodaho", "Тадодахо", "🐍")]
SC += [
    scene("condolence_us", "Обряд утешения", ["sig_condolence_us"], 2, "📿", "утешить вампумом", "icon_ally",
          ["миротворец", "скорбящий"], "chapel"),
    scene("clan_mother_us", "Слово матери кланов", ["sig_clan_mother_us"], 2, "🌽", "получить поддержку", "icon_ally",
          ["мать кланов", "миротворец"], "royal_oak"),
    scene("comb_snakes_us", "Расчесать змей из волос", ["sig_comb_snakes_us"], 3, "🐍", "убедить вождя", "icon_crown",
          ["Хайавата", "миротворец", "вождь"], "deulino_village"),
    scene("onondaga_war_us", "Идти на Онондагу войной", ["sig_onondaga_war_us"], 2, "⚔️", "напасть", "icon_dead",
          ["нападающий", "вождь"], "forest_ambush"),
]
RU += [
    rule("condolence_us_sig", "Миротворец вытирает слёзы скорбящему нитями вампума — так рождается обряд утешения",
         "sig_condolence_us", [actor("A", 0, tags=["deganawida"]), actor("B", 1, tags=["hiawatha"])], [setf("B", "consoled_us")]),
    rule("clan_mother_us_sig", "Мать кланов первой принимает Великий закон мира — без женщин совета не будет",
         "sig_clan_mother_us", [actor("A", 0, tags=["jigonsaseh"]), actor("B", 1, tags=["deganawida"])], [setf("B", "backed_us")]),
    rule("onondaga_war_us_sig", "Нападение на грозного вождя только множит кровную месть",
         "sig_onondaga_war_us", [actor("A", 0), actor("B", 1, tags=["tadodaho"])], [setf("A", "blood_feud_us")]),
    rule("comb_snakes_us_sig", "Утешенный Хайавата и Миротворец расчёсывают змей из волос Тадодахо — и он принимает мир",
         "sig_comb_snakes_us", [actor("A", 0, tags=["hiawatha"], flags=["consoled_us"], notFlags=["blood_feud_us"]),
                                actor("B", 1, tags=["deganawida"], flags=["backed_us"], notFlags=["blood_feud_us"]),
                                actor("C", 2, tags=["tadodaho"])],
         [setf("C", "great_law_us")]),
]
LV.append(level("haudenosaunee", 110, ACT2, "c", "comb_snakes_us", 3,
    ["condolence_us", "clan_mother_us", "comb_snakes_us", "onondaga_war_us"], ["deganawida", "hiawatha", "jigonsaseh", "tadodaho"],
    {"tadodaho": ["standing", "strong", "reigns"]}, [],
    [flag("tadodaho", "great_law_us")],
    [("condolence_us", ["deganawida", "hiawatha"]), ("clan_mother_us", ["jigonsaseh", "deganawida"]),
     ("comb_snakes_us", ["hiawatha", "deganawida", "tadodaho"])],
    "simplification"))
TX.update(texts("haudenosaunee", "Великий закон мира",
    "Миротворец, скорбящий отец и мать кланов уговаривают самого грозного вождя — и пять народов объединяются в Лигу",
    "Силой змей из волос не вычешешь. Сначала исцелить горе, потом заручиться словом женщин — и только тогда идти к Тадодахо.",
    "Леса нынешнего штата Нью-Йорк, примерно XV век. Пять народов — мохоки, онайда, онондага, кайюга и сенека — тонут в кровной мести. У онондага правит Тадодахо: по преданию, в его волосах шевелятся змеи. У Хайаваты погибли дочери, и горе сделало его безумным.",
    "Устная традиция хауденосауни рассказывает: Миротворец Деганавида встретил скорбящего Хайавату и вытер ему слёзы нитями из раковин-вампума — так появился обряд утешения, с которого и сегодня начинаются советы. Первой Великий закон мира приняла мать кланов Джигонсаси; с тех пор вождей Лиги выбирают и смещают старшие женщины кланов. Последним сдался Тадодахо — Хайавата и Деганавида «вычесали змей из его волос», и он стал хранителем совета. Пять народов закопали оружие под Великим деревом мира — белой сосной. Когда возникла Лига, точно неизвестно: оценки — от XII до XVI века. Лига хауденосауни существует до сих пор, а вампумный пояс Хайаваты — её флаг.",
    "Устная традиция хауденосауни (Гаянашагова); А. Паркер, «Конституция пяти народов» (1916)"))

# ---------------------------------------------------------------- columbus_1492
CH += [C("columbus", "Христофор Колумб", "⛵"), C("guacanagari", "Касик Гуаканагари", "🌺"),
       C("rodrigo_triana", "Матрос Родриго де Триана", "👀"), C("luis_torres", "Переводчик Луис де Торрес", "📜")]
SC += [
    scene("tierra_us", "«Земля!»", ["sig_tierra_us"], 2, "🔭", "увидеть землю", "icon_crown",
          ["матрос", "адмирал"], "golden_hind"),
    scene("great_khan_us", "Посольство к Великому хану", ["sig_great_khan_us"], 2, "🐉", "искать Китай", "icon_plot",
          ["переводчик", "касик"], "khan_court"),
    scene("guaca_gifts_us", "Дары касика", ["sig_guaca_gifts_us"], 2, "🎁", "заключить дружбу", "icon_ally",
          ["адмирал", "касик"], "kealakekua"),
    scene("navidad_us", "Крушение и форт Навидад", ["sig_navidad_us"], 2, "🏚️", "построить форт из обломков", "icon_crown",
          ["адмирал", "касик"], "botany_bay"),
]
RU += [
    rule("tierra_us_sig", "Матрос первым кричит «Земля!» — но обещанную награду адмирал оставит себе",
         "sig_tierra_us", [actor("A", 0, tags=["rodrigo_triana"]), actor("B", 1, tags=["columbus"])], [setf("B", "landfall_us")]),
    rule("great_khan_us_sig", "Переводчик заговаривает с касиком по-арабски и по-еврейски — Колумб уверен, что рядом Азия",
         "sig_great_khan_us", [actor("A", 0, tags=["luis_torres"]), actor("B", 1, tags=["guacanagari"])], [setf("A", "lost_in_asia_us")]),
    rule("guaca_gifts_us_sig", "Касик встречает пришельцев дарами и помогает им — золото для них важнее людей",
         "sig_guaca_gifts_us", [actor("A", 0, tags=["columbus"], flags=["landfall_us"]), actor("B", 1, tags=["guacanagari"])],
         [addr("ally_of", "B", "A")]),
    rule("navidad_us_sig", "«Санта-Мария» садится на риф; люди касика спасают груз, из досок строят форт Навидад",
         "sig_navidad_us", [actor("A", 0, tags=["columbus"]),
                            actor("B", 1, tags=["guacanagari"], relations=[{"rel": "ally_of", "to": "A"}])],
         [setf("A", "navidad_us")]),
]
LV.append(level("columbus_1492", 120, ACT2, "t", "tierra_us", 3,
    ["tierra_us", "guaca_gifts_us", "navidad_us", "great_khan_us"], ["columbus", "guacanagari", "rodrigo_triana", "luis_torres"],
    {"columbus": ["standing", "strong"], "guacanagari": ["standing", "reigns"]}, [],
    [flag("columbus", "navidad_us")],
    [("tierra_us", ["rodrigo_triana", "columbus"]), ("guaca_gifts_us", ["columbus", "guacanagari"]), ("navidad_us", ["columbus", "guacanagari"])],
    "fact"))
TX.update(texts("columbus_1492", "Контакт",
    "Колумб ищет путь в Азию, а находит острова Карибского моря — встреча, после которой обе половины мира изменятся навсегда",
    "Заметить землю — дело матроса, а форт без помощи хозяев острова не построить. Искать Великого хана бесполезно: его здесь нет.",
    "12 октября 1492 года. Три испанских корабля плывут на запад уже больше месяца: генуэзец Христофор Колумб уверен, что так короче всего добраться до Китая и Индии. Королева обещала 10 000 мараведи тому, кто первым увидит землю. На борту есть переводчик — крещёный еврей Луис де Торрес, знающий арабский: с ним Колумб собирается говорить с Великим ханом.",
    "Землю первым увидел матрос Родриго де Триана, но пожизненную пенсию Колумб присудил себе — сказал, что заметил огонь ещё вечером. На острове Эспаньола касик таино Гуаканагари встретил пришельцев дружелюбно; когда в рождественскую ночь «Санта-Мария» села на риф, его люди помогли спасти груз, а из обломков построили форт Навидад — первое европейское поселение в Америке. Колумб так и умер уверенным, что был в Азии. Сам он не ступал на землю нынешних США, но именно с 1492 года начался «Колумбов обмен»: в Америку пришли лошади, пшеница и оспа, в Европу — картофель, кукуруза и табак. Для коренных народов он обернулся порабощением и эпидемиями, унёсшими большинство жителей островов за несколько десятилетий.",
    "Дневник первого плавания Колумба (в пересказе Лас Касаса); Альфред Кросби, «Колумбов обмен» (1972)"))

# ---------------------------------------------------------------- st_augustine_1565
CH += [C("menendez_aviles", "Педро Менендес де Авилес", "⚓"), C("ribault", "Жан Рибо", "⚜️"),
       C("saturiwa", "Вождь Сатурива", "🪶"), C("lopez_mendoza", "Капеллан Лопес де Мендоса", "✝️")]
SC += [
    scene("founding_mass_us", "Первая месса на берегу", ["sig_founding_mass_us"], 2, "✝️", "основать город", "icon_crown",
          ["капеллан", "адмирал"], "cathedral_altar"),
    scene("hurricane_us", "Ураган разбивает флот", ["sig_hurricane_us"], 1, "🌀", "выйти в море", "icon_dead",
          ["капитан"], "fireships"),
    scene("matanzas_us", "Бухта Матансас", ["sig_matanzas_us"], 2, "🗡️", "принять сдачу", "icon_dead",
          ["адмирал", "капитан"], "massacre_pass"),
    bait("saturiwa_talks_us", "Переговоры с Сатуривой", "v_parley", 2, "hostage_chief", PARLEY),
]
RU += [
    rule("founding_mass_us_sig", "Капеллан служит мессу, адмирал объявляет город Сан-Агустин",
         "sig_founding_mass_us", [actor("A", 0, tags=["lopez_mendoza"]), actor("B", 1, tags=["menendez_aviles"])], [setf("B", "founded_us")]),
    rule("hurricane_us_sig", "Француз ведёт флот на испанцев — ураган выбрасывает корабли на берег",
         "sig_hurricane_us", [actor("A", 0, tags=["ribault"])], [setf("A", "shipwrecked_us")]),
    rule("matanzas_strong_us_sig", "Нападать на целый французский флот — самоубийство",
         "sig_matanzas_us", [actor("A", 0, tags=["menendez_aviles"]), actor("B", 1, tags=["ribault"], notFlags=["shipwrecked_us"])],
         [setf("A", "defeated")]),
    rule("matanzas_us_sig", "Выброшенные на берег французы сдаются — и испанцы казнят их как еретиков",
         "sig_matanzas_us", [actor("A", 0, tags=["menendez_aviles"], flags=["founded_us"]), actor("B", 1, tags=["ribault"], flags=["shipwrecked_us"])],
         [setf("B", "dead")]),
]
LV.append(level("st_augustine_1565", 130, ACT2, "t", "founding_mass_us", 3,
    ["founding_mass_us", "hurricane_us", "matanzas_us", "saturiwa_talks_us"], ["menendez_aviles", "ribault", "saturiwa", "lopez_mendoza"],
    {"menendez_aviles": ["standing", "strong"], "ribault": ["standing", "strong"], "saturiwa": ["standing", "reigns"]}, [],
    [flag("menendez_aviles", "founded_us"), flag("ribault", "dead"), nflag("menendez_aviles", "defeated")],
    [("founding_mass_us", ["lopez_mendoza", "menendez_aviles"]), ("hurricane_us", ["ribault"]),
     ("matanzas_us", ["menendez_aviles", "ribault"])],
    "fact"))
TX.update(texts("st_augustine_1565", "Сан-Агустин",
    "Испанский адмирал основывает старейший город США — и уничтожает французских соперников, которых погубил ураган",
    "Город прежде войны. Атаковать сильный флот в лоб — гибель: подожди, пока природа сделает своё дело.",
    "1565 год. Во Флориде соперничают две империи и две веры: французские протестанты-гугеноты построили форт Каролина, а испанский король шлёт адмирала Педро Менендеса де Авилеса выбить «еретиков». Земли вокруг принадлежат тимукуа; их вождь Сатурива дружит с французами.",
    "8 сентября 1565 года капеллан Лопес де Мендоса отслужил мессу, и Менендес основал Сан-Агустин — старейший постоянно населённый европейский город на территории континентальных США. Француз Жан Рибо повёл флот на испанцев, но ураган разбил его корабли о берег. Менендес тем временем захватил форт Каролина, а затем у бухты встретил выброшенных на сушу французов: те сдались, и сотни из них, включая Рибо, казнили как протестантов. Бухту до сих пор называют Матансас — «бойня». Испанская Флорида продержалась больше двухсот лет; сюда, к испанцам, потом будут бежать беглецы из английских колоний.",
    "Франсиско Лопес де Мендоса Грахалес, «Записки» (1565); Гонсало Солис де Мерас, «Мемориал» (1567)"))

# ---------------------------------------------------------------- roanoke_1587
CH += [C("john_white", "Губернатор Джон Уайт", "🗺️"), C("eleanor_dare", "Элинор Дэр", "👶"), C("manteo", "Мантео", "🪶")]
SC += [
    scene("sail_supplies_us", "Отплыть за припасами", ["sig_sail_supplies_us"], 1, "⛵", "плыть в Англию", "icon_ally",
          ["губернатор"], "aboard_v"),
    scene("croatoan_carve_us", "Слово на столбе", ["sig_croatoan_carve_us"], 1, "🪵", "вырезать знак", "icon_plot",
          ["колонистка"], "forest_ambush"),
    scene("cross_carve_us", "Мальтийский крест — знак беды", ["sig_cross_carve_us"], 1, "✝️", "вырезать крест", "icon_dead",
          ["колонистка"], "forest_ambush"),
    scene("return_1590_us", "Возвращение через три года", ["sig_return_1590_us"], 2, "🏝️", "найти колонию", "icon_crown",
          ["губернатор", "колонистка"], "botany_bay"),
]
RU += [
    rule("sail_supplies_us_sig", "Губернатор уплывает за припасами — Англии вот-вот будет не до колоний: идёт Армада",
         "sig_sail_supplies_us", [actor("A", 0, tags=["john_white"])], [setf("A", "sailed_us")]),
    rule("cross_carve_us_sig", "Колонисты вырезают крест — условленный знак, что ушли в беде",
         "sig_cross_carve_us", [actor("A", 0, tags=["eleanor_dare"])], [setf("A", "distress_us")]),
    rule("croatoan_carve_us_sig", "Уходя, колонисты вырезают на столбе слово CROATOAN — без креста",
         "sig_croatoan_carve_us", [actor("A", 0, tags=["eleanor_dare"], notFlags=["distress_us"])], [setf("A", "word_us")]),
    rule("return_1590_us_sig", "Вернувшись, губернатор находит пустые дома и слово CROATOAN — без креста беды",
         "sig_return_1590_us", [actor("A", 0, tags=["john_white"], flags=["sailed_us"]), actor("B", 1, tags=["eleanor_dare"], flags=["word_us"])],
         [setf("A", "croatoan_found_us")]),
]
LV.append(level("roanoke_1587", 140, ACT2, "t", "return_1590_us", 3,
    ["sail_supplies_us", "croatoan_carve_us", "cross_carve_us", "return_1590_us"], ["john_white", "eleanor_dare", "manteo"],
    {"john_white": ["standing"]}, [],
    [flag("john_white", "croatoan_found_us"), nflag("eleanor_dare", "distress_us")],
    [("sail_supplies_us", ["john_white"]), ("croatoan_carve_us", ["eleanor_dare"]), ("return_1590_us", ["john_white", "eleanor_dare"])],
    "fact"))
TX.update(texts("roanoke_1587", "Пропавшая колония",
    "Губернатор уплывает за припасами, а вернувшись через три года, находит лишь слово CROATOAN на столбе",
    "Губернатор должен уплыть — иначе не будет и возвращения. Крест был условным знаком беды — а его не нашли.",
    "1587 год. На острове Роанок у берегов нынешней Северной Каролины высаживаются около 115 английских колонистов во главе с художником Джоном Уайтом. Его дочь Элинор Дэр рожает Вирджинию — первого ребёнка англичан, родившегося в Америке. Рядом — Мантео, человек из народа кроатоан, побывавший в Лондоне и ставший посредником.",
    "Уайт уплыл в Англию за припасами, договорившись: если колонисты уйдут, они вырежут название места, а если в беде — мальтийский крест. Вернуться ему не давали три года: Англия воевала с испанской Армадой. В августе 1590 года он нашёл пустые дома и вырезанное на столбе слово CROATOAN — без креста. Шторм не позволил доплыть до острова Кроатоан, и Уайт больше никогда не увидел ни дочери, ни внучки. Судьба колонии — главная загадка ранней Америки: вероятнее всего, колонисты разошлись и смешались с соседними алгонкинскими народами. Археологи до сих пор находят английские вещи на островах Хаттерас.",
    "Джон Уайт, отчёт о плавании 1590 года (в сборнике Ричарда Хаклюйта); Дэвид Куинн, «Курс на Роанок» (1985)"))

# ---------------------------------------------------------------- jamestown_1607
CH += [C("john_smith", "Капитан Джон Смит", "⚔️"), C("powhatan", "Вахунсенакау (Похатан)", "🪶"),
       C("matoaka", "Матоака (Покахонтас)", "🌸"), C("john_rolfe", "Джон Рольф", "🌿")]
SC += [
    scene("corn_trade_us", "Кукуруза в голодную зиму", ["sig_corn_trade_us"], 2, "🌽", "выменять еду", "icon_ally",
          ["капитан", "верховный вождь"], "hostage_chief"),
    scene("tobacco_us", "Сладкий табак с Тринидада", ["sig_tobacco_us"], 1, "🌿", "посадить табак", "icon_crown",
          ["плантатор"], "plough_field"),
    scene("rolfe_wedding_us", "Свадьба в Джеймстауне", ["sig_rolfe_wedding_us"], 3, "💍", "заключить союз", "icon_crown",
          ["жених", "невеста", "отец"], "palace_chapel"),
    scene("jamestown_raid_us", "Напасть на деревни Похатана", ["sig_jamestown_raid_us"], 2, "⚔️", "напасть", "icon_dead",
          ["нападающий", "защитник"], "forest_ambush"),
]
RU += [
    rule("corn_trade_us_sig", "Капитан выменивает кукурузу у людей верховного вождя — колония переживает зиму",
         "sig_corn_trade_us", [actor("A", 0, tags=["john_smith"]), actor("B", 1, tags=["powhatan"], notFlags=["at_war_us"])],
         [setf("A", "colony_fed_us")]),
    rule("tobacco_us_sig", "Плантатор сажает сладкий табак — у колонии появляется товар, за который Лондон платит золотом",
         "sig_tobacco_us", [actor("A", 0, tags=["john_rolfe"])], [setf("A", "tobacco_us")]),
    rule("raid_powhatan_us_sig", "Набег на деревни — и торговля кукурузой прекращается",
         "sig_jamestown_raid_us", [actor("A", 0, tags=["john_smith"]), actor("B", 1, tags=["powhatan"])], [setf("B", "at_war_us")]),
    rule("rolfe_wedding_us_sig", "Дочь верховного вождя, крещёная Ребеккой, выходит за табачного плантатора — наступает мир",
         "sig_rolfe_wedding_us", [actor("A", 0, tags=["john_rolfe"], flags=["tobacco_us"]), actor("B", 1, tags=["matoaka"]),
                                  actor("C", 2, tags=["powhatan"])],
         [setf("C", "peace_1614_us"), setf("A", "married"), setf("B", "married")]),
]
LV.append(level("jamestown_1607", 150, ACT2, "t", "corn_trade_us", 3,
    ["corn_trade_us", "tobacco_us", "rolfe_wedding_us", "jamestown_raid_us"], ["john_smith", "powhatan", "matoaka", "john_rolfe"],
    {"powhatan": ["standing", "reigns", "strong"], "john_smith": ["standing"]}, [],
    [flag("john_smith", "colony_fed_us"), flag("powhatan", "peace_1614_us")],
    [("corn_trade_us", ["john_smith", "powhatan"]), ("tobacco_us", ["john_rolfe"]), ("rolfe_wedding_us", ["john_rolfe", "matoaka", "powhatan"])],
    "simplification"))
TX.update(texts("jamestown_1607", "Джеймстаун и Похатан",
    "Голодающая английская колония выживает благодаря кукурузе Похатанской конфедерации, табаку и браку Покахонтас с Джоном Рольфом",
    "Кто кормит колонию — с тем не воюют. Мир скрепляют браком, но сначала у жениха должно быть, на что жить.",
    "1607 год. Сто четыре англичанина основывают Джеймстаун на болотистом берегу реки в Вирджинии. Вокруг — земли Похатанской конфедерации: тридцать с лишним народов под властью верховного вождя Вахунсенакау, которого англичане зовут Похатаном. Колонистов спасает от голода только торговля кукурузой.",
    "Капитан Джон Смит выменивал еду у людей Похатана; позже он рассказывал, что дочь вождя, Матоака по прозвищу Покахонтас, спасла его от казни, но историки сомневаются в этой красивой сцене. В «голодную зиму» 1609–1610 года колонисты дошли до людоедства. Спас колонию табак: Джон Рольф привёз сладкий сорт, и Вирджиния начала богатеть. В 1613 году англичане взяли Матоаку в заложницы; в плену её крестили под именем Ребекка, и в 1614 году она вышла за Рольфа — наступил «мир Покахонтас». В 1617 году она умерла в Англии, где её показывали как пример «цивилизованной индианки». Через четыре года после смерти Похатана, в 1622 году, война вспыхнула снова.",
    "Джон Смит, «Общая история Вирджинии» (1624); Камилла Таунсенд, «Покахонтас и дилемма Похатанов» (2004)"))

# ---------------------------------------------------------------- virginia_1619
CH += [C("yeardley", "Губернатор Джордж Йердли", "🎩"), C("john_pory", "Спикер Джон Пори", "📜"), C("burgess_us", "Бёрджесс", "🗳️")]
SC += [
    scene("great_charter_us", "Великая хартия компании", ["sig_great_charter_us"], 1, "📜", "огласить хартию", "icon_crown",
          ["губернатор"], "council"),
    scene("elect_burgess_us", "Выборы бёрджессов", ["sig_elect_burgess_us"], 2, "🗳️", "избрать представителя", "icon_ally",
          ["губернатор", "кандидат"], "council_b"),
    scene("first_assembly_us", "Первая ассамблея в церкви", ["sig_first_assembly_us"], 2, "🏛️", "открыть заседание", "icon_crown",
          ["спикер", "бёрджесс"], "chapel"),
    bait("summer_fever_us", "Разъехаться от жары и лихорадки", "v_flee", 1, "exile_road", ["кто уезжает"]),
]
RU += [
    rule("great_charter_us_sig", "Губернатор оглашает хартию компании: колонисты получают право на собственное собрание",
         "sig_great_charter_us", [actor("A", 0, tags=["yeardley"])], [setf("A", "charter_us")]),
    rule("elect_burgess_us_sig", "Свободные мужчины каждого поселения выбирают по двое представителей",
         "sig_elect_burgess_us", [actor("A", 0, tags=["yeardley"], flags=["charter_us"]), actor("B", 1, tags=["burgess_us"])],
         [setf("B", "elected_us")]),
    rule("first_assembly_us_sig", "В церкви Джеймстауна открывается первая выборная ассамблея в Америке",
         "sig_first_assembly_us", [actor("A", 0, tags=["john_pory"]), actor("B", 1, tags=["burgess_us"], flags=["elected_us"], notFlags=["away"])],
         [setf("A", "assembly_us")]),
]
LV.append(level("virginia_1619", 160, ACT2, "c", "first_assembly_us", 3,
    ["great_charter_us", "elect_burgess_us", "first_assembly_us", "summer_fever_us"], ["yeardley", "john_pory", "burgess_us", "john_rolfe"],
    {"yeardley": ["standing", "reigns"]}, [],
    [flag("john_pory", "assembly_us")],
    [("great_charter_us", ["yeardley"]), ("elect_burgess_us", ["yeardley", "burgess_us"]), ("first_assembly_us", ["john_pory", "burgess_us"])],
    "fact"))
TX.update(texts("virginia_1619", "1619: ассамблея и корабль «Белый лев»",
    "Вирджиния получает первое в Америке выборное собрание — и в том же году к её берегам привозят первых задокументированных африканцев",
    "Собрание начинается с права, данного хартией, и с выборов. Жара и лихорадка гонят депутатов прочь — но заседание надо довести до конца.",
    "1619 год. Вирджинская компания хочет привлечь колонистов и даёт им хартию: колония будет сама принимать часть законов. Губернатор Джордж Йердли объявляет выборы, а секретарь колонии Джон Пори станет спикером первого собрания.",
    "30 июля 1619 года в церкви Джеймстауна собралась Генеральная ассамблея — двадцать два бёрджесса от одиннадцати поселений. Это первое выборное законодательное собрание в английской Америке; заседание прервали через шесть дней из-за жары и малярии. В конце августа того же года к мысу Пойнт-Комфорт подошёл английский корсар «Белый лев» с «двадцатью с чем-то неграми» — людьми из Анголы, захваченными с португальского невольничьего корабля. Их обменяли на продовольствие. Это первые задокументированные африканцы в английской Вирджинии; одна из них, Анджела, упомянута в переписи 1625 года. Их правовой статус сначала был неопределённым, но в следующие десятилетия законы Вирджинии превратили рабство в пожизненное и наследственное — по расовому признаку. Свобода и рабство в Америке родились в одном году.",
    "Джон Пори, отчёт о заседании ассамблеи (1619); письмо Джона Рольфа Эдвину Сэндису (январь 1620)"))

# ---------------------------------------------------------------- mayflower_1620
CH += [C("bradford", "Уильям Брэдфорд", "📖"), C("carver", "Джон Карвер", "🎩"),
       C("hopkins_s", "Стивен Хопкинс", "😠"), C("standish", "Майлз Стэндиш", "🗡️")]
SC += [
    scene("north_landing_us", "Шторм уносит на север", ["sig_north_landing_us"], 1, "🌊", "встать у Кейп-Кода", "icon_plot",
          ["старейшина"], "fireships"),
    scene("compact_us", "Соглашение в каюте", ["sig_compact_us"], 2, "✍️", "подписать соглашение", "icon_crown",
          ["старейшина", "чужак"], "portsmouth_table"),
    scene("strangers_leave_us", "«Здесь нам никто не указ»", ["sig_strangers_leave_us"], 2, "🚪", "разойтись", "icon_dead",
          ["чужак", "капитан"], "exile_road"),
    scene("plymouth_rock_us", "Разведка берега", ["sig_plymouth_rock_us"], 2, "🧭", "выбрать место", "icon_ally",
          ["капитан", "летописец"], "botany_bay"),
]
RU += [
    rule("north_landing_us_sig", "Шторм уносит корабль к Кейп-Коду — за пределы хартии, данной на Вирджинию",
         "sig_north_landing_us", [actor("A", 0, tags=["carver"])], [setf("A", "no_charter_us")]),
    rule("strangers_leave_us_sig", "Чужаки кричат, что вне Вирджинии их никто не вправе судить, — колония раскалывается",
         "sig_strangers_leave_us", [actor("A", 0, tags=["hopkins_s"]), actor("B", 1, tags=["standish"])], [setf("A", "away")]),
    rule("compact_us_sig", "Сорок один мужчина подписывает соглашение о «гражданском политическом организме»; Карвер — губернатор",
         "sig_compact_us", [actor("A", 0, tags=["carver"], flags=["no_charter_us"]), actor("B", 1, tags=["hopkins_s"], notFlags=["away"])],
         [setf("B", "signed_us"), setf("A", "governor_us")]),
    rule("plymouth_rock_us_sig", "Отряд Стэндиша находит гавань с пресной водой и расчищенными полями — Плимут",
         "sig_plymouth_rock_us", [actor("A", 0, tags=["standish"]), actor("B", 1, tags=["bradford"])], [setf("B", "plymouth_us")]),
]
LV.append(level("mayflower_1620", 170, ACT2, "c", "compact_us", 3,
    ["north_landing_us", "compact_us", "strangers_leave_us", "plymouth_rock_us"], ["bradford", "carver", "hopkins_s", "standish"],
    {"standish": ["standing", "strong"]}, [],
    [flag("carver", "governor_us"), flag("hopkins_s", "signed_us"), flag("bradford", "plymouth_us")],
    [("north_landing_us", ["carver"]), ("compact_us", ["carver", "hopkins_s"]), ("plymouth_rock_us", ["standish", "bradford"])],
    "fact"))
TX.update(texts("mayflower_1620", "Соглашение «Мэйфлауэра»",
    "Шторм уносит пилигримов за пределы их хартии — и, чтобы не разбежаться, они сами подписывают договор о власти",
    "Без беды нет и нужды в договоре. Уговори того, кто хочет уйти, — а не отпускай его.",
    "Ноябрь 1620 года. После 66 дней в океане «Мэйфлауэр» с 102 пассажирами подходит к Америке. Около сорока из них — «святые», пуритане-сепаратисты, бежавшие от английской церкви; остальные — «чужаки», нанятые ремесленники и слуги. У них хартия на поселение в Вирджинии, но шторм уносит корабль далеко на север.",
    "Вне Вирджинии хартия не действовала, и некоторые «чужаки» заявили, что сойдя на берег, будут делать что хотят. Среди них, вероятно, был Стивен Хопкинс — в 1609 году он уже участвовал в бунте потерпевших крушение на Бермудах. 11 ноября 41 мужчина подписал в каюте Мэйфлауэрское соглашение: они «сочетаются в гражданский политический организм» и будут подчиняться законам, принятым для общего блага. Губернатором избрали Джона Карвера. Разведка Майлза Стэндиша нашла гавань с полями, расчищенными людьми вампаноаг — селение которых недавно опустошила эпидемия. В первую зиму умерла половина колонистов. Женщины соглашение не подписывали — но оно стало одним из первых документов американского самоуправления.",
    "Уильям Брэдфорд, «О Плимутской плантации» (1630–1651); текст Мэйфлауэрского соглашения (1620)"))

# ---------------------------------------------------------------- plymouth_1621
CH += [C("squanto", "Тисквантум (Скуанто)", "🐟"), C("massasoit", "Осамекин (Массасоит)", "🪶"), C("winslow_e", "Эдвард Уинслоу", "📝")]
SC += [
    scene("corn_lesson_us", "Кукуруза и рыба в лунке", ["sig_corn_lesson_us"], 2, "🌽", "научить сажать", "icon_ally",
          ["учитель", "губернатор"], "plough_field"),
    scene("treaty_1621_us", "Договор с вампаноагами", ["sig_treaty_1621_us"], 3, "🤝", "заключить союз", "icon_crown",
          ["сахем", "переводчик", "губернатор"], "council_b"),
    scene("harvest_feast_us", "Три дня урожайного пира", ["sig_harvest_feast_us"], 2, "🦃", "разделить урожай", "icon_crown",
          ["сахем", "губернатор"], "feast"),
    bait("plymouth_muskets_us", "Салют из мушкетов", "v_prepare", 1, "militia_muster", ["кто стреляет"]),
]
RU += [
    rule("corn_lesson_us_sig", "Скуанто учит колонистов сажать кукурузу, подкладывая в лунку рыбу",
         "sig_corn_lesson_us", [actor("A", 0, tags=["squanto"]), actor("B", 1, tags=["bradford"])], [setf("B", "harvest_us")]),
    rule("treaty_1621_us_sig", "Через переводчика вампаноаги и колонисты обещают не вредить друг другу и помогать против врагов",
         "sig_treaty_1621_us", [actor("A", 0, tags=["massasoit"]), actor("B", 1, tags=["squanto"]), actor("C", 2, tags=["bradford"])],
         [setf("A", "allied_1621_us"), setf("C", "allied_1621_us")]),
    rule("harvest_feast_us_sig", "Сахем приходит с девяноста воинами, приносит пять оленей — три дня пира",
         "sig_harvest_feast_us", [actor("A", 0, tags=["massasoit"], flags=["allied_1621_us"]), actor("B", 1, tags=["bradford"], flags=["harvest_us"])],
         [setf("B", "feast_us")]),
]
LV.append(level("plymouth_1621", 180, ACT2, "c", "harvest_feast_us", 3,
    ["corn_lesson_us", "treaty_1621_us", "harvest_feast_us", "plymouth_muskets_us"], ["squanto", "massasoit", "bradford", "winslow_e"],
    {"massasoit": ["standing", "reigns", "strong"]}, [],
    [flag("bradford", "feast_us")],
    [("corn_lesson_us", ["squanto", "bradford"]), ("treaty_1621_us", ["massasoit", "squanto", "bradford"]),
     ("harvest_feast_us", ["massasoit", "bradford"])],
    "simplification"))
TX.update(texts("plymouth_1621", "Урожайный пир",
    "Скуанто учит пилигримов сажать кукурузу, Массасоит заключает союз — и осенью 1621 года они вместе празднуют урожай",
    "Без урожая праздновать нечего, а без переводчика двум народам не договориться.",
    "Весна 1621 года. В Плимуте за зиму умерла половина колонистов. В поселение входит индеец Самосет и здоровается по-английски, а вскоре приводит Тисквантума, или Скуанто, из народа патуксет. Когда-то англичане похитили его и продали в рабство в Испании; он сбежал, жил в Лондоне и, вернувшись домой, нашёл свою деревню вымершей от эпидемии.",
    "Скуанто научил пилигримов сажать кукурузу, кладя в лунку рыбу как удобрение, и стал переводчиком на переговорах с Осамекином — верховным сахемом вампаноагов, которого англичане называли Массасоит. Союз был выгоден обеим сторонам: ослабленные эпидемией вампаноаги искали защиты от соседей-наррагансеттов. Осенью колонисты устроили праздник урожая; Массасоит пришёл с девяноста воинами и принёс пять оленей, и пир длился три дня. Его не называли «Днём благодарения» — национальным праздником он стал только в 1863 году при Линкольне. Союз Массасоита с Плимутом продержался пятьдесят лет, до войны его сына Метакома.",
    "Эдвард Уинслоу, письмо из «Отношения Мурта» (1622); Уильям Брэдфорд, «О Плимутской плантации»"))

if __name__ == "__main__":
    run(CH, SC, RU, LV, TX)
