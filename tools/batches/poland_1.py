#!/usr/bin/env python3
"""Пачка 1 главы «Польша» (epoch poland): легенды и ранние Пясты, 8 уровней.

Идемпотентно: upsert персонажей/сцен/правил в Content/rome/{characters,scenes,rules}.json (по id),
запись Content/poland/levels/<id>.json, копия арта сцен (донор → новая сцена), копия спрайтов
персонажей из фабрики (Content/art_v2 → Content/art, все позы), регистрация главы в chapters.json,
upsert ключей в Content/i18n/ru.json (indent=1, ensure_ascii=False, sort_keys=True).

Все персонажи главы нарисованы своей фабрикой (factory/recipes/*.json), ни одной генерации.

    python3 tools/batches/poland_1.py [repo_root]
"""
import json, os, shutil, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
def rp(*p): return os.path.join(ROOT, *p)

CHARS = rp("Content/rome/characters.json")
SCENES = rp("Content/rome/scenes.json")
RULES = rp("Content/rome/rules.json")
CATALOG = rp("Content/i18n/ru.json")
CHAPTERS = rp("Content/chapters.json")
LEVELS = rp("Content/poland/levels")
ART = rp("Content/art")
ART_V2 = rp("Content/art_v2")
POSES = ("", "_triumph", "_defeated", "_plot", "_dead")

ACT1 = "Акт I · Легенды"
ACT2 = "Акт II · Пясты"

CHAPTER = {"id": "poland", "number": 7, "cover": "eagle_nest_pl", "icon": "shield.fill", "free": False,
           "minAppVersion": "1.0"}
CHAPTER_TEXTS = {
    "chapter.poland.title": "Польша",
    "chapter.poland.subtitle": "От легенд до 1918 года",
    "map.poland": "Польша",
    "act.poland.1": ACT1,
    "act.poland.2": ACT2,
}

# ---------------------------------------------------------------- helpers
def char(id, name, tags, emoji):
    return {"id": id, "name": name, "tags": tags, "emoji": emoji}

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
        "id": id, "order": order, "epoch": "poland", "act": act, "music": music,
        "cover": cover, "panels": panels, "scenes": scenes, "characters": chars,
        "initialState": {"flags": flags, "relations": [list(r) for r in rels]},
        "goal": {"all": goal},
        "solution": [{"scene": s, "characters": c} for s, c in solution],
        "factCard": {"accuracy": accuracy},
    }

def texts(id, title, goal, hint, intro, fact, source):
    return {f"level.{id}.title": title, f"level.{id}.goal": goal, f"level.{id}.hint": hint,
            f"level.{id}.intro": intro, f"level.{id}.fact": fact, f"level.{id}.source": source}

NEW_CHARS = [
    char("lech", "Лех", ["brother_pl", "legend_pl"], "🦅"),
    char("czech", "Чех", ["brother_pl", "legend_pl"], "⛰️"),
    char("rus", "Рус", ["brother_pl", "legend_pl"], "🌅"),
    char("popiel", "Князь Попель", ["cruel_pl", "prince_pl"], "🐭"),
    char("piast", "Пяст-колесник", ["peasant_pl"], "🛞"),
    char("siemowit", "Земовит", ["child_pl"], "👦"),
    char("wanderers_pl", "Странники", ["wanderer_pl"], "🧙"),
    char("mieszko1", "Мешко I", ["piast_pl", "prince_pl"], "🛡️"),
    char("dobrawa", "Добрава", ["czech_pl", "christian_pl"], "👸"),
    char("hodo", "Маркграф Ходон", ["margrave_pl", "german_pl"], "⚔️"),
    char("jordan_bp", "Епископ Иордан", ["bishop_pl", "christian_pl"], "⛪"),
    char("czcibor", "Чцибор", ["piast_pl"], "🗡️"),
    char("chrobry", "Болеслав Храбрый", ["piast_pl", "prince_pl"], "👑"),
    char("otto3", "Оттон III", ["emperor_pl", "german_pl"], "👑"),
    char("wojciech", "Святой Войцех", ["missionary_pl", "christian_pl"], "✝️"),
    char("prussian_pl", "Вождь пруссов", ["prussian_pl", "pagan_pl"], "🪓"),
    char("casimir1", "Казимир Восстановитель", ["piast_pl", "prince_pl"], "🏰"),
    char("rycheza", "Королева Рыкса", ["queen_pl", "german_pl"], "👸"),
    char("bretislav", "Бржетислав Чешский", ["czech_duke_pl"], "⚔️"),
    char("krzywousty", "Болеслав Кривоустый", ["piast_pl", "prince_pl", "father_pl"], "🗡️"),
    char("henry5_hre", "Император Генрих V", ["emperor_pl", "german_pl"], "👑"),
    char("glogow_burgher", "Горожанин Глогова", ["burgher_pl"], "🏘️"),
    char("wladyslaw2", "Владислав Изгнанник", ["son_pl", "eldest_pl"], "🗡️"),
    char("boleslaw4", "Болеслав Кудрявый", ["son_pl"], "🌀"),
    char("mieszko3", "Мешко Старый", ["son_pl"], "🌾"),
]

NEW_SCENES = []   # (scene, donor)
NEW_RULES = []
NEW_LEVELS = []
TEXTS = {}

