#!/usr/bin/env python3
"""Пачка B главы «Италия» (epoch borgia): 10 уровней.

Идемпотентно: upsert сцен/правил в Content/rome/{scenes,rules}.json (по id),
запись Content/borgia/levels/<id>.json, копия арта сцен (донор → новая сцена),
upsert ключей в Content/i18n/ru.json (indent=1, ensure_ascii=False, sort_keys=True),
перенумерация order внутри акта I (целые order, свободных номеров не было).

    python3 italy_b.py [repo_root]
"""
import json, os, shutil, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
def rp(*p): return os.path.join(ROOT, *p)

SCENES = rp("Content/rome/scenes.json")
RULES = rp("Content/rome/rules.json")
CATALOG = rp("Content/i18n/ru.json")
LEVELS = rp("Content/borgia/levels")
ART = rp("Content/art")

ACT1 = "Акт I · Гвельфы и гибеллины"
ACT3 = "Акт III · Яд и власть"
ACT5 = "Акт V · Медичи и Макиавелли"
ACT6 = "Акт VI · Инквизиция"
ACT7 = "Акт VII · Рисорджименто"

# ---------------------------------------------------------------- helpers
def scene(id, name, tags, slots, emoji, action, icon, roles, donor):
    s = {"id": id, "name": name, "tags": tags, "slots": slots, "emoji": emoji,
         "action": action, "actionIcon": icon}
    if roles:
        s["roles"] = roles
    return s, donor

def actor(var, slot=None, tags=None, flags=None, notFlags=None, relations=None):
    a = {"var": var}
    if slot is not None: a["slot"] = slot
    if tags: a["tags"] = tags
    if flags: a["flags"] = flags
    if notFlags: a["notFlags"] = notFlags
    if relations: a["relations"] = relations
    return a

def setf(t, f): return {"type": "setFlag", "target": t, "flag": f}
def remf(t, f): return {"type": "removeFlag", "target": t, "flag": f}
def addr(rel, a, b): return {"type": "addRelation", "rel": rel, "from": a, "to": b}

def rule(id, comment, sceneTag, actors, effects, priority=10):
    return {"id": id, "comment": comment, "priority": priority,
            "trigger": {"sceneTags": [sceneTag], "actors": actors}, "effects": effects}

def flag(c, f): return {"flag": {"char": c, "is": f}}
def nflag(c, f): return {"not": flag(c, f)}

def level(id, order, act, music, cover, panels, scenes, chars, flags, rels, goal, solution, accuracy):
    return {
        "id": id, "order": order, "epoch": "borgia", "act": act, "music": music,
        "cover": cover, "panels": panels, "scenes": scenes, "characters": chars,
        "initialState": {"flags": flags, "relations": [list(r) for r in rels]},
        "goal": {"all": goal},
        "solution": [{"scene": s, "characters": c} for s, c in solution],
        "factCard": {"accuracy": accuracy},
    }

def texts(id, title, goal, hint, intro, fact, source):
    return {f"level.{id}.title": title, f"level.{id}.goal": goal, f"level.{id}.hint": hint,
            f"level.{id}.intro": intro, f"level.{id}.fact": fact, f"level.{id}.source": source}

NEW_SCENES = []   # (scene, donor)
NEW_RULES = []
NEW_LEVELS = []
TEXTS = {}

# ================================================================ 1. francis_sultan (1219)
NEW_SCENES += [
    scene("take_the_cross", "Взять меч, как в юности", ["v_prepare"], 1, "⚔️", "подготовка", "icon_ally",
          ["кто вооружается"], "militia_muster"),
    scene("cross_the_lines", "Через линию фронта", ["sig_cross_lines"], 1, "🕊️", "идти к врагу без оружия",
          "icon_ally", ["пилигрим"], "desert_march"),
    scene("sultan_tent", "Шатёр аль-Камиля", ["sig_sultan_tent"], 2, "🌙", "проповедовать султану", "icon_crown",
          ["пилигрим", "султан"], "jaffa_treaty"),
    scene("damietta_siege", "Штурм Дамиетты", ["v_battle"], 2, "🏰", "битва", "icon_dead",
          ["нападающий", "защитник"], "storm_jerusalem"),
]
NEW_RULES += [
    rule("cross_lines_sig", "Нищий без оружия идёт через линию под Дамиеттой; дозорные бьют его и ведут к султану",
         "sig_cross_lines",
         [actor("A", 0, tags=["friar_i"], notFlags=["strong", "at_war", "away"])],
         [setf("A", "unarmed"), setf("A", "standing")]),
    rule("sultan_tent_sig", "Султан несколько дней слушает проповедь, отказывается от предложенного золота и отпускает с охранной грамотой",
         "sig_sultan_tent",
         [actor("A", 0, tags=["friar_i"], flags=["unarmed"]),
          actor("B", 1, tags=["sultan_i"], notFlags=["defeated"])],
         [setf("A", "heard"), setf("A", "safe_conduct"), setf("B", "merciful"),
          addr("ally_of", "A", "B"), addr("ally_of", "B", "A")]),
]
NEW_LEVELS.append(level(
    "francis_sultan", 2, ACT1, "theme", "sultan_tent", 2,
    ["take_the_cross", "cross_the_lines", "sultan_tent", "damietta_siege"],
    ["francis", "al_kamil", "frederick2"],
    {"al_kamil": ["reigns", "standing", "strong"], "frederick2": ["crowned", "standing"]},
    [("enemy_of", "al_kamil", "frederick2"), ("enemy_of", "frederick2", "al_kamil")],
    [flag("francis", "heard"), flag("al_kamil", "merciful"), nflag("frederick2", "at_war")],
    [("cross_the_lines", ["francis"]), ("sultan_tent", ["francis", "al_kamil"])],
    "fact"))
TEXTS.update(texts("francis_sultan",
    "Франциск и султан",
    "Нищий монах переходит линию фронта без оружия — и султан, вместо того чтобы отрубить ему голову, отпускает его с миром",
    "Сначала — через линию под Дамиеттой безоружным: взявший меч уже не пилигрим. Безоружного пилигрима султан слушает и отпускает. Император в Дамиетту так и не приехал — не ведите его в бой.",
    "Пятый крестовый поход застрял под Дамиеттой в дельте Нила. Крестоносцы ждут императора Фридриха II, который взял крест четыре года назад и всё не едет. В лагерь приходит нищий из Ассизи и просит у легата позволения пойти к султану — проповедовать.",
    "В сентябре 1219 года, после разгрома крестоносцев 29 августа, Франциск с братом Иллюминатом перешёл линию фронта под Дамиеттой; сарацинские дозорные избили их и привели к султану аль-Камилю, племяннику Саладина. Султан несколько дней слушал проповедь, предложил золото — Франциск отказался — и отпустил обоих с охранной грамотой; в Ассизи до сих пор хранят подаренный султаном рог из слоновой кости. Тогда же аль-Камиль предлагал крестоносцам Иерусалим в обмен на уход из Египта — легат Пелагий отказался, в ноябре взял Дамиетту, а в 1221-м потерял и её, и войско в разливе Нила. Фридрих II, которого ждали под Дамиеттой, приплыл на Восток лишь в 1228-м и получил Иерусалим у того же аль-Камиля — договором, без боя.",
    "Жак де Витри, письмо 1220 г.; Фома Челанский, «Первое житие»; Бонавентура, «Большая легенда»"))

