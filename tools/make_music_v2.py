#!/usr/bin/env python3
"""Фоновая музыка глав: длинные формы (60–90 с) с секциями A/B/A′ на движке audio_engine.

Чем отличается от старых make_music/make_tudor_music/make_epoch_music (все три заменяет):
  * форма: 20–28 тактов с развитием и мотивом главы, а не 16-секундная петля из 4 аккордов;
  * тембр: щипок Karplus–Strong, пад с расстройкой, колокол с инегармониками, барабан-мембрана;
  * пространство: у каждой главы своя IR (собор / зал / камерная палата);
  * луп бесшовный по построению (события пишутся по кругу, реверб — циклическая свёртка);
  * стерео 44.1 кГц вместо моно 22 050.

Имена треков совпадают со старыми — поле `music` в уровнях менять не нужно.

Usage: python3 tools/make_music_v2.py [out_dir] [--only name1,name2]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_engine import (SR, bell, bowed_chord, choir, chord, convolve_loop, drum, flute,
                          make_ir, master, note, place, place_stereo, pluck, write_wav)


# ─────────────────────────────────────────────────────────── палитры глав

# pluck: (damp, bright, body) — чем выше damp, тем длиннее звон; bright — яркость медиатора.
PALETTES = {
    "rome": dict(                      # кифара/лира: сухой античный щипок, каменный зал
        pluck=dict(damp=0.9938, bright=0.42, body=0.30),
        pad_kind="pad", pad_harm=8, pad_detune=7.0,
        ir=dict(rt60=1.9, damping=0.5, predelay=0.016), rev_mix=0.30,
        bell_decay=0.9, drum_freq=64.0,
    ),
    "tudor": dict(                     # лютня: яркий щипок, зал придворной капеллы
        pluck=dict(damp=0.9962, bright=0.62, body=0.40),
        pad_kind="pad", pad_harm=10, pad_detune=6.0,
        ir=dict(rt60=2.3, damping=0.45, predelay=0.020), rev_mix=0.33,
        bell_decay=1.3, drum_freq=70.0,
    ),
    "revolution": dict(                # струнный оркестр + барабан: улица и марш
        pluck=dict(damp=0.9930, bright=0.55, body=0.28),
        pad_kind="pad", pad_harm=12, pad_detune=9.0,
        ir=dict(rt60=1.6, damping=0.6, predelay=0.012), rev_mix=0.24,
        bell_decay=1.0, drum_freq=58.0,
    ),
    "empire": dict(                    # русский хор и колокола: собор, длинный хвост
        pluck=dict(damp=0.9950, bright=0.38, body=0.45),
        pad_kind="choir", pad_harm=12, pad_detune=11.0,
        ir=dict(rt60=3.4, damping=0.35, predelay=0.026), rev_mix=0.40,
        bell_decay=2.4, drum_freq=54.0,
    ),
    "borgia": dict(                    # ренессансная лютня, камерная палата
        pluck=dict(damp=0.9968, bright=0.70, body=0.38),
        pad_kind="pad", pad_harm=9, pad_detune=5.0,
        ir=dict(rt60=1.5, damping=0.55, predelay=0.011), rev_mix=0.26,
        bell_decay=1.1, drum_freq=66.0,
    ),
    "byzantium": dict(                 # исон и хор Св. Софии: самый длинный реверб
        pluck=dict(damp=0.9946, bright=0.34, body=0.42),
        pad_kind="choir", pad_harm=14, pad_detune=13.0,
        ir=dict(rt60=4.2, damping=0.30, predelay=0.030), rev_mix=0.44,
        bell_decay=2.8, drum_freq=56.0,
    ),
}

# Мотив главы: (ступень аккорда, длительность в долях). Появляется в секции B и в коде —
# это то, по чему глава узнаётся на слух.
MOTIFS = {
    "rome":       [(2, 1.0), (1, 1.0), (0, 2.0), (1, 1.0), (2, 3.0)],
    "tudor":      [(0, 1.0), (2, 1.0), (1, 2.0), (0, 1.0), (2, 1.0), (1, 2.0)],
    "revolution": [(0, 0.5), (0, 0.5), (1, 1.0), (2, 2.0), (1, 1.0), (0, 3.0)],
    "empire":     [(2, 2.0), (1, 2.0), (0, 4.0)],
    "borgia":     [(2, 0.5), (1, 0.5), (2, 1.0), (0, 2.0), (1, 4.0)],
    "byzantium":  [(0, 3.0), (1, 1.0), (2, 4.0)],
}


# ─────────────────────────────────────────────────────────── композитор

BEATS = 4  # такт 4/4


def _bar_dur(bpm: float) -> float:
    return BEATS * 60.0 / bpm


def compose(*, epoch: str, bpm: float, sections: list[dict], seed: int = 0) -> np.ndarray:
    """Собрать трек из секций. Секция: dict(bars, chords, ...gains).

    Гейны слоёв: pad, arp, bass, bell, drum, motif, air (духовая). Ноль — слой выключен.
    `arp` управляется полями step (доля шага), pattern (индексы ступеней), oct (множитель).
    """
    pal = PALETTES[epoch]
    bar = _bar_dur(bpm)
    total_bars = sum(s["bars"] for s in sections)
    n = int(round(total_bars * bar * SR))
    buf = np.zeros((n, 2), dtype=np.float32)
    rng = np.random.default_rng(seed)
    motif = MOTIFS[epoch]

    t = 0.0
    for si, sec in enumerate(sections):
        chords = sec["chords"]
        g_pad = sec.get("pad", 0.55)
        g_arp = sec.get("arp", 0.0)
        g_bass = sec.get("bass", 0.0)
        g_bell = sec.get("bell", 0.0)
        g_drum = sec.get("drum", 0.0)
        g_motif = sec.get("motif", 0.0)
        g_air = sec.get("air", 0.0)
        step = sec.get("step", 0.5)
        pattern = sec.get("pattern", [0, 2, 1, 2])
        arp_oct = sec.get("oct", 2.0)
        drum_step = sec.get("drum_step", 1.0)

        for b in range(sec["bars"]):
            ch = chords[b % len(chords)]
            t0 = t + b * bar

            # ── пад / хор: держит аккорд такта с перекрытием в следующий (легато)
            if g_pad > 0:
                dur = bar * 1.35
                # Держащий слой — смычковые той же физмодели, что и щипок. Синусный пад
                # (`pad`) отсюда убран: его расстроенные голоса давали ровное биение,
                # то самое «вувувуву», по которому звук и опознавался как компьютерный.
                if pal["pad_kind"] == "choir":
                    l, r = choir(ch, dur, seed=int(rng.integers(1 << 30)))
                else:
                    l, r = bowed_chord(ch, dur, bright=pal.get("bow_bright", 0.4),
                                       seed=int(rng.integers(1 << 30)))
                env = np.ones(len(l), dtype=np.float32)
                a, d = int(SR * 0.35), int(SR * bar * 0.45)
                env[:a] = np.linspace(0, 1, a) ** 1.3
                env[-d:] = np.linspace(1, 0, d) ** 1.5
                place_stereo(buf, l * env, r * env, t0, gain=g_pad)

            # ── бас: корень аккорда щипком. Октаву вниз не уводим — там 33–65 Гц, которые
            # телефон не воспроизводит, зато они съедали запас громкости и давили гулом.
            if g_bass > 0:
                s = pluck(ch[0], bar * 0.95, damp=pal["pluck"]["damp"],
                          bright=0.30, body=0.42, seed=int(rng.integers(1 << 30)))
                place(buf, s, t0 + rng.uniform(0, 0.012), gain=g_bass * 0.8, pan=0.5)

            # ── арпеджио: щипок по ступеням аккорда, с гуманизацией тайминга и громкости
            if g_arp > 0:
                steps = int(round(bar / step))
                for k in range(steps):
                    deg = pattern[(b * steps + k) % len(pattern)]
                    f = ch[deg % len(ch)] * arp_oct
                    s = pluck(f, min(step * 3.2, 2.4), damp=pal["pluck"]["damp"],
                              bright=pal["pluck"]["bright"], body=pal["pluck"]["body"],
                              seed=int(rng.integers(1 << 30)))
                    accent = 1.0 if k % 4 == 0 else (0.72 if k % 2 == 0 else 0.58)
                    place(buf, s, t0 + k * step + rng.normal(0, 0.006),
                          gain=g_arp * accent * rng.uniform(0.9, 1.1),
                          pan=0.5 + 0.22 * math_sin(k))

            # ── колокол: удар на сильную долю такта
            if g_bell > 0 and b % max(1, sec.get("bell_every", 2)) == 0:
                s = bell(ch[0] * sec.get("bell_oct", 1.0), min(bar * 2.6, 7.0),
                         decay=pal["bell_decay"], seed=int(rng.integers(1 << 30)))
                place(buf, s, t0, gain=g_bell, pan=0.5 + rng.uniform(-0.08, 0.08))

            # ── барабан: маршевый пульс
            if g_drum > 0:
                hits = int(round(bar / drum_step))
                for k in range(hits):
                    # Барабан подняли по тону и убавили: на 54–70 Гц он бил в ту же полосу,
                    # что и пад, и вместе они давали удар «по нервам».
                    s = drum(min(drum_step * 1.6, 0.9), freq=pal["drum_freq"] * 1.45,
                             tight=9.0, snap=0.42, seed=int(rng.integers(1 << 30)))
                    place(buf, s, t0 + k * drum_step + rng.normal(0, 0.004),
                          gain=g_drum * 0.62 * (1.0 if k == 0 else 0.68), pan=0.5)

            # ── мотив главы: одна фраза на секцию, поверх первого такта
            if g_motif > 0 and b == 0:
                mt = 0.0
                for deg, dur_beats in motif:
                    f = ch[deg % len(ch)] * sec.get("motif_oct", 2.0)
                    d = dur_beats * 60.0 / bpm
                    if g_air > 0:
                        s = flute(f, d * 0.98, seed=int(rng.integers(1 << 30)))
                    else:
                        s = pluck(f, min(d * 1.8, 3.0), damp=pal["pluck"]["damp"],
                                  bright=pal["pluck"]["bright"] * 1.15,
                                  body=pal["pluck"]["body"], seed=int(rng.integers(1 << 30)))
                    place(buf, s, t0 + mt, gain=max(g_motif, g_air), pan=0.44)
                    mt += d

        t += sec["bars"] * bar

    ir = make_ir(**pal["ir"], seed=hash(epoch) % 9973)
    out = convolve_loop(buf / (np.max(np.abs(buf)) + 1e-9), ir, mix=pal["rev_mix"])
    return master(out)


def math_sin(k: int) -> float:
    """Детерминированное «покачивание» панорамы арпеджио (без импорта math в горячем цикле)."""
    return float(np.sin(k * 1.7))


# ─────────────────────────────────────────────────────────── аккордовые последовательности
# Прогрессии унаследованы от старых треков (в них уже заложена эпохальная окраска),
# секции B/A′ добавляют смену голосоведения и регистра.

C = chord

PROG = {
    # Рим — дорийский/минорный античный колорит
    "rome_tension":   [C("A2", "C3", "E3"), C("F2", "A2", "C3"), C("G2", "B2", "D3"), C("E2", "G2", "B2")],
    "rome_tension_b": [C("D3", "F3", "A3"), C("A2", "C3", "E3"), C("Bb2", "D3", "F3"), C("E2", "G2", "B2")],
    "rome_theme":     [C("D3", "F3", "A3"), C("Bb2", "D3", "F3"), C("F2", "A2", "C3"), C("C3", "E3", "G3")],
    "rome_theme_b":   [C("G2", "Bb2", "D3"), C("D3", "F3", "A3"), C("A2", "C3", "E3"), C("F2", "A2", "C3")],
    "rome_ceremony":  [C("C3", "E3", "G3"), C("G2", "B2", "D3"), C("A2", "C3", "E3"), C("F2", "A2", "C3")],
    "rome_romance":   [C("F2", "A2", "C3"), C("D3", "F3", "A3"), C("Bb2", "D3", "F3"), C("C3", "E3", "G3")],
    "rome_battle":    [C("D3", "F3", "A3"), C("C3", "E3", "G3"), C("Bb2", "D3", "F3"), C("A2", "C3", "E3")],

    # Тюдоры
    "tudor_court":    [C("G2", "B2", "D3"), C("D3", "F#3", "A3"), C("E3", "G3", "B3"), C("C3", "E3", "G3")],
    "tudor_court_b":  [C("C3", "E3", "G3"), C("G2", "B2", "D3"), C("A2", "C3", "E3"), C("D3", "F#3", "A3")],
    "tudor_romance":  [C("F2", "A2", "C3"), C("D3", "F3", "A3"), C("Bb2", "D3", "F3"), C("C3", "E3", "G3")],
    "tudor_lament":   [C("D3", "F3", "A3"), C("Bb2", "D3", "F3"), C("G2", "Bb2", "D3"), C("A2", "C#3", "E3")],
    "tudor_battle":   [C("E3", "G3", "B3"), C("C3", "E3", "G3"), C("D3", "F#3", "A3"), C("A2", "C3", "E3")],

    # Революция
    "revolution_tension":   [C("D3", "F3", "A3"), C("Bb2", "D3", "F3"), C("G2", "Bb2", "D3"), C("A2", "C#3", "E3")],
    "revolution_battle":    [C("A2", "C3", "E3"), C("F2", "A2", "C3"), C("C3", "E3", "G3"), C("G2", "B2", "D3")],
    "revolution_ceremony":  [C("C3", "E3", "G3"), C("G2", "B2", "D3"), C("A2", "C3", "E3"), C("F2", "A2", "C3")],
    "revolution_romance":   [C("F2", "A2", "C3"), C("D3", "F3", "A3"), C("Bb2", "D3", "F3"), C("C3", "E3", "G3")],

    # Империя
    "empire_tension":   [C("A2", "C3", "E3"), C("D3", "F3", "A3"), C("E2", "G#2", "B2"), C("F2", "A2", "C3")],
    "empire_battle":    [C("E3", "G3", "B3"), C("C3", "E3", "G3"), C("G2", "B2", "D3"), C("D3", "F#3", "A3")],
    "empire_ceremony":  [C("C3", "E3", "G3"), C("A2", "C3", "E3"), C("F2", "A2", "C3"), C("G2", "B2", "D3")],
    "empire_romance":   [C("Bb2", "D3", "F3"), C("G2", "Bb2", "D3"), C("Eb3", "G3", "Bb3"), C("F2", "A2", "C3")],

    # Борджиа
    "borgia_tension":   [C("A2", "C3", "E3"), C("D3", "F3", "A3"), C("E2", "G#2", "B2"), C("A2", "C3", "E3")],
    "borgia_battle":    [C("D3", "F3", "A3"), C("A2", "C#3", "E3"), C("G2", "Bb2", "D3"), C("A2", "C#3", "E3")],
    "borgia_ceremony":  [C("C3", "E3", "G3"), C("G2", "B2", "D3"), C("F2", "A2", "C3"), C("C3", "E3", "G3")],
    "borgia_romance":   [C("F2", "A2", "C3"), C("D3", "F3", "A3"), C("Bb2", "D3", "F3"), C("C3", "E3", "G3")],

    # Византия — фригийский
    "byzantium_tension":   [C("E3", "G3", "B3"), C("F2", "A2", "C3"), C("E2", "G2", "B2"), C("D3", "F3", "A3")],
    "byzantium_battle":    [C("E3", "G3", "B3"), C("C3", "E3", "G3"), C("G2", "B2", "D3"), C("D3", "F#3", "A3")],
    "byzantium_ceremony":  [C("C3", "E3", "G3"), C("A2", "C3", "E3"), C("F2", "A2", "C3"), C("G2", "B2", "D3")],
    "byzantium_romance":   [C("D3", "F3", "A3"), C("Bb2", "D3", "F3"), C("F2", "A2", "C3"), C("C3", "E3", "G3")],
}


# ─────────────────────────────────────────────────────────── формы настроений
# Каждая — A (изложение) → B (развитие с мотивом) → A′ (реприза плотнее) → кода (разрежение).


def form_tension(prog, prog_b=None, *, bell=0.0, air=0.0):
    b = prog_b or prog
    return [
        dict(bars=6, chords=prog, pad=0.60, bass=0.16, arp=0.10, step=2.0, pattern=[0, 2], oct=1.0,
             bell=bell * 0.7, bell_every=3),
        dict(bars=6, chords=b, pad=0.55, bass=0.20, arp=0.16, step=1.0, pattern=[0, 2, 1, 2], oct=2.0,
             motif=0.24, air=air, bell=bell, bell_every=2),
        dict(bars=6, chords=prog, pad=0.62, bass=0.22, arp=0.13, step=1.0, pattern=[2, 0, 1, 0], oct=2.0,
             bell=bell * 0.8, bell_every=2),
        dict(bars=4, chords=prog[:2], pad=0.50, bass=0.14, arp=0.08, step=2.0, pattern=[0, 2], oct=1.0,
             bell=bell * 0.5, bell_every=4),
    ]


def form_battle(prog, *, drum=0.5, bell=0.0):
    return [
        dict(bars=4, chords=prog, pad=0.34, bass=0.24, arp=0.22, step=0.5, pattern=[0, 1, 2, 1],
             oct=2.0, drum=drum * 0.7, drum_step=1.0),
        dict(bars=6, chords=prog, pad=0.36, bass=0.28, arp=0.30, step=0.25,
             pattern=[0, 1, 2, 1, 0, 2, 1, 2], oct=2.0, drum=drum, drum_step=0.5, motif=0.26),
        dict(bars=6, chords=prog[::-1], pad=0.32, bass=0.30, arp=0.32, step=0.25,
             pattern=[2, 1, 0, 1, 2, 0, 1, 0], oct=2.0, drum=drum, drum_step=0.5, bell=bell,
             bell_every=3),
        dict(bars=4, chords=prog, pad=0.40, bass=0.26, arp=0.24, step=0.5, pattern=[0, 2, 1, 2],
             oct=2.0, drum=drum * 0.8, drum_step=1.0),
    ]


def form_ceremony(prog, *, bell=0.3, drum=0.0, air=0.0):
    return [
        dict(bars=6, chords=prog, pad=0.58, bass=0.20, arp=0.20, step=1.0, pattern=[0, 2, 1, 2],
             oct=2.0, bell=bell, bell_every=2, drum=drum, drum_step=2.0),
        dict(bars=6, chords=prog, pad=0.54, bass=0.24, arp=0.28, step=0.5,
             pattern=[0, 2, 1, 2, 0, 1, 2, 1], oct=2.0, bell=bell, bell_every=2, motif=0.30,
             air=air, drum=drum, drum_step=1.0),
        dict(bars=6, chords=prog[1:] + prog[:1], pad=0.60, bass=0.26, arp=0.30, step=0.5,
             pattern=[2, 0, 1, 0, 2, 1, 0, 1], oct=2.0, bell=bell * 1.15, bell_every=1,
             drum=drum, drum_step=1.0),
        dict(bars=4, chords=prog[:2], pad=0.52, bass=0.18, arp=0.16, step=1.0, pattern=[0, 2],
             oct=2.0, bell=bell * 0.8, bell_every=2),
    ]


def form_romance(prog, *, bell=0.0, air=0.0):
    return [
        dict(bars=6, chords=prog, pad=0.62, bass=0.16, arp=0.16, step=1.0, pattern=[0, 1, 2, 1],
             oct=2.0),
        dict(bars=6, chords=prog, pad=0.58, bass=0.18, arp=0.22, step=0.5,
             pattern=[0, 1, 2, 1, 2, 1, 0, 1], oct=2.0, motif=0.26, air=air, bell=bell,
             bell_every=4),
        dict(bars=6, chords=prog[2:] + prog[:2], pad=0.64, bass=0.20, arp=0.20, step=1.0,
             pattern=[2, 1, 0, 1], oct=2.0, bell=bell * 0.7, bell_every=3),
        dict(bars=4, chords=prog[:2], pad=0.56, bass=0.14, arp=0.12, step=1.0, pattern=[0, 2],
             oct=2.0),
    ]


# ─────────────────────────────────────────────────────────── таблица треков

TRACKS: dict[str, dict] = {
    # ===== Рим (theme — главное меню и карта) =====
    "theme": dict(epoch="rome", bpm=68,
                  sections=form_ceremony(PROG["rome_theme"], bell=0.20, air=0.30)),
    "tension": dict(epoch="rome", bpm=64,
                    sections=form_tension(PROG["rome_tension"], PROG["rome_tension_b"], bell=0.16)),
    "ceremony": dict(epoch="rome", bpm=72,
                     sections=form_ceremony(PROG["rome_ceremony"], bell=0.26, drum=0.16)),
    "romance": dict(epoch="rome", bpm=60,
                    sections=form_romance(PROG["rome_romance"], air=0.28)),
    "battle": dict(epoch="rome", bpm=104,
                   sections=form_battle(PROG["rome_battle"], drum=0.52)),

    # ===== Тюдоры =====
    "tudor_court": dict(epoch="tudor", bpm=76,
                        sections=form_ceremony(PROG["tudor_court"], bell=0.14)),
    "tudor_romance": dict(epoch="tudor", bpm=62,
                          sections=form_romance(PROG["tudor_romance"], air=0.24)),
    "tudor_lament": dict(epoch="tudor", bpm=52,
                         sections=form_tension(PROG["tudor_lament"], bell=0.30)),
    "tudor_battle": dict(epoch="tudor", bpm=100,
                         sections=form_battle(PROG["tudor_battle"], drum=0.48)),

    # ===== Революция =====
    "revolution_tension": dict(epoch="revolution", bpm=66,
                               sections=form_tension(PROG["revolution_tension"])),
    "revolution_battle": dict(epoch="revolution", bpm=112,
                              sections=form_battle(PROG["revolution_battle"], drum=0.58)),
    "revolution_ceremony": dict(epoch="revolution", bpm=80,
                                sections=form_ceremony(PROG["revolution_ceremony"], bell=0.18,
                                                       drum=0.26)),
    "revolution_romance": dict(epoch="revolution", bpm=58,
                               sections=form_romance(PROG["revolution_romance"], air=0.26)),

    # ===== Империя =====
    "empire_tension": dict(epoch="empire", bpm=56,
                           sections=form_tension(PROG["empire_tension"], bell=0.28)),
    "empire_battle": dict(epoch="empire", bpm=98,
                          sections=form_battle(PROG["empire_battle"], drum=0.56, bell=0.20)),
    "empire_ceremony": dict(epoch="empire", bpm=66,
                            sections=form_ceremony(PROG["empire_ceremony"], bell=0.36)),
    "empire_romance": dict(epoch="empire", bpm=58,
                           sections=form_romance(PROG["empire_romance"], air=0.22)),

    # ===== Борджиа =====
    "borgia_tension": dict(epoch="borgia", bpm=70,
                           sections=form_tension(PROG["borgia_tension"])),
    "borgia_battle": dict(epoch="borgia", bpm=106,
                          sections=form_battle(PROG["borgia_battle"], drum=0.46)),
    "borgia_ceremony": dict(epoch="borgia", bpm=74,
                            sections=form_ceremony(PROG["borgia_ceremony"], bell=0.22)),
    "borgia_romance": dict(epoch="borgia", bpm=62,
                           sections=form_romance(PROG["borgia_romance"], air=0.24)),

    # ===== Византия =====
    "byzantium_tension": dict(epoch="byzantium", bpm=54,
                              sections=form_tension(PROG["byzantium_tension"], bell=0.26)),
    "byzantium_battle": dict(epoch="byzantium", bpm=96,
                             sections=form_battle(PROG["byzantium_battle"], drum=0.54, bell=0.18)),
    "byzantium_ceremony": dict(epoch="byzantium", bpm=60,
                               sections=form_ceremony(PROG["byzantium_ceremony"], bell=0.38)),
    "byzantium_romance": dict(epoch="byzantium", bpm=56,
                              sections=form_romance(PROG["byzantium_romance"], bell=0.14, air=0.22)),
}


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = None
    for a in sys.argv[1:]:
        if a.startswith("--only"):
            only = set(a.split("=", 1)[1].split(",")) if "=" in a else None
    root = Path(__file__).resolve().parent.parent
    out_dir = Path(args[0]) if args else root / "Content" / "audio_v2"
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, (name, spec) in enumerate(TRACKS.items()):
        if only and name not in only:
            continue
        x = compose(seed=1000 + i * 17, **spec)
        write_wav(out_dir / f"{name}.wav", x)
        print(f"  {name}.wav  {len(x)/SR:5.1f}s  {spec['epoch']}", flush=True)


if __name__ == "__main__":
    main()
