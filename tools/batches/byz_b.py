#!/usr/bin/env python3
"""Пачка B главы «Византия»: 7 новых уровней (идемпотентно).

    python3 byz_b.py [repo_root]

Делает: upsert сцен/правил в Content/rome/{scenes,rules}.json, пишет
Content/byzantium/levels/<id>.json, копирует арт сцен (копии существующих файлов —
ничего не генерирует), upsert-ит ключи в Content/i18n/ru.json, перенумеровывает
order соседних уровней актов VI–VII (только поле order — в актах не было целых
промежутков, а iOS декодирует order как Int).
"""
import json, os, shutil, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
CONTENT = os.path.join(ROOT, "Content")
SCENES = os.path.join(CONTENT, "rome", "scenes.json")
RULES = os.path.join(CONTENT, "rome", "rules.json")
CHARS = os.path.join(CONTENT, "rome", "characters.json")
RU = os.path.join(CONTENT, "i18n", "ru.json")
ART = os.path.join(CONTENT, "art")
LEVELS = os.path.join(CONTENT, "byzantium", "levels")

ACT6 = "Акт VI · Иконы и Македонцы"
ACT7 = "Акт VII · Крестоносцы и падение"
ACT5 = "Акт V · Ираклий и ислам"
ACT4 = "Акт IV · Слава и закат"


def scene(id, name, tags, slots, emoji, action, icon, roles, art_donor):
    s = {"id": id, "name": name, "tags": tags, "slots": slots, "emoji": emoji,
         "action": action, "actionIcon": icon, "roles": roles}
    s["_art"] = art_donor
    return s


def rule(id, comment, tags, actors, effects, priority=10):
    return {"id": id, "comment": comment, "priority": priority,
            "trigger": {"sceneTags": tags, "actors": actors}, "effects": effects}


def A(var, slot, tags=None, flags=None, notFlags=None, relations=None):
    a = {"var": var, "slot": slot}
    if tags: a["tags"] = tags
    if flags: a["flags"] = flags
    if notFlags: a["notFlags"] = notFlags
    if relations: a["relations"] = relations
    return a


def setf(t, f): return {"type": "setFlag", "target": t, "flag": f}
def remf(t, f): return {"type": "removeFlag", "target": t, "flag": f}
def addr(rel, a, b): return {"type": "addRelation", "rel": rel, "from": a, "to": b}
def remr(rel, a, b): return {"type": "removeRelation", "rel": rel, "from": a, "to": b}
def F(c, f): return {"flag": {"char": c, "is": f}}
def R(rel, a, b): return {"relation": {"rel": rel, "from": a, "to": b}}
def NOT(x): return {"not": x}


