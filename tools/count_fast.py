#!/usr/bin/env python3
"""Fast canonical-solution counter for 3-panel levels."""
import json, sys, itertools
from pathlib import Path

content = Path(sys.argv[1])
chars = {c["id"]: c for c in json.loads((content/"characters.json").read_text())}
scenes = {s["id"]: s for s in json.loads((content/"scenes.json").read_text())}
rules = sorted(json.loads((content/"rules.json").read_text()), key=lambda r:-r.get("priority",0))

def actor_matches(a, cid, b, flags, rels):
    cd = chars[cid]
    ct = cd.get("tags",[])
    if not all(t in ct for t in a.get("tags",[])): return False
    fl = flags.get(cid,())
    if not all(f in fl for f in a.get("flags",[])): return False
    if any(f in fl for f in a.get("notFlags",[])): return False
    for rc in a.get("relations",[]):
        o = b.get(rc["to"])
        if o is None or (rc["rel"],cid,o) not in rels: return False
    return True

def bindings(actors, present, flags, rels):
    alive=[c for c in present if "dead" not in flags.get(c,())]
    slotted=[a for a in actors if a.get("slot") is not None]
    res=[]
    if slotted:
        b={}; used=set()
        for a in slotted:
            s=a["slot"]
            if s>=len(present): return []
            c=present[s]
            if "dead" in flags.get(c,()) or c in used: return []
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

def simulate(panels, iflags, irels):
    flags={k:set(v) for k,v in iflags.items()}
    rels=set(irels)
    for sid,present in panels:
        if sid is None: continue
        st=scenes[sid].get("tags",[])
        for rule in rules:
            trig=rule["trigger"]
            if not all(t in st for t in trig.get("sceneTags",[])): continue
            for b in bindings(trig["actors"],present,flags,rels):
                if all("dead" not in flags.get(b[a["var"]],()) and actor_matches(a,b[a["var"]],b,flags,rels) for a in trig["actors"]):
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
    if "flag" in g: return g["flag"]["is"] in flags.get(g["flag"]["char"],())
    if "relation" in g:
        r=g["relation"]; return (r["rel"],r["from"],r["to"]) in rels
    raise ValueError(g)

lvl=json.loads(Path(sys.argv[2]).read_text())
iflags={k:list(v) for k,v in lvl.get("initialState",{}).get("flags",{}).items()}
irels=[tuple(x) for x in lvl.get("initialState",{}).get("relations",[])]
cs=lvl["characters"]
opts=[]
for sid in lvl["scenes"]:
    sl=scenes[sid].get("slots",2)
    for k in range(0,min(sl,len(cs))+1):
        for perm in itertools.permutations(cs,k):
            opts.append((sid,list(perm)))
seen=set(); n=0
for asg in itertools.product(opts,repeat=lvl["panels"]):
    f,r=simulate(list(asg),iflags,irels)
    if goal_met(lvl["goal"],f,r):
        key=tuple((sid,tuple(ch) if scenes[sid].get("roles") else tuple(sorted(ch))) for sid,ch in asg)
        seen.add(key); n+=1
print(f"{lvl['id']}: space={len(opts)**lvl['panels']} raw={n} canonical={len(seen)}")
