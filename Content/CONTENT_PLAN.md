# Контент-план History Teller

## Как устроен контент (data-driven)

Всё — данные, движок не знает про конкретных персонажей. Иерархия:

```
Эпоха/Глава (chapter)  →  Уровни (levels), отсортированы по `order` = ХРОНОЛОГИЯ
```

- Карта эпохи показывает уровни по возрастанию `order`, открывает по цепочке (пройден предыдущий → открыт следующий).
- Значит порядок `order` = хронологический ход истории. Игрок проживает эпоху последовательно.

### Схема уровня (JSON в `Content/<эпоха>/levels/<id>.json`)

| поле | смысл |
|---|---|
| `id` | уникальный ключ (`caesar_assassination`) |
| `order` | **хронологическая позиция** (10, 20, 30… — шаг 10, чтобы вставлять между) |
| `title` | заголовок главы («И ты, Брут?») |
| `epoch` | эпоха (`rome`) |
| `panels` | сколько панелей-кадров (2–4) |
| `scenes` | доступные сцены (id из `scenes.json`) |
| `characters` | доступный каст (id из `characters.json`) |
| `initialState` | стартовые флаги/отношения («Клеопатра — locked_out») |
| `initialText` | вводная строка-контекст |
| `goal` | дерево-предикат победы (all/any/not/flag/relation) |
| `goalText` | цель одним предложением (виден в заголовке) |
| `goalHint` | подсказка/запрет (для инфо-кнопки) |
| `solution` | эталонная расстановка (для диагностики ошибок и подсказок) |
| `factCard` | историческая справка + `accuracy` (fact/simplification/legend) + `source` |

Новые правила-механики — только когда нужен новый *тип* взаимодействия (в `rules.json`, параметризованы тегами). Новый уровень = новый JSON + строка в загрузчике (`RomeContent.levelIds`).

---

## Глава 1 — Древний Рим: «Падение Республики» (49–30 до н.э.)

14 уровней в **3 акта** (поле `act` в JSON группирует карту). Все реализованы, арт есть,
`solution`-поля провалидированы движком, каждый уровень решается 1–4 различимыми путями.

### Акт I · Восхождение (49–48 до н.э.)
| order | id | Событие | Механика |
|---|---|---|---|
| 10 | `rubicon` | Жребий брошен — переход Рубикона (49) | befriend → cross_rubicon |
| 20 | `pharsalus` | Фарсал — разгром Помпея (48) | cross_rubicon → civil_war |
| 30 | `pompey_death` | Гибель Помпея в Египте (48) | civil_war → slay_fugitive |

### Акт II · Царица и диктатор (48–44 до н.э.)
| 40 | `cleopatra_charm` | Клеопатра тайно к Цезарю (48) | smuggle → charm |
| 50 | `cleopatra_throne` | Разгром Птолемея, царица (47) | conquer → back_ruler → enthrone |
| 60 | `cleopatra_heir` (id `cleopatra_rome`) | Клеопатра в Риме, сенат ропщет (46) | voyage → honor → senate_envy |
| 70 | `caesar_crown` | Корона на Луперкалиях (44) | offer_crown |
| 80 | `caesar_assassination` | Мартовские иды (44) | conspire(+Кассий) → betrayal_kill |

### Акт III · Наследники (43–30 до н.э.)
| 90 | `triumvirate` | Второй триумвират (43) | befriend → conspire |
| 100 | `philippi` | Месть за Цезаря, Филиппы (42) | battle_justice |
| 110 | `tarsus` | Царица и полководец, Тарс (41) | smuggle → charm + go_east |
| 120 | `discord` | Раскол Антоний/Октавиан (33) | go_east → eastern_split |
| 130 | `actium` | Акциум, разгром флота (31) | go_east → naval_rout |
| 140 | `alexandria` | Аспид Клеопатры (30) | fall_on_sword + widow → aspic |

`rivals` — вне линии (файл сохранён, легенда/что-если). Новые персонажи: `pompey`, `octavian`.
Новые сцены: `rubicon`(frontier), `harbor`(shore), `naval`(naval), `tomb`(tomb).
Новые правила (тайтово по тегам, старые уровни не задеты): cross_rubicon, civil_war, slay_fugitive,
go_east, eastern_split, naval_rout, fall_on_sword, widow, aspic. Флаги: at_war, victor, fugitive,
eastern, treacherous, widowed. **Движок матчит только ЖИВЫХ** — смерть-после-смерти делать через флаг
(widowed), не через мёртвого актора.