# ================================================================ 1. lech_eagle (легенда)
NEW_SCENES += [
    scene("crossroads_pl", "Три брата на распутье", ["sig_crossroads_pl"], 3, "🛤️", "разойтись по свету", "icon_ally",
          ["на юг, к горе Ржип", "на восток", "остаётся"], "exile_road"),
    scene("eagle_nest_pl", "Гнездо белого орла", ["sig_eagle_nest_pl"], 1, "🦅", "основать град", "icon_crown",
          ["кто увидел орла"], "royal_oak"),
    scene("rich_valley_pl", "Тучная долина", ["sig_rich_valley_pl"], 1, "🌾", "осесть на богатой земле", "icon_ally",
          ["кто садится"], "deulino_village"),
]
NEW_RULES += [
    rule("crossroads_pl_sig", "Братья расходятся: первый уходит на юг, к горе Ржип, второй — на восток, третий остаётся",
         "sig_crossroads_pl",
         [actor("A", 0, tags=["brother_pl"], notFlags=["settled", "away"]),
          actor("B", 1, tags=["brother_pl"], notFlags=["settled", "away"]),
          actor("C", 2, tags=["brother_pl"], notFlags=["settled", "away"])],
         [setf("A", "went_south"), setf("A", "away"), setf("B", "went_east"), setf("B", "away"), setf("C", "stays")]),
    rule("eagle_nest_pl_sig", "Оставшийся брат видит на дубе белого орла над гнездом в лучах заката — и ставит здесь град Гнезно",
         "sig_eagle_nest_pl",
         [actor("A", 0, tags=["brother_pl"], flags=["stays"], notFlags=["settled"])],
         [setf("A", "founder_pl"), setf("A", "settled"), setf("A", "standing")]),
    rule("rich_valley_pl_sig", "Брат оседает там, где земля жирнее, — и уже не ищет знака",
         "sig_rich_valley_pl",
         [actor("A", 0, tags=["brother_pl"], notFlags=["settled", "away"])],
         [setf("A", "settled")]),
]
NEW_LEVELS.append(level(
    "lech_eagle", 10, ACT1, "poland_ceremony", "eagle_nest_pl", 2,
    ["crossroads_pl", "eagle_nest_pl", "rich_valley_pl"],
    ["lech", "czech", "rus"],
    {}, [],
    [flag("lech", "founder_pl"), flag("czech", "went_south"), flag("rus", "went_east")],
    [("crossroads_pl", ["czech", "rus", "lech"]), ("eagle_nest_pl", ["lech"])],
    "legend"))
TEXTS.update(texts("lech_eagle",
    "Лех, Чех и Рус",
    "Три брата расходятся по свету, и тот, кто остался, ставит град там, где увидел белого орла",
    "Сначала распутье: каждому брату своя дорога. Чех уходит к своей горе на юг, Рус — туда, где встаёт солнце. Лех садится не там, где земля богаче, а там, где ему подан знак.",
    "Давным-давно трое братьев вели свои роды с юга на поиски новой земли. Дорога одна, а народ растёт, и жить вместе тесно. Братьям пора расходиться: каждый найдёт свою землю, но знать, где именно, будет лишь тот, кому подадут знак.",
    "Три брата — Лех, Чех и Рус — долго вели свои роды в поисках новой земли, пока дорога не разошлась натрое. Чех повёл людей на юг, поднялся на гору Ржип и сказал: здесь будет наш дом. Рус ушёл на восток, туда, где встаёт солнце. А Лех шёл на север через леса и озёра, пока однажды на закате не увидел на огромном дубе гнездо и над ним — белого орла, раскинувшего крылья на фоне багрового неба. Лех понял, что это знак: здесь он поставил свой град и назвал его Гнезно — от «гнезда», а белого орла на красном поле сделал своим гербом. Братья разошлись, но остались братьями — так, говорят, появились поляки, чехи и русины.",
    "«Великопольская хроника» (кон. XIII — нач. XIV в.); Козьма Пражский, «Чешская хроника» (ок. 1120)"))

# ================================================================ 2. popiel_piast (легенда)
NEW_SCENES += [
    scene("popiel_feast_pl", "Пир князя Попеля", ["sig_popiel_feast_pl"], 2, "🍖", "прогнать гостей", "icon_plot",
          ["князь", "гости"], "feast_p"),
    scene("piast_hut_pl", "Хата колесника", ["sig_piast_hut_pl"], 3, "🛖", "принять гостей", "icon_crown",
          ["хозяин", "гости", "сын"], "fili_hut"),
    scene("mice_tower_pl", "Башня над Гопло", ["sig_mice_tower_pl"], 1, "🐭", "запереться в башне", "icon_dead",
          ["кто в башне"], "peronne_tower"),
    scene("secret_council_pl", "Тайная сходка", ["v_plot"], 2, "🗡️", "заговор", "icon_plot",
          ["заговорщик", "заговорщик"], "court_whisper"),
]
NEW_RULES += [
    rule("popiel_feast_pl_sig", "На пиру по случаю постригов княжича Попель гонит со двора двух нищих странников",
         "sig_popiel_feast_pl",
         [actor("A", 0, tags=["cruel_pl"]),
          actor("B", 1, tags=["wanderer_pl"], notFlags=["driven_away"])],
         [setf("B", "driven_away"), setf("A", "inhospitable")]),
    rule("piast_hut_pl_sig", "Прогнанных странников зовёт к себе бедный колесник; угощения становится всё больше — и странники стригут его сына, предрекая ему княжество",
         "sig_piast_hut_pl",
         [actor("A", 0, tags=["peasant_pl"]),
          actor("B", 1, tags=["wanderer_pl"], flags=["driven_away"], notFlags=["welcomed"]),
          actor("C", 2, tags=["child_pl"])],
         [setf("B", "welcomed"), setf("A", "blessed"), setf("C", "chosen_pl")]),
    rule("mice_tower_pl_sig", "Негостеприимного князя настигает кара: из тел отравленных им родичей выходят мыши и съедают его в башне",
         "sig_mice_tower_pl",
         [actor("A", 0, tags=["cruel_pl"], flags=["inhospitable"])],
         [setf("A", "dead"), setf("A", "eaten_pl")]),
]
NEW_LEVELS.append(level(
    "popiel_piast", 20, ACT1, "poland_tension", "piast_hut_pl", 3,
    ["popiel_feast_pl", "piast_hut_pl", "mice_tower_pl", "secret_council_pl"],
    ["popiel", "piast", "siemowit", "wanderers_pl"],
    {"popiel": ["reigns", "standing"]}, [],
    [flag("popiel", "eaten_pl"), flag("siemowit", "chosen_pl"), nflag("piast", "plotting")],
    [("popiel_feast_pl", ["popiel", "wanderers_pl"]), ("piast_hut_pl", ["piast", "wanderers_pl", "siemowit"]),
     ("mice_tower_pl", ["popiel"])],
    "legend"))