# ---------------------------------------------------------------- сцены
NEW_SCENES = [
    # --- secret_history
    scene("wars_dictation", "«Войны»: шатёр полководца", ["sig_b2_wars"], 2, "📜",
          "записывать походы за полководцем", "icon_ally", ["летописец", "полководец"], "africa_b"),
    scene("anekdota_desk", "Ночь над рукописью", ["sig_b2_anekdota"], 2, "🕯️",
          "писать в стол о том, чего нельзя сказать вслух", "icon_plot", ["летописец", "героиня пасквиля"], "slander_b"),
    scene("buildings_praise", "«О постройках»", ["sig_b2_buildings"], 2, "🏛️",
          "восславить строителя Святой Софии", "icon_crown", ["летописец", "император"], "hagia"),
    scene("copyists_forum", "Переписчики Августеона", ["sig_b2_publish"], 1, "📖",
          "отдать рукопись переписчикам", "icon_dead", ["автор"], "sophia_library"),
    scene("confide_antonina", "Жена полководца", ["sig_b2_confide"], 2, "🤫",
          "показать рукопись наперснице императрицы", "icon_plot", ["летописец", "наперсница"], "intrigue_b"),
    # --- heraclius_coup
    scene("africa_grain", "Хлеб Африки", ["sig_b2_grain"], 2, "🌾",
          "перекрыть столице хлебные корабли", "icon_plot", ["сын экзарха", "тиран"], "pelusium_grain"),
    scene("persian_front", "Персы на Евфрате", ["v_battle"], 2, "💥",
          "битва", "icon_dead", ["нападающий", "защитник"], "persian_border"),
    scene("fleet_610", "Флот из Карфагена, 610", ["v_prepare"], 1, "⛵",
          "подготовка", "icon_ally", ["кто снаряжает флот"], "carthage_fleet"),
    scene("so_you_ruled", "«Так ли ты правил?»", ["sig_b2_ruled"], 2, "🩸",
          "спросить связанного — и казнить", "icon_dead", ["победитель", "в цепях"], "chalcedon_pier"),
    scene("khosrow_envoys", "Посольство к Хосрову", ["v_bribe"], 2, "💰",
          "подкуп", "icon_plot", ["плательщик", "покупаемый"], "pay_arabs"),
    # --- romanos_blinded
    scene("adana_field", "Под Аданой", ["v_battle"], 2, "💥",
          "битва", "icon_dead", ["нападающий", "защитник"], "manzikert_field"),
    scene("bishops_oath", "Клятва трёх епископов", ["sig_b2_bishops"], 2, "✝️",
          "обещать жизнь под присягой епископов", "icon_ally", ["дука", "разбитый"], "oak_synod"),
    scene("kotyaion_road", "Котиэй, 29 июня 1072", ["sig_b2_kotyaion"], 2, "🩸",
          "ослепить вопреки клятве", "icon_dead", ["клятвопреступник", "монах"], "exile_road"),
    scene("sultan_rescue", "Султан идёт на выручку", ["v_rescue"], 2, "🏹",
          "выручка", "icon_ally", ["кто выручает", "разбитый"], "sultan_boot"),
    scene("sultan_refuge", "Уйти к султану", ["v_flee"], 1, "🐎",
          "уход", "icon_ally", ["уходящий"], "khliat_fort"),
    # --- bohemond_antioch
    scene("two_sisters_tower", "Башня Двух Сестёр", ["sig_b2_firouz"], 1, "🪜",
          "купить башню у армянина Фируза", "icon_plot", ["норманн"], "chalke_ladder"),
    scene("philomelion", "Филомелий", ["v_flee"], 1, "🐎",
          "уход", "icon_ally", ["кто поворачивает назад"], "flee_thrace"),
    scene("prince_of_antioch", "Князь Антиохии", ["sig_b2_claim"], 2, "🏰",
          "оставить город себе: император не пришёл", "icon_crown", ["крестоносец", "император"], "nicaea_banners"),
    scene("hand_over_antioch", "Вернуть город империи", ["v_parley"], 2, "🤝",
          "переговоры", "icon_ally", ["кто требует", "кто уступает"], "emperor_mediates"),
    scene("dorylaeum", "Дорилей", ["v_battle"], 2, "⚔️",
          "битва", "icon_dead", ["нападающий", "защитник"], "nicaea_siege"),
    # --- zara
    scene("san_marco_cross", "Крест на Сан-Марко", ["sig_b2_cross_doge"], 1, "✝️",
          "нашить крест на шапку слепого дожа", "icon_crown", ["дож"], "venice_denounce"),
    scene("zara_walls", "Стены Зары", ["sig_b2_zara"], 1, "⚔️",
          "взять христианский город за долг", "icon_dead", ["дож"], "april_1204"),
    scene("papal_anathema", "Отлучение", ["sig_b2_anathema"], 2, "📜",
          "отлучить всё войско", "icon_dead", ["папа", "отлучаемый"], "anathema"),
    scene("papal_legate", "Легат папы", ["v_parley"], 2, "⛪",
          "переговоры", "icon_ally", ["кто требует", "кто уступает"], "bull_on_altar"),
    # --- theophano_widow
    scene("caesarea_shield", "Кесария, 2 июля 963", ["sig_b2_shield"], 2, "🛡️",
          "поднять на щит по уговору племянника", "icon_crown", ["полководец", "племянник"], "danube_winter"),
    scene("godfather_oath", "Крёстный отец", ["sig_b2_godfather"], 2, "⛪",
          "поклясться, что он не крестил её детей", "icon_ally", ["император", "вдова"], "palace_chapel"),
    scene("nea_wedding", "Венчание в Новой церкви", ["v_wed"], 2, "💒",
          "свадьба", "icon_love", ["император", "вдова"], "nuptial"),
    # --- mehmed_ultimatum
    scene("urban_foundry", "Литейщик Урбан", ["sig_b2_urban"], 2, "💣",
          "не заплатить мастеру — и отдать его султану", "icon_plot", ["кто не заплатил", "кто заплатил"], "urban_bombard"),
    scene("lemnos_promise", "Остров Лемнос", ["v_bribe"], 2, "💰",
          "подкуп", "icon_plot", ["император", "кондотьер"], "palace_gold"),
    scene("st_romanus_gate", "Ворота святого Романа", ["sig_b2_gate"], 2, "🛡️",
          "поставить кондотьера во главе обороны", "icon_ally", ["кондотьер", "император"], "giustiniani_wounded"),
    scene("morea_offer", "Удел в Морее", ["v_parley", "sig_b2_defy"], 2, "🌙",
          "ответить на ультиматум", "icon_crown", ["султан", "император"], "ultimatum"),
    scene("rumeli_hisar", "Богазкесен", ["v_prepare"], 1, "🏰",
          "подготовка", "icon_ally", ["кто готовится"], "khliat_fort"),
]

