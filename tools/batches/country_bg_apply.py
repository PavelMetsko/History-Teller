#!/usr/bin/env python3
"""Раздать 15 фонов (Art/source/<pre>_bg) по новым сценам главы — только сцены пачек <pre>_1..4,
общие и старые сцены не трогаются.

    /usr/bin/python3 tools/batches/country_bg_apply.py <england|france|russia|italy>
"""
import importlib, json, sys, pathlib
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

if __name__ == "__main__":
    pre = sys.argv[1]
    sys.argv = [sys.argv[0]]
    own = {s["id"] for n in (1, 2, 3, 4) for s, _ in importlib.import_module(f"{pre}_{n}").SC}
    MAP = json.load(open(HERE / f"{pre}_bg_map.json", encoding="utf-8"))
    seen, n = set(), 0
    for bg, scenes in MAP.items():
        im = Image.open(ROOT / f"Art/source/{pre}_bg/{bg}.png").convert("RGB").resize((1024, 1024), Image.LANCZOS)
        for s in scenes:
            assert s in own, f"{s} — не сцена пачек {pre}"
            assert s not in seen, f"{s} дважды"
            seen.add(s)
            dst = ROOT / f"Content/art/scene_{s}.webp"
            assert dst.exists(), dst
            im.save(dst, "WEBP", quality=80, method=6)
            n += 1
    assert seen == own, f"без фона: {sorted(own - seen)[:5]}"
    print(f"{pre}: {n} сцен, {len(MAP)} фонов")