TEXTS.update(texts("popiel_piast",
    "Попель и мыши",
    "Жестокий князь гонит странников со своего пира, бедный колесник их принимает — и его сын становится князем, а Попеля съедают мыши",
    "Странники приходят сначала к князю — к колеснику они идут прогнанными. Пяст не заговорщик: князем его род сделал не мятеж, а гостеприимство. А с Попелем разберутся без людей.",
    "В Гнезно правит князь Попель — жестокий и, по слухам, отравивший своих дядей. У него пир: княжичу впервые стригут волосы, это обряд постригов, после которого мальчик становится мужчиной. В город приходят двое странников. В посаде у колесника Пяста и его жены Репки тоже постриги — их сына Земовита, — но у бедняков угощения на один стол.",
    "Князь Попель был жесток: по преданию, он отравил на пиру своих дядей и бросил их тела без погребения. Когда на княжеский пир по случаю постригов его сына пришли двое странников, их прогнали со двора. Странники постучались в хату бедного колесника Пяста и его жены Репки — у тех тоже был праздник, постриги их сына Земовита, но угощения хватало лишь на один стол. Пяст принял гостей как родных — и тогда случилось чудо: бочонок мёда и кусок свинины в его хате прибывали и прибывали, пока ими не накормили даже гостей князя. Странники остригли Земовита и предрекли ему княжество. А Попеля настигла кара: из тел отравленных дядей вышли полчища мышей, загнали князя в башню над озером Гопло и съели. Народ выбрал князем Земовита — с него начался род Пястов, правивший Польшей больше четырёхсот лет.",
    "Галл Аноним, «Хроника и деяния князей или правителей польских», I, 1–3; Винцентий Кадлубек, «Хроника»"))

# ================================================================ 3. mieszko_baptism (966)
NEW_SCENES += [
    scene("dobrawa_match_pl", "Сватовство в Праге", ["sig_dobrawa_match_pl"], 2, "💍", "взять в жёны чешскую княжну", "icon_ally",
          ["князь", "невеста"], "polish_wedding"),
    scene("baptism_966_pl", "Крещение", ["sig_baptism_966_pl"], 2, "💧", "креститься", "icon_crown",
          ["крещаемый", "через кого"], "cathedral_altar"),
    scene("poznan_see_pl", "Епископство в Познани", ["sig_poznan_see_pl"], 2, "⛪", "основать епископство", "icon_crown",
          ["князь", "епископ"], "reims_cathedral"),
    scene("bow_margrave_pl", "Поклон маркграфу", ["v_parley"], 2, "🤝", "переговоры", "icon_ally",
          ["кто требует", "кто уступает"], "court_present"),
]
NEW_RULES += [
    rule("dobrawa_match_pl_sig", "Князь-язычник берёт в жёны дочь чешского князя — союз с христианской Прагой против маркграфов",
         "sig_dobrawa_match_pl",
         [actor("A", 0, tags=["piast_pl"], flags=["pagan"]),
          actor("B", 1, tags=["czech_pl"], notFlags=["married"])],
         [addr("wed", "A", "B"), addr("wed", "B", "A"), setf("A", "allied_cz"), setf("B", "married")]),
    rule("baptism_966_cz_pl", "Крещение через чешскую жену и чешских священников: христианство без немецкого господина",
         "sig_baptism_966_pl",
         [actor("A", 0, tags=["piast_pl"], flags=["pagan", "allied_cz"]),
          actor("B", 1, tags=["czech_pl"])],
         [setf("A", "baptized"), remf("A", "pagan")]),
    rule("baptism_966_de_pl", "Крещение из рук маркграфа: вместе с верой князь получает и немецкого сюзерена",
         "sig_baptism_966_pl",
         [actor("A", 0, tags=["piast_pl"], flags=["pagan"]),
          actor("B", 1, tags=["margrave_pl"])],
         [setf("A", "baptized"), remf("A", "pagan"), setf("A", "vassal_de")]),
    rule("poznan_see_pl_sig", "Крещёный князь, никому не подвластный, получает своего епископа — миссионерское епископство в Познани",
         "sig_poznan_see_pl",
         [actor("A", 0, tags=["piast_pl"], flags=["baptized"], notFlags=["vassal_de"]),
          actor("B", 1, tags=["bishop_pl"])],
         [setf("B", "bishop_poznan"), setf("A", "own_church")]),
]
NEW_LEVELS.append(level(
    "mieszko_baptism", 30, ACT2, "poland_ceremony", "baptism_966_pl", 3,
    ["dobrawa_match_pl", "baptism_966_pl", "poznan_see_pl", "bow_margrave_pl"],
    ["mieszko1", "dobrawa", "hodo", "jordan_bp"],
    {"mieszko1": ["pagan", "reigns", "standing"], "hodo": ["strong", "standing"]},
    [("enemy_of", "hodo", "mieszko1"), ("enemy_of", "mieszko1", "hodo")],
    [flag("mieszko1", "baptized"), flag("jordan_bp", "bishop_poznan"),
     nflag("mieszko1", "vassal_de"), nflag("mieszko1", "conceded")],
    [("dobrawa_match_pl", ["mieszko1", "dobrawa"]), ("baptism_966_pl", ["mieszko1", "dobrawa"]),
     ("poznan_see_pl", ["mieszko1", "jordan_bp"])],
    "simplification"))
