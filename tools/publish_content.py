#!/usr/bin/env python3
"""Сборка облачного бандла контента из Content/ — третья цель того же пайплайна,
что и tools/sync_content.py (тот разливает Content/ по бандлам платформ).

Раскладка на выходе:
    manifest.json          индекс: главы, зависимости, хеши. Короткий TTL.
    f/<sha256>             сами файлы, адресуемые по содержимому. Иммутабельны → кешируются вечно.

Контент-адресация даёт бесплатный дедуп: одна и та же картинка фона, использованная в семи
сценах, лежит в облаке одним объектом.

Клиент качает manifest → core (игра становится работоспособной) → файлы главы при её открытии.
Проверяет sha256, кладёт во временную папку и переключается атомарно.

Usage:
    python3 tools/publish_content.py [--out dist/content] [--version N] [--serve [PORT]]
"""
from __future__ import annotations   # системный python3 здесь 3.9 — без этого `str | None` не парсится

import argparse
import hashlib
import http.server
import json
import shutil
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "Content"

# Позы персонажей: докладываются к базовому спрайту, если файл есть (движок сам решает, рисовать ли).
POSES = ["dead", "defeated", "plot", "triumph"]
# SFX — имена из Audio.SFX (iOS) / Audio.SFX (Android). Нужны всегда, не привязаны к главе.
SFX = ["place", "select", "accent", "win", "error"]
# Персонажи на главном экране (MenuView.swift / MenuScreen в Root.kt).
MENU_CHARACTERS = ["caesar", "cleopatra"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# id уровня → файл. Имя файла не всегда совпадает с id (cleopatra_rome лежит в cleopatra_heir.json),
# поэтому в облаке ключом служит id, а путь берём отсюда.
LEVEL_PATHS: dict = {}


def load_levels() -> list[dict]:
    out = []
    for p in sorted(CONTENT.glob("*/levels/*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        LEVEL_PATHS[d["id"]] = p
        out.append(d)
    return out


def art(name: str) -> str | None:
    """Логический путь к арту, если файл существует (поз может не быть — это нормально)."""
    return f"art/{name}.webp" if (CONTENT / "art" / f"{name}.webp").exists() else None


def chapter_files(level: dict) -> set[str]:
    """Всё, без чего уровень не отрисуется."""
    files = {f"content/levels/{level['id']}.json"}
    for sid in list(level.get("scenes", [])) + [level.get("cover")]:
        if sid and (a := art(f"scene_{sid}")):
            files.add(a)
    for cid in level.get("characters", []):
        for name in [f"char_{cid}"] + [f"char_{cid}_{p}" for p in POSES]:
            if a := art(name):
                files.add(a)
    if music := level.get("music"):
        if (CONTENT / "audio" / f"{music}.m4a").exists():
            files.add(f"audio/{music}.m4a")
    return files


def load_demo() -> str | None:
    """Показательный уровень — `Content/demo.json`. На нём построены онбординг и экран
    загрузки главы, поэтому он и его арт лежат в core: оба экрана показываются ДО того,
    как скачана хоть одна глава."""
    f = CONTENT / "demo.json"
    return json.loads(f.read_text(encoding="utf-8")).get("level") if f.exists() else None


def core_files(chapters: list, levels: list) -> set[str]:
    """Нужно до открытия любой главы: БД, локализация, пропсы, звуки интерфейса, тема меню,
    а также арт, который видно ещё до выбора главы — иначе первый запуск встречает пустым
    меню и карточками глав без обложек."""
    files = {"content/characters.json", "content/scenes.json", "content/rules.json", "content/chapters.json"}
    files |= {f"content/i18n/{p.stem}.json" for p in (CONTENT / "i18n").glob("*.json")}
    files |= {f"art/{p.name}" for p in (CONTENT / "art").glob("prop_*.webp")}
    files |= {f"audio/{n}.m4a" for n in SFX if (CONTENT / "audio" / f"{n}.m4a").exists()}
    if (CONTENT / "audio" / "theme.m4a").exists():
        files.add("audio/theme.m4a")
    # Метаданные склейки лупа (priming AAC) — нужны Android-плееру для бесшовного лупа.
    if (CONTENT / "audio" / "loops.json").exists():
        files.add("audio/loops.json")
    # Обложки всех глав — экран выбора эпохи.
    for c in chapters:
        if a := art(f"scene_{c['cover']}"):
            files.add(a)
    # Спрайты на главном экране (заданы в MenuView / MenuScreen).
    for cid in MENU_CHARACTERS:
        if a := art(f"char_{cid}"):
            files.add(a)
    # Демо-уровень целиком: его разбирает онбординг и собирает экран загрузки главы.
    if demo := load_demo():
        lv = next((l for l in levels if l["id"] == demo), None)
        if lv is None:
            sys.exit(f"demo.json ссылается на уровень {demo}, которого нет")
        files |= chapter_files(lv)
    return files


def source_of(logical: str) -> Path:
    """Логический путь → файл в Content/. Глобальная БД исторически лежит в Content/rome/."""
    if logical.startswith("content/levels/"):
        return LEVEL_PATHS[logical.rsplit("/", 1)[1][:-5]]
    if logical.startswith("content/i18n/"):
        return CONTENT / "i18n" / logical.rsplit("/", 1)[1]
    if logical == "content/chapters.json":
        return CONTENT / "chapters.json"
    if logical.startswith("content/"):
        return CONTENT / "rome" / logical.rsplit("/", 1)[1]
    return CONTENT / logical


def load_disabled() -> list:
    """Выключенные уровни — `Content/disabled.json`. Это рубильник: правишь файл, публикуешь
    манифест, и уровень пропадает у всех, кто уже поставил игру. Пересборка не нужна."""
    f = CONTENT / "disabled.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


def build(out: Path, version: int) -> dict:
    chapters_meta = json.loads((CONTENT / "chapters.json").read_text(encoding="utf-8"))
    levels = load_levels()
    disabled = load_disabled()

    per_chapter: dict[str, set[str]] = {}
    level_ids: dict[str, list[str]] = {}
    for lv in levels:
        epoch = lv["epoch"]
        per_chapter.setdefault(epoch, set()).update(chapter_files(lv))
        level_ids.setdefault(epoch, []).append(lv["id"])

    core = core_files(chapters_meta, levels)
    known = {c["id"] for c in chapters_meta}
    if orphans := set(per_chapter) - known:
        sys.exit(f"уровни ссылаются на главы, которых нет в chapters.json: {sorted(orphans)}")

    # Файлы, попавшие сразу в несколько глав (общий арт), остаются в каждой — клиент качает
    # по хешу, так что физически объект всё равно один.
    all_logical = core | {f for s in per_chapter.values() for f in s}

    files = {}
    fdir = out / "f"
    fdir.mkdir(parents=True, exist_ok=True)
    for logical in sorted(all_logical):
        src = source_of(logical)
        if not src.exists():
            sys.exit(f"нет исходника для {logical} (искал {src})")
        h = sha256(src)
        files[logical] = {"h": h, "s": src.stat().st_size}
        dst = fdir / h
        if not dst.exists():
            shutil.copy(src, dst)

    manifest = {
        "version": version,
        "minAppVersion": "1.0",
        "chapters": [
            {**c,
             "levels": sorted(level_ids.get(c["id"], []),
                              key=lambda i: next(l["order"] for l in levels if l["id"] == i))}
            for c in sorted(chapters_meta, key=lambda c: c["number"])
            if c["id"] in per_chapter
        ],
        "disabled": disabled,
        "demo": load_demo(),
        "core": sorted(core),
        "chapterFiles": {k: sorted(v) for k, v in sorted(per_chapter.items())},
        "files": files,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8")
    return manifest


def report(manifest: dict, out: Path):
    files = manifest["files"]
    total = sum(f["s"] for f in files.values())
    objects = len({f["h"] for f in files.values()})
    on_disk = sum(p.stat().st_size for p in (out / "f").iterdir())
    core = sum(files[f]["s"] for f in manifest["core"])
    print(f"манифест v{manifest['version']}: {len(manifest['chapters'])} глав, "
          f"{len(files)} логических файлов → {objects} объектов")
    print(f"дедуп: {total/1e6:.1f} МБ логически → {on_disk/1e6:.1f} МБ в облаке "
          f"(минус {(total-on_disk)/1e6:.1f} МБ)")
    print(f"core (первый запуск): {core/1e6:.2f} МБ")
    if manifest["disabled"]:
        print(f"выключено: {', '.join(manifest['disabled'])}")
    for c in manifest["chapters"]:
        s = sum(files[f]["s"] for f in manifest["chapterFiles"][c["id"]])
        print(f"  {c['number']}. {c['id']:11s} {len(c['levels']):2d} уровней  {s/1e6:5.2f} МБ")


def serve(out: Path, port: int):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(out), **kw)

        def end_headers(self):
            # Манифест перечитываем часто, объекты иммутабельны — как в проде.
            self.send_header("Cache-Control",
                             "no-cache" if self.path.endswith("manifest.json") else "max-age=31536000, immutable")
            super().end_headers()

        def log_message(self, fmt, *a):
            # Лог нужен: когда устройство молча играет на старом кеше, единственный способ
            # понять, дошёл ли до стенда хоть один запрос, — увидеть его здесь.
            print(f"  {self.client_address[0]}  {fmt % a}", flush=True)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"стенд: http://localhost:{port}/manifest.json  (Ctrl-C для остановки)")
        httpd.serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist/content")
    ap.add_argument("--version", type=int, default=1)
    ap.add_argument("--serve", nargs="?", type=int, const=8787)
    ap.add_argument("--allow-holes", action="store_true")
    a = ap.parse_args()
    out = (ROOT / a.out) if not Path(a.out).is_absolute() else Path(a.out)
    # Страховка: каталог с дырами уезжать не должен — приложение подставляет русский вместо
    # недостающего ключа, и игрок видит смесь языков. Сначала tools/i18n/translate.py --missing.
    ru_keys = set(json.loads((CONTENT / "i18n" / "ru.json").read_text(encoding="utf-8")))
    holes = {}
    for f in sorted((CONTENT / "i18n").glob("*.json")):
        if f.stem == "ru":
            continue
        miss = ru_keys - set(json.loads(f.read_text(encoding="utf-8")))
        if miss:
            holes[f.stem] = sorted(miss)
    if holes and "--allow-holes" not in sys.argv:
        for lang, miss in holes.items():
            print(f"!! {lang}: нет {len(miss)} ключей, напр. {miss[:5]}")
        sys.exit("публикация остановлена: сначала python3 tools/i18n/translate.py --missing")
    report(build(out, a.version), out)
    if a.serve:
        serve(out, a.serve)
