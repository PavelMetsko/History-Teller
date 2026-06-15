#!/usr/bin/env python3
"""Фоновый амбиент-луп (16 c, бесшовный): тёплый пад + тихое «лирное» арпеджио.

Usage: python3 tools/make_music.py [out.wav]
Default: UnityProject/Assets/Resources/Music/theme.wav
"""
import math
import struct
import sys
from pathlib import Path

SR = 22050
CHORD_DUR = 4.0          # секунд на аккорд
# Am – F – C – G (тёплый минорный цикл), частоты от A3=220
CHORDS = [
    [220.0, 261.63, 329.63],   # Am: A C E
    [174.61, 220.0, 261.63],   # F:  F A C
    [130.81, 164.81, 196.0],   # C:  C E G (ниже, для дыхания)
    [196.0, 246.94, 293.66],   # G:  G B D
]
TOTAL = CHORD_DUR * len(CHORDS)
N = int(SR * TOTAL)

# арпеджио: нота каждые полтакта, паттерн по ступеням аккорда (октавой выше)
ARP_STEP = 0.5
ARP_PATTERN = [0, 1, 2, 1, 0, 2, 1, 2]


def pad_sample(t):
    """Пад: кроссфейд соседних аккордов, лёгкое вибрато."""
    pos = (t % TOTAL) / CHORD_DUR
    idx = int(pos) % len(CHORDS)
    frac = pos - int(pos)
    # кроссфейд 25% в конце аккорда
    xf = max(0.0, (frac - 0.75) * 4.0)
    cur, nxt = CHORDS[idx], CHORDS[(idx + 1) % len(CHORDS)]
    vib = 1.0 + 0.003 * math.sin(2 * math.pi * 0.6 * t)
    s = 0.0
    for f in cur:
        s += (1 - xf) * math.sin(2 * math.pi * f * vib * t)
    for f in nxt:
        s += xf * math.sin(2 * math.pi * f * vib * t)
    return s / 6.0


def arp_sample(t):
    """Щипковая нота: затухающий тон с лёгкой второй гармоникой."""
    step = int((t % TOTAL) / ARP_STEP)
    chord = CHORDS[int((t % TOTAL) / CHORD_DUR) % len(CHORDS)]
    note = chord[ARP_PATTERN[step % len(ARP_PATTERN)] % len(chord)] * 2.0
    lt = (t % TOTAL) % ARP_STEP
    env = math.exp(-lt * 6.0) * min(1.0, lt * 200)
    return (math.sin(2 * math.pi * note * lt)
            + 0.3 * math.sin(4 * math.pi * note * lt)) * env * 0.5


def main(out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    samples = []
    for i in range(N):
        t = i / SR
        s = 0.55 * pad_sample(t) + 0.30 * arp_sample(t)
        samples.append(max(-1.0, min(1.0, s)) * 0.5)  # негромко: это фон
    with open(out, "wb") as fh:
        import wave
        with wave.open(fh, "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(b"".join(
                struct.pack("<h", int(s * 32767)) for s in samples))
    print(f"{out} ({TOTAL:.0f}s loop, {out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        root / "UnityProject" / "Assets" / "Resources" / "Music" / "theme.wav"
    main(out)