TEXTS.update(texts("mieszko_baptism",
    "Крещение Мешко",
    "Князь-язычник женится на чешской княжне, крестится через Прагу, а не через немцев, — и получает своего епископа",
    "Крест можно принять из разных рук. Из рук маркграфа вместе с верой приходит господин. Сначала нужен союз с Прагой: чешская невеста — и чешские священники.",
    "Середина X века. Князь полян Мешко — язычник, и для соседей это повод: немецкие маркграфы называют войну с язычниками крестовым делом. Маркграф Ходон уже стоит на Одре. Креститься Мешко придётся — вопрос только, от кого.",
    "В 965 году Мешко женился на Добраве, дочери чешского князя Болеслава I, а в 966-м принял крещение — точная дата неизвестна, по традиции это Пасха, 14 апреля. Немецкий хронист Титмар Мерзебургский пишет, что Добрава в первый Великий пост нарочно ела мясо вместе с мужем, чтобы расположить его к вере. Крещение через Чехию, а не через немецкие епископства, позволило Мешко не подчинить свою церковь Магдебургу, основанному как раз в 968 году для обращения славян. В том же 968-м в Познани появился первый епископ — Иордан, подчинённый, по распространённой версии, напрямую Риму. 966 год считается датой рождения польского государства.",
    "Титмар Мерзебургский, «Хроника», IV, 55–56; Галл Аноним, I, 5; «Анналы капитула Краковского»"))

# ================================================================ 4. cedynia_972
NEW_SCENES += [
    scene("oder_feint_pl", "Отступление за Одру", ["sig_oder_feint_pl"], 2, "🏃", "заманить врага", "icon_plot",
          ["кто отступает", "кто гонится"], "hal_retreats"),
    scene("cedynia_ambush_pl", "Удар с тыла под Цедыней", ["sig_cedynia_ambush_pl"], 2, "⚔️", "ударить из засады", "icon_dead",
          ["засада", "враг"], "forest_ambush"),
    scene("cedynia_front_pl", "Лобовая атака", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "open_battle"),
    scene("cedynia_muster_pl", "Собрать дружину", ["v_prepare"], 1, "🛡️", "подготовка", "icon_ally",
          ["кто вооружается"], "campaign"),
]
NEW_RULES += [
    rule("oder_feint_pl_sig", "Князь отходит от переправы, и маркграф в азарте бросается следом, растянув строй",
         "sig_oder_feint_pl",
         [actor("A", 0, tags=["piast_pl"], notFlags=["defeated"]),
          actor("B", 1, tags=["margrave_pl"], flags=["strong"])],
         [setf("B", "lured"), remf("B", "strong"), setf("A", "feigned")]),
    rule("cedynia_ambush_pl_sig", "Другой отряд, не отступавший, бьёт растянутое войско маркграфа с тыла",
         "sig_cedynia_ambush_pl",
         [actor("A", 0, tags=["piast_pl"], notFlags=["feigned", "defeated"]),
          actor("B", 1, tags=["margrave_pl"], flags=["lured"])],
         [setf("B", "defeated"), setf("A", "victor"), setf("A", "hero_cedynia")]),
]
NEW_LEVELS.append(level(
    "cedynia_972", 40, ACT2, "poland_battle", "cedynia_ambush_pl", 2,
    ["oder_feint_pl", "cedynia_ambush_pl", "cedynia_front_pl", "cedynia_muster_pl"],
    ["mieszko1", "czcibor", "hodo"],
    {"mieszko1": ["reigns", "standing"], "czcibor": ["standing"], "hodo": ["strong", "standing"]},
    [("enemy_of", "hodo", "mieszko1"), ("enemy_of", "mieszko1", "hodo"),
     ("enemy_of", "hodo", "czcibor"), ("enemy_of", "czcibor", "hodo")],
    [flag("hodo", "defeated"), flag("czcibor", "hero_cedynia"), nflag("mieszko1", "defeated")],
    [("oder_feint_pl", ["mieszko1", "hodo"]), ("cedynia_ambush_pl", ["czcibor", "hodo"])],
    "simplification"))
TEXTS.update(texts("cedynia_972",
    "Цедыня",
    "Князь отступает, маркграф бросается в погоню — и брат князя бьёт его с тыла",
    "Маркграф сильнее, и в лоб его не взять — даже с собранной дружиной. Пусть он сам растянет строй в погоне. Но ударить должен тот, кто не убегал.",
    "Июнь 972 года. Маркграф Ходон без ведома императора идёт на Мешко — за добычей и землёй на Одре. Его тяжёлая конница сильнее польской дружины. У князя есть брат Чцибор и знание переправ.",
    "24 июня 972 года у Цедыни, на правом берегу Одры, войско Ходона было разбито; Титмар Мерзебургский пишет, что польский удар нанёс Чцибор, брат Мешко, и что из всех знатных воинов маркграфа спаслись лишь сам Ходон и отец хрониста, граф Зигфрид. Ложное отступление — реконструкция историков: хроника говорит только о поражении маркграфа, а не о том, как его заманили. Император Оттон I вызвал обоих на суд в Кведлинбург, и Мешко пришлось отправить туда заложником сына — будущего Болеслава Храброго. Цедыня — первая битва в польской истории, о которой мы знаем.",
    "Титмар Мерзебургский, «Хроника», II, 29"))

