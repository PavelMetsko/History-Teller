#!/usr/bin/env python3
"""Быстрая проверка пачек США без записи в базу: эталонное решение проходит, пустая доска — нет.
Только reference-прогон (миллисекунды), без перебора.

    python3 tools/batches/usa_check.py
"""
import sys, importlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0]]
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import simulate as S
from pathlib import Path

chars, scenes, rules = S.load_content(Path(HERE, "..", "..", "Content", "rome"))
levels = []
for n in range(1, 8):
    m = importlib.import_module(f"usa_{n}")
    chars.update({c["id"]: c for c in m.CH})
    scenes.update({s["id"]: s for s, _ in m.SC})
    new = {r["id"] for r in m.RU}
    rules = [r for r in rules if r["id"] not in new] + m.RU
    levels += m.LV
rules.sort(key=lambda r: -r.get("priority", 0))
bad = 0
for L in levels:
    sol = [(p["scene"], p["characters"]) for p in L["solution"]]
    issues = []
    if len(sol) != L["panels"]:
        issues.append("panels")
    for s, c in sol:
        if s not in L["scenes"] or len(c) > scenes[s].get("slots", 2):
            issues.append(f"bad panel {s}")
    if not S.goal_met(L["goal"], S.simulate(sol, S.initial_world(L), scenes, rules, chars)):
        issues.append("REF FAILS")
    if S.goal_met(L["goal"], S.initial_world(L)):
        issues.append("TRIVIAL")
    if issues:
        bad += 1
        print(L["id"], issues)
print(len(levels), "уровней, с ошибками:", bad)