# ================================================================ 2. bordeaux_duel (1283)
NEW_SCENES += [
    scene("challenge_bordeaux", "Вызов на сто рыцарей", ["sig_challenge_b"], 2, "🧤", "бросить перчатку", "icon_plot",
          ["вызывающий", "вызванный"], "duel_challenge"),
    scene("lists_bordeaux", "Ристалище в Бордо", ["sig_lists_b"], 1, "🏇", "явиться в свой час", "icon_crown",
          ["король"], "saint_antoine_lists"),
    scene("duel_field_b", "Бой ста на сто", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "duel_h"),
    scene("ask_edward", "Судья — Эдуард", ["v_parley"], 2, "⚖️", "переговоры", "icon_ally",
          ["кто требует", "кто уступает"], "treaty_king"),
    scene("messina_council", "Совет в Мессине", ["v_plot"], 2, "🗡️", "заговор", "icon_plot",
          ["заговорщик", "король"], "aragon_pact"),
]
NEW_RULES += [
    rule("challenge_b_sig", "Анжуец вызывает врага на суд Божий: сто рыцарей против ста, в Бордо, 1 июня — оба клянутся приехать",
         "sig_challenge_b",
         [actor("A", 0, tags=["angevin"], notFlags=["at_war"]),
          actor("B", 1, tags=["king"], relations=[{"rel": "enemy_of", "to": "A"}])],
         [setf("A", "duel_set"), setf("B", "duel_set")]),
    rule("lists_b_sig", "Король выезжает на ристалище один, в свой час, требует от сенешаля запись о явке — и объявляет противника трусом",
         "sig_lists_b",
         [actor("A", 0, tags=["king"], flags=["duel_set"], notFlags=["at_war", "appeared", "away"])],
         [setf("A", "appeared"), setf("A", "standing")]),
]
NEW_LEVELS.append(level(
    "bordeaux_duel", 5, ACT1, "tension", "lists_bordeaux", 3,
    ["challenge_bordeaux", "lists_bordeaux", "duel_field_b", "ask_edward", "messina_council"],
    ["charles_anjou", "peter_aragon", "edward1", "procida"],
    {"charles_anjou": ["crowned", "standing"], "peter_aragon": ["crowned", "standing"],
     "edward1": ["crowned", "standing"]},
    [("enemy_of", "charles_anjou", "peter_aragon"), ("enemy_of", "peter_aragon", "charles_anjou")],
    [flag("charles_anjou", "appeared"), flag("peter_aragon", "appeared"),
     nflag("charles_anjou", "at_war"), nflag("edward1", "conceded")],
    [("challenge_bordeaux", ["charles_anjou", "peter_aragon"]),
     ("lists_bordeaux", ["peter_aragon"]), ("lists_bordeaux", ["charles_anjou"])],
    "fact"))
TEXTS.update(texts("bordeaux_duel",
    "Поединок в Бордо",
    "Два короля вызывают друг друга на бой ста рыцарей против ста — и оба приезжают на ристалище в разное время, чтобы объявить другого трусом",
    "Сначала вызов: анжуец бросает перчатку врагу. Потом ристалище — но на нём одно место: каждый король выходит на поле один, в свой час. Судьёй должен был быть Эдуард — и отказался; а скрестить мечи значит сделать то, чего не было.",
    "После Сицилийской вечерни Карл Анжуйский потерял остров, а Педро Арагонский надел его корону. Вместо войны Карл предлагает решить спор по-рыцарски: сто рыцарей против ста, в Бордо, на землях английского короля Эдуарда, 1 июня 1283 года. Папа запрещает Эдуарду судить. Оба короля клянутся приехать.",
    "Утром 1 июня 1283 года Педро Арагонский, проехавший через всю Испанию под видом слуги торговца лошадьми, въехал на ристалище в Бордо с тремя спутниками, заявил сенешалю Эдуарда, что явился, потребовал письменного свидетельства — и ускакал до полудня. В назначенный час приехал Карл Анжуйский со своей сотней рыцарей, объехал пустое поле и объявил противника клятвопреступником; то же самое о Карле объявил Педро. Эдуард I по запрету папы Мартина IV отказался судить, и бой не состоялся: поединок был нужен обоим лишь как повод не воевать в неудобный момент. Пока короли меряли честь, адмирал Педро Руджеро ди Лаурия 8 июня разбил анжуйский флот у Мальты, а в 1284-м взял в плен сына Карла в Неаполитанском заливе; сам Карл умер в январе 1285-го, так и не вернув Сицилию.",
    "Бернат Десклот, «Хроника»; Бартоломео да Неокастро, «Сицилийская история»; С. Рансимен, «Сицилийская вечерня»"))

# ================================================================ 3. cola_death (1354)
NEW_SCENES += [
    scene("avignon_pardon", "Авиньон: снять отлучение", ["sig_pardon_c"], 2, "📜", "сделать узника сенатором", "icon_crown",
          ["папа", "узник"], "avignon_pope"),
    scene("wine_tax", "Налог на вино", ["sig_wine_tax"], 1, "🍷", "обложить Рим налогом", "icon_plot",
          ["сенатор"], "fruit_tax"),
    scene("capitol_fire_1354", "Капитолий горит", ["sig_capitol_fire"], 2, "🔥", "отдать толпе", "icon_dead",
          ["барон", "сенатор"], "capitol_mob_i"),
    scene("beggar_disguise", "Переодеться нищим", ["v_flee"], 1, "🧥", "уход", "icon_ally",
          ["сенатор"], "escape"),
]
NEW_RULES += [
    rule("pardon_c_sig", "Папе нужен свой человек в Риме: с еретика снимают отлучение и посылают его сенатором вместе с легатом",
         "sig_pardon_c",
         [actor("A", 0, tags=["pope"]),
          actor("B", 1, tags=["tribune_i"], flags=["condemned"])],
         [setf("B", "senator"), setf("B", "standing"), remf("B", "condemned"), remf("B", "away")]),
    rule("wine_tax_sig", "Наёмникам надо платить: сенатор вводит налог на вино и соль — город, носивший его на руках, теперь его ненавидит",
         "sig_wine_tax",
         [actor("A", 0, tags=["tribune_i"], flags=["senator"], notFlags=["rallied"])],
         [setf("A", "hated"), remf("A", "standing")]),
    rule("capitol_fire_sig", "Бароны подстрекают толпу; Капитолий горит, сенатор мажет лицо сажей — его выдают золотые браслеты",
         "sig_capitol_fire",
         [actor("A", 0, tags=["baron"], notFlags=["bought", "defeated"]),
          actor("B", 1, tags=["tribune_i"], flags=["hated"], notFlags=["away"])],
         [setf("B", "dead"), setf("A", "avenged")]),
]
NEW_LEVELS.append(level(
    "cola_death", 10, ACT1, "tension", "capitol_fire_1354", 3,
    ["avignon_pardon", "wine_tax", "capitol_fire_1354", "capitol_tribune", "bribe_barons", "beggar_disguise"],
    ["cola", "colonna", "pope"],
    {"cola": ["condemned", "away"], "colonna": ["standing", "strong"], "pope": ["crowned", "standing"]},
    [("enemy_of", "cola", "colonna"), ("enemy_of", "colonna", "cola")],
    [flag("cola", "senator"), flag("cola", "dead"), flag("colonna", "avenged"), nflag("cola", "rallied")],
    [("avignon_pardon", ["pope", "cola"]), ("wine_tax", ["cola"]), ("capitol_fire_1354", ["colonna", "cola"])],
    "simplification"))