# ================================================================ 5. gniezno_1000
NEW_SCENES += [
    scene("prussia_mission_pl", "Миссия к пруссам", ["sig_prussia_mission_pl"], 2, "✝️", "проповедовать язычникам", "icon_dead",
          ["миссионер", "язычник"], "grove_furrina"),
    scene("relic_ransom_pl", "Мощи на вес золота", ["sig_relic_ransom_pl"], 2, "⚖️", "выкупить тело святого", "icon_ally",
          ["князь", "язычник"], "gold_scales"),
    scene("gniezno_congress_pl", "Съезд в Гнезно", ["sig_gniezno_congress_pl"], 2, "👑", "принять императора", "icon_crown",
          ["князь", "император"], "cathedral_procession"),
    scene("punitive_raid_pl", "Карательный поход", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "battlefield"),
]
NEW_RULES += [
    rule("prussia_mission_pl_sig", "Миссионер приходит к пруссам в священную рощу — и гибнет от их копий; тело остаётся у язычников",
         "sig_prussia_mission_pl",
         [actor("A", 0, tags=["missionary_pl"]),
          actor("B", 1, tags=["prussian_pl"], notFlags=["defeated"])],
         [setf("A", "dead"), setf("A", "martyr_pl"), setf("B", "holds_relics")]),
    rule("relic_ransom_pl_sig", "Князь выкупает тело мученика за столько золота, сколько оно весит",
         "sig_relic_ransom_pl",
         [actor("A", 0, tags=["piast_pl"]),
          actor("B", 1, tags=["prussian_pl"], flags=["holds_relics"], notFlags=["defeated"])],
         [setf("A", "relics"), remf("B", "holds_relics")]),
    rule("gniezno_congress_pl_sig", "К гробнице святого приходит паломником император — надевает свою диадему на голову князя и зовёт его братом и союзником",
         "sig_gniezno_congress_pl",
         [actor("A", 0, tags=["piast_pl"], flags=["relics"]),
          actor("B", 1, tags=["emperor_pl"])],
         [setf("A", "recognized_pl"), setf("A", "standing"), setf("B", "pilgrim_pl"),
          addr("ally_of", "A", "B"), addr("ally_of", "B", "A")]),
]
NEW_LEVELS.append(level(
    "gniezno_1000", 50, ACT2, "poland_ceremony", "gniezno_congress_pl", 3,
    ["prussia_mission_pl", "relic_ransom_pl", "gniezno_congress_pl", "punitive_raid_pl"],
    ["chrobry", "otto3", "wojciech", "prussian_pl"],
    {"chrobry": ["reigns", "standing", "strong"], "otto3": ["crowned", "standing"]},
    [("enemy_of", "chrobry", "prussian_pl"), ("enemy_of", "prussian_pl", "chrobry")],
    [flag("chrobry", "recognized_pl"), flag("wojciech", "martyr_pl")],
    [("prussia_mission_pl", ["wojciech", "prussian_pl"]), ("relic_ransom_pl", ["chrobry", "prussian_pl"]),
     ("gniezno_congress_pl", ["chrobry", "otto3"])],
    "simplification"))
TEXTS.update(texts("gniezno_1000",
    "Съезд в Гнезно",
    "Святой гибнет у пруссов, князь выкупает его тело на вес золота — и к гробнице приходит паломником император",
    "Император едет не к князю, а к святому: без мощей звать его не к чему. Мощи у пруссов — и война с ними их не вернёт, а только испортит торг.",
    "997 год. Бывший епископ Праги Войцех, друг юного императора Оттона III, просит князя Болеслава отпустить его проповедовать язычникам-пруссам. Болеслав даёт ему лодку и охрану. Император мечтает о новой христианской империи — Риме, к которому примкнут славяне.",
    "23 апреля 997 года Войцеха убили пруссы; Болеслав выкупил его тело за столько золота, сколько оно весило, и похоронил в Гнезно. В марте 1000 года Оттон III пришёл к гробнице паломником, босиком. Галл Аноним пишет, что император снял с себя диадему и надел её на голову Болеслава, назвал его «братом и сотрудником империи» и подарил копию копья святого Маврикия, а взамен получил руку святого. Тогда же в Гнезно основали архиепископство с епископствами в Кракове, Вроцлаве и Колобжеге — польская церковь стала самостоятельной. Королём Болеслав короновался лишь в 1025 году, за несколько месяцев до смерти.",
    "Галл Аноним, I, 6; Титмар Мерзебургский, IV, 45–46; «Житие святого Адальберта»"))

