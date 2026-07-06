#!/usr/bin/env python3
"""
Синхронизация контента: Content/ (единый источник правды) -> бандлы iOS и Android.
Запускать ПОСЛЕ любых правок в Content/ и ПЕРЕД сборкой билда.

Игра НЕ читает Content/ напрямую — контент бандлится отдельными копиями:
  iOS     : ios/Modules/GameContent/Resources/           (плоско: <id>.json, characters/scenes/rules.json, i18n_<lang>.json)
  Android : android/app/src/main/assets/content/levels/  (+ content/{characters,scenes,rules}.json, i18n/<lang>.json)

Usage:  python3 tools/sync_content.py
"""
import glob, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IOS  = f"{ROOT}/ios/Modules/GameContent/Resources"
ANDC = f"{ROOT}/android/app/src/main/assets/content"
ANDL = f"{ANDC}/levels"
ANDI = f"{ROOT}/android/app/src/main/assets/i18n"

def main():
    if not os.path.isdir(IOS) or not os.path.isdir(ANDL):
        sys.exit("bundle dirs not found — run from repo root")

    n = 0
    # 1) уровни (плоско в оба бандла)
    src_levels = {os.path.basename(p): p for p in glob.glob(f"{ROOT}/Content/*/levels/*.json")}
    for b, src in src_levels.items():
        shutil.copy(src, f"{IOS}/{b}")
        shutil.copy(src, f"{ANDL}/{b}")
        n += 1
    # удалить в бандлах уровни, которых больше нет в источнике (переименованный/удалённый id)
    for bundle in (IOS, ANDL):
        for p in glob.glob(f"{bundle}/*.json"):
            b = os.path.basename(p)
            if b in ("characters.json", "scenes.json", "rules.json") or b.startswith("i18n"):
                continue
            if b not in src_levels:
                os.remove(p); print(f"  removed stale level: {bundle}/{b}")

    # 2) глобальная БД
    for name in ("characters.json", "scenes.json", "rules.json"):
        src = f"{ROOT}/Content/rome/{name}"
        shutil.copy(src, f"{IOS}/{name}")
        shutil.copy(src, f"{ANDC}/{name}")
        n += 1

    # 3) локализация (iOS: i18n_<lang>.json ; Android: i18n/<lang>.json)
    for src in glob.glob(f"{ROOT}/Content/i18n/*.json"):
        lang = os.path.basename(src)[:-5]
        shutil.copy(src, f"{IOS}/i18n_{lang}.json")
        shutil.copy(src, f"{ANDI}/{lang}.json")
        n += 1

    print(f"synced {n} files (levels + db + i18n) -> iOS & Android bundles")
    print("next: validate `cd android && ./gradlew -q :engine:run` (0 fails, all ✓sol), then build.")

if __name__ == "__main__":
    main()
