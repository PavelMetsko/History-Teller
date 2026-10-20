#!/usr/bin/env python3
"""Сборка playable-рекламы (AppLovin Ads и др.): один самодостаточный HTML ≤ 5 МБ.

Уровень разбирается тем же движком, что в игре (android/engine-js → JS), поэтому любая
расстановка игрока ведёт себя как на настоящей доске. Внутрь вкладываются: движок, контент
уровня (герои/сцены — только нужные, правила — только для сцен уровня), арт (webp), звуки,
тексты на 9 языках и иконка приложения. Внешних запросов нет — так требуют рекламные сети.

Usage:
    sh tools/build_editor.sh          # или: (cd android && ./gradlew :engine-js:build)
    python3 tools/playable/build_playable.py [level_id]
Результат: dist/playable/history_teller_<level>.html
"""
import base64
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVEL = sys.argv[1] if len(sys.argv) > 1 else "cleopatra_throne"
EPOCH = "rome"
LANGS = ["en", "ru", "es", "de", "fr", "it", "pt", "pl", "nl"]
POSES = ["", "_triumph", "_defeated", "_dead", "_plot"]
SOUNDS = ["place", "select", "accent", "win", "error"]
STORE = {
    "ios": "https://apps.apple.com/app/id6787477739",
    "android": "https://play.google.com/store/apps/details?id=com.decima.historyteller",
}

