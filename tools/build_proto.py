#!/usr/bin/env python3
"""Сборка играбельного прототипа: инжектирует JSON-контент в template.html.

Usage:
    python3 tools/build_proto.py [content_dir] [template] [out]
Defaults:
    content_dir = Content/rome
    template    = prototype/template.html
    out         = prototype/index.html
"""
import json
import sys
from pathlib import Path

MARKER = "/*__DATA__*/null"


def build(content_dir: Path, template: Path, out: Path):
    levels = []
    for f in sorted((content_dir / "levels").glob("*.json")):
        levels.append(json.loads(f.read_text(encoding="utf-8")))
    data = {
        "characters": json.loads((content_dir / "characters.json").read_text(encoding="utf-8")),
        "scenes": json.loads((content_dir / "scenes.json").read_text(encoding="utf-8")),
        "rules": json.loads((content_dir / "rules.json").read_text(encoding="utf-8")),
        "levels": levels,
    }
    tpl = template.read_text(encoding="utf-8")
    if MARKER not in tpl:
        sys.exit(f"marker {MARKER!r} not found in {template}")
    out.write_text(tpl.replace(MARKER, json.dumps(data, ensure_ascii=False)), encoding="utf-8")
    print(f"built {out}: {len(levels)} levels, "
          f"{len(data['characters'])} characters, {len(data['rules'])} rules")


if __name__ == "__main__":
    args = sys.argv[1:]
    root = Path(__file__).resolve().parent.parent
    content = Path(args[0]) if len(args) > 0 else root / "Content" / "rome"
    template = Path(args[1]) if len(args) > 1 else root / "prototype" / "template.html"
    out = Path(args[2]) if len(args) > 2 else root / "prototype" / "index.html"
    build(content, template, out)
