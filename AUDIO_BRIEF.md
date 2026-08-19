# Задание на генерацию звука для History Teller

## Чем генерировать
- **Эффекты** — ElevenLabs Sound Effects (платный тариф даёт коммерческие права на вывод).
- **Музыка** — Suno или Udio, **платный** тариф: только там лицензия разрешает коммерческое использование. На бесплатном — нельзя, это важно.

## Общие требования
- Музыка: **без вокала**, 60–120 секунд, инструментал, зацикливание сделаю сам.
- Формат: WAV или MP3 320 — я сам сконвертирую в m4a и выровняю громкость.
- Эффекты: короткие, 0.3–1.5 секунды, без реверберационного хвоста длиннее полсекунды.
- Складывай всё в одну папку и пришли мне путь — имена файлов ниже, их лучше сохранить.

---

# ЭФФЕКТЫ (16 штук)

| файл | промпт |
|---|---|
| `place.wav` | soft wooden card placed on a table, single dry tap, close-miked, no reverb |
| `remove.wav` | wooden card lifted off a table, short paper-and-wood scrape, dry |
| `select.wav` | light UI tick, small wooden click, warm, very short |
| `ally.wav` | two hands clasping in a firm handshake, cloth rustle, warm and short |
| `conspire.wav` | conspiratorial whisper hiss without words, cloth movement, close and dry |
| `love.wav` | soft harp glissando upward, two notes, warm and brief |
| `kill.wav` | dagger thrust into cloth and flesh, muffled, no scream, short |
| `crown.wav` | metal crown set on a stone altar, bright ring with quick decay |
| `envy.wav` | low dissonant string swell, two seconds, ominous but quiet |
| `win.wav` | small triumphant brass and harp flourish, one second, medieval |
| `error.wav` | dull wooden thud, low and flat, no musical pitch |
| `clash.wav` | two swords striking once, metallic, short, no echo |
| `coin.wav` | handful of gold coins dropped on wood, bright, one second |
| `gavel.wav` | judge gavel striking a wooden block, single dry hit |
| `drum.wav` | single war drum hit, deep, leather, short decay |
| `flee.wav` | quick footsteps running away on stone, three steps, fading |

---

# МУЗЫКА (25 тем)

Для каждой главы — четыре настроения. Общий стиль всей игры: **исторический инструментал,
камерный, негромкий, без вокала; музыка фоновая и не должна перебивать чтение.**

## Общие (глава «Древний Рим» и меню)
| файл | промпт |
|---|---|
| `theme.wav` | slow cinematic main theme, solo lyre and low strings, ancient Mediterranean, contemplative, no vocals |
| `battle.wav` | Roman military march, war drums and low brass, steady and grim, instrumental |
| `ceremony.wav` | Roman triumph, ceremonial brass and timpani, stately, instrumental |
| `romance.wav` | intimate ancient lyre and flute duet, tender, slow, instrumental |
| `tension.wav` | quiet suspense, plucked strings and low drone, conspiracy in the Senate, instrumental |

## Англия — `tudor_*`
| файл | промпт |
|---|---|
| `tudor_battle.wav` | Tudor era battle, snare drums, fifes and low brass, English renaissance, instrumental |
| `tudor_court.wav` | Tudor royal court dance, harpsichord, viols and recorder, courtly and bright, instrumental |
| `tudor_lament.wav` | English renaissance lament, solo lute and viola da gamba, mournful, instrumental |
| `tudor_romance.wav` | Tudor love song without words, lute and recorder, gentle, instrumental |

## Франция — `revolution_*`
| файл | промпт |
|---|---|
| `revolution_battle.wav` | French revolutionary march, snare drums and brass, urgent, instrumental |
| `revolution_ceremony.wav` | Napoleonic imperial ceremony, grand brass and timpani, pompous, instrumental |
| `revolution_romance.wav` | French salon romance, solo piano and strings, delicate, instrumental |
| `revolution_tension.wav` | pre-revolution unrest, tremolo strings and distant drum, anxious, instrumental |

## Россия — `empire_*`
| файл | промпт |
|---|---|
| `empire_battle.wav` | Russian imperial battle, low brass, drums and male-choir-like strings, heavy, instrumental |
| `empire_ceremony.wav` | Russian orthodox ceremony, church bells and deep strings, solemn, instrumental |
| `empire_romance.wav` | Russian romance, solo piano and cello, melancholic and warm, instrumental |
| `empire_tension.wav` | Russian palace intrigue, low strings and sparse balalaika, cold and tense, instrumental |

## Италия — `borgia_*`
| файл | промпт |
|---|---|
| `borgia_battle.wav` | Italian renaissance battle, drums, shawms and brass, sharp and driving, instrumental |
| `borgia_ceremony.wav` | Vatican ceremony, pipe organ and choir-like strings, majestic and cold, instrumental |
| `borgia_romance.wav` | Italian renaissance love dance, lute and mandolin, sweet and light, instrumental |
| `borgia_tension.wav` | poison and conspiracy in a Renaissance palace, harpsichord and low strings, sinister, instrumental |

## Византия — `byzantium_*`
| файл | промпт |
|---|---|
| `byzantium_battle.wav` | Byzantine war, deep drums, brass horns and modal strings, eastern Roman, instrumental |
| `byzantium_ceremony.wav` | Byzantine imperial ceremony, modal choir-like strings and bells, golden and vast, instrumental |
| `byzantium_romance.wav` | Byzantine court romance, kanun and soft strings, eastern modal, tender, instrumental |
| `byzantium_tension.wav` | Byzantine palace conspiracy, low modal drone and plucked strings, cold, instrumental |

---

## Что делаю я, когда пришлёшь файлы
Конвертирую в m4a, выровняю громкость по всем трекам (чтобы главы не скакали по громкости),
сделаю бесшовные петли, положу в контент-бандл, опубликую и соберу билды.
Старые файлы сохраню — если новая музыка не понравится, откат в одну команду.