# ================================================================ 6. odnowiciel_1039
NEW_SCENES += [
    scene("exile_mother_pl", "У матери в изгнании", ["sig_exile_mother_pl"], 2, "🕯️", "просить помощи", "icon_ally",
          ["изгнанник", "мать"], "exile_tent"),
    scene("krakow_capital_pl", "Новая столица — Краков", ["sig_krakow_capital_pl"], 1, "🏰", "вернуться и править", "icon_crown",
          ["кто возвращается"], "restored_throne"),
    scene("gniezno_raid_pl", "Набег на Гнезно", ["sig_gniezno_raid_pl"], 1, "🔥", "разорить столицу", "icon_dead",
          ["захватчик"], "city_on_bones"),
    scene("silesia_war_pl", "Отбить Силезию", ["v_battle"], 2, "⚔️", "битва", "icon_dead",
          ["нападающий", "защитник"], "battlefield"),
]
NEW_RULES += [
    rule("exile_mother_pl_sig", "Изгнанный князь у матери-королевы при немецком дворе: она добывает ему у императора пятьсот рыцарей",
         "sig_exile_mother_pl",
         [actor("A", 0, tags=["piast_pl"], flags=["exiled"]),
          actor("B", 1, tags=["queen_pl"])],
         [setf("A", "backed"), setf("A", "strong"), remf("A", "away")]),
    rule("krakow_capital_pl_sig", "С отрядом рыцарей князь возвращается в разорённую страну — и правит уже не из сожжённого Гнезно, а из Кракова",
         "sig_krakow_capital_pl",
         [actor("A", 0, tags=["piast_pl"], flags=["backed"], notFlags=["at_war", "defeated"])],
         [setf("A", "restorer_pl"), setf("A", "reigns"), setf("A", "standing"), remf("A", "exiled")]),
    rule("gniezno_raid_pl_sig", "Чешский князь грабит беззащитное Гнезно и увозит в Прагу мощи святого Войцеха",
         "sig_gniezno_raid_pl",
         [actor("A", 0, tags=["czech_duke_pl"], notFlags=["raided"])],
         [setf("A", "raided"), setf("A", "relics")]),
]
NEW_LEVELS.append(level(
    "odnowiciel_1039", 60, ACT2, "poland_tension", "krakow_capital_pl", 2,
    ["exile_mother_pl", "krakow_capital_pl", "gniezno_raid_pl", "silesia_war_pl"],
    ["casimir1", "rycheza", "bretislav"],
    {"casimir1": ["exiled", "away"], "rycheza": ["crowned", "standing"], "bretislav": ["strong", "standing"]},
    [("enemy_of", "casimir1", "bretislav"), ("enemy_of", "bretislav", "casimir1")],
    [flag("casimir1", "restorer_pl"), nflag("casimir1", "at_war")],
    [("exile_mother_pl", ["casimir1", "rycheza"]), ("krakow_capital_pl", ["casimir1"])],
    "simplification"))
TEXTS.update(texts("odnowiciel_1039",
    "Казимир Восстановитель",
    "Изгнанный князь возвращается с рыцарями, добытыми матерью, — и восстанавливает страну, сделав столицей Краков",
    "Без помощи из-за границы возвращаться не с чем. Вернувшись, не бросайтесь сразу отбивать Силезию: сначала страну надо поднять из руин, а воевать с Чехией сейчас — потерять и то, что осталось.",
    "1030-е годы. После смерти Мешко II государство Пястов рухнуло: восстали язычники, знать разбежалась, молодого Казимира изгнали. Его мать Рыкса, племянница императора Оттона III, живёт в Германии. А чешский князь Бржетислав видит, что Польша беззащитна.",
    "В 1038 или 1039 году Бржетислав разорил Гнезно и Познань и увёз в Прагу мощи святого Войцеха — Гнезно так и не оправилось. В 1039 году Казимир вернулся с отрядом, который Галл Аноним оценивает в пятьсот рыцарей, — помощь дал император Генрих III. Князь сделал центром страны Краков, которого почти не коснулось разорение, — Краков оставался столицей до 1596 года. Силезию Казимир вернул лишь в 1050 году, а мир с Чехией в 1054-м заключили при посредничестве императора, за ежегодную дань. Прозвище «Восстановитель» — Odnowiciel — ему дали позднейшие историки.",
    "Галл Аноним, I, 19; Козьма Пражский, II, 2–5"))

# ================================================================ 7. psie_pole (1109)
NEW_SCENES += [
    scene("glogow_messenger_pl", "Гонец из Глогова", ["sig_glogow_messenger_pl"], 2, "🐎", "спросить приказа", "icon_ally",
          ["гонец", "князь"], "liege_ride"),
    scene("glogow_engines_pl", "Заложники на осадных машинах", ["sig_glogow_engines_pl"], 2, "🏰", "штурм стен", "icon_dead",
          ["осаждающий", "защитник"], "siege"),
    scene("psie_pole_pl", "Пёсье поле", ["v_battle"], 2, "🐕", "битва", "icon_dead",
          ["нападающий", "защитник"], "open_battle_s"),
    scene("truce_talks_pl", "Мирные переговоры", ["v_parley"], 2, "🤝", "переговоры", "icon_ally",
          ["кто требует", "кто уступает"], "council"),
]
NEW_RULES += [
    rule("glogow_messenger_pl_sig", "Горожане за пять дней перемирия посылают к князю — и князь запрещает сдаваться, что бы ни случилось",
         "sig_glogow_messenger_pl",
         [actor("A", 0, tags=["burgher_pl"]),
          actor("B", 1, tags=["piast_pl"])],
         [setf("A", "steadfast_pl")]),
    rule("glogow_engines_hold_pl", "Император привязывает заложников к осадным машинам, но стойкий город не сдаётся — осада проваливается",
         "sig_glogow_engines_pl",
         [actor("A", 0, tags=["emperor_pl"]),
          actor("B", 1, tags=["burgher_pl"], flags=["steadfast_pl"])],
         [setf("A", "siege_failed"), remf("A", "strong")]),
    rule("glogow_engines_yield_pl", "Без княжеского слова горожане не выдерживают вида детей на машинах — и открывают ворота",
         "sig_glogow_engines_pl",
         [actor("A", 0, tags=["emperor_pl"]),
          actor("B", 1, tags=["burgher_pl"], notFlags=["steadfast_pl"])],
         [setf("B", "surrendered_pl"), setf("A", "victor")]),
]
NEW_LEVELS.append(level(
    "psie_pole", 70, ACT2, "poland_battle", "glogow_engines_pl", 3,
    ["glogow_messenger_pl", "glogow_engines_pl", "psie_pole_pl", "truce_talks_pl"],
    ["krzywousty", "henry5_hre", "glogow_burgher"],
    {"krzywousty": ["reigns", "standing", "strong"], "henry5_hre": ["crowned", "standing", "strong"]},
    [("enemy_of", "krzywousty", "henry5_hre"), ("enemy_of", "henry5_hre", "krzywousty"),
     ("enemy_of", "henry5_hre", "glogow_burgher")],
    [flag("henry5_hre", "defeated"), nflag("glogow_burgher", "surrendered_pl"), nflag("henry5_hre", "conceded")],
    [("glogow_messenger_pl", ["glogow_burgher", "krzywousty"]), ("glogow_engines_pl", ["henry5_hre", "glogow_burgher"]),
     ("psie_pole_pl", ["krzywousty", "henry5_hre"])],
    "simplification"))
