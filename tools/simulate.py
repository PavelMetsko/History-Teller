#!/usr/bin/env python3
"""Reference simulator + solver for History Teller content.

Mirrors the semantics of the C# Simulation library 1:1.
Usage:
    python3 simulate.py <content_dir> <level_file>   # solve one level
    python3 simulate.py <content_dir> --all          # validate all levels
"""
import json
import sys
import itertools
from pathlib import Path


# ---------- content ----------

def load_content(content_dir: Path):
    chars = {c["id"]: c for c in json.loads((content_dir / "characters.json").read_text())}
    scenes = {s["id"]: s for s in json.loads((content_dir / "scenes.json").read_text())}
    rules = sorted(json.loads((content_dir / "rules.json").read_text()),
                   key=lambda r: -r.get("priority", 0))
    return chars, scenes, rules


# ---------- world state ----------

class World:
    def __init__(self):
        self.flags = {}        # char_id -> set(str)
        self.relations = set() # {(rel, from, to)}

    def has_flag(self, char, flag):
        return flag in self.flags.get(char, set())

    def set_flag(self, char, flag):
        self.flags.setdefault(char, set()).add(flag)

    def remove_flag(self, char, flag):
        self.flags.get(char, set()).discard(flag)

    def has_rel(self, rel, a, b):
        return (rel, a, b) in self.relations

    def alive(self, char):
        return not self.has_flag(char, "dead")


# ---------- engine ----------

def actor_matches(actor, char_id, binding, world, char_defs):
    cdef = char_defs[char_id]
    if not all(t in cdef.get("tags", []) for t in actor.get("tags", [])):
        return False
    if not all(world.has_flag(char_id, f) for f in actor.get("flags", [])):
        return False
    if any(world.has_flag(char_id, f) for f in actor.get("notFlags", [])):
        return False
    for rc in actor.get("relations", []):
        other = binding.get(rc["to"])
        if other is None or not world.has_rel(rc["rel"], char_id, other):
            return False
    return True


def find_bindings(actors, present, world, char_defs):
    """All injective assignments of alive present characters to actor vars.
    Relation conditions are checked after full assignment (vars may reference each other)."""
    alive = [c for c in present if world.alive(c)]
    out = []
    for perm in itertools.permutations(alive, len(actors)):
        binding = {a["var"]: c for a, c in zip(actors, perm)}
        if all(actor_matches(a, binding[a["var"]], binding, world, char_defs)
               for a in actors):
            out.append(binding)
    return out


def apply_effects(effects, binding, world):
    for e in effects:
        t = e["type"]
        if t == "setFlag":
            world.set_flag(binding[e["target"]], e["flag"])
        elif t == "removeFlag":
            world.remove_flag(binding[e["target"]], e["flag"])
        elif t == "addRelation":
            world.relations.add((e["rel"], binding[e["from"]], binding[e["to"]]))
        elif t == "removeRelation":
            world.relations.discard((e["rel"], binding[e["from"]], binding[e["to"]]))
        else:
            raise ValueError(f"unknown effect type {t}")


def simulate(panels, world, scenes, rules, char_defs, log=None):
    """panels: list of (scene_id, [char_ids]). Mutates and returns world."""
    for i, (scene_id, present) in enumerate(panels):
        if scene_id is None:
            continue
        scene_tags = scenes[scene_id].get("tags", [])
        for rule in rules:  # already sorted by priority desc
            trig = rule["trigger"]
            if not all(t in scene_tags for t in trig.get("sceneTags", [])):
                continue
            # re-evaluate bindings against current world (effects in this panel count)
            for binding in find_bindings(trig["actors"], present, world, char_defs):
                # binding may have been invalidated by a previous effect in same panel
                # (e.g. a character died) — re-check aliveness and conditions
                if all(world.alive(binding[a["var"]]) and
                       actor_matches(a, binding[a["var"]], binding, world, char_defs)
                       for a in trig["actors"]):
                    apply_effects(rule["effects"], binding, world)
                    if log is not None:
                        log.append(f"panel {i+1}: rule '{rule['id']}' {binding}")
    return world