TEXTS.update(texts("cola_death",
    "Возвращение трибуна",
    "Помилованный папой трибун возвращается в Рим сенатором — и, обложив римлян налогом на вино, гибнет от толпы, которая семь лет назад несла его на руках",
    "Сначала Авиньон: папа снимает отлучение — узник становится сенатором. Сенатор вводит налог на вино — Рим его ненавидит. Ненавидимого сенатора бароны отдают толпе. Объявлять себя трибуном снова бесполезно: во второй раз Рим не поднялся. Откупаться от Колонны и переодеваться нищим — тоже.",
    "Бежавший из Рима трибун семь лет скитался: жил у отшельников, пророчествовал императору Карлу IV в Праге, сидел в цепях в Авиньоне. Папе Иннокентию VI нужен свой человек в Риме — и он снимает с еретика отлучение, чтобы отправить его сенатором вместе с легатом Альборносом. Рим встречает его цветами. Ненадолго.",
    "1 августа 1354 года Кола ди Риенцо вернулся в Рим папским сенатором с наёмниками, нанятыми на деньги братьев кондотьера фра Мориале; через месяц он обезглавил самого Мориале, чтобы забрать его казну. Чтобы платить солдатам, он ввёл налог на вино и соль — и город, который в 1347-м носил его на руках, возненавидел его. 8 октября толпа с криком «Смерть предателю!» подожгла Капитолий; Кола вымазал лицо сажей, накинул пастушеский плащ и попытался уйти вместе с грабителями, но его выдали золотые браслеты на руках. Его закололи на ступенях Капитолия, тело два дня висело за ноги у Сан-Марчелло, напротив дворца Колонна, потом его сожгли. Через пять веков Вагнер напишет о нём оперу «Риенци», а Муссолини поставит ему статую у подножия Капитолия.",
    "Anonimo romano, «Жизнь Кола ди Риенцо» (XIV в.); Ф. Грегоровиус, «История города Рима в Средние века», кн. XI"))

# ================================================================ 4. lorenzo_deathbed (1492)
NEW_SCENES += [
    scene("prior_san_marco", "Приор Сан-Марко", ["sig_prior_sm"], 1, "⛪", "не идти на поклон", "icon_crown",
          ["монах"], "pulpit_e"),
    scene("careggi_bedside", "Постель в Кареджи", ["sig_bedside_c"], 2, "🕯️", "позвать и исповедаться", "icon_ally",
          ["умирающий", "монах"], "deathbed_m"),
    scene("face_to_wall", "Лицом к стене", ["sig_wall_c"], 1, "🧱", "не вернуть Флоренции свободу", "icon_dead",
          ["умирающий"], "deathbed"),
    scene("gold_for_san_marco", "Золото в монастырскую кружку", ["v_bribe"], 2, "💰", "подкуп", "icon_plot",
          ["плательщик", "монах"], "bank_loan"),
    scene("pearl_potion", "Толчёный жемчуг", ["sig_pearls_c"], 1, "💊", "выпить снадобье врача", "icon_dead",
          ["больной"], "poison_vial"),
]
NEW_RULES += [
    rule("prior_sm_sig", "Избранный приор отказывается, по обычаю, явиться к Лоренцо: «Меня избрал Бог, а не он»",
         "sig_prior_sm",
         [actor("A", 0, tags=["friar"], notFlags=["bought"])],
         [setf("A", "prior"), setf("A", "standing")]),
    rule("bedside_c_sig", "Умирающий зовёт единственного, кто ему не кланялся; тот ставит три условия — на два первых Лоренцо говорит «да»",
         "sig_bedside_c",
         [actor("A", 0, tags=["medici"], flags=["dying"]),
          actor("B", 1, tags=["friar"], flags=["prior"], notFlags=["bought"])],
         [setf("A", "confessed"), setf("B", "unbending"), setf("B", "at_bedside")]),
    rule("wall_c_sig", "Третье условие — вернуть Флоренции свободу; Лоренцо отворачивается к стене, монах уходит без отпущения",
         "sig_wall_c",
         [actor("A", 0, tags=["medici"], flags=["confessed"])],
         [setf("A", "refused_liberty"), setf("A", "unabsolved"), setf("A", "dead")]),
    rule("pearls_c_sig", "Врач Пьер Леони поит больного толчёным жемчугом с самоцветами; наутро самого врача найдут в колодце",
         "sig_pearls_c",
         [actor("A", 0, tags=["medici"], flags=["dying"], notFlags=["confessed"])],
         [setf("A", "dead"), setf("A", "poisoned")]),
]
NEW_LEVELS.append(level(
    "lorenzo_deathbed", 14, ACT1, "theme", "careggi_bedside", 3,
    ["prior_san_marco", "careggi_bedside", "face_to_wall", "gold_for_san_marco", "pearl_potion"],
    ["lorenzo", "savonarola", "rodrigo"],
    {"lorenzo": ["dying", "standing"], "savonarola": ["standing"], "rodrigo": ["standing"]},
    [],
    [flag("lorenzo", "unabsolved"), flag("lorenzo", "dead"), flag("savonarola", "unbending"),
     nflag("savonarola", "bought")],
    [("prior_san_marco", ["savonarola"]), ("careggi_bedside", ["lorenzo", "savonarola"]), ("face_to_wall", ["lorenzo"])],
    "legend"))
TEXTS.update(texts("lorenzo_deathbed",
    "Смертный одр Лоренцо",
    "Умирающий Лоренцо зовёт монаха, который отказался ему кланяться, — и, по легенде, тот уходит без отпущения: свободы Флоренции Медичи не вернул",
    "Сначала Сан-Марко: монах — приор и никому не кланяется. Только неподкупного приора умирающий зовёт к постели — и исповедуется. Потом — лицом к стене: третьего условия он не выполнит. Золото на монастырь купит кого угодно, только не этого монаха; кардинал Борджиа отпустил бы грехи за деньги — но у постели он бесполезен. Жемчуг врача раньше времени — смерть без исповеди.",
    "Апрель 1492 года, вилла Кареджи. Лоренцо Великолепному сорок три, подагра добралась до сердца; врач поит его толчёным жемчугом. Он пережил заговор Пацци, папское отлучение и войну — и просит позвать единственного человека во Флоренции, который отказался прийти к нему на поклон: приора Сан-Марко Джироламо Савонаролу.",
    "Лоренцо умер вечером 8 апреля 1492 года в Кареджи. Его секретарь Полициано, бывший при этом, писал, что Савонарола пришёл, призвал умирающего к твёрдости в вере и благословил его. Но спустя годы последователи монаха рассказали другое: он поставил три условия — веровать (Лоренцо ответил «да»), вернуть отнятое («да») и вернуть Флоренции свободу; тут Лоренцо отвернулся к стене, и монах ушёл без отпущения. Проверить нельзя: обе версии писали заинтересованные люди. Точно известно, что в 1491-м Савонарола, избранный приором, отказался, по обычаю, явиться к Лоренцо — «меня избрал Бог, а не он», — а золото, присланное в монастырскую кружку, раздал бедным. Врача Пьера Леони, поившего больного жемчугом, на следующий день нашли в колодце; Полициано умер через два года, Пико делла Мирандола — в день, когда войска Карла VIII входили во Флоренцию, а Савонарола четыре года правил городом и кончил на костре.",
    "А. Полициано, письмо Якопо Антиквари (май 1492); П. Бурламакки, «Жизнь Савонаролы»; Р. Ридольфи, «Жизнь Джироламо Савонаролы»"))