# ---------------------------------------------------------------- правила
NEW_RULES = [
    # secret_history
    rule("b2_wars_sig", "Секретарь Велизария записывает его походы — так рождается историк «Войн»",
         ["sig_b2_wars"], [A("A", 0, tags=["writer_b"], notFlags=["away"]), A("B", 1, tags=["strategos"])],
         [setf("A", "historian"), setf("A", "standing")]),
    rule("b2_anekdota_sig", "Историк, вхожий ко двору, пишет в стол о бывшей актрисе — «Тайную историю»; разоблачённый уже ничего не пишет",
         ["sig_b2_anekdota"], [A("A", 0, tags=["writer_b"], flags=["historian"], notFlags=["exposed"]), A("B", 1, tags=["actress"])],
         [setf("A", "anekdota"), setf("B", "slandered")]),
    rule("b2_buildings_sig", "С пасквилем в ящике стола он пишет императору панегирик «О постройках»",
         ["sig_b2_buildings"], [A("A", 0, tags=["writer_b"], flags=["anekdota"], notFlags=["exposed"]), A("B", 1, tags=["augustus"])],
         [setf("B", "praised"), setf("A", "court_favour")]),
    rule("b2_publish_sig", "Отдать «Тайную историю» переписчикам при живом императоре — смерть автора",
         ["sig_b2_publish"], [A("A", 0, flags=["anekdota"])],
         [setf("A", "exposed"), setf("A", "dead")]),
    rule("b2_confide_sig", "Наперсница императрицы доносит — автор разоблачён",
         ["sig_b2_confide"], [A("A", 0, flags=["anekdota"]), A("B", 1, tags=["confidante"])],
         [setf("A", "exposed")]),
    # heraclius_coup
    rule("b2_grain_sig", "Экзарх Африки перекрывает столице хлеб — тиран без зерна теряет войско и голодает; разбитый или воюющий с персами этого не сделает",
         ["sig_b2_grain"], [A("A", 0, tags=["basileus"], notFlags=["defeated", "at_war", "away"]),
                            A("B", 1, tags=["usurper_b"], flags=["reigns"])],
         [setf("B", "starved"), remf("B", "strong"), setf("A", "standing")]),
    rule("b2_ruled_sig", "«Так ли ты правил империей?» — «А ты будешь править лучше?» Сильный сын экзарха казнит разбитого и голодного тирана и коронуется в тот же день",
         ["sig_b2_ruled"], [A("A", 0, tags=["basileus"], flags=["strong", "standing"], notFlags=["at_war", "defeated"]),
                            A("B", 1, tags=["usurper_b"], flags=["starved", "defeated"], notFlags=["strong"])],
         [setf("B", "dead"), setf("B", "executed"), remf("B", "reigns"),
          setf("A", "crowned"), setf("A", "reigns")]),
    # romanos_blinded
    rule("b2_bishops_sig", "Разбитому императору три епископа клянутся, что его не тронут, — он сдаётся и принимает постриг; выручённый или ушедший не сдаётся",
         ["sig_b2_bishops"], [A("A", 0, tags=["doukas"], notFlags=["defeated"]),
                              A("B", 1, tags=["basileus_m"], flags=["defeated"], notFlags=["away", "grateful"])],
         [setf("B", "surrendered"), setf("B", "tonsured"), setf("A", "sworn_safety")]),
    rule("b2_kotyaion_sig", "Клятву трёх епископов нарушают: сдавшегося монаха ослепляют на дороге в Котиэе",
         ["sig_b2_kotyaion"], [A("A", 0, tags=["doukas"], flags=["sworn_safety"]), A("B", 1, flags=["surrendered"])],
         [setf("B", "blinded"), remf("B", "standing"), setf("A", "oathbreaker")]),
    # bohemond_antioch
    rule("b2_firouz_sig", "Норманн подкупает начальника Башни Двух Сестёр и входит в Антиохию; купленный, уступивший, ушедший или разбитый башен не покупает",
         ["sig_b2_firouz"], [A("A", 0, tags=["crusader"], notFlags=["bought", "conceded", "away", "defeated"])],
         [setf("A", "inside_antioch")]),
    rule("b2_claim_sig", "Император повернул назад — клятва Влахерн ничтожна: вошедший в город норманн зовёт себя князем Антиохии",
         ["sig_b2_claim"], [A("A", 0, tags=["crusader"], flags=["inside_antioch"], notFlags=["bought", "conceded", "away"]),
                            A("B", 1, tags=["basileus_k"], flags=["away"])],
         [setf("A", "prince"), setf("A", "oathbreaker"), setf("B", "cheated"),
          remr("ally_of", "A", "B"), remr("ally_of", "B", "A")]),
    # zara
    rule("b2_cross_doge_sig", "Слепой дож сам берёт крест в Сан-Марко — теперь он крестоносец и сила похода; уступивший папе никуда не плывёт",
         ["sig_b2_cross_doge"], [A("A", 0, tags=["doge"], notFlags=["conceded"])],
         [setf("A", "cross_taken"), setf("A", "strong"), setf("A", "standing")]),
    rule("b2_zara_sig", "Дож-крестоносец ведёт войско на христианскую Зару — за долг; купленный царевичем пошёл бы прямо на Царьград",
         ["sig_b2_zara"], [A("A", 0, tags=["doge"], flags=["cross_taken"], notFlags=["conceded", "bought"])],
         [setf("A", "zara_taken"), setf("A", "victor")]),
    rule("b2_anathema_sig", "Папа отлучает того, кто поднял меч на христианский город",
         ["sig_b2_anathema"], [A("A", 0, tags=["pope_i"]), A("B", 1, flags=["zara_taken"])],
         [setf("B", "excommunicated"), setf("A", "standing")]),
    # theophano_widow
    rule("b2_shield_sig", "Племянник уговаривает — и войско под Кесарией поднимает сильного полководца на щит",
         ["sig_b2_shield"], [A("A", 0, tags=["basileus"], flags=["strong"]), A("B", 1, tags=["general"])],
         [setf("A", "acclaimed"), setf("A", "crowned"), setf("A", "reigns"), setf("B", "kingmaker")]),
    rule("b2_godfather_sig", "Патриарх против: он крёстный её детей. Священник клянётся, что нет, — препятствие снято",
         ["sig_b2_godfather"], [A("A", 0, tags=["basileus"], flags=["acclaimed"]), A("B", 1, tags=["basilissa"], flags=["locked_out"])],
         [remf("B", "locked_out"), setf("B", "dispensed")]),
    # mehmed_ultimatum
    rule("b2_urban_sig", "Император не может заплатить литейщику — мастер уходит к султану, и пушка теперь у султана",
         ["sig_b2_urban"], [A("A", 0, tags=["basileus"], notFlags=["away"]), A("B", 1, tags=["sultan"])],
         [setf("B", "cannon"), setf("B", "strong"), setf("A", "no_gold")]),
    rule("b2_gate_sig", "Кондотьер, которому обещан остров, встаёт во главе обороны у ворот святого Романа — и город снова сила",
         ["sig_b2_gate"], [A("A", 0, tags=["genoese"], flags=["bought"], relations=[{"rel": "ally_of", "to": "B"}]),
                           A("B", 1, tags=["basileus"], notFlags=["away", "conceded"])],
         [setf("A", "commander"), setf("B", "strong")]),
    rule("b2_defy_sig", "Султан с пушкой предлагает жизнь и Морею за город; сильный император отвечает: город не в его власти отдать",
         ["sig_b2_defy"], [A("A", 0, tags=["sultan"], flags=["cannon"]),
                           A("B", 1, tags=["basileus"], flags=["strong"], notFlags=["away", "conceded"])],
         [setf("B", "defiant"), setf("A", "resolved")], priority=12),
]

