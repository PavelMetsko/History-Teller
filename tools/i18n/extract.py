#!/usr/bin/env python3
"""Сверить каталог `Content/i18n/ru.json` с контентом: дописать недостающие ключи, назвать дыры.

Каталог — источник правды для ВСЕХ текстов, включая русский. Скрипт его не пересобирает,
а только дополняет: пишет `char.<id>` и `scene.<id>[.action]` для персонажей и сцен, которых
в каталоге ещё нет, и печатает список уровней без текстов и ключей-сирот.

Раньше он собирал каталог с нуля, вычитывая `title`/`goalText`/`goalHint`/`initialText`
и `factCard` из файлов уровней. Тексты оттуда вынесены (уровень описывает только механику),
а UI-строки лежали здесь же вторым списком и успели разойтись с каталогом. Один прогон
в том виде стирал около четырёхсот ключей во всех девяти языках — поэтому пересборка убрана
насовсем: удалить ключ можно только руками.
"""
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def rp(*p): return os.path.join(ROOT, *p)

CATALOG = rp("Content/i18n/ru.json")
cat = json.load(open(CATALOG, encoding="utf-8"))
before = len(cat)
added = []

# --- имена персонажей и сцен всё ещё живут в контенте: оттуда и заводим ключи ---
def put(key, value):
    if value and key not in cat:
        cat[key] = value
        added.append(key)

for c in json.load(open(rp("Content/rome/characters.json"), encoding="utf-8")):
    put(f"char.{c['id']}", c.get("name"))
for s in json.load(open(rp("Content/rome/scenes.json"), encoding="utf-8")):
    put(f"scene.{s['id']}", s.get("name"))
    put(f"scene.{s['id']}.action", s.get("action"))

# --- уровни: текстов в их файлах нет, поэтому только проверяем, что каталог их описывает ---
REQUIRED = ("title", "goal")          # без названия и цели уровень не показать
OPTIONAL = ("hint", "intro", "fact", "source")
levels, gaps = [], []
for p in sorted(glob.glob(rp("Content/*/levels/*.json"))):
    lid = json.load(open(p, encoding="utf-8"))["id"]
    levels.append(lid)
    missing = [k for k in REQUIRED if f"level.{lid}.{k}" not in cat]
    if missing:
        gaps.append((lid, missing))

# --- сироты: ключи, чей уровень/персонаж/сцена из контента исчезли ---
known_chars = {c["id"] for c in json.load(open(rp("Content/rome/characters.json"), encoding="utf-8"))}
known_scenes = {s["id"] for s in json.load(open(rp("Content/rome/scenes.json"), encoding="utf-8"))}
orphans = []
for k in cat:
    parts = k.split(".")
    if parts[0] == "level" and len(parts) > 2 and parts[1] not in levels: orphans.append(k)
    elif parts[0] == "char" and parts[1] not in known_chars: orphans.append(k)
    elif parts[0] == "scene" and parts[1] not in known_scenes: orphans.append(k)

if added:
    json.dump(cat, open(CATALOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)

print(f"Content/i18n/ru.json: {before} ключей" + (f" → {len(cat)} (+{len(added)})" if added else ", изменений нет"))
for k in added:
    print(f"  + {k}")
if gaps:
    print(f"\nбез текстов ({len(gaps)}) — допиши в каталог или через редактор:")
    for lid, missing in gaps:
        print(f"  {lid}: нет {', '.join('level.%s.%s' % (lid, m) for m in missing)}")
if orphans:
    print(f"\nсироты ({len(orphans)}) — контента под этими ключами больше нет:")
    for k in sorted(orphans):
        print(f"  {k}")
if added:
    print("\nновые ключи есть только по-русски — доперевести:  python3 tools/i18n/translate.py --missing")