# ---------- goals ----------

def goal_met(goal, world):
    if "all" in goal:
        return all(goal_met(g, world) for g in goal["all"])
    if "any" in goal:
        return any(goal_met(g, world) for g in goal["any"])
    if "not" in goal:
        return not goal_met(goal["not"], world)
    if "flag" in goal:
        f = goal["flag"]
        return world.has_flag(f["char"], f["is"])
    if "relation" in goal:
        r = goal["relation"]
        return world.has_rel(r["rel"], r["from"], r["to"])
    raise ValueError(f"unknown goal node {goal}")


# ---------- initial state ----------

def initial_world(level):
    """Мир с учётом стартовых условий уровня (initialState)."""
    w = World()
    init = level.get("initialState", {})
    for char, flags in init.get("flags", {}).items():
        for f in flags:
            w.set_flag(char, f)
    for rel, frm, to in init.get("relations", []):
        w.relations.add((rel, frm, to))
    return w


# ---------- solver ----------

def panel_options(level, scenes):
    """All (scene, char_subset) fillings for a single panel."""
    opts = []
    chars = level["characters"]
    for sid in level["scenes"]:
        slots = scenes[sid].get("slots", 2)
        for k in range(0, min(slots, len(chars)) + 1):
            for combo in itertools.combinations(chars, k):
                opts.append((sid, list(combo)))
    return opts


def solve(level, scenes, rules, char_defs, max_solutions=None):
    opts = panel_options(level, scenes)
    solutions = []
    for assignment in itertools.product(opts, repeat=level["panels"]):
        w = simulate(list(assignment), initial_world(level), scenes, rules, char_defs)
        if goal_met(level["goal"], w):
            solutions.append(assignment)
            if max_solutions and len(solutions) >= max_solutions:
                break
    return solutions, len(opts) ** level["panels"]


def pretty(assignment, scenes, char_defs):
    return " | ".join(
        f"[{scenes[s]['name']}: {', '.join(char_defs[c]['name'] for c in cs) or '—'}]"
        for s, cs in assignment)


MAX_EXHAUSTIVE = 500_000  # выше — пропускаем полный перебор (только проверка эталона)


def validate_level(level_path, content_dir):
    char_defs, scenes, rules = load_content(content_dir)
    level = json.loads(Path(level_path).read_text())
    print(f"=== {level['id']} — «{level['title']}» ===")
    ok = True

    # 1. Эталонное решение из level['solution'] обязано решать уровень
    if "solution" in level:
        panels = [(p["scene"], p["characters"]) for p in level["solution"]]
        log = []
        w = simulate(panels, initial_world(level), scenes, rules, char_defs, log)
        if goal_met(level["goal"], w):
            print(f"reference solution: OK — {pretty(panels, scenes, char_defs)}")
            for line in log:
                print("  " + line)
        else:
            print("!! REFERENCE SOLUTION DOES NOT SOLVE THE LEVEL !!")
            ok = False
    else:
        print("warning: no reference solution in level file")

    # 2. Полный перебор (если пространство разумное)
    opts_count = len(panel_options(level, scenes))
    space = opts_count ** level["panels"]
    if space <= MAX_EXHAUSTIVE:
        sols, _ = solve(level, scenes, rules, char_defs)
        print(f"search space: {space}, solutions: {len(sols)}")
        if not sols:
            print("!! UNSOLVABLE !!")
            ok = False
        elif len(sols) > 8:
            print(f"warning: {len(sols)} solutions — пазл может быть слишком лёгким")
    else:
        print(f"search space: {space} (> {MAX_EXHAUSTIVE}) — exhaustive check skipped")

    return ok


if __name__ == "__main__":
    content = Path(sys.argv[1])
    ok = True
    if sys.argv[2] == "--all":
        for lf in sorted((content / "levels").glob("*.json")):
            ok &= validate_level(lf, content)
            print()
    else:
        ok = validate_level(sys.argv[2], content)
    sys.exit(0 if ok else 1)