# ---------------------------------------------------------------- уровни
def level(id, order, act, music, cover, panels, scenes, chars, flags, rels, goal, solution, accuracy):
    return {"id": id, "order": order, "epoch": "byzantium", "act": act, "music": music, "cover": cover,
            "panels": panels, "scenes": scenes, "characters": chars,
            "initialState": {"flags": flags, "relations": rels},
            "goal": goal, "solution": [{"scene": s, "characters": c} for s, c in solution],
            "factCard": {"accuracy": accuracy}}


LEVELS_DEF = [
    level("secret_history", 132, ACT4, "tension", "anekdota_desk", 3,
          ["wars_dictation", "anekdota_desk", "buildings_praise", "copyists_forum", "confide_antonina"],
          ["procopius", "belisarius", "theodora", "justinian", "antonina"],
          {"procopius": ["standing"], "belisarius": ["standing", "strong"], "theodora": ["queen", "standing"],
           "justinian": ["reigns", "standing"], "antonina": ["standing"]}, [],
          {"all": [F("theodora", "slandered"), F("justinian", "praised"), F("procopius", "anekdota"),
                   NOT(F("procopius", "exposed"))]},
          [("wars_dictation", ["procopius", "belisarius"]), ("anekdota_desk", ["procopius", "theodora"]),
           ("buildings_praise", ["procopius", "justinian"])], "simplification"),

    level("heraclius_coup", 138, ACT5, "tension", "so_you_ruled", 4,
          ["africa_grain", "fleet_610", "persian_front", "so_you_ruled", "khosrow_envoys"],
          ["heraclius", "phocas_c", "khosrow"],
          {"heraclius": ["standing"], "phocas_c": ["reigns", "crowned", "strong", "standing"],
           "khosrow": ["strong", "standing"]},
          [["enemy_of", "khosrow", "phocas_c"], ["enemy_of", "khosrow", "heraclius"], ["enemy_of", "heraclius", "khosrow"]],
          {"all": [F("phocas_c", "dead"), F("heraclius", "crowned")]},
          [("africa_grain", ["heraclius", "phocas_c"]), ("fleet_610", ["heraclius"]),
           ("persian_front", ["khosrow", "phocas_c"]), ("so_you_ruled", ["heraclius", "phocas_c"])], "simplification"),

    level("romanos_blinded", 158, ACT6, "tension", "kotyaion_road", 3,
          ["adana_field", "bishops_oath", "kotyaion_road", "sultan_rescue", "sultan_refuge"],
          ["romanos4", "andronikos_doukas", "alp_arslan"],
          {"romanos4": ["ransomed", "standing"], "andronikos_doukas": ["strong", "standing", "traitor"],
           "alp_arslan": ["strong", "standing"]},
          [["enemy_of", "andronikos_doukas", "romanos4"]],
          {"all": [F("romanos4", "blinded"), F("andronikos_doukas", "oathbreaker")]},
          [("adana_field", ["andronikos_doukas", "romanos4"]), ("bishops_oath", ["andronikos_doukas", "romanos4"]),
           ("kotyaion_road", ["andronikos_doukas", "romanos4"])], "fact"),

    level("bohemond_antioch", 161, ACT7, "tension", "prince_of_antioch", 3,
          ["two_sisters_tower", "philomelion", "prince_of_antioch", "hand_over_antioch", "dorylaeum"],
          ["alexios1", "bohemond", "kilij"],
          {"alexios1": ["reigns", "standing", "strong"], "bohemond": ["sworn", "standing"], "kilij": ["standing"]},
          [["ally_of", "alexios1", "bohemond"], ["ally_of", "bohemond", "alexios1"],
           ["enemy_of", "bohemond", "kilij"], ["enemy_of", "kilij", "bohemond"]],
          {"all": [F("bohemond", "prince"), F("alexios1", "cheated"), NOT(F("bohemond", "conceded"))]},
          [("two_sisters_tower", ["bohemond"]), ("philomelion", ["alexios1"]),
           ("prince_of_antioch", ["bohemond", "alexios1"])], "simplification"),

    level("zara", 162, ACT7, "tension", "zara_walls", 4,
          ["san_marco_cross", "zara_walls", "papal_anathema", "promise_marks", "papal_legate"],
          ["dandolo", "alexios4", "innocent3"],
          {"dandolo": ["standing"], "alexios4": ["standing"], "innocent3": ["standing"]}, [],
          {"all": [F("dandolo", "zara_taken"), F("dandolo", "excommunicated"), F("dandolo", "bought"),
                   R("ally_of", "alexios4", "dandolo"), NOT(F("dandolo", "conceded"))]},
          [("san_marco_cross", ["dandolo"]), ("zara_walls", ["dandolo"]),
           ("papal_anathema", ["innocent3", "dandolo"]), ("promise_marks", ["alexios4", "dandolo"])], "simplification"),

    level("theophano_widow", 154, ACT6, "theme", "caesarea_shield", 3,
          ["caesarea_shield", "godfather_oath", "nea_wedding", "theophano_lover", "hippodrome_honour"],
          ["nikephoros", "theophano", "tzimiskes"],
          {"nikephoros": ["strong", "standing"], "theophano": ["locked_out", "standing"], "tzimiskes": ["standing"]}, [],
          {"all": [F("nikephoros", "acclaimed"), R("wed", "nikephoros", "theophano"), F("theophano", "queen"),
                   NOT(R("loves", "theophano", "tzimiskes"))]},
          [("caesarea_shield", ["nikephoros", "tzimiskes"]), ("godfather_oath", ["nikephoros", "theophano"]),
           ("nea_wedding", ["nikephoros", "theophano"])], "simplification"),

    level("mehmed_ultimatum", 168, ACT7, "tension", "morea_offer", 4,
          ["urban_foundry", "lemnos_promise", "st_romanus_gate", "morea_offer", "rumeli_hisar", "leave_city"],
          ["constantine11", "mehmed2", "giustiniani"],
          {"constantine11": ["reigns", "crowned", "standing"], "mehmed2": ["reigns", "standing"], "giustiniani": ["standing"]},
          [["enemy_of", "constantine11", "mehmed2"], ["enemy_of", "mehmed2", "constantine11"]],
          {"all": [F("constantine11", "defiant"), F("mehmed2", "cannon"), F("giustiniani", "commander"),
                   NOT(F("constantine11", "conceded")), NOT(F("mehmed2", "bought"))]},
          [("urban_foundry", ["constantine11", "mehmed2"]), ("lemnos_promise", ["constantine11", "giustiniani"]),
           ("st_romanus_gate", ["giustiniani", "constantine11"]), ("morea_offer", ["mehmed2", "constantine11"])],
          "simplification"),
]