# ================================================================ 5. imola_1502
NEW_SCENES += [
    scene("engineer_patent", "Патент генерального инженера", ["v_bribe"], 2, "📜", "подкуп", "icon_plot",
          ["плательщик", "кого нанимают"], "hire_condottieri"),
    scene("map_of_imola", "План Имолы", ["sig_map_i"], 2, "🗺️", "вымерить город шагами", "icon_crown",
          ["инженер", "герцог"], "plan_t"),
    scene("envoy_watches", "Посол при герцоге", ["sig_envoy_i"], 2, "✒️", "наблюдать и писать депеши", "icon_ally",
          ["посол", "герцог"], "ask_post"),
    scene("imola_meeting", "Встреча в Имоле", ["v_befriend"], 2, "🤝", "дружба", "icon_ally", None, "old_friends"),
]
NEW_RULES += [
    rule("map_i_sig", "Нанятый инженер вымеряет Имолу шагами и одометром и чертит первый в Европе план города «сверху»; крепости герцога в порядке",
         "sig_map_i",
         [actor("A", 0, tags=["artist"], flags=["bought"], relations=[{"rel": "ally_of", "to": "B"}]),
          actor("B", 1, tags=["borgia"])],
         [setf("A", "cartographer"), setf("B", "fortified")]),
    rule("envoy_i_sig", "Посол без полномочий три месяца смотрит на укреплённого герцога и почти ежедневно пишет в Синьорию — из этих депеш вырастет «Государь»",
         "sig_envoy_i",
         [actor("A", 0, tags=["secretary"], notFlags=["bought"]),
          actor("B", 1, tags=["borgia"], flags=["fortified"])],
         [setf("A", "observing"), setf("B", "standing")]),
]
NEW_LEVELS.append(level(
    "imola_1502", 62, ACT3, "theme", "map_of_imola", 3,
    ["engineer_patent", "map_of_imola", "envoy_watches", "imola_meeting"],
    ["leonardo", "cesare", "machiavelli"],
    {"cesare": ["standing", "strong"], "leonardo": ["standing"], "machiavelli": ["standing"]},
    [],
    [flag("leonardo", "cartographer"), flag("cesare", "fortified"), flag("machiavelli", "observing"),
     nflag("machiavelli", "bought")],
    [("engineer_patent", ["cesare", "leonardo"]), ("map_of_imola", ["leonardo", "cesare"]),
     ("envoy_watches", ["machiavelli", "cesare"])],
    "fact"))
TEXTS.update(texts("imola_1502",
    "Имола",
    "Герцог Валентино покупает лучшего инженера Италии, тот чертит первый в мире план города «с высоты птичьего полёта» — а флорентийский посол смотрит на герцога и пишет депеши, из которых вырастет «Государь»",
    "Сначала патент: герцог нанимает художника — тот куплен и в свите. Купленный инженер чертит Имолу — крепости герцога в порядке. Посол смотрит на укреплённого герцога и записывает. Не давайте герцогу купить посла: Флоренция кондотты ему не дала, и Макиавелли остался наблюдателем, а не слугой.",
    "Осень 1502 года. Чезаре Борджиа взял Романью и сидит в Имоле, а его кондотьеры сговариваются против него в Маджоне. В свите герцога — Леонардо да Винчи с патентом «архитектора и генерального инженера»; во дворец приезжает посол Флоренции Никколо Макиавелли с приказом тянуть время и ничего не обещать. Три человека, которые больше никогда не окажутся в одной комнате.",
    "Патент от 18 августа 1502 года велел всем офицерам Чезаре пропускать «нашего превосходнейшего и любимейшего архитектора и генерального инженера Леонардо да Винчи», давать ему людей и слушать его о крепостях. В Имоле Леонардо вычертил план города, вымерив улицы шагами и колёсным одометром, — первый в европейской истории точный план города «сверху», а не «сбоку» (Виндзорская коллекция, RL 12284). Макиавелли прибыл в Имолу 7 октября 1502 года и провёл при герцоге три месяца, посылая депеши почти ежедневно: «Этот государь великолепен и величествен... в делах не знает отдыха». Чезаре просил у Флоренции кондотту и денег — Синьория отвечала уклончиво, и посол не получил полномочий ни на что. Встречались ли Леонардо и Макиавелли в Имоле, документы молчат; но летом 1503-го они вместе будут пытаться отвести Арно от Пизы.",
    "Н. Макиавелли, «Легации», депеши из Имолы, октябрь–декабрь 1502; патент Чезаре Борджиа от 18.08.1502; У. Айзексон, «Леонардо да Винчи»"))

# ================================================================ 6. senigallia (31.12.1502)
NEW_SCENES += [
    scene("feigned_peace", "Притворный мир", ["sig_feign_s"], 2, "🕊️", "простить заговорщиков", "icon_ally",
          ["герцог", "кондотьер"], "viceroy_pact"),
    scene("senigallia_gate", "Ворота Синигальи", ["sig_senigallia"], 2, "🪢", "обнять и удавить", "icon_dead",
          ["герцог", "кондотьер"], "arrest_d"),
    scene("dispatch_florence", "Депеша в Синьорию", ["sig_dispatch_s"], 2, "✒️", "описать «прекраснейший обман»", "icon_crown",
          ["посол", "герцог"], "long_letter"),
    scene("magione_castle", "Замок Маджоне", ["v_plot"], 2, "🗡️", "заговор", "icon_plot",
          ["заговорщик", "гость"], "hunting_plot"),
    scene("french_lances", "Французские копья", ["v_prepare"], 1, "🐎", "подготовка", "icon_ally",
          ["полководец"], "army_p"),
    scene("open_battle_s", "Открытый бой в Романье", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "open_battle"),
]
NEW_RULES += [
    rule("feign_s_sig", "Герцог, у которого меньше солдат, вдруг ласков: прощает, обещает, подписывает — кондотьеры верят и разводят войска по деревням",
         "sig_feign_s",
         [actor("A", 0, tags=["borgia"], notFlags=["defeated", "at_war"]),
          actor("B", 1, tags=["cardinal_b"], flags=["plotting"])],
         [setf("B", "trusting"), remf("B", "plotting"), remf("B", "strong"),
          addr("ally_of", "A", "B"), addr("ally_of", "B", "A")]),
    rule("senigallia_sig", "В вечер Нового года герцог обнимает каждого, вводит в дом и велит схватить; ночью их душат на одной скамье",
         "sig_senigallia",
         [actor("A", 0, tags=["borgia"]),
          actor("B", 1, tags=["cardinal_b"], flags=["trusting"])],
         [setf("B", "dead"), setf("B", "strangled"), setf("A", "ruthless")]),
    rule("dispatch_s_sig", "Посол, ждавший в передней, той же ночью пишет в Синьорию — потом из этого выйдет «Описание того, как герцог Валентино убил...»",
         "sig_dispatch_s",
         [actor("A", 0, tags=["secretary"], notFlags=["plotting", "bought"]),
          actor("B", 1, tags=["borgia"], flags=["ruthless"])],
         [setf("A", "witness")]),
]
NEW_LEVELS.append(level(
    "senigallia", 65, ACT3, "tension", "senigallia_gate", 3,
    ["feigned_peace", "senigallia_gate", "dispatch_florence", "magione_castle", "french_lances", "open_battle_s"],
    ["cesare", "orsini", "machiavelli"],
    {"cesare": ["standing"], "orsini": ["standing", "strong", "plotting"], "machiavelli": ["standing"]},
    [("enemy_of", "cesare", "orsini"), ("enemy_of", "orsini", "cesare")],
    [flag("orsini", "strangled"), flag("machiavelli", "witness"),
     nflag("machiavelli", "plotting"), nflag("cesare", "at_war")],
    [("feigned_peace", ["cesare", "orsini"]), ("senigallia_gate", ["cesare", "orsini"]),
     ("dispatch_florence", ["machiavelli", "cesare"])],
    "simplification"))
