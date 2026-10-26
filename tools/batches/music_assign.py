#!/usr/bin/env python3
"""Своя музыка для Англии, Франции, России и Италии: проставляет поле music всем уровням глав.

Новые уровни берут настроение из своих пачек (<pre>_common.MUSIC), старые — из old_level_moods.json
(разметка GPT по названию и цели). Идемпотентно.

    python3 tools/batches/music_assign.py
"""
import glob, importlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv = [sys.argv[0]]
import poland_1 as P

CHAPTERS = {"england": "tudor", "france": "revolution", "russia": "empire", "italy": "borgia"}
OLD = json.load(open(os.path.join(HERE, "old_level_moods.json"), encoding="utf-8"))

changed, missing = 0, set()
for pre, epoch in CHAPTERS.items():
    music = {}
    for n in (1, 2, 3, 4):
        for l in importlib.import_module(f"{pre}_{n}").LV:
            music[l["id"]] = l["music"]
    for path in sorted(glob.glob(P.rp(f"Content/{epoch}/levels/*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        m = music.get(d["id"]) or f"{pre}_{OLD[d['id']]}"
        if not os.path.exists(P.rp(f"Content/audio/{m}.m4a")):
            missing.add(m)
        if d["music"] != m:
            d["music"] = m
            P.dump_compact(d, path)
            changed += 1
print("music: уровней обновлено", changed)
if missing:
    print("ещё нет треков (собери import_music + build_audio):", " ".join(sorted(missing)))
