#!/usr/bin/env python3
"""Раздать 15 фонов Nano Banana (Art/source/poland_bg) по сценам главы «Польша».
Трогает только собственные сцены главы (*_pl) — общие сцены других глав не меняются.

    /usr/bin/python3 tools/batches/poland_bg_apply.py
"""
import json, pathlib
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "Art/source/poland_bg"
ART = ROOT / "Content/art"

MAP = json.load(open(pathlib.Path(__file__).with_name("poland_bg_map.json"), encoding="utf-8"))

if __name__ == "__main__":
    seen, n = set(), 0
    for bg, scenes in MAP.items():
        im = Image.open(SRC / f"{bg}.png").convert("RGB").resize((1024, 1024), Image.LANCZOS)
        for s in scenes:
            assert s.endswith("_pl"), s
            assert s not in seen, f"{s} дважды"
            seen.add(s)
            dst = ART / f"scene_{s}.webp"
            assert dst.exists(), dst
            im.save(dst, "WEBP", quality=80, method=6)
            n += 1
    print(f"{n} сцен, {len(MAP)} фонов")
