# Промпты для генерации музыки (Suno)

Игра просит 25 треков. Генерить все сразу не нужно: восемь верхних обслуживают 64 из 91
привязки уровней, остальные — по одному-два уровня каждый.

**Общие правила для всех промптов**
- Обязательно `[Instrumental]` — вокал на фоне головоломки мешает читать тексты.
- Проси **петлевую, безостановочную** музыку без финального затухания: концовку всё равно
  срежем, но с ней меньше материала пригодного под петлю.
- Длина: бери самый длинный вариант, который даёт сервис. Нам нужно ≥ 80 секунд ровного
  материала, чтобы вырезать петлю на 60–75 с.
- Динамика ровная: это фон, под который думают. Никаких резких брейков и тишины.

**Как принести в игру**

```bash
python3 tools/import_music.py ~/Downloads/файл.mp3 --as tension --dry-run
python3 tools/import_music.py ~/Downloads/файл.mp3 --as tension
```

Сначала с `--dry-run`: он покажет длину петли, попадание в долю и скачок на стыке. Если
ругается на обрыв — подними `--fade`, если на долю — подвигай `--len` на 1–2 секунды.
Без `--dry-run` файл ложится в игру и сразу нормализуется под −20 LUFS.

---

## Приоритет 1 — без них не обойтись

| Трек | Уровней | Промпт |
|---|---|---|
| `tension` | 15 | `[Instrumental] Ancient Roman suspense loop, low bowed strings drone, sparse plucked lyre, distant war drum pulse, dorian mode, 62 BPM, tense but restrained, no crescendo, seamless loop, no fade out` |
| `battle` | 12 | `[Instrumental] Ancient Roman battle loop, driving frame drums and taiko, short brass calls, urgent ostinato strings, phrygian mode, 104 BPM, relentless, no vocals, seamless loop, no fade out` |
| `tudor_court` | 8 | `[Instrumental] Tudor court dance loop, lute and viol consort, harpsichord, tabor drum, renaissance pavane feel, 76 BPM, stately and bright, seamless loop, no fade out` |
| `revolution_tension` | 8 | `[Instrumental] French revolution dread loop, tense tremolo strings, distant snare march, low piano ostinato, minor key, 66 BPM, oppressive, seamless loop, no fade out` |
| `borgia_tension` | 7 | `[Instrumental] Renaissance Italian intrigue loop, dark lute, viola da gamba, harpsichord, soft hand drum, minor key, 70 BPM, elegant and sinister, seamless loop, no fade out` |
| `empire_tension` | 7 | `[Instrumental] Russian imperial dread loop, low male choir pad, deep church bell, dark cello ostinato, minor key, 56 BPM, heavy and cold, seamless loop, no fade out` |
| `byzantium_tension` | 5 | `[Instrumental] Byzantine chant loop, ison drone, kanonaki and lyra, low bell, phrygian mode, 54 BPM, sacred and foreboding, seamless loop, no fade out` |
| `theme` | меню | `[Instrumental] Historical storybook main theme, warm strings and harp, soft cimbalom, gentle Roman lyre motif, 68 BPM, curious and inviting, seamless loop, no fade out` |

## Приоритет 2 — церемонии и битвы глав

| Трек | Промпт |
|---|---|
| `byzantium_ceremony` | `[Instrumental] Byzantine imperial ceremony, male choir, great bells, slow processional, 60 BPM, sacred grandeur, seamless loop, no fade out` |
| `empire_ceremony` | `[Instrumental] Russian coronation processional, orthodox choir, massive bells, brass, 66 BPM, solemn triumph, seamless loop, no fade out` |
| `borgia_ceremony` | `[Instrumental] Papal renaissance ceremony, organ, sackbuts, lute, choir pad, 74 BPM, ornate and grand, seamless loop, no fade out` |
| `revolution_battle` | `[Instrumental] Napoleonic march loop, snare drums, brass fanfare, driving strings, 112 BPM, martial and heroic, seamless loop, no fade out` |
| `empire_battle` | `[Instrumental] Russian battle loop, heavy drums, low brass, choir shouts pad, 98 BPM, brutal and cold, seamless loop, no fade out` |
| `byzantium_battle` | `[Instrumental] Byzantine battle loop, war drums, low horns, chant fragments, 96 BPM, ancient and grim, seamless loop, no fade out` |
| `tudor_battle` | `[Instrumental] Tudor battle loop, tabor drums, shawms, viols, 100 BPM, rough and driving, seamless loop, no fade out` |
| `borgia_battle` | `[Instrumental] Italian condottieri battle loop, drums, brass, strings ostinato, 106 BPM, sharp and fast, seamless loop, no fade out` |
| `ceremony` (Рим) | `[Instrumental] Roman triumph processional, cornu and tuba brass, frame drums, lyre, 72 BPM, imperial and proud, seamless loop, no fade out` |

## Приоритет 3 — по одному-двум уровням

| Трек | Промпт |
|---|---|
| `romance` (Рим) | `[Instrumental] Ancient romance loop, solo aulos flute, harp, warm strings, 60 BPM, tender and intimate, seamless loop, no fade out` |
| `tudor_romance` | `[Instrumental] Tudor love song instrumental, solo lute, recorder, viol, 62 BPM, tender, seamless loop, no fade out` |
| `tudor_lament` | `[Instrumental] Tudor funeral lament, viol consort, tolling bell, low choir pad, 52 BPM, mournful, seamless loop, no fade out` |
| `borgia_romance` | `[Instrumental] Renaissance love loop, lute duet, soft strings, 62 BPM, warm and courtly, seamless loop, no fade out` |
| `byzantium_romance` | `[Instrumental] Byzantine intimate loop, lyra, soft choir, distant bell, 56 BPM, warm and sacred, seamless loop, no fade out` |
| `empire_romance` | `[Instrumental] Russian romance loop, balalaika tremolo, warm strings, 58 BPM, tender and nostalgic, seamless loop, no fade out` |
| `revolution_romance` | `[Instrumental] Empire-era salon loop, solo piano, light strings, 58 BPM, tender and elegant, seamless loop, no fade out` |
| `revolution_ceremony` | `[Instrumental] Napoleonic coronation, grand brass, choir pad, timpani, 80 BPM, imperial pomp, seamless loop, no fade out` |

---

## Звуковые эффекты

Suno для них не годится: нужны сухие удары в 0.1–2 секунды, а не музыкальные фразы.
Нынешние 11 звуков синтезированы `tools/make_sfx_v2.py` слоями (транзиент + тело + хвост),
их ты не ругал. Если захочется живых — это библиотеки сэмплов, не генерация музыки.
