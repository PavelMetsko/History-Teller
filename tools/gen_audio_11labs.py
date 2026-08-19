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