TEXTS.update(texts("senigallia",
    "Синигалья",
    "Герцог мирится с кондотьерами, которые сговорились против него, зовёт их в Синигалью — и в вечер Нового года душит в отведённых покоях; посол Флоренции всё видит и всё записывает",
    "Сначала притворный мир: герцог мирится с заговорщиком — тот верит и распускает войска. Доверившегося герцог зовёт в Синигалью — и душит. Посол смотрит на беспощадного герцога и пишет депешу. Открытого боя не будет: кондотьеры сильнее, и французские копья тут не спасут. И не давайте послу вступать в заговор — Флоренция в Маджоне не пошла.",
    "Октябрь 1502 года. Кондотьеры Чезаре — Орсини, Вителли, Оливеротто — собрались в замке Маджоне и сговорились против хозяина: солдат у них больше. Герцог, которому не хватает войск, вдруг становится ласков: прощает, обещает, подписывает. Флорентийский посол Макиавелли пишет из Имолы в Синьорию: не верю ни одному его слову.",
    "Сговор в Маджоне (октябрь 1502) едва не стоил Чезаре Романьи, но он взял в долг французские копья, подписал с мятежниками мир и попросил их взять для него Синигалью. 31 декабря 1502 года кондотьеры встретили его у города почти без войск — те были разведены по деревням; Чезаре обнял каждого, ввёл в дом и велел схватить всех. Вителлоццо Вителли и Оливеротто да Фермо задушили той же ночью на одной скамье, Паоло Орсини и герцога Гравины — 18 января, когда пришла весть, что папа арестовал в Риме кардинала Орсини. Макиавелли, ехавший с герцогом и ждавший в передней, в ту же ночь писал в Синьорию, а позже составил «Описание того, как герцог Валентино убил Вителлоццо Вителли...»; Паоло Джовио назвал это «прекраснейшим обманом». Через полгода папа Александр умер, и всё, что построил Чезаре, рассыпалось за месяц.",
    "Н. Макиавелли, «Описание того, как герцог Валентино убил Вителлоццо Вителли, Оливеротто да Фермо, синьора Паоло и герцога Гравину Орсини»; депеши из Синигальи 31.12.1502 и 1.01.1503"))

# ================================================================ 7. michelangelo_flight (1506)
NEW_SCENES += [
    scene("night_flight", "Ночью прочь из Рима", ["v_flee"], 1, "🐎", "уход", "icon_ally",
          ["скульптор"], "flee_florence"),
    scene("signoria_pressure", "Синьория уговаривает", ["sig_signoria_m"], 2, "🏛️", "«мы не хотим войны из-за тебя»", "icon_plot",
          ["секретарь", "скульптор"], "priorate"),
    scene("bologna_pardon", "Прощение в Болонье", ["sig_bologna_m"], 2, "🙏", "явиться с верёвкой на шее", "icon_crown",
          ["папа", "скульптор"], "julius_summons"),
    scene("rome_summons", "Папский вызов в Рим", ["v_parley"], 2, "📜", "переговоры", "icon_ally",
          ["кто требует", "кто уступает"], "summons_t"),
    scene("golden_horn", "Мост через Золотой Рог", ["sig_golden_horn"], 1, "🌉", "принять зов султана", "icon_plot",
          ["скульптор"], "bosphorus_monastery"),
]
NEW_RULES += [
    rule("signoria_m_sig", "Гонфалоньер беглецу: «Ты поступил с папой так, как не посмел бы король Франции; мы не хотим из-за тебя войны»",
         "sig_signoria_m",
         [actor("A", 0, tags=["secretary"]),
          actor("B", 1, tags=["artist"], flags=["away"], notFlags=["in_turkey"])],
         [setf("B", "pressed")]),
    rule("bologna_m_sig", "Папа только что взял Болонью; кающийся получает прощение и заказ на бронзовую статую — её потом перельют в пушку",
         "sig_bologna_m",
         [actor("A", 0, tags=["pope_i"], flags=["standing"]),
          actor("B", 1, tags=["artist"], flags=["pressed"], notFlags=["in_turkey", "conceded"])],
         [setf("B", "pardoned"), setf("B", "bronze_commission"), remf("B", "away"), setf("A", "standing")]),
    rule("golden_horn_sig", "Султан Баязид зовёт строить мост от Константинополя до Перы — беглец всерьёз собирается ехать",
         "sig_golden_horn",
         [actor("A", 0, tags=["artist"], flags=["away"])],
         [setf("A", "in_turkey")]),
]
NEW_LEVELS.append(level(
    "michelangelo_flight", 134, ACT5, "tension", "bologna_pardon", 3,
    ["night_flight", "signoria_pressure", "bologna_pardon", "rome_summons", "golden_horn"],
    ["michelangelo", "rovere", "machiavelli"],
    {"rovere": ["reigns", "crowned", "standing", "strong"], "michelangelo": ["standing"], "machiavelli": ["standing"]},
    [],
    [flag("michelangelo", "pardoned"), flag("michelangelo", "bronze_commission"),
     nflag("michelangelo", "conceded"), nflag("michelangelo", "in_turkey")],
    [("night_flight", ["michelangelo"]), ("signoria_pressure", ["machiavelli", "michelangelo"]),
     ("bologna_pardon", ["rovere", "michelangelo"])],
    "fact"))
