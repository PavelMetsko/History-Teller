#!/usr/bin/env python3
"""Локальный сервер редактора: отдаёт репозиторий и принимает правки контента.

Слушает только localhost — это инструмент для работы за столом, наружу его выставлять нельзя.
Вариант «где угодно» будет писать через GitHub API, здесь же правки ложатся прямо в рабочее
дерево, чтобы их было видно в `git diff` и можно было откатить.

    POST /api/save     {"files": {"<путь в Content/>": "<содержимое>"}}
    POST /api/publish  прогон валидатора → сборка манифеста → заливка в R2

Usage:
    python3 tools/editor_server.py [--port 8080]
    открыть http://localhost:8080/editor/
"""
from __future__ import annotations

import argparse
import http.server
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "Content"


def save(payload: dict) -> dict:
    files = payload.get("files") or {}
    if not files:
        return {"ok": False, "error": "нечего сохранять"}

    written = []
    for rel, text in files.items():
        # Путь приходит из браузера — пускаем строго внутрь Content/, иначе редактор
        # превращается в способ переписать что угодно на диске.
        dst = (CONTENT / rel).resolve()
        if not dst.is_relative_to(CONTENT.resolve()):
            return {"ok": False, "error": f"путь за пределами Content/: {rel}"}
        if dst.suffix != ".json":
            return {"ok": False, "error": f"ожидается .json: {rel}"}
        try:
            json.loads(text)          # не даём записать сломанный JSON
        except json.JSONDecodeError as e:
            return {"ok": False, "error": f"{rel}: невалидный JSON — {e}"}
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        written.append(rel)
    return {"ok": True, "written": written}


def run(cmd: list, cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)


def publish(payload: dict) -> dict:
    """Валидатор → манифест → R2. Порядок важен: публиковать сломанный контент нельзя."""
    steps = []

    code, out = run(["./gradlew", "-q", ":engine:run"], ROOT / "android")
    steps.append({"name": "валидатор", "ok": code == 0, "log": out[-4000:]})
    if code != 0:
        return {"ok": False, "steps": steps, "error": "валидатор нашёл проблемы — публикация отменена"}

    version = int(payload.get("version") or 0)
    args = ["python3", "tools/publish_content.py"] + (["--version", str(version)] if version else [])
    code, out = run(args, ROOT)
    steps.append({"name": "манифест", "ok": code == 0, "log": out[-4000:]})
    if code != 0:
        return {"ok": False, "steps": steps, "error": "не удалось собрать манифест"}

    code, out = run(["python3", "tools/upload_r2.py"], ROOT)
    steps.append({"name": "заливка", "ok": code == 0, "log": out[-4000:]})
    return {"ok": code == 0, "steps": steps}


def current_version() -> int:
    f = ROOT / "dist/content/manifest.json"
    if not f.exists():
        return 0
    return json.loads(f.read_text(encoding="utf-8")).get("version", 0)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def do_POST(self):
        routes = {"/api/save": save, "/api/publish": publish}
        fn = routes.get(self.path)
        if not fn:
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            result = fn(payload)
        except Exception as e:                       # noqa: BLE001 — ответ важнее стектрейса в консоли
            result = {"ok": False, "error": str(e)}
        body = json.dumps(result, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/version":
            body = json.dumps({"version": current_version()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        # Контент правится постоянно — браузеру кешировать его незачем.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    port = ap.parse_args().port
    if not (ROOT / "editor/engine.js").exists():
        sys.exit("нет editor/engine.js — сначала ./tools/build_editor.sh")
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as srv:
        print(f"редактор: http://localhost:{port}/editor/   (Ctrl-C чтобы остановить)")
        srv.serve_forever()
