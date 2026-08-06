#!/usr/bin/env python3
"""Вынос текстов уровней из их JSON в каталоги i18n.

Тексты жили в двух местах сразу: русский — прямо в файле уровня, переводы — в i18n. Редактору
пришлось бы держать их синхронными, а рано или поздно они бы разъехались. После этого прогона
файл уровня описывает только механику (каст, сцены, цель-предикат, эталон), а всё читаемое
человеком живёт в каталогах — там же, где переводы.

Что переезжает:
    title       → level.<id>.title
    goalText    → level.<id>.goal
    goalHint    → level.<id>.hint
    initialText → level.<id>.intro
    factCard.text   → level.<id>.fact
    factCard.source → level.<id>.source

`factCard.accuracy` остаётся в уровне: это метаданные (факт / упрощение / легенда), а не текст.

Скрипт идемпотентен и не теряет данные: если ключа в ru.json нет — он создаётся из значения
в уровне; если есть и отличается — прогон останавливается, чтобы правку разобрал человек.

Usage:
    python3 tools/extract_level_texts.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "Content"

FIELDS = [("title", "title"), ("goalText", "goal"), ("goalHint", "hint"), ("initialText", "intro")]
FACT = [("text", "fact"), ("source", "source")]


def run(dry: bool):
    ru_path = CONTENT / "i18n/ru.json"
    ru = json.loads(ru_path.read_text(encoding="utf-8"))

    moved = added = 0
    conflicts = []
    touched = []

    for path in sorted(CONTENT.glob("*/levels/*.json")):
        level = json.loads(path.read_text(encoding="utf-8"))
        lid = level["id"]
        changed = False

        def relocate(value, key):
            nonlocal added
            if value is None:
                return
            full = f"level.{lid}.{key}"
            if full not in ru:
                ru[full] = value
                added += 1
            elif ru[full] != value:
                conflicts.append((lid, key))

        for field, key in FIELDS:
            if field in level:
                relocate(level[field], key)
                del level[field]
                changed = True

        fc = level.get("factCard")
        if isinstance(fc, dict):
            for field, key in FACT:
                if field in fc:
                    relocate(fc[field], key)
                    del fc[field]
                    changed = True

        if changed:
            moved += 1
            touched.append(path)
            if not dry:
                path.write_text(json.dumps(level, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    if conflicts:
        print("ОСТАНОВЛЕНО: текст в уровне расходится с каталогом, разберись вручную:")
        for lid, key in conflicts[:20]:
            print(f"  {lid} · {key}")
        sys.exit(1)

    if not dry:
        ru_path.write_text(json.dumps(ru, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("dry-run (ничего не записано)" if dry else "готово")
    print(f"уровней затронуто: {moved}")
    print(f"ключей добавлено в ru.json: {added} (остальные уже были)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    run(ap.parse_args().dry_run)