TEXTS.update(texts("michelangelo_flight",
    "Побег от папы",
    "Скульптор, которого папа не пустил на порог, той же ночью бежит во Флоренцию — и возвращается к нему лишь в Болонью, «с верёвкой на шее», за прощением и новым заказом",
    "Сначала — ночью прочь из Рима: беглец вне досягаемости. Флорентийскую власть представляет секретарь: город не хочет войны с папой из-за одного скульптора — беглец уговорён. Только уговорённого папа прощает в Болонье. Явиться на папский вызов в Рим — уступить; мост через Золотой Рог — соблазн, от которого он отказался.",
    "Апрель 1506 года. Микеланджело два года возит мрамор для гробницы Юлия II, а папа, увлёкшийся собором Браманте, перестаёт платить. 17 апреля конюх не пускает его во дворец: «Мне приказано». Ночью скульптор садится на коня. Юлий шлёт за ним пятерых всадников и три грамоты флорентийской Синьории: вернуть.",
    "Микеланджело бежал из Рима в ночь на 18 апреля 1506 года — накануне закладки первого камня нового собора Святого Петра; всадники папы догнали его в Поджибонси, но он отказался вернуться и ответил письмом. Юлий II слал грамоты Синьории, и гонфалоньер Содерини сказал ему: «Ты поступил с папой так, как не посмел бы король Франции; мы не хотим из-за тебя войны». Тем временем султан Баязид II звал его в Константинополь строить мост через Золотой Рог, и, по словам Кондиви, он всерьёз собирался ехать. В ноябре 1506 года Юлий взял Болонью, и Микеланджело явился к нему туда просить прощения — «с верёвкой на шее», как он сам потом писал; епископа, заступившегося за «невежественного художника», папские слуги вытолкали, а художник получил прощение и заказ на бронзовую статую Юлия для Сан-Петронио. Он лил её два года; в 1511-м болонцы её сбросили, а Альфонсо д'Эсте перелил бронзу в пушку и назвал её «Джулия».",
    "А. Кондиви, «Жизнь Микеланджело»; письмо Микеланджело Джулиано да Сангалло от 2.05.1506; Дж. Вазари, «Жизнеописания»"))

# ================================================================ 8. castel_escape (1538–39)
NEW_SCENES += [
    scene("jewel_accusation", "Донос о папских камнях", ["v_speech"], 2, "💎", "речь", "icon_plot",
          ["оратор", "обвиняемый"], "court_denounce"),
    scene("bedsheet_rope", "Верёвка из простыней", ["sig_rope_c"], 1, "🪢", "спуститься со стены", "icon_ally",
          ["узник"], "roof_escape"),
    scene("french_intercession", "Слово короля Франции", ["sig_intercede_c"], 2, "⚜️", "вытребовать узника", "icon_crown",
          ["король", "узник"], "court_pardon"),
    scene("farnese_gallows", "Виселица Пьера Луиджи", ["v_execute"], 2, "🪢", "казнь", "icon_dead",
          ["кто казнит", "осуждённый"], "despenser_gallows"),
    scene("flee_to_france", "Бежать во Францию", ["v_flee"], 1, "🐎", "уход", "icon_ally",
          ["беглец"], "exile_road"),
]
NEW_RULES += [
    rule("rope_c_sig", "Узник режет простыни на полосы, выламывает скобы, спускается с башни и стены — и, прыгая с последней высоты, ломает ногу",
         "sig_rope_c",
         [actor("A", 0, tags=["artist"], flags=["condemned"], notFlags=["away"])],
         [setf("A", "escaped_once"), setf("A", "broken_leg")]),
    rule("intercede_c_sig", "Кардинал д'Эсте от имени Франциска I просит папу отпустить ювелира — тот выходит и уезжает в Париж",
         "sig_intercede_c",
         [actor("A", 0, tags=["king", "french"]),
          actor("B", 1, tags=["artist"], flags=["broken_leg", "condemned"])],
         [setf("B", "freed"), setf("B", "to_france"), remf("B", "condemned"), setf("B", "standing")]),
]
NEW_LEVELS.append(level(
    "castel_escape", 146, ACT5, "tension", "bedsheet_rope", 3,
    ["jewel_accusation", "bedsheet_rope", "french_intercession", "farnese_gallows", "flee_to_france"],
    ["cellini", "pope", "francis1"],
    {"pope": ["reigns", "crowned", "standing"], "cellini": ["standing"], "francis1": ["crowned", "standing"]},
    [("enemy_of", "pope", "cellini")],
    [flag("cellini", "escaped_once"), flag("cellini", "freed"), nflag("cellini", "dead")],
    [("jewel_accusation", ["pope", "cellini"]), ("bedsheet_rope", ["cellini"]),
     ("french_intercession", ["francis1", "cellini"])],
    "simplification"))
TEXTS.update(texts("castel_escape",
    "Побег из замка Святого Ангела",
    "Ювелира сажают в замок за кражу папских камней, он спускается по верёвке из простыней и ломает ногу — а вызволяет его из тюрьмы король Франции",
    "Сначала обвинение: папа с весом осуждает своего врага — ювелир в замке. Осуждённый рвёт простыни и спускается со стены — побег и сломанная нога. Беглеца со сломанной ногой вытаскивает из тюрьмы король Франции. Виселица сына папы — смерть; бежать во Францию до ареста — не выйдет, из замка так не уходят.",
    "1538 год. Бывший подмастерье доносит папе Павлу III: Челлини в 1527-м, переплавляя тиары в осаждённом замке, украл камней на восемьдесят тысяч дукатов. Ювелира сажают в тот самый замок Святого Ангела, со стен которого он одиннадцать лет назад стрелял по ландскнехтам. Комендант сходит с ума и считает себя летучей мышью, сын папы Пьер Луиджи требует виселицы — а в Париже о пленнике справляется Франциск I.",
    "Челлини был арестован в октябре 1538 года по доносу Перуджино, бывшего подмастерья, и заперт в замке Святого Ангела. По его собственному рассказу, он разрезал простыни на полосы, выломал скобы двери, спустился по верёвке с башни, затем со стены — и, прыгая с последней высоты, сломал ногу; дополз до ворот, где его подобрали слуги кардинала Корнаро. Павел III, узнав о побеге, велел вернуть его в замок, в сырую камеру под садом, где, по его словам, ему являлся ангел, а над головой с тех пор стояло сияние. Освободили его в декабре 1539 года по просьбе кардинала Ипполито д'Эсте от имени Франциска I; в 1540-м Челлини уехал в Париж и сделал королю золотую солонку — единственное сохранившееся его ювелирное изделие. Пьер Луиджи Фарнезе, добивавшийся его казни, в 1547-м был заколот собственными придворными.",
    "Б. Челлини, «Жизнь Бенвенуто, сына маэстро Джованни Челлини, флорентийца, написанная им самим», кн. I, гл. CIX–CXXVIII"))

