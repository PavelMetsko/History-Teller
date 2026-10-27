#!/usr/bin/env python3
"""Фоны новых сцен глав Англии/Франции/России/Италии через Nano Banana — рецепт poland_bg.py / usa_bg.py.
Списки (по 15 на страну) утверждены пользователем 2026-10-27; описания — <pre>_bg_prompts.json, раздача — <pre>_bg_map.json.

    source ~/.zshenv; /usr/bin/python3 tools/batches/country_bg.py <england|france|russia|italy> [name ...]
Исходники PNG → Art/source/<pre>_bg/<name>.png. Раздача по сценам — country_bg_apply.py.
"""
import json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(HERE))
from genart import gen
from poland_bg import STYLE, REF
from PIL import Image

if __name__ == "__main__":
    pre = sys.argv[1]
    BG = json.load(open(HERE / f"{pre}_bg_prompts.json", encoding="utf-8"))
    names = sys.argv[2:] or list(BG)
    out = ROOT / f"Art/source/{pre}_bg"; out.mkdir(parents=True, exist_ok=True)
    ref = out / "_ref.png"
    Image.open(REF).convert("RGB").resize((768, 768)).save(ref)
    for n in names:
        p = out / f"{n}.png"
        if p.exists():
            print("skip", n); continue
        gen(ref, STYLE + BG[n], p)
        print("ok", n, flush=True)
