#!/usr/bin/env python3
"""Проверка ловушек пачки B «Византия»: соблазнительные расстановки НЕ должны решать уровень.

    python3 byz_b_traps.py [repo_root]
"""
import json, os, sys
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
sys.path.insert(0, os.path.join(ROOT, "tools"))
from pathlib import Path
import simulate as S

chars, scenes, rules = S.load_content(Path(ROOT) / "Content/rome")
LV = Path(ROOT) / "Content/byzantium/levels"


def leaves(goal, world, out, neg=False):
    if "all" in goal:
        for g in goal["all"]: leaves(g, world, out, neg)
    elif "any" in goal:
        for g in goal["any"]: leaves(g, world, out, neg)
    elif "not" in goal:
        leaves(goal["not"], world, out, not neg)
    else:
        ok = S.goal_met(goal, world) != neg
        if not ok:
            if "flag" in goal:
                f = goal["flag"]; out.append(("not " if neg else "") + f"{f['char']}.{f['is']}")
            else:
                r = goal["relation"]; out.append(("not " if neg else "") + f"{r['rel']}({r['from']}->{r['to']})")


TRAPS = {
    "secret_history": [
        ("панегирик раньше пасквиля (порядок): «О постройках» до «Тайной истории»",
         [("wars_dictation", ["procopius", "belisarius"]), ("buildings_praise", ["procopius", "justinian"]), ("anekdota_desk", ["procopius", "theodora"])]),
        ("обнародовать при жизни: рукопись — переписчикам",
         [("wars_dictation", ["procopius", "belisarius"]), ("anekdota_desk", ["procopius", "theodora"]), ("copyists_forum", ["procopius"])]),
        ("Антонина-приманка: показать рукопись жене полководца",
         [("wars_dictation", ["procopius", "belisarius"]), ("anekdota_desk", ["procopius", "theodora"]), ("confide_antonina", ["procopius", "antonina"])]),
        ("пасквиль без ремесла историка (без «Войн»)",
         [("anekdota_desk", ["procopius", "theodora"]), ("buildings_praise", ["procopius", "justinian"]), ("wars_dictation", ["procopius", "belisarius"])]),
    ],
    "heraclius_coup": [
        ("Хосров-приманка: Ираклий сперва идёт на персов — разбит",
         [("persian_front", ["heraclius", "khosrow"]), ("africa_grain", ["heraclius", "phocas_c"]), ("fleet_610", ["heraclius"]), ("so_you_ruled", ["heraclius", "phocas_c"])]),
        ("сильный Ираклий воюет с Хосровом (ничья, at_war) — суд над Фокой невозможен",
         [("africa_grain", ["heraclius", "phocas_c"]), ("fleet_610", ["heraclius"]), ("persian_front", ["heraclius", "khosrow"]), ("so_you_ruled", ["heraclius", "phocas_c"])]),
        ("порядок: персы бьют Фоку ДО хлебной блокады — Фока ещё силён, ничья",
         [("persian_front", ["khosrow", "phocas_c"]), ("africa_grain", ["heraclius", "phocas_c"]), ("fleet_610", ["heraclius"]), ("so_you_ruled", ["heraclius", "phocas_c"])]),
        ("жадная подготовка: Фока набирает войско после блокады",
         [("africa_grain", ["heraclius", "phocas_c"]), ("fleet_610", ["phocas_c"]), ("persian_front", ["khosrow", "phocas_c"]), ("so_you_ruled", ["heraclius", "phocas_c"])]),
        ("посольство к Хосрову вместо флота",
         [("africa_grain", ["heraclius", "phocas_c"]), ("khosrow_envoys", ["heraclius", "khosrow"]), ("persian_front", ["khosrow", "phocas_c"]), ("so_you_ruled", ["heraclius", "phocas_c"])]),
    ],
    "romanos_blinded": [
        ("Алп-Арслан-приманка: султан выручает разбитого — сдаваться некому",
         [("adana_field", ["andronikos_doukas", "romanos4"]), ("sultan_rescue", ["alp_arslan", "romanos4"]), ("bishops_oath", ["andronikos_doukas", "romanos4"])]),
        ("порядок: ослепить до клятвы",
         [("adana_field", ["andronikos_doukas", "romanos4"]), ("kotyaion_road", ["andronikos_doukas", "romanos4"]), ("bishops_oath", ["andronikos_doukas", "romanos4"])]),
        ("уйти к султану после поражения",
         [("adana_field", ["andronikos_doukas", "romanos4"]), ("sultan_refuge", ["romanos4"]), ("bishops_oath", ["andronikos_doukas", "romanos4"])]),
        ("роли: Роман нападает на Дуку (нападающий — Дука, не Роман)",
         [("adana_field", ["romanos4", "andronikos_doukas"]), ("bishops_oath", ["andronikos_doukas", "romanos4"]), ("kotyaion_road", ["andronikos_doukas", "romanos4"])]),
    ],
    "bohemond_antioch": [
        ("дипломатия: император уговаривает Боэмунда вернуть город",
         [("two_sisters_tower", ["bohemond"]), ("hand_over_antioch", ["alexios1", "bohemond"]), ("prince_of_antioch", ["bohemond", "alexios1"])]),
        ("порядок: князь Антиохии, пока император ещё не повернул назад",
         [("two_sisters_tower", ["bohemond"]), ("prince_of_antioch", ["bohemond", "alexios1"]), ("philomelion", ["alexios1"])]),
        ("жадный уход: в Филомелии уходит Боэмунд",
         [("two_sisters_tower", ["bohemond"]), ("philomelion", ["bohemond"]), ("prince_of_antioch", ["bohemond", "alexios1"])]),
        ("Кылыч-приманка: Дорилей вместо башни",
         [("dorylaeum", ["bohemond", "kilij"]), ("philomelion", ["alexios1"]), ("prince_of_antioch", ["bohemond", "alexios1"])]),
    ],
    "zara": [
        ("порядок/замок: посулы царевича ДО Зары — купленный дож не идёт на Зару",
         [("san_marco_cross", ["dandolo"]), ("promise_marks", ["alexios4", "dandolo"]), ("zara_walls", ["dandolo"]), ("papal_anathema", ["innocent3", "dandolo"])]),
        ("папа-приманка: послушать легата до креста — уступивший дож",
         [("papal_legate", ["innocent3", "dandolo"]), ("san_marco_cross", ["dandolo"]), ("zara_walls", ["dandolo"]), ("papal_anathema", ["innocent3", "dandolo"])]),
        ("отлучение до взятия Зары",
         [("san_marco_cross", ["dandolo"]), ("papal_anathema", ["innocent3", "dandolo"]), ("zara_walls", ["dandolo"]), ("promise_marks", ["alexios4", "dandolo"])]),
        ("Зара без креста",
         [("zara_walls", ["dandolo"]), ("san_marco_cross", ["dandolo"]), ("papal_anathema", ["innocent3", "dandolo"]), ("promise_marks", ["alexios4", "dandolo"])]),
    ],
    "theophano_widow": [
        ("Цимисхий-приманка: любовь императрицы и племянника (не в этой серии)",
         [("theophano_lover", ["theophano", "tzimiskes"]), ("caesarea_shield", ["nikephoros", "tzimiskes"]), ("nea_wedding", ["nikephoros", "theophano"])]),
        ("жадное венчание: вдову венчают с Цимисхием",
         [("caesarea_shield", ["nikephoros", "tzimiskes"]), ("godfather_oath", ["nikephoros", "theophano"]), ("nea_wedding", ["tzimiskes", "theophano"])]),
        ("флаг-замок: венчание без снятия духовного родства",
         [("caesarea_shield", ["nikephoros", "tzimiskes"]), ("nea_wedding", ["nikephoros", "theophano"]), ("godfather_oath", ["nikephoros", "theophano"])]),
        ("«провозглашение» на ипподроме вместо щита в Кесарии",
         [("hippodrome_honour", ["nikephoros", "tzimiskes"]), ("godfather_oath", ["nikephoros", "theophano"]), ("nea_wedding", ["nikephoros", "theophano"])]),
    ],
    "mehmed_ultimatum": [
        ("флаг-замок: ультиматум слабому императору — он уступает",
         [("urban_foundry", ["constantine11", "mehmed2"]), ("lemnos_promise", ["constantine11", "giustiniani"]), ("morea_offer", ["mehmed2", "constantine11"]), ("st_romanus_gate", ["giustiniani", "constantine11"])]),
        ("султан-приманка: купить мир у Мехмеда",
         [("urban_foundry", ["constantine11", "mehmed2"]), ("lemnos_promise", ["constantine11", "mehmed2"]), ("st_romanus_gate", ["giustiniani", "constantine11"]), ("morea_offer", ["mehmed2", "constantine11"])]),
        ("Богазкесен вместо пушки: султан силён, но без бомбарды ультиматума нет",
         [("rumeli_hisar", ["mehmed2"]), ("lemnos_promise", ["constantine11", "giustiniani"]), ("st_romanus_gate", ["giustiniani", "constantine11"]), ("morea_offer", ["mehmed2", "constantine11"])]),
        ("уплыть в Морею",
         [("urban_foundry", ["constantine11", "mehmed2"]), ("lemnos_promise", ["constantine11", "giustiniani"]), ("leave_city", ["constantine11"]), ("morea_offer", ["mehmed2", "constantine11"])]),
    ],
}

