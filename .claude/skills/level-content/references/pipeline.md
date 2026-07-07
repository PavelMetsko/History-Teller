# Пайплайн: валидация, локализация, синк, ассеты

Все команды — из корня репо.

## Валидация уровня (обязательно после каждой правки контента)

```bash
python3 tools/simulate.py Content/rome Content/<epoch>/levels/<id>.json   # один уровень
python3 tools/simulate.py Content/rome --all                              # вся игра (после правок общей БД)
```

Первый аргумент — всегда `Content/rome` (там общая БД). Выход:
- `reference solution: OK` + лог сработавших правил — прочитай лог: там видно,
  не сработало ли лишнее правило, которого ты не ждал.
- `solutions: N (canonical: M)` — M ≤ 8; при > 500 000 расстановок полный перебор
  пропускается — тогда посчитай канонику быстрым счётчиком:
  `python3 tools/count_fast2.py Content/rome Content/<epoch>/levels/<id>.json`
- Проверка ловушек: собери «соблазнительную» расстановку руками и убедись, что она
  не решает уровень (мини-скрипт на базе `simulate.simulate()` + `goal_met()`).

## Локализация (9 языков: ru исходный + en/es/de/fr/it/pt/pl/nl)

```bash
python3 tools/i18n/extract.py         # пересобирает Content/i18n/ru.json из контента
GEMINI_API_KEY=… python3 tools/i18n/translate.py   # дотягивает переводы недостающих ключей
```

Ключи выводятся из id автоматически (`level.<id>.title/goal/hint/intro/fact/source`,
`char.<id>`, `scene.<id>[.action]`). Ключи глав/актов/карты (`chapter.*`, `act.*`,
`map.*`) прописаны в `extract.py` руками — новую главу добавь туда.

## Синк бандлов (без него приложения правок не увидят)

```bash
python3 tools/sync_content.py
```

Копирует `Content/*/levels/*.json`, общую БД и i18n в
`ios/Modules/GameContent/Resources/` и `android/app/src/main/assets/…`.
Запускать после ЛЮБОЙ правки контента, перед сборкой/коммитом.

## Регистрация нового уровня (iOS — обязательно!)

Android находит уровни сам (сканирует `assets/content/levels/`), а **iOS грузит
только id из списка** `levelIds` в `ios/Modules/GameContent/Sources/RomeContent.swift`
— отсутствующие тихо пропускаются. Новый уровень добавь в список в правильное
место главы/акта, иначе на iOS он просто не появится. Там же видно паттерн
исключения уровня из линии (`"rivals"` закомментирован, файл сохранён).

## Снапшот-фикстуры (опционально, для визуального ревью уровня)

```bash
python3 tools/gen_arrangements.py <level_id>
```

Генерит все полные расстановки уровня в Swift-фикстуру; iOS-тесты рендерят PNG-галерею.

## Новая глава — что кроме уровней

1. **Персонажи и арт** — `tools/genart.py`: пайплайн Nano Banana (Gemini image API,
   референс стиля, вырез магенты). Эмоции — `tools/make_emotions.py`.
2. **Сцены** — арт тем же пайплайном; сцене нужны emoji, action, actionIcon.
3. **Музыка** — 4 трека на главу (`<epoch>_battle/tension/romance/ceremony`,
   допустимы свои настроения, как `tudor_court`): `tools/make_epoch_music.py`
   (процедурная генерация). SFX общие: `tools/make_sfx.py`.
4. **i18n** — chapter/map/act-ключи в `tools/i18n/extract.py`, затем translate.
5. **Регистрация эпохи** в iOS/Android (список глав, гейтинг IAP) — ищи по
   существующему epoch id (например `byzantium`) в `ios/` и `android/`.

## Структура главы (устоявшийся формат)

13 уровней, `order` 10…130 с шагом 10, 3 акта (примерно 4–5 уровней на акт),
арка «возвышение → триумф → падение» вокруг 2–3 центральных фигур. Первый
уровень главы — простой (2 панели, 1 ловушка), обучает локальным механикам;
сложность и число негативных условий растут к финалу акта.