# ================================================================ 9. bellarmine_1616
NEW_SCENES += [
    scene("holy_office_1616", "Богословы Святой палаты", ["sig_verdict_1616"], 1, "⚖️", "объявить движение Земли ересью", "icon_plot",
          ["инквизитор"], "holy_office"),
    scene("admonition_1616", "Увещевание", ["sig_admonish_1616"], 2, "🤫", "предупредить по-дружески", "icon_ally",
          ["кардинал", "астроном"], "court_whisper"),
    scene("certificate_1616", "Свидетельство Беллармина", ["sig_certificate_1616"], 2, "📜", "попросить бумагу", "icon_crown",
          ["астроном", "кардинал"], "anonymous_diploma"),
    scene("formal_abjuration", "Формальное отречение", ["v_parley"], 2, "🙏", "переговоры", "icon_ally",
          ["кто требует", "кто уступает"], "abjuration"),
    scene("barberini_ode", "Ода кардинала Барберини", ["v_befriend"], 2, "🎼", "дружба", "icon_ally", None, "old_friends"),
]
NEW_RULES += [
    rule("verdict_1616_sig", "Одиннадцать богословов за два дня: «Солнце неподвижно» — формальная ересь, «Земля движется» — ошибка в вере; папа поручает кардиналу увещевать",
         "sig_verdict_1616",
         [actor("A", 0, tags=["inquisitor"])],
         [setf("A", "decree"), setf("A", "standing")]),
    rule("admonish_1616_sig", "Кардинал по-дружески велит оставить это мнение; астроном подчиняется — и молчит семь лет",
         "sig_admonish_1616",
         [actor("A", 0, tags=["inquisitor"], flags=["decree"]),
          actor("B", 1, tags=["astronomer"], notFlags=["away", "conceded"])],
         [setf("B", "admonished"), setf("B", "silenced")]),
    rule("certificate_1616_sig", "Слухи об отречении; астроном просит справку — кардинал пишет, что отречения не было. Через семнадцать лет бумага станет уликой",
         "sig_certificate_1616",
         [actor("A", 0, tags=["astronomer"], flags=["admonished"], notFlags=["conceded"]),
          actor("B", 1, tags=["inquisitor"])],
         [setf("A", "certificate"), setf("A", "paper_trail")]),
]
NEW_LEVELS.append(level(
    "bellarmine_1616", 154, ACT6, "tension", "admonition_1616", 3,
    ["holy_office_1616", "admonition_1616", "certificate_1616", "formal_abjuration", "barberini_ode", "flee_venice"],
    ["galileo", "bellarmine", "urban8"],
    {"galileo": ["standing"], "bellarmine": ["standing"], "urban8": ["standing"]},
    [],
    [flag("galileo", "admonished"), flag("galileo", "certificate"), nflag("galileo", "conceded")],
    [("holy_office_1616", ["bellarmine"]), ("admonition_1616", ["bellarmine", "galileo"]),
     ("certificate_1616", ["galileo", "bellarmine"])],
    "fact"))
TEXTS.update(texts("bellarmine_1616",
    "Предупреждение 1616 года",
    "Святая палата объявляет движение Земли ересью, кардинал мягко предупреждает астронома, а тот просит бумагу, что не отрекался, — и через семнадцать лет эта бумага ляжет на стол его судей",
    "Сначала Святая палата: инквизитор получает декрет. С декретом в руках кардинал предупреждает астронома — тот предупреждён и молчит. Предупреждённый просит у кардинала свидетельство. Отрекаться формально нельзя — в 1616-м отречения не было; бежать в Венецию тоже — он сам уехал из-под её защиты. Барберини пока лишь друг и поэт.",
    "Зима 1616 года. Галилей приезжает в Рим доказывать, что Земля движется, и спорит об этом в салонах; друзья пишут ему: замолчи. Богословы Святой палаты собираются оценить два тезиса: Солнце неподвижно в центре мира, Земля вращается. Кардинал Беллармин — тот, что судил Бруно, — получает поручение папы. Кардинал Маффео Барберини, друг и почитатель Галилея, пока ещё только кардинал.",
    "24 февраля 1616 года богословы Святой палаты объявили тезис о неподвижном Солнце «формально еретическим», а о движении Земли — «по меньшей мере ошибочным в вере». 26 февраля кардинал Беллармин по приказу Павла V вызвал Галилея и увещевал его оставить это мнение; Галилей подчинился. 5 марта Конгрегация Индекса запретила книгу Коперника «до исправления». Когда по Риму пошли слухи, что Галилей отрёкся и наказан, он попросил у Беллармина справку: 26 мая кардинал письменно подтвердил, что ни отречения, ни епитимьи не было — ему лишь объявили решение. Но в деле осталась и другая, никем не подписанная записка нотария: Галилею предписано «не держаться, не преподавать и не защищать никаким образом». В 1633 году именно её предъявили на суде, а справка Беллармина, которую Галилей привёз как оправдание, стала доказательством, что о запрете он знал. Беллармин к тому времени двенадцать лет как умер, а кардинал Барберини был папой Урбаном VIII.",
    "Документы процесса Галилея (Ватиканский секретный архив); свидетельство Беллармина от 26.05.1616; А. Фантоли, «Галилей: в защиту учения Коперника и достоинства Святой Церкви»"))

# ================================================================ 10. aspromonte (1862)
NEW_SCENES += [
    scene("roma_o_morte", "«Рим или смерть!»", ["sig_roma_o_morte"], 1, "🔴", "поднять добровольцев", "icon_crown",
          ["генерал"], "the_thousand"),
    scene("royal_proclamation", "Королевская прокламация", ["sig_proclamation_a"], 2, "📜", "объявить поход мятежом", "icon_plot",
          ["король", "генерал"], "manifest_1861"),
    scene("aspromonte_1862", "Плато Аспромонте", ["sig_aspromonte"], 2, "🩸", "«Не стреляйте!»", "icon_dead",
          ["король", "генерал"], "calatafimi"),
    scene("french_rome", "Французский гарнизон Рима", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "assault_rome_c"),
    scene("rattazzi_wink", "Кивок Раттацци", ["v_befriend"], 2, "😉", "дружба", "icon_ally", None, "plombieres"),
]
NEW_RULES += [
    rule("roma_o_morte_sig", "В Палермо генерал собирает добровольцев с криком «Рим или смерть!» и переправляется в Калабрию",
         "sig_roma_o_morte",
         [actor("A", 0, tags=["rebel"], notFlags=["defeated"])],
         [setf("A", "rallied"), setf("A", "strong"), setf("A", "marching")]),
    rule("proclamation_a_sig", "Король, которому генерал подарил полстраны, объявляет его поход мятежом — теперь они по разные стороны",
         "sig_proclamation_a",
         [actor("A", 0, tags=["savoy"]),
          actor("B", 1, tags=["rebel"], flags=["marching"])],
         [setf("A", "disowns"), addr("enemy_of", "A", "B"), addr("enemy_of", "B", "A")]),
    rule("aspromonte_sig", "Берсальеры открывают огонь; генерал запрещает своим отвечать — «не стрелять в итальянских солдат» — и падает с пулей в ноге",
         "sig_aspromonte",
         [actor("A", 0, tags=["savoy"], flags=["disowns"]),
          actor("B", 1, tags=["rebel"], flags=["marching"], notFlags=["at_war"])],
         [setf("B", "wounded"), setf("B", "prisoner"), setf("B", "defeated"),
          remf("B", "strong"), remf("B", "marching"), setf("A", "standing")]),
]
NEW_LEVELS.append(level(
    "aspromonte", 161, ACT7, "tension", "aspromonte_1862", 3,
    ["roma_o_morte", "royal_proclamation", "aspromonte_1862", "march_on_rome_g", "french_rome", "rattazzi_wink"],
    ["garibaldi", "victor_emmanuel", "napoleon3"],
    {"victor_emmanuel": ["crowned", "king_of_italy", "standing", "strong"],
     "napoleon3": ["crowned", "standing", "strong"], "garibaldi": ["standing"]},
    [("enemy_of", "garibaldi", "napoleon3"), ("enemy_of", "napoleon3", "garibaldi")],
    [flag("garibaldi", "wounded"), flag("garibaldi", "prisoner"), nflag("garibaldi", "at_war")],
    [("roma_o_morte", ["garibaldi"]), ("royal_proclamation", ["victor_emmanuel", "garibaldi"]),
     ("aspromonte_1862", ["victor_emmanuel", "garibaldi"])],
    "fact"))
