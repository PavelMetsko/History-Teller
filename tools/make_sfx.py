#!/usr/bin/env python3
"""Синтез SFX-заглушек для игры (16-bit mono WAV, 44100 Hz).

Usage: python3 tools/make_sfx.py [out_dir]
Default out_dir: UnityProject/Assets/Resources/Sfx
"""
import math
import struct
import sys
import wave
from pathlib import Path

SR = 44100


def env(i, n, attack=0.01, release=0.4):
    """Огибающая: атака + экспоненциальный спад."""
    t = i / n
    a = min(1.0, t / max(attack, 1e-6))
    r = math.exp(-t / release * 5)
    return a * r


def tone(freq_from, freq_to, dur, vol=0.6, wave_fn='sine', release=0.4):
    n = int(SR * dur)
    out = []
    phase = 0.0
    for i in range(n):
        f = freq_from + (freq_to - freq_from) * (i / n)
        phase += 2 * math.pi * f / SR
        if wave_fn == 'sine':
            s = math.sin(phase)
        elif wave_fn == 'square':
            s = 1.0 if math.sin(phase) > 0 else -1.0
        else:  # triangle
            s = 2 / math.pi * math.asin(math.sin(phase))
        out.append(s * vol * env(i, n, release=release))
    return out


def noise(dur, vol=0.5, release=0.25):
    import random
    rnd = random.Random(42)
    n = int(SR * dur)
    return [rnd.uniform(-1, 1) * vol * env(i, n, release=release) for i in range(n)]


def mix(*tracks):
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, s in enumerate(t):
            out[i] += s
    peak = max(1.0, max(abs(s) for s in out))
    return [s / peak for s in out]


def seq(*parts, gap=0.0):
    out = []
    for p in parts:
        out.extend(p)
        out.extend([0.0] * int(SR * gap))
    return out


def save(name, samples, out_dir):
    path = out_dir / f"{name}.wav"
    with wave.open(str(path), 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b''.join(
            struct.pack('<h', int(max(-1, min(1, s)) * 32767)) for s in samples))
    print(f"{path} ({len(samples)/SR:.2f}s)")


def main(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    # интерфейс
    save("select", tone(1100, 1300, 0.05, 0.35, release=0.6), out_dir)
    save("place", tone(520, 320, 0.10, 0.55, 'triangle', release=0.5), out_dir)
    save("remove", tone(320, 520, 0.08, 0.4, 'triangle', release=0.5), out_dir)
    save("error", tone(160, 140, 0.16, 0.45, 'square', release=0.8), out_dir)
    # правила
    save("ally", mix(tone(392, 392, 0.16, 0.4), tone(523, 523, 0.16, 0.3)), out_dir)
    save("conspire", tone(233, 175, 0.28, 0.5, 'triangle', release=0.7), out_dir)
    save("love", seq(tone(523, 523, 0.09, 0.45), tone(784, 784, 0.16, 0.45)), out_dir)
    save("envy", tone(466, 415, 0.22, 0.5, 'triangle', release=0.6), out_dir)
    save("crown", seq(tone(523, 523, 0.07, 0.4), tone(659, 659, 0.07, 0.4),
                      tone(784, 784, 0.14, 0.45)), out_dir)
    save("kill", mix(noise(0.18, 0.5), tone(90, 55, 0.22, 0.9, release=0.5)), out_dir)
    # финал
    save("win", seq(tone(523, 523, 0.10, 0.45), tone(659, 659, 0.10, 0.45),
                    tone(784, 784, 0.10, 0.45), tone(1047, 1047, 0.30, 0.5)), out_dir)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        root / "UnityProject" / "Assets" / "Resources" / "Sfx"
    main(out)
