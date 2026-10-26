#!/usr/bin/env python3
"""Генерация звука игры через ElevenLabs (музыка + эффекты).

Ключ читается ТОЛЬКО из окружения / .r2.env — в код и логи не попадает.
Usage: python3 tools/gen_audio_11labs.py [--only theme,select] [--out Content/audio_v2]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.elevenlabs.io/v1"

def _key() -> str:
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        env = ROOT / ".r2.env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("ELEVENLABS_API_KEY="):
                    k = line.split("=", 1)[1].strip().strip('"')
    if not k:
        sys.exit("нет ELEVENLABS_API_KEY")
    return k

STYLE = ("Classical orchestral, acoustic only: string section, woodwinds, French horn, harp, "
         "timpani. Slow, calm, cinematic, no vocals, no drums kit, no synthesizers, no electronic "
         "elements. Warm concert-hall reverb. Suitable as a quiet game background loop.")

MUSIC = {
    "theme":   {"prompt": f"{STYLE} Main theme: gentle adagio in D minor, flute melody over "
                          f"sustained strings, harp arpeggios, a soft oboe answer, resolves back to "
                          f"the start so it can loop seamlessly.", "ms": 60000},
    "tension": {"prompt": f"{STYLE} Mysterious andante in G minor: low cellos and basses ostinato, "
                          f"horn pedal, sparse pizzicato, a single oboe phrase, timpani on downbeats. "
                          f"Intrigue and suspense, never loud. Loops seamlessly.", "ms": 60000},
    # глава «Польша»: польский колорит — мазурка, полонез, Шопен, старопольские колокола
    "poland_tension":  {"prompt": f"{STYLE} Polish historical mood, Chopin-like melancholy: slow "
                                  f"mazurka rhythm in A minor on low strings, solo clarinet melody with "
                                  f"a folk modal turn, distant church bell, quiet harp. Uneasy, "
                                  f"brooding, never loud. Loops seamlessly.", "ms": 60000},
    "poland_battle":   {"prompt": f"{STYLE} Heroic Polish cavalry charge, winged hussars: driving "
                                  f"3/4 polonaise-march rhythm in D minor, strong timpani, horns and "
                                  f"trumpets in unison, urgent strings ostinato, epic but controlled, "
                                  f"no drum kit. Loops seamlessly.", "ms": 60000},
    "poland_ceremony": {"prompt": f"{STYLE} Stately Polish court ceremony: majestic polonaise in "
                                  f"G major, brass fanfare phrases, bright strings, harpsichord-like "
                                  f"harp, Wawel cathedral bell, coronation pomp, dignified tempo. "
                                  f"Loops seamlessly.", "ms": 60000},
    "poland_romance":  {"prompt": f"{STYLE} Tender Polish romance, Chopin nocturne character "
                                  f"arranged for orchestra: solo violin and cello duet over soft "
                                  f"strings, rubato feel, gentle harp, nostalgic and longing, quiet. "
                                  f"Loops seamlessly.", "ms": 60000},
    # глава «США»: американский колорит — фолк, спиричуэлс, фифы и барабаны, Копленд
    "usa_tension":  {"prompt": f"{STYLE} Early American frontier suspense: low strings drone in E minor, solo "
                               f"fiddle with an Appalachian folk modal melody, sparse banjo-like harp plucks, soft "
                               f"bass drum heartbeat. Uneasy, open-prairie loneliness, never loud. Loops seamlessly.",
                     "ms": 60000},
    "usa_battle":   {"prompt": f"{STYLE} American Revolution and Civil War battle march: fife-like piccolo and "
                               f"field snare rudiments over driving strings in D minor, brass calls, timpani, "
                               f"determined and urgent, no drum kit. Loops seamlessly.", "ms": 60000},
    "usa_ceremony": {"prompt": f"{STYLE} Stately American ceremonial theme, mid-century concert-hall style: open "
                               f"fifths, broad brass chorale in C major, bright strings, wide landscape feeling, "
                               f"hopeful and dignified. Loops seamlessly.", "ms": 60000},
    "usa_romance":  {"prompt": f"{STYLE} Tender American folk ballad, Shenandoah-like: solo cello and warm "
                               f"strings, gentle harp, a quiet fiddle answer, nostalgic and longing, slow. "
                               f"Loops seamlessly.", "ms": 60000},
    # глава «Англия»: английский колорит — лютня, виолы, хорал, народные баллады, медь торжеств
    "england_tension":  {"prompt": f"{STYLE} English historical intrigue: consort of viols in D minor, slow pavane rhythm, "
                                   f"a solo lute melody in Dorian mode, distant cathedral bell, low drone. Courtly suspense, "
                                   f"never loud. Loops seamlessly.", "ms": 60000},
    "england_battle":   {"prompt": f"{STYLE} English medieval and early modern battle: martial tabor-like timpani pulse, "
                                   f"horns and trumpets in fourths, driving low strings in E minor, a fife-like piccolo "
                                   f"countermelody, determined, epic but controlled, no drum kit. Loops seamlessly.", "ms": 60000},
    "england_ceremony": {"prompt": f"{STYLE} Stately English coronation ceremony: broad brass chorale and choir-like "
                                   f"strings in D major, pealing church bells, processional tempo, Westminster Abbey pomp, "
                                   f"dignified and bright. Loops seamlessly.", "ms": 60000},
    "england_romance":  {"prompt": f"{STYLE} Tender English folk ballad, Greensleeves-like modal melancholy: solo lute and "
                                   f"recorder over soft viols in A minor, gentle harp, longing and intimate, quiet. "
                                   f"Loops seamlessly.", "ms": 60000},
    # глава «Франция»: французский колорит — клавесин, гобой, барабан и марш, мюзет
    "france_tension":   {"prompt": f"{STYLE} French court intrigue: harpsichord-like harp ostinato in C minor, slow "
                                   f"sarabande rhythm, solo oboe melody, pizzicato low strings, a distant snare tap. Elegant "
                                   f"suspense, never loud. Loops seamlessly.", "ms": 60000},
    "france_battle":    {"prompt": f"{STYLE} French revolutionary and Napoleonic battle march: military snare rudiments, "
                                   f"bold trumpets and horns in G minor, urgent strings, timpani, heroic and driving, no drum "
                                   f"kit. Loops seamlessly.", "ms": 60000},
    "france_ceremony":  {"prompt": f"{STYLE} Majestic French royal ceremony, Versailles grandeur: dotted French-overture "
                                   f"rhythm in D major, trumpets and timpani, bright strings, harp flourishes, stately and "
                                   f"festive. Loops seamlessly.", "ms": 60000},
    "france_romance":   {"prompt": f"{STYLE} Tender French romance: solo flute and clarinet over soft strings in F major, "
                                   f"gentle waltz-like lilt, delicate harp, wistful and intimate, quiet. Loops seamlessly.",
                         "ms": 60000},
    # глава «Россия»: русский колорит — колокола, хоровые гармонии, балалаечный щипок, глубокий минор
    "russia_tension":   {"prompt": f"{STYLE} Russian historical suspense: deep cellos and basses drone in B minor, low "
                                   f"Orthodox-chant-like horn chords, distant church bells, sparse plucked strings like a "
                                   f"balalaika, solo bassoon phrase. Brooding, never loud. Loops seamlessly.", "ms": 60000},
    "russia_battle":    {"prompt": f"{STYLE} Russian epic battle: heavy timpani, brass in unison, driving low strings in "
                                   f"D minor, ringing bells, folk-modal horn calls, broad and powerful but controlled, no drum "
                                   f"kit. Loops seamlessly.", "ms": 60000},
    "russia_ceremony":  {"prompt": f"{STYLE} Russian coronation in the Kremlin: full peal of Orthodox church bells, majestic "
                                   f"brass chorale and rich strings in E-flat major, choir-like sustained chords, solemn and "
                                   f"grand. Loops seamlessly.", "ms": 60000},
    "russia_romance":   {"prompt": f"{STYLE} Tender Russian romance: solo cello melody in G minor over soft strings, "
                                   f"gentle harp, a clarinet answer with a folk song turn, melancholic and warm, quiet. "
                                   f"Loops seamlessly.", "ms": 60000},
    # глава «Италия»: итальянский колорит — мандолина, лютня, оперная кантилена, тарантелла
    "italy_tension":    {"prompt": f"{STYLE} Italian Renaissance intrigue: plucked lute and mandolin ostinato in E minor, "
                                   f"low strings, a solo cor anglais melody, distant Roman church bell, conspiratorial and "
                                   f"quiet. Loops seamlessly.", "ms": 60000},
    "italy_battle":     {"prompt": f"{STYLE} Italian Risorgimento battle: brisk march in A minor, bold trumpets and horns, "
                                   f"driving strings with tarantella-like triplets, timpani, heroic and urgent, no drum kit. "
                                   f"Loops seamlessly.", "ms": 60000},
    "italy_ceremony":   {"prompt": f"{STYLE} Italian ceremonial grandeur, Venetian and papal pomp: antiphonal brass "
                                   f"chorale in C major, bright strings, festive bells, stately and luminous. Loops seamlessly.",
                         "ms": 60000},
    "italy_romance":    {"prompt": f"{STYLE} Tender Italian romance, operatic bel canto feeling: solo violin cantilena in "
                                   f"F major over soft strings, gentle mandolin tremolo and harp, warm and longing, quiet. "
                                   f"Loops seamlessly.", "ms": 60000},
}

SFX = {
    "place":  ("a thick paper playing card laid down flat on a wooden table, soft slap of card "
               "on wood, muted, close-miked, completely dry, under half a second", 0.6),
    "select": ("the quietest possible wooden tap: a fingertip barely touching a small wooden "
               "block once, soft, muffled, warm, no pitch, no ring, completely dry, very short", 0.5),
    "accent": ("short orchestral accent: pizzicato strings with a soft French horn note, brief "
               "concert hall tail, cinematic, no drums", 1.6),
    "win":    ("short triumphant orchestral flourish: ascending harp glissando, strings swell, "
               "tubular bell strike, timpani roll, warm hall reverb, about two seconds", 2.8),
    "error":  ("single dull timpani hit, low and flat, muted, no pitch, very short", 0.8),
}

def _post(path: str, body: dict, key: str, timeout: int = 300) -> bytes:
    req = urllib.request.Request(f"{API}/{path}", data=json.dumps(body).encode(),
                                 headers={"xi-api-key": key, "Content-Type": "application/json",
                                          "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def gen_music(name: str, key: str, out: Path) -> None:
    spec = MUSIC[name]
    body = {"prompt": spec["prompt"], "music_length_ms": spec["ms"]}
    data = _post("music?output_format=mp3_44100_192", body, key)
    (out / f"{name}.mp3").write_bytes(data)
    print(f"  {name}.mp3  {len(data)//1024} KB")

def gen_sfx(name: str, key: str, out: Path) -> None:
    text, dur = SFX[name]
    body = {"text": text, "duration_seconds": dur, "prompt_influence": 0.4}
    data = _post("sound-generation?output_format=mp3_44100_128", body, key)
    (out / f"{name}.mp3").write_bytes(data)
    print(f"  {name}.mp3  {len(data)//1024} KB")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default="Content/audio_raw")
    a = ap.parse_args()
    key = _key()
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    names = [x for x in a.only.split(",") if x] or list(MUSIC) + list(SFX)
    for n in names:
        try:
            (gen_music if n in MUSIC else gen_sfx)(n, key, out)
        except urllib.error.HTTPError as e:
            print(f"  {n}: HTTP {e.code} — {e.read()[:300].decode(errors='replace')}")
        time.sleep(1.0)