TEXTS.update(texts("psie_pole",
    "Глогов и Пёсье поле",
    "Горожане Глогова не сдаются, даже когда император привязывает их детей к осадным машинам, — и князь бьёт ослабевшее войско",
    "Пока император в силе, в поле его не одолеть. Город устоит, только если знает волю князя, — без неё он сдастся. И никакого мира: император ушёл ни с чем.",
    "1109 год. Император Генрих V идёт на Польшу — посадить на трон изгнанного брата Болеслава Кривоустого, Збигнева. Первым на пути стоит Глогов на Одре. Горожане выпросили пять дней перемирия и дали заложников, обещая сдаться, если князь не придёт.",
    "Галл Аноним, современник событий, рассказывает, что Болеслав запретил глоговцам сдаваться, а когда перемирие кончилось, император велел привязать заложников, детей горожан, к осадным машинам, — но защитники всё равно отбили штурм. Осада провалилась, и войско Генриха, изматываемое партизанской войной, ушло. О битве на Пёсьем поле под Вроцлавом 24 августа 1109 года впервые пишет Винцентий Кадлубек век спустя: будто поле назвали так из-за собак, растаскивавших трупы, — это скорее легенда, Галл о большой битве молчит. Зато он приводит насмешливую песню, которую пели над немцами: «Златом Польшу не возьмёшь».",
    "Галл Аноним, III, 5–15; Винцентий Кадлубек, «Хроника», III"))

# ================================================================ 8. krzywousty_will (1138)
NEW_SCENES += [
    scene("will_senior_pl", "Завещание: Краков старшему", ["sig_will_senior_pl"], 2, "📜", "назначить сеньора", "icon_crown",
          ["отец", "старший сын"], "will_read_d"),
    scene("will_provinces_pl", "Уделы младшим сыновьям", ["sig_will_provinces_pl"], 3, "🗺️", "разделить земли", "icon_ally",
          ["отец", "сын", "сын"], "council_b"),
    scene("all_to_one_pl", "Всё — одному", ["sig_all_to_one_pl"], 2, "👑", "оставить страну одному", "icon_crown",
          ["отец", "наследник"], "throne_b"),
    scene("krzywousty_death_pl", "Смерть князя", ["sig_krzywousty_death_pl"], 1, "🕯️", "умереть", "icon_dead",
          ["князь"], "deathbed"),
]
NEW_RULES += [
    rule("will_senior_pl_sig", "Князь завещает Краков и верховную власть старшему сыну — сеньору над братьями",
         "sig_will_senior_pl",
         [actor("A", 0, tags=["father_pl"], notFlags=["will_made"]),
          actor("B", 1, tags=["son_pl"])],
         [setf("B", "senior_pl"), setf("A", "will_made")]),
    rule("will_provinces_pl_sig", "Младшим сыновьям — по уделу в вечное владение",
         "sig_will_provinces_pl",
         [actor("A", 0, tags=["father_pl"], flags=["will_made"]),
          actor("B", 1, tags=["son_pl"], notFlags=["senior_pl", "sole_heir"]),
          actor("C", 2, tags=["son_pl"], notFlags=["senior_pl", "sole_heir"])],
         [setf("B", "duke_province"), setf("C", "duke_province")]),
    rule("all_to_one_pl_sig", "Отец оставляет всё одному сыну — братья ополчаются на него ещё у отцовского гроба",
         "sig_all_to_one_pl",
         [actor("A", 0, tags=["father_pl"], notFlags=["will_made"]),
          actor("B", 1, tags=["son_pl"])],
         [setf("B", "sole_heir"), setf("A", "will_made")]),
    rule("krzywousty_death_pl_sig", "Князь умирает, и завещание вступает в силу",
         "sig_krzywousty_death_pl",
         [actor("A", 0, tags=["father_pl"], flags=["will_made"])],
         [setf("A", "dead")]),
]
NEW_LEVELS.append(level(
    "krzywousty_will", 80, ACT2, "poland_tension", "will_senior_pl", 3,
    ["will_senior_pl", "will_provinces_pl", "all_to_one_pl", "krzywousty_death_pl"],
    ["krzywousty", "wladyslaw2", "boleslaw4", "mieszko3"],
    {"krzywousty": ["reigns", "standing"]}, [],
    [flag("wladyslaw2", "senior_pl"), flag("boleslaw4", "duke_province"), flag("mieszko3", "duke_province"),
     flag("krzywousty", "dead")],
    [("will_senior_pl", ["krzywousty", "wladyslaw2"]), ("will_provinces_pl", ["krzywousty", "boleslaw4", "mieszko3"]),
     ("krzywousty_death_pl", ["krzywousty"])],
    "simplification"))
