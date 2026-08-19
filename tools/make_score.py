#!/usr/bin/env python3
"""Партитуры History Teller на движке orchestra.py: две петли и пять эффектов.

Оркестр: струнный квинтет (2 скрипки, альт, виолончель, контрабас), флейта, гобой, валторна,
арфа, литавры, трубчатые колокола. Всё в темперированном строе, без расстроек.

Usage: python3 tools/make_score.py [--only theme,tension,...] [--out Content/audio_v2]
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import orchestra as o
from orchestra import hz, SR, put

BPM = 66
BEAT = 60.0 / BPM          # четверть ≈ 0.909 с
BAR = 4 * BEAT             # 4/4


def _buf(bars: int) -> np.ndarray:
    return np.zeros((int(bars * BAR * SR), 2), dtype=np.float32)


def _violin_hi(freq, dur, *, seed=0):
    return o.violin(freq * 2, dur, seed=seed)


def _voice_chord(buf, notes, t0, dur, gain, seed, inst=o.violin, spread=0.36):
    """Аккорд ансамблем: каждый голос — свой инструмент, своя фаза, свой микровход."""
    rng = np.random.default_rng(seed)
    k = len(notes)
    for i, nm in enumerate(notes):
        pan = 0.5 + spread * (i - (k - 1) / 2) / max(1, (k - 1) / 2)
        put(buf, inst(hz(nm), dur, seed=seed * 31 + i), t0 + rng.uniform(0, 0.04), gain, pan)


# ─────────────────────────────────────────── ТЕМА: Adagio, ре минор → фа мажор, 16 тактов


def theme() -> np.ndarray:
    """Главная тема. Adagio 66, 16 тактов (~58 с).

    Форма A(8) B(8): A — струнные держат гармонию, флейта поёт; B — вступают гобой и валторна,
    подъём к фа мажору и возврат в ре минор перед стыком, чтобы петля замыкалась естественно.
    Гармония: Dm – Bb – F – C | Dm – Gm – A – Dm  ×  A-часть; в B — F – C – Dm – Bb | Gm – A – Dm – A.
    """
    buf = _buf(16)
    A = [(["D3", "F3", "A3"], "D2"), (["Bb2", "D3", "F3"], "Bb1"), (["F3", "A3", "C4"], "F2"), (["E3", "G3", "C4"], "C2"),
         (["D3", "F3", "A3"], "D2"), (["D3", "G3", "Bb3"], "G2"), (["C#3", "E3", "A3"], "A1"), (["D3", "F3", "A3"], "D2")]
    B = [(["F3", "A3", "C4"], "F2"), (["E3", "G3", "C4"], "C2"), (["D3", "F3", "A3"], "D2"), (["D3", "F3", "Bb3"], "Bb1"),
         (["D3", "G3", "Bb3"], "G2"), (["C#3", "E3", "A3"], "A1"), (["D3", "F3", "A3"], "D2"), (["C#3", "E3", "A3"], "A1")]
    for i, (voices, bass) in enumerate(A + B):
        t0 = i * BAR
        # струнные: скрипки/альт держат аккорд целый такт с лёгким перекрытием
        _voice_chord(buf, voices, t0, BAR * 1.08, 0.24, seed=100 + i)
        # первые скрипки октавой выше — без них оркестр глухой (замер: выше 1.2 кГц было 3 %)
        _voice_chord(buf, [voices[1], voices[2]], t0, BAR * 1.06, 0.20, seed=150 + i, inst=_violin_hi)
        # виолончель — бас, контрабас — октавой ниже, тише
        put(buf, o.cello(hz(bass), BAR * 1.06, seed=200 + i), t0, 0.26, 0.5)
        put(buf, o.cello(hz(bass) / 2, BAR * 1.06, seed=250 + i), t0, 0.16, 0.5)
        # арфа: арпеджио восьмыми на 3–4 доли, только в A-части и в конце B
        if i < 8 or i >= 14:
            for k, nm in enumerate(voices + [voices[0]]):
                f = hz(nm) * (2 if k == len(voices) else 1)
                put(buf, o.harp(f, 2.2, seed=300 + i * 8 + k), t0 + 2 * BEAT + k * BEAT / 2, 0.11, 0.35 + 0.08 * k)
    # мелодия флейты (A): секунды от начала, длительности в долях
    mel_a = [("A4", 0, 3), ("F4", 3, 1), ("G4", 4, 2), ("A4", 6, 2),
             ("Bb4", 8, 3), ("A4", 11, 1), ("G4", 12, 2), ("F4", 14, 2),
             ("A4", 16, 2), ("D5", 18, 2), ("C5", 20, 3), ("Bb4", 23, 1),
             ("A4", 24, 2), ("G4", 26, 1), ("F4", 27, 1), ("D4", 28, 4)]
    for k, (nm, beat, dur) in enumerate(mel_a):
        put(buf, o.flute(hz(nm), dur * BEAT * 0.98, seed=400 + k), beat * BEAT, 0.20, 0.54)
    # B-часть: гобой ведёт, валторна держит педаль, флейта отвечает
    mel_b = [("C5", 32, 3), ("A4", 35, 1), ("Bb4", 36, 2), ("C5", 38, 2),
             ("D5", 40, 3), ("C5", 43, 1), ("Bb4", 44, 2), ("A4", 46, 2),
             ("G4", 48, 2), ("A4", 50, 2), ("Bb4", 52, 2), ("A4", 54, 2),
             ("F4", 56, 2), ("E4", 58, 2), ("D4", 60, 3), ("E4", 63, 1)]
    for k, (nm, beat, dur) in enumerate(mel_b):
        put(buf, o.oboe(hz(nm), dur * BEAT * 0.96, seed=500 + k), beat * BEAT, 0.14, 0.44)
    for i, nm in enumerate(["F3", "C3", "D3", "Bb2", "G3", "A3", "D3", "A2"]):
        put(buf, o.horn(hz(nm), BAR * 1.05, seed=600 + i), (8 + i) * BAR, 0.10, 0.62)
    # флейта в B — эхо на слабые такты
    for k, (nm, beat) in enumerate([("F5", 34), ("D5", 42), ("Bb4", 50), ("A4", 58)]):
        put(buf, o.flute(hz(nm), 1.8 * BEAT, seed=700 + k), beat * BEAT, 0.12, 0.6)
    ir = o.hall_ir(rt60=2.6)
    return o.seal(o.finish(o.reverb_loop(buf, ir, 0.28), 0.9))


# ─────────────────────────────────────────── НАПРЯЖЕНИЕ: Andante misterioso, соль минор


def tension() -> np.ndarray:
    """Тема интриги. 16 тактов. Низкие струнные, педаль валторны, литавры на сильную долю через
    такт, гобой одной фразой в середине. Гармония остинато: Gm – Gm – Eb – Eb | Cm – D – Gm – D.
    """
    buf = _buf(16)
    prog = [(["G3", "Bb3", "D4"], "G2"), (["G3", "Bb3", "D4"], "G2"), (["G3", "Bb3", "Eb4"], "Eb2"), (["G3", "Bb3", "Eb4"], "Eb2"),
            (["G3", "C4", "Eb4"], "C2"), (["F#3", "A3", "D4"], "D2"), (["G3", "Bb3", "D4"], "G2"), (["F#3", "A3", "D4"], "D2")] * 2
    for i, (voices, bass) in enumerate(prog):
        t0 = i * BAR
        _voice_chord(buf, voices, t0, BAR * 1.1, 0.21, seed=800 + i, spread=0.3)
        _voice_chord(buf, [voices[2]], t0, BAR * 1.08, 0.14, seed=850 + i, inst=_violin_hi)
        put(buf, o.cello(hz(bass), BAR * 1.08, seed=900 + i), t0, 0.28, 0.5)
        put(buf, o.cello(hz(bass) / 2, BAR * 1.08, seed=950 + i), t0, 0.18, 0.5)
        if i % 2 == 0:
            put(buf, o.timpani(hz(bass) if hz(bass) < 100 else hz(bass) / 2, 2.5, seed=1000 + i), t0, 0.22, 0.5)
        # пиццикато виолончели на 3-ю долю — пульс
        put(buf, o.harp(hz(bass) * 2, 1.2, seed=1100 + i), t0 + 2 * BEAT, 0.09, 0.42)
    # валторна: педаль соль/ре через 4 такта
    for i, nm in enumerate(["G2", "Eb3", "C3", "D3", "G2", "Eb3", "G2", "D3"]):
        put(buf, o.horn(hz(nm), 2 * BAR * 1.02, seed=1200 + i), 2 * i * BAR, 0.11, 0.6)
    # гобой: одна фраза в тактах 9–12
    for k, (nm, beat, dur) in enumerate([("D5", 32, 3), ("Eb5", 35, 1), ("D5", 36, 2), ("Bb4", 38, 2),
                                          ("C5", 40, 3), ("Bb4", 43, 1), ("A4", 44, 4)]):
        put(buf, o.oboe(hz(nm), dur * BEAT * 0.96, seed=1300 + k), beat * BEAT, 0.12, 0.46)
    # колокол на границе половин
    put(buf, o.bell(hz("G4"), 5.0, seed=1400), 0.0, 0.05, 0.6)
    put(buf, o.bell(hz("D4"), 5.0, seed=1401), 8 * BAR, 0.05, 0.4)
    ir = o.hall_ir(rt60=3.0)
    return o.seal(o.finish(o.reverb_loop(buf, ir, 0.32), 0.88))


# ─────────────────────────────────────────── ЭФФЕКТЫ (не петли, с хвостом)


def _one_shot(sec: float) -> np.ndarray:
    return np.zeros((int(sec * SR), 2), dtype=np.float32)


def sfx_place() -> np.ndarray:
    """Кадр поставлен: короткий щипок арфы, низко и мягко."""
    b = _one_shot(0.6)
    put(b, o.harp(hz("D4"), 0.55, seed=1), 0.0, 0.5, 0.5)
    return o.finish(b, 0.6)


def sfx_select() -> np.ndarray:
    """Тап: высокая короткая арфа, тише."""
    b = _one_shot(0.4)
    put(b, o.harp(hz("A5"), 0.35, seed=2), 0.0, 0.4, 0.5)
    return o.finish(b, 0.5)


def sfx_accent() -> np.ndarray:
    """Событие на доске: аккорд струнных pizzicato-стиля (арфа) плюс валторна — короткий акцент."""
    b = _one_shot(1.8)
    for k, nm in enumerate(["D3", "A3", "D4"]):
        put(b, o.harp(hz(nm), 1.4, seed=10 + k), 0.02 * k, 0.32, 0.4 + 0.1 * k)
    put(b, o.horn(hz("D3"), 1.2, seed=13), 0.0, 0.16, 0.5)
    return o.finish(o.reverb_loop(b, o.hall_ir(1.4), 0.2), 0.75)


def sfx_win() -> np.ndarray:
    """Уровень пройден: восходящая арфа по ре мажору, струнные, колокол."""
    b = _one_shot(3.0)
    for k, nm in enumerate(["D4", "F#4", "A4", "D5", "F#5"]):
        put(b, o.harp(hz(nm), 2.2, seed=20 + k), 0.08 * k, 0.28, 0.38 + 0.06 * k)
    _voice_chord(b, ["D4", "F#4", "A4"], 0.15, 2.4, 0.18, seed=25)
    put(b, o.bell(hz("D5"), 2.6, seed=26), 0.12, 0.14, 0.5)
    put(b, o.timpani(hz("D2"), 2.0, seed=27), 0.0, 0.18, 0.5)
    return o.finish(o.reverb_loop(b, o.hall_ir(2.2), 0.28), 0.86)


def sfx_error() -> np.ndarray:
    """Не сходится: глухая литавра, без музыкальной жалобы."""
    b = _one_shot(0.9)
    put(b, o.timpani(hz("A1"), 0.85, seed=30), 0.0, 0.5, 0.5)
    return o.finish(b, 0.62)


PIECES = {"theme": theme, "tension": tension, "place": sfx_place, "select": sfx_select,
          "accent": sfx_accent, "win": sfx_win, "error": sfx_error}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default="Content/audio_v2")
    a = ap.parse_args()
    out = Path(__file__).resolve().parent.parent / a.out
    out.mkdir(parents=True, exist_ok=True)
    for name in ([x for x in a.only.split(",") if x] or list(PIECES)):
        x = PIECES[name]()
        o.write(out / f"{name}.wav", x)
        print(f"  {name}.wav  {len(x) / SR:.1f} с")
