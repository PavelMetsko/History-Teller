#!/usr/bin/env python3
"""Сборка играбельного прототипа: инжектирует JSON-контент в template.html.

Usage:
    python3 tools/build_proto.py [content_dir] [template] [out]
Defaults:
    content_dir = Content/rome
    template    = prototype/template.html
    out         = prototype/index.html
"""
import base64
import json
import sys
from pathlib import Path

MARKER = "/*__DATA__*/null"


def build(content_dir: Path, template: Path, out: Path):
    levels = []
    for f in sorted((content_dir / "levels").glob("*.json")):
        levels.append(json.loads(f.read_text(encoding="utf-8")))

    # арт: Art/src/*.svg → base64 (портреты char_*, фоны scene_*)
    art = {}
    art_dir = content_dir.resolve().parent.parent / "Art" / "src"
    if art_dir.exists():
        for f in sorted(art_dir.glob("*.svg")):
            art[f.stem] = base64.b64encode(f.read_bytes()).decode("ascii")

    data = {
        "characters": json.loads((content_dir / "characters.json").read_text(encoding="utf-8")),
        "scenes": json.loads((content_dir / "scenes.json").read_text(encoding="utf-8")),
        "rules": json.loads((content_dir / "rules.json").read_text(encoding="utf-8")),
        "levels": levels,
        "art": art,
    }
    tpl = template.read_text(encoding="utf-8")
    if MARKER not in tpl:
        sys.exit(f"marker {MARKER!r} not found in {template}")
    out.write_text(tpl.replace(MARKER, json.dumps(data, ensure_ascii=False)), encoding="utf-8")
    print(f"built {out}: {len(levels)} levels, "
          f"{len(data['characters'])} characters, {len(data['rules'])} rules, "
          f"{len(art)} art assets")


if __name__ == "__main__":
    args = sys.argv[1:]
    root = Path(__file__).resolve().parent.parent
    content = Path(args[0]) if len(args) > 0 else root / "Content" / "rome"
    template = Path(args[1]) if len(args) > 1 else root / "prototype" / "template.html"
    out = Path(args[2]) if len(args) > 2 else root / "prototype" / "index.html"
    build(content, template, out)