---

## Глава 2 — Тюдоры: «Дом Тюдоров» (1485–1603) ✅

Династическая сага в **3 акта, 13 уровней**. Все реализованы, арт есть, `solution` провалидированы,
Рим регрессией не задет. Своя тюдоровская музыка (tudor_court/romance/lament).

### Акт I · Восхождение (1485–1486)
| 10 | `bosworth` | Генрих VII свергает Ричарда III | usurp (битва) |
| 20 | `union` | Союз Алой и Белой розы + наследник | marry → bear_heir |

### Акт II · Шесть жён (1533–1547) — «разведена/казнена/умерла/разведена/казнена/выжила»
| 30 | `aragon_divorce` | Екатерина — разведена | break_from_rome(defiant) → annul (Ватикан+Папа=приманка) |
| 40 | `anne_boleyn` | Анна Болейн — казнена | marry → accuse → behead |
| 50 | `jane_seymour` | Джейн Сеймур — умерла | marry → bear_heir → childbed_fever |
| 60 | `anne_cleves` | Анна Клевская — разведена (жива) | arrange(gate) → marry → annul |
| 70 | `howard` | Кэтрин Говард — казнена | marry → accuse → behead |
| 80 | `parr` | Кэтрин Парр — выжила | marry → accuse → reconcile (Тауэр=приманка!) |

### Акт III · Наследники (1547–1603)
| 90 | `jane_grey` | Джейн Грей — 9 дней и плаха | crown → depose → execute_rival |
| 100 | `bloody_mary` | Кровавая Мэри | crown → restore_rome → marry(Филипп) |
| 110 | `elizabeth` | Королева-девственница | crown → settle_church (брак=ловушка) |
| 120 | `mary_stuart` | Мария Стюарт — казнена | condemn_rival → execute_rival |
| 130 | `armada` | Непобедимая армада разбита | repel_armada (капелла=ловушка) |

Каст (17): henry+6 жён+cromwell+pope (Акт II); henry7, richard3, eliz_york (Акт I); jane_grey, mary1,
philip, elizabeth, mary_stuart (Акт III). Сцены (7): chapel, court, tribunal, tower, chamber, vatican,
abbey. Правила (17, на НОВЫХ тегах — с Римом ноль пересечений). `break_from_rome` гейчен флагом
`defiant` (только Генрих VIII, иначе коронации Акта I/III делали монархов «главой церкви»). Правило
`repel_armada`: у Филиппа `foreign` — ТЕГ, не флаг. Женщина-монарх казнит через `execute_rival`
(флаг `reigns`), а Генрих VIII — через `behead` (тег `king`).

**Многоглавье**: общий ContentDb (правила глобальны), уровни фильтруются по полю `epoch`. Загрузчик
грузит все id; `Pack.levels(epoch:)`; RootView.selectedEpoch (+хук HT_EPOCH); EpochMapView(title:);
доступность главы — в RootView.chapters(). Тюдоровские правила заскоуплены тегами сцен
(wedding/court/tribunal/tower/chamber/vatican) и персонажей (king/lady/advisor/pope).

## Глава 3 — Древний Египет (🔲 будущий пак)
Фараоны/боги: объединение Египта → пирамиды → Эхнатон и Атон → Тутанхамон → (мостик к Клеопатре).

## Глава 4 — Наполеон (🔲 будущий пак)
Тулон → Италия → Египет → Коронация → Аустерлиц → Москва → Ватерлоо → Сто дней.

---

## Порядок наполнения (workflow)

1. Пишем JSON уровня по схеме (сцены/каст/цель/solution/factCard).
2. **Солвер** проверяет решаемость (`Solver.solve` — brute-force, у нас в тестах).
3. Добавляем id в загрузчик, `order` ставит его в нужное место хронологии.
4. Не хватает арта — генерим сцену/персонажа через Nano Banana (см. память `art-generation-pipeline`).
5. Историческая справка — 1–3 абзаца + источник + плашка факт/легенда.