# перенумерация order соседей (только поле order; относительный порядок сохранён)
REORDER = {"phokas": 155, "basil_bulgar": 156, "manzikert": 157, "schism": 159,
           "komnenos_crusade": 160, "sack_1204": 163}

# ---------------------------------------------------------------- тексты
TEXTS = {
    "secret_history": {
        "title": "Тайная история",
        "goal": "Летописец славит императора-строителя в книге — и прячет в стол пасквиль, который прочтут через тысячу лет",
        "hint": "Сначала походы с полководцем — так становятся историком. Пасквиль об актрисе — ночью, в стол; и лишь потом, с ядом в ящике, — хвала императору. Переписчикам и наперснице рукопись не показывать: при живом императоре это смерть.",
        "intro": "Прокопий из Кесарии — секретарь Велизария, свидетель Ники, чумы и всех войн Юстиниана. Днём он пишет то, что можно читать при дворе. Ночью — то, за что убивают: об императоре-демоне и об императрице из ипподрома.",
        "fact": "Прокопий Кесарийский с 527 года служил при Велизарии советником и секретарём и по горячим следам написал «Войны» в восьми книгах — официальную историю царствования. Около 550 года он же тайно закончил «Анекдоту» («Неизданное»): Юстиниан там — демон, который по ночам ходит по дворцу без головы, Феодора — актриса с непристойными номерами с гусями, а Велизарий — подкаблучник Антонины. Между 554 и 560 годами он написал панегирик «О постройках» — во славу того же императора и той же Святой Софии. Рукопись пасквиля пролежала в тайне тысячу лет: её нашли в Ватиканской библиотеке и издали лишь в 1623 году. Почти всё, что мы знаем о Юстиниане и Феодоре, рассказано одним человеком — и который из его голосов лжёт, спорят до сих пор.",
        "source": "Прокопий Кесарийский, «Тайная история» (Anekdota); «Войны»; «О постройках»",
    },
    "heraclius_coup": {
        "title": "«Так ли ты правил?»",
        "goal": "Африка перекрывает столице хлеб, персы бьют тирана — и сын экзарха входит в гавань, чтобы задать связанному Фоке один вопрос",
        "hint": "Сначала хлеб: тиран без африканского зерна теряет войско. Ослабевшего бьёт сильный Хосров — тот, кто мстит за Маврикия. Флот — сила сына экзарха. И только сильный, не воевавший с персами, судит разбитого и голодного тирана. К Хосрову с золотом не ходи — мира он не примет.",
        "intro": "Восемь лет Фока правит террором; Хосров II ведёт войну «за Маврикия» и берёт город за городом. В Карфагене экзарх Африки и его сын Ираклий решают, что империя не переживёт этого императора. У них есть хлеб, которым кормится столица, и флот.",
        "fact": "В 608 году экзарх Африки Ираклий Старший поднял мятеж и перекрыл поставки африканского и египетского зерна в Константинополь; в столице начался голод. Персы Хосрова II тем временем взяли Эдессу и Амиду и вышли к Евфрату. Осенью 610 года Ираклий-младший привёл из Карфагена флот; синие открыли гавань, гвардия перешла на его сторону. Связанного Фоку приволокли на корабль, и Ираклий спросил: «Так ли ты правил империей?» — «А ты будешь править лучше?» — ответил тот. Фоку обезглавили, тело сожгли на Бычьем форуме; 5 октября 610 года патриарх Сергий короновал Ираклия, и в тот же день он обвенчался. Новый император тут же предложил Хосрову мир — тот отказал, и война, начатая «за Маврикия», продлилась ещё восемнадцать лет.",
        "source": "Иоанн Никиусский, «Хроника», CIX–CX; Феофан Исповедник, «Хронография»; Chronicon Paschale",
    },
    "romanos_blinded": {
        "title": "Клятва трёх епископов",
        "goal": "Султан отпустил императора — свои разбили его, дали слово трёх епископов и ослепили вопреки слову",
        "hint": "Сначала поле под Аданой: сильный Дука бьёт вернувшегося из плена. Разбитому обещают жизнь под присягой епископов — он сдаётся и принимает постриг. И тогда клятвопреступник ослепляет монаха. Султан — не спаситель в этой истории: выручать разбитого ему не давай.",
        "intro": "Алп-Арслан отпустил Романа с миром и дарами — но пока он шёл домой, в столице клан Дук провозгласил императором его пасынка. Роману пишут: сложи венец. Он не складывает. Против него посылают Андроника Дуку — того, кто увёл арьергард с Манцикертского поля.",
        "fact": "Освобождённый Алп-Арсланом Роман IV узнал в пути, что 24 октября 1071 года его низложили; в столице правили Михаил VII и кесарь Иоанн Дука. Роман собрал войска в Каппадокии и был дважды разбит — под Докией и весной 1072 года у Аданы, где имперской армией командовал Андроник Дука. Он сдался под письменную клятву трёх епископов — Халкидонского, Гераклейского и Колонейского, — что его не тронут, и принял постриг. Кесарь Иоанн приказал ослепить его; 29 июня 1072 года в Котиэе это сделал неумелый палач, и Роман умер от заражения через несколько недель на острове Проте. Михаил Пселл написал ему письмо с поздравлением: Бог, мол, отнял у него глаза, потому что счёл достойным высшего света. Алп-Арслан, узнав, сказал, что клятва ромеев ничего не стоит, — и погиб в том же году.",
        "source": "Михаил Атталиат, «История»; Михаил Пселл, «Хронография», VII",
    },
    "bohemond_antioch": {
        "title": "Князь Антиохии",
        "goal": "Норманн покупает башню, император поворачивает назад — и клятва, данная во Влахернах, разорвана: Антиохия остаётся Боэмунду",
        "hint": "Башню Двух Сестёр покупает тот, кто не куплен, никому не уступил и не разбит. Император должен повернуть назад в Филомелии — уйти. И только тогда норманн, вошедший в город, объявляет себя князем перед тем, кто не пришёл. Уговоры вернуть город — путь к другой истории; в этой он не вернулся.",
        "intro": "Восемь месяцев крестоносцы стоят под Антиохией, голодают и едят коней. Боэмунд тайно сговорился с армянином Фирузом, начальником башни, — и требует у вождей: город достанется тому, кто его возьмёт, если император не придёт на помощь. Алексей Комнин с войском идёт через Анатолию.",
        "fact": "Осада Антиохии длилась с октября 1097 по 3 июня 1098 года. Боэмунд подкупил Фируза, армянина-вероотступника, командовавшего Башней Двух Сестёр, и заранее вытребовал у остальных вождей согласие: город достанется тому, кто его возьмёт, если Алексей не явится. В ночь на 3 июня его люди поднялись по лестницам — Антиохия пала. Через два дня к городу подошёл Кербога из Мосула и осадил осаждавших. Дезертир Стефан Блуаский встретил Алексея в Филомелии и уверил его, что крестоносцы обречены; император повернул назад. 28 июня крестоносцы, обретя Святое Копьё, разбили Кербогу — и Боэмунд объявил клятву Влахерн ничтожной: император не пришёл. Раймунд Тулузский спорил, но остался в меньшинстве. В 1108 году по Девольскому договору Боэмунд признал себя вассалом Алексея за Антиохию — и больше в неё не вернулся; умер в 1111 году в Апулии.",
        "source": "Анна Комнина, «Алексиада», XI; «Деяния франков» (Gesta Francorum); Раймунд Ажильский, «История франков, взявших Иерусалим»",
    },
    "zara": {
        "title": "Зара",
        "goal": "Слепой дож нашивает крест, ведёт крестоносцев на христианский город за долг, получает отлучение — и предложение царевича",
        "hint": "Сначала крест на Сан-Марко: дож — крестоносец и сила. Только крестоносец берёт Зару — и не купленный: посулы царевича приходят после. Отлучает папа того, кто уже взял город. Легата слушать нельзя: уступивший папе дож никуда не поплывёт.",
        "intro": "Крестоносцы собрались в Венеции, но их втрое меньше, чем договаривались, и они должны республике тридцать четыре тысячи марок. Слепой дож Дандоло знает, как отработать долг: на пути лежит Зара — христианский город, отпавший к венгерскому королю. Папа Иннокентий грозит отлучением всякому, кто поднимет меч на христиан.",
        "fact": "По договору 1201 года Венеция построила флот на 33 500 крестоносцев за 85 000 марок, но к лету 1202 года собралось около 12 000, и войско недоплатило 34 000. Дож Энрико Дандоло, слепой и, по хронистам, за восемьдесят, предложил отсрочку в обмен на помощь против Зары и в сентябре 1202 года в Сан-Марко сам взял крест — Виллардуэн пишет, что его нашили на его хлопковую шапку. Иннокентий III через легата Петра Капуанского запретил нападать на христиан под страхом отлучения; письмо утаили от войска. Зара пала 24 ноября 1202 года после пяти дней осады; папа отлучил всё войско, потом простил франков — но не венецианцев, и Дандоло скрыл это от рядовых. 1 января 1203 года в Зару прибыли послы царевича Алексея с обещанием двухсот тысяч марок, унии церквей и войска — и флот повернул на Константинополь.",
        "source": "Жоффруа де Виллардуэн, «Завоевание Константинополя», §§ 56–108; регистры Иннокентия III, V, 160–161",
    },
    "theophano_widow": {
        "title": "Вдова и полководец",
        "goal": "Племянник поднимает полководца на щит, священник клянётся, что тот не крестил детей вдовы, — и «бледная смерть сарацин» женится на императрице",
        "hint": "Сначала Кесария: сильного полководца поднимают на щит по уговору племянника. Провозглашённому снимают препятствие — духовное родство с вдовой. И только тогда венчание: император и вдова, в этом порядке. Любовь императрицы и племянника — через шесть лет, не в этой серии; и венчать её с ним не надо.",
        "intro": "Роман II умер в двадцать четыре года — говорят, вдова помогла. Феофано, дочь трактирщика, — регентша при двух малолетних сыновьях; евнух Вринга хочет ослепить Никифора Фоку, покорителя Крита. Племянник Никифора, Иоанн Цимисхий, привозит дяде эту новость в лагерь под Кесарией.",
        "fact": "После смерти Романа II 15 марта 963 года регентшей при Василии и Константине стала Феофано, а власть держал паракимомен Иосиф Вринга. Он попытался перекупить Иоанна Цимисхия против Никифора Фоки; Цимисхий рассказал дяде и, по Льву Диакону, уговорил его взять венец. 2 июля 963 года войско под Кесарией подняло Никифора на щит, 16 августа патриарх Полиевкт короновал его в Святой Софии, а 20 сентября он обвенчался с Феофано в Новой церкви. Полиевкт запретил ему вход в алтарь: Никифор был крёстным отцом её детей, а духовное родство — препятствие к браку; тогда священник Стилиан и отец императора Варда поклялись, что крёстным он не был, и патриарх уступил. Через шесть лет та же Феофано откроет тому же Цимисхию окно спальни, а на гробнице Никифора напишут: «Ты победил всех, кроме женщины».",
        "source": "Лев Диакон, «История», II–III; Иоанн Скилица, «Обозрение историй»",
    },
    "mehmed_ultimatum": {
        "title": "Ультиматум",
        "goal": "Пушка Урбана достаётся султану, Джустиниани получает ворота и остров — и император отвечает на предложение уйти в Морею: город не в его власти отдать",
        "hint": "Литейщику не заплатил император — заплатил султан: пушка у султана. Кондотьеру обещают Лемнос — купленный берёт ворота святого Романа, и император снова сила. Только сильному есть чем ответить на ультиматум сильного; слабый уступит. Уплыть в Морею он отказался; султана не купить.",
        "intro": "Весна 1453 года. У султана Мехмеда восемьдесят тысяч и крепость Богазкесен на Босфоре; у Константина — семь тысяч, цепь через Золотой Рог и венгр Урбан, который просит за свою пушку денег, каких в казне нет. Из Генуи приплыл кондотьер Джустиниани с семью сотнями латников. Султан предлагает императору жизнь и удел в Морее — за город.",
        "fact": "В 1452 году венгерский литейщик Урбан предложил свою бомбарду Константину XI — тот не смог заплатить, и мастер ушёл к Мехмеду, который дал вчетверо больше: пушку длиной восемь метров, стрелявшую ядрами в полтонны, тащили из Эдирне шестьдесят быков. 26 января 1453 года в город на двух кораблях пришёл генуэзец Джованни Джустиниани Лонго с семью сотнями воинов; император поставил его во главе обороны у ворот святого Романа и обещал ему остров Лемнос. Перед решающим штурмом Мехмед в последний раз предложил сдать город: Константину — жизнь и Морея, жителям — свобода. По Дуке, император ответил: «Отдать тебе город не в моей власти и ни в чьей из живущих в нём — мы все единодушно решили умереть по своей воле». Это было за три дня до 29 мая.",
        "source": "Дука, «Византийская история», XXXV, XXXVIII–XXXIX; Георгий Сфрандзи, «Хроника»",
    },
}


