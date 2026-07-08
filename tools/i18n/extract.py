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
for base in ["Content/rome/levels", "Content/tudor/levels", "Content/revolution/levels", "Content/empire/levels", "Content/borgia/levels", "Content/byzantium/levels"]:
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
 "chapter.revolution.title": "Французская революция", "chapter.revolution.subtitle": "Робеспьер · Дантон · Наполеон",
 "chapter.empire.title": "Российская империя", "chapter.empire.subtitle": "Грозный · Пётр · Екатерина",
 "chapter.borgia.title": "Дом Борджиа", "chapter.borgia.subtitle": "Родриго · Чезаре · Лукреция",
 "chapter.byzantium.title": "Византия", "chapter.byzantium.subtitle": "Юстиниан · Феодора · Велизарий",
 "map.rome": "Древний Рим", "map.tudor": "Дом Тюдоров", "map.egypt": "Древний Египет",
 "map.revolution": "Французская революция", "map.empire": "Российская империя", "map.borgia": "Дом Борджиа",
 "map.byzantium": "Византия",
 "act.rome.1": "Акт I · Восхождение", "act.rome.2": "Акт II · Царица и диктатор", "act.rome.3": "Акт III · Наследники",
 "act.tudor.1": "Акт I · Восхождение", "act.tudor.2": "Акт II · Шесть жён", "act.tudor.3": "Акт III · Наследники",
 "act.revolution.1": "Акт I · Революция", "act.revolution.2": "Акт II · Террор", "act.revolution.3": "Акт III · Наполеон",
 "act.empire.1": "Акт I · Иван Грозный", "act.empire.2": "Акт II · Пётр Великий", "act.empire.3": "Акт III · Екатерина Великая",
 "act.borgia.1": "Акт I · Восхождение", "act.borgia.2": "Акт II · Яд и власть", "act.borgia.3": "Акт III · Государь",
 "act.byzantium.1": "Акт I · Восхождение", "act.byzantium.2": "Акт II · Ника", "act.byzantium.3": "Акт III · Слава и закат",
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
 "ui.wrong_order": "Всё то — да не в том порядке",
 "ui.hint": "Подсказка",
 "ui.replay": "Заново",
 "ui.how_to_play": "Как играть",
 "ui.downloading_chapter": "Загрузка главы…",
 "ui.ready": "Готово!",
 "ui.tip.1": "Перетаскивай сцены между панелями — порядок иногда решает всё.",
 "ui.tip.2": "Лишний герой — это приманка. Не каждого нужно ставить.",
 "ui.tip.3": "Порядок панелей — причина и следствие: сначала дружба, потом кинжал.",
 "ui.tip.4": "Один и тот же герой в разных сценах творит разное.",
 "ui.tip.5": "Жёлтая подсветка — те герои, да не в том порядке.",
 "ui.tip.6": "Каждый уровень — реальный эпизод истории. Разгадай — узнаешь, как было.",
 "ui.tip.7": "Одна деталь меняет всё: пир станет роковым, если подмешать яд.",
 "ui.tip.8": "Спроси себя: какими тремя способами тут можно ошибиться?",
 "ui.next": "Далее",
 "ui.start": "Начать",
 "ui.onb.1.title": "Собери историю",
 "ui.onb.1.body": "Каждый уровень — реальный эпизод. Расставь героев по сценам — и если всё сойдётся, история случится.",
 "ui.onb.2.title": "Панели — кадры комикса",
 "ui.onb.2.body": "Читай слева направо: сначала причина, потом следствие. Порядок панелей часто решает всё.",
 "ui.onb.3.title": "Двигай сцены",
 "ui.onb.3.body": "Не уверен в порядке? Перетаскивай сцены между панелями прямо на доске.",
 "ui.onb.4.title": "Не каждый герой нужен",
 "ui.onb.4.body": "Лишние персонажи — приманка. Иногда верный ход — оставить кого-то в стороне.",
 "ui.onb.5.title": "Читай подсветку",
 "ui.onb.5.body": "Жёлтая рамка — герои те, да порядок не тот. Красная — совсем мимо.",
 "ui.onb.6.title": "Награда — правда",
 "ui.onb.6.body": "Разгадав уровень, узнаешь, как было на самом деле, с историческим источником.",
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
