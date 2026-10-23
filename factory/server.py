#!/usr/bin/env python3
"""Локальный сервер редактора персонажей. Только стандартная библиотека + PIL.

    /usr/bin/python3 factory/server.py      → http://localhost:8091

API:
  GET  /api/catalog              слоты, варианты, параметры
  GET  /api/cast                 персонажи игры: id, имя, есть ли старый и новый спрайт, есть ли рецепт
  GET  /api/recipe?id=X          рецепт (404 — нет)
  POST /api/render  {recipe}     → {poses: {base: "<svg…>", …}}
  POST /api/save    {recipe, png: {base: dataURL, …}} → рецепт в factory/recipes, спрайты в Content/art_v2
  GET  /art/…, /art_v2/…         картинки старого и нового арта
"""
from __future__ import annotations

import base64
import json
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402
import catalog  # noqa: E402
import rig  # noqa: E402

PORT = 8091
ART = ROOT / "Content" / "art"
ART_V2 = ROOT / "Content" / "art_v2"
ID_RE = re.compile(r"^[a-z][a-z0-9_]{0,40}$")


def full_svg(rec: dict, pose: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{build.W}" height="{build.H}" '
            f'viewBox="0 0 {build.W} {build.H}"><defs>{rig.defs("f")}</defs>{rig.render(rec, pose, "f")}</svg>')


def cast() -> list[dict]:
    chars = json.loads((ROOT / "Content" / "rome" / "characters.json").read_text())
    ru = json.loads((ROOT / "Content" / "i18n" / "ru.json").read_text())
    have = {p.stem for p in catalog.RECIPES_DIR.glob("*.json")}
    ids = [c["id"] for c in chars] + sorted(have - {c["id"] for c in chars})
    names = {c["id"]: c.get("name", c["id"]) for c in chars}
    return [{"id": i, "name": ru.get(f"char.{i}", names.get(i, i)),
             "old": (ART / f"char_{i}.webp").exists(), "new": (ART_V2 / f"char_{i}.webp").exists(),
             "recipe": i in have} for i in ids]


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(HERE / "editor"), **kw)

    def log_message(self, fmt, *args):
        if args and "/api/" in str(args[0]):
            super().log_message(fmt, *args)

    def send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, path: Path):
        if not path.is_file():
            return self.send_error(404)
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "image/webp" if path.suffix == ".webp" else "image/png")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/catalog":
            return self.send_json(catalog.schema())
        if u.path == "/api/cast":
            return self.send_json(cast())
        if u.path == "/api/recipe":
            rid = parse_qs(u.query).get("id", [""])[0]
            p = catalog.RECIPES_DIR / f"{rid}.json"
            return self.send_json(json.loads(p.read_text())) if ID_RE.match(rid) and p.exists() else self.send_json({}, 404)
        for prefix, base in (("/art/", ART), ("/art_v2/", ART_V2)):
            if u.path.startswith(prefix):
                name = u.path[len(prefix):]
                return self.send_file(base / name) if re.match(r"^[a-z0-9_]+\.webp$", name) else self.send_error(404)
        return super().do_GET()

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        rec = body.get("recipe", {})
        if not ID_RE.match(rec.get("id", "")):
            return self.send_json({"error": "id: латиница в нижнем регистре, цифры и _"}, 400)
        try:
            built = catalog.build(rec)
        except Exception as e:  # кривой рецепт не должен ронять сервер
            return self.send_json({"error": f"рецепт: {e}"}, 400)
        if self.path == "/api/render":
            return self.send_json({"poses": {p: full_svg(built, p) for p in rig.POSE_ORDER}})
        if self.path == "/api/save":
            pngs = body.get("png", {})
            if set(pngs) != set(rig.POSE_ORDER):
                return self.send_json({"error": "нужны все позы"}, 400)
            poses = {}
            for pose, url in pngs.items():
                im = Image.open(BytesIO(base64.b64decode(url.split(",", 1)[1]))).convert("RGBA")
                poses[pose] = im.resize((build.W, build.H), Image.LANCZOS)
            final = build.normalize(poses)
            paths = build.save_sprites(rec["id"], final)
            catalog.RECIPES_DIR.mkdir(exist_ok=True)
            (catalog.RECIPES_DIR / f"{rec['id']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2))
            return self.send_json({"saved": [str(p.relative_to(ROOT)) for p in paths]})
        self.send_json({"error": "нет такого метода"}, 404)


if __name__ == "__main__":
    print(f"редактор: http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