TEXTS.update(texts("aspromonte",
    "Аспромонте",
    "Герой Тысячи снова собирает добровольцев с криком «Рим или смерть!» — и король, которому он подарил полстраны, останавливает его пулей в ногу",
    "Сначала «Рим или смерть»: генерал поднимает добровольцев — в силе и в походе. Король отрекается от похода — теперь они враги. Отрёкшийся король встречает идущего генерала в Аспромонте: тот велит не стрелять — ранен и в плену. Штурмовать Рим у французов и биться с берсальерами — не то, что он сделал: «Не стреляйте!»",
    "1862 год. Италия едина, но без Рима: там папа под охраной французского гарнизона Наполеона III. В Палермо Гарибальди при молчаливом попустительстве правительства Раттацци собирает добровольцев — «Рим или смерть!» — и переправляется в Калабрию. Наполеон грозит; король Виктор Эммануил, два года назад пожавший ему руку в Теано, выпускает прокламацию: это мятеж.",
    "Гарибальди отплыл из Катании в Калабрию 24 августа 1862 года с двумя тысячами добровольцев без артиллерии и без плана — только с лозунгом «Roma o morte». Ещё 3 августа король объявил поход незаконным, а 29 августа на плато Аспромонте полковник Паллавичини с берсальерами открыл огонь; Гарибальди запретил своим отвечать — «не стрелять в итальянских солдат» — и был ранен двумя пулями, в бедро и в правую лодыжку. Его увезли в крепость Вариньяно под Специей; врачи со всей Европы спорили, где сидит пуля, и лишь в ноябре флорентиец Дзанетти извлёк её зондом, присланным из Парижа хирургом Нелатоном. 5 октября король амнистировал всех; правительство Раттацци, само подтолкнувшее поход, пало. Рим взяли только в 1870-м, когда Наполеон III потерял армию под Седаном, — без Гарибальди. Пулю из Аспромонте он хранил до смерти.",
    "Дж. Гарибальди, «Мемуары»; Дж. Тревельян, «Гарибальди и создание Италии»; Д. Мак Смит, «Гарибальди»"))

# ---------------------------------------------------------------- перенумерация акта I
# У акта I order 1..10 сплошные, а акт II начинается с 11 — целые order, вставить некуда.
# Единственная правка существующих уровней: поле order (содержимое не трогаем).
REORDER = {
    "francis": 1, "francis_sultan": 2, "frederick2": 3, "vespers": 4, "bordeaux_duel": 5,
    "dante": 6, "marco_polo": 7, "cola": 8, "black_death": 9, "cola_death": 10,
    "cosimo": 11, "pazzi": 12, "lorenzo_naples": 13, "lorenzo_deathbed": 14, "conclave": 15,
}

# ---------------------------------------------------------------- apply
def dump_compact(obj, path, trailing_newline=False):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        if trailing_newline:
            f.write("\n")

def upsert(lst, item):
    for i, x in enumerate(lst):
        if x["id"] == item["id"]:
            lst[i] = item
            return "updated"
    lst.append(item)
    return "added"

def main():
    scenes = json.load(open(SCENES, encoding="utf-8"))
    rules = json.load(open(RULES, encoding="utf-8"))
    known_scene_ids = {s["id"] for s in scenes}
    known_rule_ids = {r["id"] for r in rules}
    new_scene_ids = {s["id"] for s, _ in NEW_SCENES}
    new_rule_ids = {r["id"] for r in NEW_RULES}
    assert len(new_scene_ids) == len(NEW_SCENES), "дубль id сцены в пачке"
    assert len(new_rule_ids) == len(NEW_RULES), "дубль id правила в пачке"

    # 1. сцены (+ арт) — своих не трогаем, чужие с тем же id — ошибка
    stats = {"scene": 0, "rule": 0, "level": 0, "art": 0, "i18n": 0, "reorder": 0}
    for s, donor in NEW_SCENES:
        existing = next((x for x in scenes if x["id"] == s["id"]), None)
        if existing is not None and existing.get("tags") != s["tags"]:
            raise SystemExit(f"сцена {s['id']} уже существует с другими тегами — коллизия id")
        if upsert(scenes, s) == "added" or existing != s:
            stats["scene"] += 1
        dst = os.path.join(ART, f"scene_{s['id']}.webp")
        src = os.path.join(ART, f"scene_{donor}.webp")
        if not os.path.exists(dst):
            if not os.path.exists(src):
                raise SystemExit(f"нет донора арта {src}")
            shutil.copyfile(src, dst)
            stats["art"] += 1
    dump_compact(scenes, SCENES)

    # 2. правила — только sig-теги, уникальные для пачки
    for r in NEW_RULES:
        tag = r["trigger"]["sceneTags"][0]
        assert tag.startswith("sig_"), r["id"]
        for s in scenes:
            if tag in s.get("tags", []) and s["id"] not in new_scene_ids:
                raise SystemExit(f"тег {tag} уже носит чужая сцена {s['id']}")
        existing = next((x for x in rules if x["id"] == r["id"]), None)
        if existing is not None and existing["trigger"]["sceneTags"] != r["trigger"]["sceneTags"]:
            raise SystemExit(f"правило {r['id']} существует с другим sceneTag — коллизия id")
        if upsert(rules, r) == "added" or existing != r:
            stats["rule"] += 1
    dump_compact(rules, RULES)

    # 3. уровни
    all_level_ids = {}
    for ep in os.listdir(rp("Content")):
        d = rp("Content", ep, "levels")
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.endswith(".json"):
                    all_level_ids[fn[:-5]] = os.path.join(d, fn)
    new_level_ids = {l["id"] for l in NEW_LEVELS}
    for l in NEW_LEVELS:
        p = all_level_ids.get(l["id"])
        if p and os.path.dirname(p) != LEVELS:
            raise SystemExit(f"id уровня {l['id']} занят в другой главе: {p}")
        for sid in l["scenes"]:
            assert sid in known_scene_ids or sid in new_scene_ids, (l["id"], sid)
        path = os.path.join(LEVELS, f"{l['id']}.json")
        old = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None
        if old != l:
            dump_compact(l, path)
            stats["level"] += 1

    # 4. order акта I
    for lid, order in REORDER.items():
        path = os.path.join(LEVELS, f"{lid}.json")
        d = json.load(open(path, encoding="utf-8"))
        if d["order"] != order:
            d["order"] = order
            dump_compact(d, path)
            stats["reorder"] += 1

    # 5. i18n (только ru; переводы — tools/i18n/translate.py)
    cat = json.load(open(CATALOG, encoding="utf-8"))
    for s, _ in NEW_SCENES:
        TEXTS[f"scene.{s['id']}"] = s["name"]
        TEXTS[f"scene.{s['id']}.action"] = s["action"]
    for k, v in TEXTS.items():
        if cat.get(k) != v:
            cat[k] = v
            stats["i18n"] += 1
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")

    print("italy_b:", ", ".join(f"{k} {v}" for k, v in stats.items()))
    print("levels:", " ".join(sorted(new_level_ids)))

if __name__ == "__main__":
    main()
