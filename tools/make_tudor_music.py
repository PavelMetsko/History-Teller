#!/usr/bin/env python3
"""Тюдоровские фоновые лупы (бесшовные): величавый двор, тёплый романс, траурный плач.

Идиом тот же, что в make_music.py (пад с кроссфейдом аккордов + щипковое арпеджио),
но тембр «ренессансный»: консортный пад + лютневый щипок, у плача — погребальный колокол.

Usage: python3 tools/make_tudor_music.py [out_dir]
"""
import math, struct, sys, wave
from pathlib import Path

SR = 22050

def pad_sample(t, chords, chord_dur, total):
    pos = (t % total) / chord_dur
    idx = int(pos) % len(chords)
    frac = pos - int(pos)
    xf = max(0.0, (frac - 0.75) * 4.0)          # кроссфейд 25% в конце аккорда
    cur, nxt = chords[idx], chords[(idx + 1) % len(chords)]
    vib = 1.0 + 0.003 * math.sin(2 * math.pi * 0.55 * t)
    s = 0.0
    for f in cur:
        s += (1 - xf) * (math.sin(2*math.pi*f*vib*t) + 0.25*math.sin(4*math.pi*f*vib*t))
    for f in nxt:
        s += xf * (math.sin(2*math.pi*f*vib*t) + 0.25*math.sin(4*math.pi*f*vib*t))
    return s / (len(cur) * 1.6)

def arp_sample(t, chords, chord_dur, total, step_dur, pattern, octave, decay, bright):
    step = int((t % total) / step_dur)
    chord = chords[int((t % total) / chord_dur) % len(chords)]
    note = chord[pattern[step % len(pattern)] % len(chord)] * octave
    lt = (t % total) % step_dur
    env = math.exp(-lt * decay) * min(1.0, lt * 200)
    tone = (math.sin(2*math.pi*note*lt)
            + bright * math.sin(4*math.pi*note*lt)
            + 0.5*bright * math.sin(6*math.pi*note*lt))
    return tone * env * 0.5

def bell_sample(t, total, period, freq):
    """Погребальный колокол: инегармоничные партиалы, долгий спад, удар раз в period."""
    lt = (t % total) % period
    env = math.exp(-lt * 1.1)
    partials = [(1.0, 1.0), (2.0, 0.6), (3.01, 0.35), (4.2, 0.2), (5.4, 0.12)]
    s = sum(a * math.sin(2*math.pi*freq*m*lt) for m, a in partials)
    return s * env * 0.5

def drum_sample(t, total, period, freq):
    """Маршевый барабан: низкий тон с быстрым спадом высоты и амплитуды, удар раз в period."""
    lt = (t % total) % period
    env = math.exp(-lt * 9.0) * min(1.0, lt * 400)
    pitch = freq * (1.0 + 3.0 * math.exp(-lt * 40.0))   # щелчок атаки
    return math.sin(2*math.pi*pitch*lt) * env * 0.9

TRACKS = {
    "tudor_court": dict(     # G–D–Em–C, величаво, яркий лютневый щипок
        chords=[[196.00,246.94,293.66],[146.83,185.00,220.00],
                [164.81,196.00,246.94],[130.81,164.81,196.00]],
        chord_dur=4.0, step_dur=0.5, pattern=[0,2,1,2,0,1,2,1],
        octave=2.0, decay=6.5, bright=0.45, pad_gain=0.5, arp_gain=0.34, bell=None),
    "tudor_romance": dict(   # F–Dm–Bb–C, тёплая, мягкий медленный щипок
        chords=[[174.61,220.00,261.63],[146.83,174.61,220.00],
                [116.54,146.83,174.61],[130.81,164.81,196.00]],
        chord_dur=4.0, step_dur=1.0, pattern=[0,1,2,1],
        octave=2.0, decay=4.0, bright=0.25, pad_gain=0.58, arp_gain=0.26, bell=None),
    "tudor_lament": dict(    # Dm–Bb–Gm–A, траурная, редкий щипок + колокол D2
        chords=[[146.83,174.61,220.00],[116.54,146.83,174.61],
                [98.00,116.54,146.83],[110.00,138.59,164.81]],
        chord_dur=5.0, step_dur=2.5, pattern=[0,2],
        octave=1.0, decay=3.0, bright=0.15, pad_gain=0.55, arp_gain=0.22,
        bell=dict(period=5.0, freq=73.42, gain=0.30)),
    "tudor_battle": dict(    # Em–C–G–D, маршевая, стаккато-щипок + барабанный пульс
        chords=[[164.81,196.00,246.94],[130.81,164.81,196.00],
                [196.00,246.94,293.66],[146.83,185.00,220.00]],
        chord_dur=2.0, step_dur=0.25, pattern=[0,1,2,1,0,2,1,2],
        octave=2.0, decay=9.0, bright=0.5, pad_gain=0.42, arp_gain=0.30,
        bell=None, drum=dict(period=0.5, freq=60.0, gain=0.5)),
}

def render(cfg, out: Path):
    total = cfg["chord_dur"] * len(cfg["chords"])
    n = int(SR * total)
    frames = bytearray()
    for i in range(n):
        t = i / SR
        s = (cfg["pad_gain"] * pad_sample(t, cfg["chords"], cfg["chord_dur"], total)
             + cfg["arp_gain"] * arp_sample(t, cfg["chords"], cfg["chord_dur"], total,
                                            cfg["step_dur"], cfg["pattern"], cfg["octave"],
                                            cfg["decay"], cfg["bright"]))
        if cfg.get("bell"):
            b = cfg["bell"]
            s += b["gain"] * bell_sample(t, total, b["period"], b["freq"])
        if cfg.get("drum"):
            d = cfg["drum"]
            s += d["gain"] * drum_sample(t, total, d["period"], d["freq"])
        s = max(-1.0, min(1.0, s)) * 0.5
        frames += struct.pack("<h", int(s * 32767))
    with wave.open(str(out), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(bytes(frames))
    print(f"{out.name}: {total:.0f}s loop, {out.stat().st_size//1024} KB")

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        root / "ios/Modules/GameContent/Resources/Audio"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, cfg in TRACKS.items():
        render(cfg, out_dir / f"{name}.wav")