bad = 0
for lid, traps in TRAPS.items():
    level = json.loads((LV / f"{lid}.json").read_text())
    ref = [(p["scene"], p["characters"]) for p in level["solution"]]
    w = S.simulate(ref, S.initial_world(level), scenes, rules, chars)
    assert S.goal_met(level["goal"], w), f"{lid}: эталон не решает!"
    print(f"=== {lid}: reference OK")
    for name, panels in traps:
        assert len(panels) == level["panels"], f"{lid}/{name}: панелей {len(panels)} != {level['panels']}"
        for sid, cs in panels:
            assert sid in level["scenes"], f"{lid}/{name}: сцена {sid} не в уровне"
            assert all(c in level["characters"] for c in cs)
        log = []
        w = S.simulate(panels, S.initial_world(level), scenes, rules, chars, log)
        met = S.goal_met(level["goal"], w)
        fails = []
        leaves(level["goal"], w, fails)
        status = "TRAP OK (goal NOT met)" if not met else "!! TRAP FAILED — solves the level"
        fired = [l.split("'")[1] for l in log]
        print(f"  [{status}] {name}\n      сработало: {', '.join(fired) or '—'}\n      не выполнено: {', '.join(fails) or '—'}")
        if met:
            bad += 1
print()
print("ALL TRAPS HOLD" if not bad else f"!! {bad} traps solve the level")
sys.exit(1 if bad else 0)
