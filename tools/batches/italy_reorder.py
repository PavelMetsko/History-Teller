#!/usr/bin/env python3
"""Перенумерация и новые акты для ВСЕХ уровней главы «Италия» по PLAN из italy_common.py,
плюс ключи актов/подзаголовка во всех языках (ru — из ACTS, остальные — tools/i18n/italy/acts.json).
Идемпотентно.

    python3 tools/batches/italy_reorder.py
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import italy_common as E
import poland_1 as P

changed = 0
for path in sorted(glob.glob(P.rp("Content/borgia/levels/*.json"))):
    d = json.load(open(path, encoding="utf-8"))
    if d["id"] not in E.PLAN:
        raise SystemExit(f"{d['id']} нет в PLAN")
    order, act = E.PLAN[d["id"]]
    if (d["order"], d["act"]) != (order, act):
        d["order"], d["act"] = order, act
        P.dump_compact(d, path)
        changed += 1

tr = json.load(open(P.rp("tools/i18n/italy/acts.json"), encoding="utf-8"))
tr["ru"] = {"sub": E.CHAPTER_TEXTS["chapter.borgia.subtitle"], "acts": E.ACTS}
for lang, t in tr.items():
    path = P.rp(f"Content/i18n/{lang}.json")
    cat = json.load(open(path, encoding="utf-8"))
    cat["chapter.borgia.subtitle"] = t["sub"]
    for i, a in enumerate(t["acts"], 1):
        cat[f"act.borgia.{i}"] = a
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
print("уровней перенумеровано:", changed, "· языков:", len(tr))