TEXTS.update(texts("krzywousty_will",
    "Завещание Кривоустого",
    "Князь делит страну между сыновьями, чтобы они не воевали, — и Польша на двести лет распадается на уделы",
    "Краков — старшему, по праву сеньора, младшим — уделы. Оставить всё одному кажется надёжнее, но братья не стали бы ждать. И завещание пишут, пока князь жив.",
    "1138 год. Болеслав Кривоустый всю жизнь воевал — с немцами, чехами, поморянами и с собственным братом Збигневом, которого велел ослепить и потом каялся. Теперь у него несколько сыновей от двух жён, и он хочет, чтобы после него они не резали друг друга.",
    "По завещанию Болеслава III, известному в пересказе Винцентия Кадлубка, старший в роду получал Краков и сеньориальный удел, а младшие сыновья — свои земли: Болеслав Кудрявый Мазовию, Мешко Старый Великопольшу, Генрих Сандомир; младшему, Казимиру, не досталось ничего. Принцип сеньората должен был сохранить единство, но уже в 1146 году старший, Владислав, попытался отнять уделы у братьев, был изгнан и умер на чужбине — отсюда прозвище «Изгнанник». Так начался период раздробленности: Польша распалась на десятки княжеств и объединилась снова лишь при Владиславе Локетке, коронованном в 1320 году. Подлинный текст завещания не сохранился.",
    "Винцентий Кадлубек, «Хроника», III, 26; Великопольская хроника"))

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
    chars = json.load(open(CHARS, encoding="utf-8"))
    scenes = json.load(open(SCENES, encoding="utf-8"))
    rules = json.load(open(RULES, encoding="utf-8"))
    known_scene_ids = {s["id"] for s in scenes}
    new_scene_ids = {s["id"] for s, _ in NEW_SCENES}
    assert len(new_scene_ids) == len(NEW_SCENES), "дубль id сцены в пачке"
    assert len({r["id"] for r in NEW_RULES}) == len(NEW_RULES), "дубль id правила в пачке"
    stats = {"char": 0, "char_art": 0, "scene": 0, "rule": 0, "level": 0, "art": 0, "i18n": 0, "chapter": 0}

    # 0. персонажи: запись в общей БД + спрайты фабрики со всеми позами
    for c in NEW_CHARS:
        existing = next((x for x in chars if x["id"] == c["id"]), None)
        if existing is not None and existing.get("tags") != c["tags"]:
            raise SystemExit(f"персонаж {c['id']} уже существует с другими тегами — коллизия id")
        if existing != c:
            upsert(chars, c)
            stats["char"] += 1
        for pose in POSES:
            src = os.path.join(ART_V2, f"char_{c['id']}{pose}.webp")
            dst = os.path.join(ART, f"char_{c['id']}{pose}.webp")
            if not os.path.exists(src):
                raise SystemExit(f"нет спрайта фабрики {src} — собери: /usr/bin/python3 factory/build.py {c['id']}")
            if not os.path.exists(dst) or open(src, "rb").read() != open(dst, "rb").read():
                shutil.copyfile(src, dst)
                stats["char_art"] += 1
    dump_compact(chars, CHARS)

    # 1. сцены (+ арт)
    for s, donor in NEW_SCENES:
        existing = next((x for x in scenes if x["id"] == s["id"]), None)
        if existing is not None and existing.get("tags") != s["tags"]:
            raise SystemExit(f"сцена {s['id']} уже существует с другими тегами — коллизия id")
        if existing != s:
            upsert(scenes, s)
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
        if existing != r:
            upsert(rules, r)
            stats["rule"] += 1
    dump_compact(rules, RULES)

    # 3. уровни
    os.makedirs(LEVELS, exist_ok=True)
    all_level_ids = {}
    for ep in os.listdir(rp("Content")):
        d = rp("Content", ep, "levels")
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.endswith(".json"):
                    all_level_ids[fn[:-5]] = os.path.join(d, fn)
    char_ids = {c["id"] for c in chars}
    for l in NEW_LEVELS:
        p = all_level_ids.get(l["id"])
        if p and os.path.dirname(p) != LEVELS:
            raise SystemExit(f"id уровня {l['id']} занят в другой главе: {p}")
        for sid in l["scenes"]:
            assert sid in known_scene_ids or sid in new_scene_ids, (l["id"], sid)
        for cid in l["characters"]:
            assert cid in char_ids, (l["id"], cid)
        path = os.path.join(LEVELS, f"{l['id']}.json")
        old = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None
        if old != l:
            dump_compact(l, path)
            stats["level"] += 1

    # 4. глава
    chapters = json.load(open(CHAPTERS, encoding="utf-8"))
    if not any(c["id"] == CHAPTER["id"] for c in chapters):
        chapters.append(CHAPTER)
        with open(CHAPTERS, "w", encoding="utf-8") as f:
            f.write("[\n" + ",\n".join("  " + json.dumps(c, ensure_ascii=False) for c in chapters) + "\n]\n")
        stats["chapter"] += 1

    # 5. i18n (только ru; переводы — tools/i18n/translate.py)
    cat = json.load(open(CATALOG, encoding="utf-8"))
    for c in NEW_CHARS:
        TEXTS[f"char.{c['id']}"] = c["name"]
    for s, _ in NEW_SCENES:
        TEXTS[f"scene.{s['id']}"] = s["name"]
        TEXTS[f"scene.{s['id']}.action"] = s["action"]
    TEXTS.update(CHAPTER_TEXTS)
    for k, v in TEXTS.items():
        if cat.get(k) != v:
            cat[k] = v
            stats["i18n"] += 1
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")

    print("poland_1:", ", ".join(f"{k} {v}" for k, v in stats.items()))
    print("levels:", " ".join(l["id"] for l in NEW_LEVELS))

if __name__ == "__main__":
    main()
