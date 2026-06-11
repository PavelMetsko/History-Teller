# History Teller — прототип движка симуляции

Narrative-puzzle в духе Storyteller на реальных исторических сюжетах. См. [GDD.md](GDD.md).

## Структура

```
Simulation/Core/    — движок: чистый C# (netstandard, без UnityEngine), Unity-ready
Simulation/Tests/   — NUnit-тесты (Unity Test Runner, Editor)
UnityProject/       — ГОТОВЫЙ Unity-проект: открыть в Hub и нажать Play (см. SETUP_UNITY.md)
Content/rome/       — контент эпохи «Рим»: персонажи, сцены, правила, уровни (JSON)
prototype/          — HTML-прототип (index.html генерируется из template.html)
tools/simulate.py   — эталонный симулятор + солвер (без Unity), валидация контента
tools/build_proto.py— сборка HTML-прототипа из JSON
```

**Запуск в Unity и на iPhone — см. [SETUP_UNITY.md](SETUP_UNITY.md).**

## Играбельный прототип (без Unity)

`prototype/index.html` — самодостаточный файл (5 уровней): движок + контент + touch-интерфейс.
Запуск на iPhone: AirDrop файла на телефон → открыть в Safari (или через приложение «Файлы»).
На Mac — просто открыть в браузере. Тесты движка: `node prototype/test.js`.

Это инструмент проверки fun-фактора и контента до сборки Unity-версии. Арт — эмодзи-заглушки.

### Цикл добавления контента

1. Правите/добавляете JSON в `Content/rome/` (уровень обязан содержать `solution` — эталонное решение).
2. `python3 tools/simulate.py Content/rome --all` — проверка решаемости и числа решений.
3. `python3 tools/build_proto.py` — пересборка `prototype/index.html` из `prototype/template.html` + JSON.
4. AirDrop на телефон, играете.

`index.html` руками не редактировать — он генерируется. UI правится в `template.html`.

Возможности контента: стартовые условия уровня (`initialState` + `initialText`, см. philippi),
порядок уровней (`order`), плашки достоверности (`fact` / `simplification` / `legend`).

## Подключение к Unity

1. Создать Unity-проект (2022 LTS+), скопировать `Simulation/` в `Assets/`.
2. Установить пакет `com.unity.nuget.newtonsoft-json` (Package Manager → Add by name).
3. Window → General → Test Framework → запустить `HistoryTeller.Simulation.Tests` (EditMode).

Загрузка контента: `ContentDb.FromJson(...)` принимает JSON-строки — скармливайте TextAsset/Addressables.

## Контент-пайплайн

Новый уровень = JSON в `Content/<epoch>/levels/`. Движок не знает персонажей — правила
параметризованы тегами (`charming`, `secret`, `senate`…) и переиспользуются между эпохами.

Проверка решаемости без Unity:

```bash
python3 tools/simulate.py Content/rome --all
```

Печатает число решений и трассировку правил. 0 решений = уровень сломан;
слишком много = пазл слишком лёгкий (эталон: «И ты, Брут?» — 2 решения на 9261 расстановку).

**Важно:** семантика `tools/simulate.py` и `Simulation/Core/Engine.cs` должна совпадать 1:1.
Меняете движок — меняйте эталон и наоборот. Ожидаемые числа в `SimulationTests.cs` берутся из эталона.

## Семантика движка (кратко)

- Панель = сцена + персонажи. Симуляция слева направо, состояние накапливается.
- Правило: триггер (теги сцены + условия на акторов: теги, флаги, отношения) → эффекты
  (set/removeFlag, add/removeRelation). Применяются по убыванию `priority`.
- Биндинги — инъективные назначения живых персонажей на переменные; после эффекта
  в той же панели биндинги перепроверяются (мёртвые не действуют).
- Цель уровня — дерево предикатов `all/any/not/flag/relation` над финальным состоянием.
