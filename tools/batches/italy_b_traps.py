#!/usr/bin/env python3
"""Проверка ловушек пачки B главы «Италия»: соблазнительные расстановки НЕ решают уровень,
эталон — решает. На базе tools/simulate.py (simulate()/goal_met()).

    python3 italy_b_traps.py [repo_root]
"""
import json, os, sys
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
sys.path.insert(0, os.path.join(ROOT, "tools"))
from pathlib import Path
import simulate as S

CHARS, SCENES, RULES = S.load_content(Path(ROOT) / "Content/rome")

def run(level, panels):
    w = S.simulate(panels, S.initial_world(level), SCENES, RULES, CHARS)
    return S.goal_met(level["goal"], w), w

def load(lid):
    return json.loads(Path(ROOT, "Content/borgia/levels", f"{lid}.json").read_text())

# lid -> [(описание ловушки, панели), ...]; каждая панель — (scene, [chars])
TRAPS = {
    "francis_sultan": [
        ("флаг-замок: взять меч (v_prepare) → strong → через линию не пройти",
         [("take_the_cross", ["francis"]), ("cross_the_lines", ["francis"])]),
        ("вооружённый Франциск сразу в шатёр — без перехода линии султан не слушает",
         [("take_the_cross", ["francis"]), ("sultan_tent", ["francis", "al_kamil"])]),
        ("приманка-император: Фридрих в штурм Дамиетты → at_war → цель not(at_war)",
         [("damietta_siege", ["frederick2", "al_kamil"]), ("sultan_tent", ["francis", "al_kamil"])]),
        ("порядок: шатёр без перехода линии — ничего",
         [("sultan_tent", ["francis", "al_kamil"]), ("cross_the_lines", ["francis"])]),
    ],
    "bordeaux_duel": [
        ("сцена-приманка: бой ста на сто → at_war → и ристалище закрыто, и цель not(at_war)",
         [("challenge_bordeaux", ["charles_anjou", "peter_aragon"]), ("duel_field_b", ["charles_anjou", "peter_aragon"]),
          ("lists_bordeaux", ["charles_anjou"])]),
        ("судья Эдуард (v_parley) → conceded → цель not(edward1 conceded)",
         [("challenge_bordeaux", ["charles_anjou", "peter_aragon"]), ("ask_edward", ["charles_anjou", "edward1"]),
          ("lists_bordeaux", ["peter_aragon"])]),
        ("порядок: ристалище до вызова — без duel_set явка не засчитана",
         [("lists_bordeaux", ["peter_aragon"]), ("challenge_bordeaux", ["charles_anjou", "peter_aragon"]),
          ("lists_bordeaux", ["charles_anjou"])]),
        ("приманка Прочида: вызов заговорщику вместо короля",
         [("challenge_bordeaux", ["charles_anjou", "procida"]), ("lists_bordeaux", ["peter_aragon"]),
          ("lists_bordeaux", ["charles_anjou"])]),
    ],
    "cola_death": [
        ("приманка-сцена: снова объявить себя трибуном (rallied) → налог не вводит, цель not(rallied)",
         [("avignon_pardon", ["pope", "cola"]), ("capitol_tribune", ["cola"]), ("capitol_fire_1354", ["colonna", "cola"])]),
        ("подкуп Колонны (v_bribe) → bought → купленный барон толпу не подстрекает",
         [("avignon_pardon", ["pope", "cola"]), ("bribe_barons", ["cola", "colonna"]), ("capitol_fire_1354", ["colonna", "cola"])]),
        ("переодеться нищим (v_flee) → away → до толпы не добраться",
         [("avignon_pardon", ["pope", "cola"]), ("beggar_disguise", ["cola"]), ("capitol_fire_1354", ["colonna", "cola"])]),
        ("порядок: налог без папского мандата — он ещё узник",
         [("wine_tax", ["cola"]), ("avignon_pardon", ["pope", "cola"]), ("capitol_fire_1354", ["colonna", "cola"])]),
    ],
    "lorenzo_deathbed": [
        ("жадный v_bribe: золото в кружку → монах bought → не приор и не у постели",
         [("gold_for_san_marco", ["lorenzo", "savonarola"]), ("careggi_bedside", ["lorenzo", "savonarola"]), ("face_to_wall", ["lorenzo"])]),
        ("приманка Борджиа: кардинал у постели вместо монаха",
         [("prior_san_marco", ["savonarola"]), ("careggi_bedside", ["lorenzo", "rodrigo"]), ("face_to_wall", ["lorenzo"])]),
        ("порядок: жемчуг врача до исповеди → смерть без исповеди",
         [("prior_san_marco", ["savonarola"]), ("pearl_potion", ["lorenzo"]), ("careggi_bedside", ["lorenzo", "savonarola"])]),
        ("порядок: постель без приорства — монах ещё не тот, кто не кланяется",
         [("careggi_bedside", ["lorenzo", "savonarola"]), ("prior_san_marco", ["savonarola"]), ("face_to_wall", ["lorenzo"])]),
    ],
    "imola_1502": [
        ("жадный v_bribe: герцог покупает посла → bought → цель not(bought), депеш нет",
         [("engineer_patent", ["cesare", "machiavelli"]), ("engineer_patent", ["cesare", "leonardo"]), ("map_of_imola", ["leonardo", "cesare"])]),
        ("посол куплен после карты — всё равно not(bought)",
         [("engineer_patent", ["cesare", "leonardo"]), ("map_of_imola", ["leonardo", "cesare"]), ("engineer_patent", ["cesare", "machiavelli"])]),
        ("порядок: карта до найма — не в свите, не чертит",
         [("map_of_imola", ["leonardo", "cesare"]), ("engineer_patent", ["cesare", "leonardo"]), ("envoy_watches", ["machiavelli", "cesare"])]),
        ("сцена-приманка: встреча Леонардо и Макиавелли вместо депеш",
         [("engineer_patent", ["cesare", "leonardo"]), ("map_of_imola", ["leonardo", "cesare"]), ("imola_meeting", ["leonardo", "machiavelli"])]),
    ],
    "senigallia": [
        ("открытый бой: герцог слабее → defeated/at_war → мира не сыграть, цель not(at_war)",
         [("open_battle_s", ["cesare", "orsini"]), ("feigned_peace", ["cesare", "orsini"]), ("senigallia_gate", ["cesare", "orsini"])]),
        ("французские копья + бой → stalemate, at_war → цель not(at_war)",
         [("french_lances", ["cesare"]), ("open_battle_s", ["cesare", "orsini"]), ("senigallia_gate", ["cesare", "orsini"])]),
        ("жадный v_plot: посол в Маджоне → plotting → цель not(plotting), депеши нет",
         [("magione_castle", ["orsini", "machiavelli"]), ("feigned_peace", ["cesare", "orsini"]), ("senigallia_gate", ["cesare", "orsini"])]),
        ("порядок: Синигалья без притворного мира — заговорщик не доверился, не пришёл",
         [("senigallia_gate", ["cesare", "orsini"]), ("feigned_peace", ["cesare", "orsini"]), ("dispatch_florence", ["machiavelli", "cesare"])]),
    ],
    "michelangelo_flight": [
        ("явиться на папский вызов (v_parley) → conceded → цель not(conceded)",
         [("rome_summons", ["rovere", "michelangelo"]), ("night_flight", ["michelangelo"]), ("bologna_pardon", ["rovere", "michelangelo"])]),
        ("мост через Золотой Рог → in_turkey → ни Синьория, ни Болонья",
         [("night_flight", ["michelangelo"]), ("golden_horn", ["michelangelo"]), ("bologna_pardon", ["rovere", "michelangelo"])]),
        ("порядок: Болонья без уговоров Синьории",
         [("night_flight", ["michelangelo"]), ("bologna_pardon", ["rovere", "michelangelo"]), ("signoria_pressure", ["machiavelli", "michelangelo"])]),
        ("Синьория до побега — уговаривать некого, он ещё в Риме",
         [("signoria_pressure", ["machiavelli", "michelangelo"]), ("night_flight", ["michelangelo"]), ("bologna_pardon", ["rovere", "michelangelo"])]),
    ],
    "castel_escape": [
        ("виселица Пьера Луиджи (v_execute) → осуждённый мёртв",
         [("jewel_accusation", ["pope", "cellini"]), ("farnese_gallows", ["pope", "cellini"]), ("french_intercession", ["francis1", "cellini"])]),
        ("бежать во Францию до ареста (v_flee) → away → верёвка не нужна, король не вытаскивает",
         [("flee_to_france", ["cellini"]), ("jewel_accusation", ["pope", "cellini"]), ("bedsheet_rope", ["cellini"])]),
        ("порядок: король просит за ювелира до побега — ещё не тот узник, о котором говорит Париж",
         [("jewel_accusation", ["pope", "cellini"]), ("french_intercession", ["francis1", "cellini"]), ("bedsheet_rope", ["cellini"])]),
        ("папа вместо короля в заступничестве",
         [("jewel_accusation", ["pope", "cellini"]), ("bedsheet_rope", ["cellini"]), ("french_intercession", ["pope", "cellini"])]),
    ],
    "bellarmine_1616": [
        ("формальное отречение (v_parley) → conceded → цель not(conceded)",
         [("holy_office_1616", ["bellarmine"]), ("formal_abjuration", ["bellarmine", "galileo"]), ("certificate_1616", ["galileo", "bellarmine"])]),
        ("бежать в Венецию → away → увещевания нет",
         [("holy_office_1616", ["bellarmine"]), ("flee_venice", ["galileo"]), ("admonition_1616", ["bellarmine", "galileo"])]),
        ("приманка Барберини: друг вместо инквизитора в увещевании",
         [("holy_office_1616", ["bellarmine"]), ("admonition_1616", ["urban8", "galileo"]), ("certificate_1616", ["galileo", "bellarmine"])]),
        ("порядок: увещевание без декрета Святой палаты",
         [("admonition_1616", ["bellarmine", "galileo"]), ("holy_office_1616", ["bellarmine"]), ("certificate_1616", ["galileo", "bellarmine"])]),
    ],
    "aspromonte": [
        ("идти на Рим против короля (v_battle) → at_war → цель not(at_war)",
         [("roma_o_morte", ["garibaldi"]), ("royal_proclamation", ["victor_emmanuel", "garibaldi"]), ("march_on_rome_g", ["garibaldi", "victor_emmanuel"])]),
        ("штурмовать французский Рим → at_war/defeated",
         [("roma_o_morte", ["garibaldi"]), ("french_rome", ["garibaldi", "napoleon3"]), ("aspromonte_1862", ["victor_emmanuel", "garibaldi"])]),
        ("без добровольцев на французов — разбит, at_war",
         [("french_rome", ["garibaldi", "napoleon3"]), ("royal_proclamation", ["victor_emmanuel", "garibaldi"]), ("aspromonte_1862", ["victor_emmanuel", "garibaldi"])]),
        ("порядок: Аспромонте без прокламации — король ещё не враг",
         [("roma_o_morte", ["garibaldi"]), ("aspromonte_1862", ["victor_emmanuel", "garibaldi"]), ("royal_proclamation", ["victor_emmanuel", "garibaldi"])]),
        ("кивок Раттацци вместо прокламации — дружба короля не заменяет отречения",
         [("roma_o_morte", ["garibaldi"]), ("rattazzi_wink", ["victor_emmanuel", "garibaldi"]), ("aspromonte_1862", ["victor_emmanuel", "garibaldi"])]),
    ],
}

bad = 0
for lid, traps in TRAPS.items():
    level = load(lid)
    ref = [(p["scene"], p["characters"]) for p in level["solution"]]
    ok, _ = run(level, ref)
    print(f"=== {lid}: reference {'OK' if ok else '!! FAIL'}")
    bad += not ok
    for desc, panels in traps:
        assert len(panels) <= level["panels"], (lid, desc)
        met, w = run(level, panels)
        mark = "trap holds" if not met else "!! TRAP SOLVES LEVEL"
        bad += met
        print(f"  [{mark}] {desc}")
print()
print("ALL GREEN" if not bad else f"PROBLEMS: {bad}")
sys.exit(1 if bad else 0)