# Интерфейс playable — своих ключей в каталоге игры у него нет.
UI = {
    "en": {"drag_scene": "Drag a scene into a frame", "drag_char": "Now add heroes to the frame",
           "drop": "Drop a scene here", "play": "Play free", "win": "You made history!",
           "again": "Not quite — try another order"},
    "ru": {"drag_scene": "Перетащи сцену в кадр", "drag_char": "Теперь добавь героев в кадр",
           "drop": "Перетащи сцену сюда", "play": "Играть бесплатно", "win": "Ты вершишь историю!",
           "again": "Почти — попробуй другой порядок"},
    "es": {"drag_scene": "Arrastra una escena a un cuadro", "drag_char": "Ahora añade héroes al cuadro",
           "drop": "Suelta una escena aquí", "play": "Juega gratis", "win": "¡Has hecho historia!",
           "again": "Casi: prueba otro orden"},
    "de": {"drag_scene": "Zieh eine Szene in ein Bild", "drag_char": "Jetzt Helden ins Bild ziehen",
           "drop": "Szene hierher ziehen", "play": "Gratis spielen", "win": "Du schreibst Geschichte!",
           "again": "Fast – probier eine andere Reihenfolge"},
    "fr": {"drag_scene": "Glisse une scène dans un cadre", "drag_char": "Ajoute maintenant des héros",
           "drop": "Dépose une scène ici", "play": "Jouer gratuitement", "win": "Tu as fait l'Histoire !",
           "again": "Presque — essaie un autre ordre"},
    "it": {"drag_scene": "Trascina una scena in un riquadro", "drag_char": "Ora aggiungi gli eroi",
           "drop": "Trascina qui una scena", "play": "Gioca gratis", "win": "Hai fatto la storia!",
           "again": "Quasi: prova un altro ordine"},
    "pt": {"drag_scene": "Arraste uma cena para um quadro", "drag_char": "Agora adicione heróis ao quadro",
           "drop": "Solte uma cena aqui", "play": "Jogue grátis", "win": "Você fez história!",
           "again": "Quase — tente outra ordem"},
    "pl": {"drag_scene": "Przeciągnij scenę do kadru", "drag_char": "Teraz dodaj bohaterów do kadru",
           "drop": "Upuść tu scenę", "play": "Graj za darmo", "win": "Tworzysz historię!",
           "again": "Prawie — spróbuj innej kolejności"},
    "nl": {"drag_scene": "Sleep een scène naar een kader", "drag_char": "Voeg nu helden toe aan het kader",
           "drop": "Sleep hier een scène", "play": "Gratis spelen", "win": "Jij schrijft geschiedenis!",
           "again": "Bijna — probeer een andere volgorde"},
}


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def main():
    content = ROOT / "Content" / EPOCH
    level_raw = (content / "levels" / f"{LEVEL}.json").read_text(encoding="utf-8")
    level = json.loads(level_raw)

    scenes_all = json.loads((content / "scenes.json").read_text(encoding="utf-8"))
    chars_all = json.loads((content / "characters.json").read_text(encoding="utf-8"))
    rules_all = json.loads((content / "rules.json").read_text(encoding="utf-8"))
    scenes = [s for s in scenes_all if s["id"] in level["scenes"]]
    chars = [c for c in chars_all if c["id"] in level["characters"]]
    # Правило может сработать, только если все его теги сцены есть у одной из сцен уровня.
    rules = [r for r in rules_all
             if any(set(r["trigger"].get("sceneTags", [])) <= set(s["tags"]) for s in scenes)]

    engine = ROOT / "android/engine-js/build/dist/js/productionExecutable/engine-js.js"
    if not engine.exists():
        sys.exit("нет engine-js.js — сначала: (cd android && ./gradlew :engine-js:build)")

    art_dir = ROOT / "Content" / "art"
    art = {}
    for s in level["scenes"]:
        art[f"scene_{s}"] = "data:image/webp;base64," + b64(art_dir / f"scene_{s}.webp")
    for c in level["characters"]:
        for pose in POSES:
            f = art_dir / f"char_{c}{pose}.webp"
            if f.exists():
                art[f"char_{c}{pose}"] = "data:image/webp;base64," + b64(f)

    # Иконка 1024 → 192 через sips (есть на любом Mac), чтобы не тащить мегабайт.
    icon_src = ROOT / "ios/App/Resources/Assets.xcassets/AppIcon.appiconset/icon_1024.png"
    icon_tmp = ROOT / "dist/playable/icon_192.png"
    icon_tmp.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["sips", "-Z", "192", str(icon_src), "--out", str(icon_tmp)],
                   check=True, capture_output=True)
    art["icon"] = "data:image/png;base64," + b64(icon_tmp)

    sounds = {n: "data:audio/mp4;base64," + b64(ROOT / "Content/audio" / f"{n}.m4a") for n in SOUNDS}

    texts = {}
    for lang in LANGS:
        cat = json.loads((ROOT / "Content/i18n" / f"{lang}.json").read_text(encoding="utf-8"))
        en = json.loads((ROOT / "Content/i18n/en.json").read_text(encoding="utf-8"))
        t = lambda k: cat.get(k) or en.get(k) or k
        texts[lang] = {
            "title": t(f"level.{LEVEL}.title"), "goal": t(f"level.{LEVEL}.goal"),
            "hint": t(f"level.{LEVEL}.hint"), "fact": t(f"level.{LEVEL}.fact"),
            "chars": {c: t(f"char.{c}") for c in level["characters"]},
            "scenes": {s: t(f"scene.{s}") for s in level["scenes"]},
            "actions": {s: t(f"scene.{s}.action") for s in level["scenes"]},
            **UI[lang],
        }

    data = {
        "level": level_raw, "characters": json.dumps(chars, ensure_ascii=False),
        "scenes": json.dumps(scenes, ensure_ascii=False), "rules": json.dumps(rules, ensure_ascii=False),
        "art": art, "sounds": sounds, "texts": texts, "store": STORE,
    }

    template = (Path(__file__).parent / "template.html").read_text(encoding="utf-8")
    html = (template
            .replace("/*__ENGINE__*/", engine.read_text(encoding="utf-8"))
            .replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False)))
    out = ROOT / "dist/playable" / f"history_teller_{LEVEL}.html"
    out.write_text(html, encoding="utf-8")
    icon_tmp.unlink()
    mb = out.stat().st_size / 1024 / 1024
    print(f"{out.relative_to(ROOT)} — {mb:.2f} МБ (лимит AppLovin 5 МБ), правил {len(rules)}/{len(rules_all)}")
    if mb > 5:
        sys.exit("больше 5 МБ — AppLovin не примет")


if __name__ == "__main__":
    main()
