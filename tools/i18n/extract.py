#!/usr/bin/env python3
"""Собрать базовый каталог локализации Content/i18n/ru.json из русских исходников контента.

Ключи: level.<id>.{title,goal,hint,intro,fact,source}, char.<id>, scene.<id>[.action],
chapter.<id>.{title,subtitle}, map.<epoch>, act.<epoch>.<n>, ui.<key>.
UI-строки и заголовки глав/актов заданы вручную ниже — держи их в синхроне с кодом (RootView и т.п.).
"""
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def rp(*p): return os.path.join(ROOT, *p)

cat = {}
for base in ["Content/rome/levels", "Content/tudor/levels"]:
    for p in sorted(glob.glob(rp(base, "*.json"))):
        d = json.load(open(p, encoding="utf-8")); i = d["id"]
        def put(k, v):
            if v: cat[f"level.{i}.{k}"] = v
        put("title", d.get("title")); put("goal", d.get("goalText"))
        put("hint", d.get("goalHint")); put("intro", d.get("initialText"))
        fc = d.get("factCard", {}); put("fact", fc.get("text")); put("source", fc.get("source"))

for c in json.load(open(rp("Content/rome/characters.json"), encoding="utf-8")):
    cat[f"char.{c['id']}"] = c["name"]
for s in json.load(open(rp("Content/rome/scenes.json"), encoding="utf-8")):
    cat[f"scene.{s['id']}"] = s["name"]
    if s.get("action"): cat[f"scene.{s['id']}.action"] = s["action"]

# --- заданные вручную (глава/акт/карта/UI) ---
cat.update({
 "chapter.rome.title": "Древний Рим", "chapter.rome.subtitle": "Цезарь · Клеопатра · Брут",
 "chapter.tudor.title": "Тюдоры", "chapter.tudor.subtitle": "Генрих VIII и наследники",
 "chapter.egypt.title": "Древний Египет", "chapter.egypt.subtitle": "Фараоны и боги",
 "map.rome": "Древний Рим", "map.tudor": "Дом Тюдоров", "map.egypt": "Древний Египет",
 "act.rome.1": "Акт I · Восхождение", "act.rome.2": "Акт II · Царица и диктатор", "act.rome.3": "Акт III · Наследники",
 "act.tudor.1": "Акт I · Восхождение", "act.tudor.2": "Акт II · Шесть жён", "act.tudor.3": "Акт III · Наследники",
 "ui.tagline_caps": "ИСТОРИЧЕСКАЯ ГОЛОВОЛОМКА",
 "ui.menu_sub": "Собери историю из панелей —\nи узнай, как было на самом деле.",
 "ui.play": "Играть", "ui.reset": "Сбросить прогресс", "ui.reset_title": "Сбросить прогресс?",
 "ui.reset_msg": "Все пройденные уровни станут заново закрытыми.\nЭто действие нельзя отменить.",
 "ui.reset_confirm": "Сбросить", "ui.cancel": "Отмена", "ui.done": "Готово", "ui.ok": "Понятно",
 "ui.choose_epoch": "Выбери эпоху", "ui.chapter_n": "Глава %d", "ui.soon": "Скоро",
 "ui.progress": "Пройдено %d из %d",
 "ui.settings": "Настройки", "ui.music": "Музыка", "ui.sound": "Звуки", "ui.haptics": "Вибрация", "ui.language": "Язык",
 "ui.tap": "тапни", "ui.scene": "сцена",
 "ui.wrong_chars": "Место то — да не те лица",
 "ui.wrong_scene": "Верные герои — да не то место",
 "ui.wrong_inert": "Совсем не то — ни место, ни лица",
 "ui.load_fail": "Не удалось загрузить контент",
 "ui.unlock_title": "Открой все главы",
 "ui.unlock_body": "Первая глава — бесплатно. Разовая покупка открывает все главы, включая будущие.",
 "ui.unlock_cta": "Открыть все главы",
 "ui.unlock_cta_price": "Открыть — %@",
 "ui.restore": "Восстановить покупку",
 "ui.unlocked_thanks": "Спасибо! Все главы открыты.",
 "ui.locked_hint": "Требуется покупка",
 "ui.solved": "Разгадано!",
 "ui.next": "Дальше",
 "ui.acc_fact": "Факт",
 "ui.acc_simplification": "Упрощение",
 "ui.acc_legend": "Легенда",
})

os.makedirs(rp("Content/i18n"), exist_ok=True)
json.dump(cat, open(rp("Content/i18n/ru.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, sort_keys=True)
print(f"Content/i18n/ru.json: {len(cat)} ключей")
