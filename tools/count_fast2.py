#!/usr/bin/env python3
"""Fast canonical-solution counter via state-memoized DFS.
Role-less scenes use combinations (order irrelevant) -> counts are canonical."""
import json, sys, itertools
from functools import lru_cache
from pathlib import Path

content = Path(sys.argv[1])
chars = {c["id"]: c for c in json.loads((content/"characters.json").read_text())}
scenes = {s["id"]: s for s in json.loads((content/"scenes.json").read_text())}
rules = sorted(json.loads((content/"rules.json").read_text()), key=lambda r:-r.get("priority",0))

def actor_matches(a, cid, b, flags, rels):
    ct = chars[cid].get("tags",[])
    if not all(t in ct for t in a.get("tags",[])): return False
    fl = flags.get(cid,frozenset())
    if not all(f in fl for f in a.get("flags",[])): return False
    if any(f in fl for f in a.get("notFlags",[])): return False
    for rc in a.get("relations",[]):
        o=b.get(rc["to"])
        if o is None or (rc["rel"],cid,o) not in rels: return False
    return True

def bindings(actors, present, flags, rels):
    alive=[c for c in present if "dead" not in flags.get(c,frozenset())]
    slotted=[a for a in actors if a.get("slot") is not None]
    res=[]
    if slotted:
        b={}; used=set()
        for a in slotted:
            s=a["slot"]
            if s>=len(present): return []
            c=present[s]
            if "dead" in flags.get(c,frozenset()) or c in used: return []
            b[a["var"]]=c; used.add(c)
        rest=[a for a in actors if a.get("slot") is None]
        free=[c for c in alive if c not in used]
        for perm in itertools.permutations(free,len(rest)):
            bb=dict(b)
            for a,c in zip(rest,perm): bb[a["var"]]=c
            if all(actor_matches(a,bb[a["var"]],bb,flags,rels) for a in actors): res.append(bb)
        return res
    for perm in itertools.permutations(alive,len(actors)):
        b={a["var"]:c for a,c in zip(actors,perm)}
        if all(actor_matches(a,b[a["var"]],b,flags,rels) for a in actors): res.append(b)
    return res

def step(sid, present, flags, rels):
    """apply one panel, return new (flags,rels) as dicts/sets"""
    flags={k:set(v) for k,v in flags.items()}; rels=set(rels)
    st=scenes[sid].get("tags",[])
    for rule in rules:
        trig=rule["trigger"]
        if not all(t in st for t in trig.get("sceneTags",[])): continue
        ffl={k:frozenset(v) for k,v in flags.items()}
        for b in bindings(trig["actors"],present,ffl,rels):
            if all("dead" not in flags.get(b[a["var"]],set()) and actor_matches(a,b[a["var"]],b,{k:frozenset(v) for k,v in flags.items()},rels) for a in trig["actors"]):
                for e in rule["effects"]:
                    t=e["type"]
                    if t=="setFlag": flags.setdefault(b[e["target"]],set()).add(e["flag"])
                    elif t=="removeFlag": flags.get(b[e["target"]],set()).discard(e["flag"])
                    elif t=="addRelation": rels.add((e["rel"],b[e["from"]],b[e["to"]]))
                    elif t=="removeRelation": rels.discard((e["rel"],b[e["from"]],b[e["to"]]))
    return flags,rels

def goal_met(g,flags,rels):
    if "all" in g: return all(goal_met(x,flags,rels) for x in g["all"])
    if "any" in g: return any(goal_met(x,flags,rels) for x in g["any"])
    if "not" in g: return not goal_met(g["not"],flags,rels)
    if "flag" in g: return g["flag"]["is"] in flags.get(g["flag"]["char"],set())
    if "relation" in g:
        r=g["relation"]; return (r["rel"],r["from"],r["to"]) in rels
    raise ValueError(g)

lvl=json.loads(Path(sys.argv[2]).read_text())
iflags={k:set(v) for k,v in lvl.get("initialState",{}).get("flags",{}).items()}
irels=set(tuple(x) for x in lvl.get("initialState",{}).get("relations",[]))
cs=lvl["characters"]; GOAL=lvl["goal"]; NP=lvl["panels"]

# canonical panel options
opts=[]
for sid in lvl["scenes"]:
    sl=scenes[sid].get("slots",2)
    # Порядок в панели значим ТОЛЬКО если правило сцены реально использует slot.
    # Наличие `roles` (UI-подписи слотов) само по себе порядок НЕ делает значимым —
    # иначе каноника — фикция (перестановки игрово идентичны; игра ещё и авто-раскладывает).
    _st=scenes[sid].get("tags",[])
    role=any(all(t in _st for t in r["trigger"].get("sceneTags",[]))
             and any(a.get("slot") is not None for a in r["trigger"]["actors"]) for r in rules)
    gen = itertools.permutations if role else itertools.combinations
    for k in range(0,min(sl,len(cs))+1):
        for combo in gen(cs,k):
            opts.append((sid,list(combo)))

def key(flags,rels):
    return (frozenset((c,frozenset(f)) for c,f in flags.items() if f), frozenset(rels))

memo={}
def dfs(flags,rels,left):
    if left==0:
        return 1 if goal_met(GOAL,flags,rels) else 0
    k=(key(flags,rels),left)
    if k in memo: return memo[k]
    tot=0
    for sid,present in opts:
        nf,nr=step(sid,present,flags,rels)
        tot+=dfs(nf,nr,left-1)
    memo[k]=tot
    return tot

print(f"{lvl['id']}: canonical_solutions={dfs(iflags,irels,NP)} (opts/panel={len(opts)})")