# ---------------------------------------------------------------- IO
def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, data, trailing_nl):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        if trailing_nl:
            f.write("\n")


def ends_nl(p):
    with open(p, "rb") as f:
        f.seek(-1, os.SEEK_END)
        return f.read(1) == b"\n"


def upsert(items, new, what):
    by_id = {x["id"]: i for i, x in enumerate(items)}
    added = updated = 0
    for n in new:
        if n["id"] in by_id:
            if items[by_id[n["id"]]] != n:
                items[by_id[n["id"]]] = n
                updated += 1
        else:
            items.append(n)
            by_id[n["id"]] = len(items) - 1
            added += 1
    print(f"{what}: +{added} added, {updated} updated")


def main():
    chars = {c["id"] for c in load(CHARS)}
    for lv in LEVELS_DEF:
        missing = [c for c in lv["characters"] if c not in chars]
        assert not missing, f"{lv['id']}: нет персонажей {missing}"

    # сцены
    scenes_nl = ends_nl(SCENES)
    scenes = load(SCENES)
    existing = {s["id"] for s in scenes}
    clean_scenes = []
    for s in NEW_SCENES:
        donor = s.pop("_art")
        src = os.path.join(ART, f"scene_{donor}.webp")
        dst = os.path.join(ART, f"scene_{s['id']}.webp")
        assert os.path.exists(src), f"нет донора арта {src}"
        if not os.path.exists(dst):
            shutil.copyfile(src, dst)
            print(f"art: scene_{s['id']}.webp <- scene_{donor}.webp")
        clean_scenes.append(s)
    upsert(scenes, clean_scenes, "scenes")
    dump(SCENES, scenes, scenes_nl)
    scene_ids = {s["id"] for s in scenes}
    for lv in LEVELS_DEF:
        miss = [x for x in lv["scenes"] + [lv["cover"]] if x not in scene_ids]
        assert not miss, f"{lv['id']}: нет сцен {miss}"

    # правила
    rules_nl = ends_nl(RULES)
    rules = load(RULES)
    upsert(rules, NEW_RULES, "rules")
    dump(RULES, rules, rules_nl)

    # уровни
    os.makedirs(LEVELS, exist_ok=True)
    for lv in LEVELS_DEF:
        p = os.path.join(LEVELS, f"{lv['id']}.json")
        dump(p, lv, True)
    # перенумерация соседей
    for lid, order in REORDER.items():
        p = os.path.join(LEVELS, f"{lid}.json")
        d = load(p)
        if d["order"] != order:
            d["order"] = order
            dump(p, d, ends_nl(p))
            print(f"order: {lid} -> {order}")
    print(f"levels: {len(LEVELS_DEF)} written")

    # i18n (ru): как extract.py — indent=1, ensure_ascii=False, sort_keys=True, ничего не стирает
    cat = load(RU)
    n = 0
    for lid, t in TEXTS.items():
        for k, v in t.items():
            key = f"level.{lid}.{k}"
            if cat.get(key) != v:
                cat[key] = v
                n += 1
    for s in clean_scenes:
        for key, v in ((f"scene.{s['id']}", s["name"]), (f"scene.{s['id']}.action", s["action"])):
            if cat.get(key) != v:
                cat[key] = v
                n += 1
    with open(RU, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print(f"i18n ru: {n} keys upserted")


if __name__ == "__main__":
    main()
