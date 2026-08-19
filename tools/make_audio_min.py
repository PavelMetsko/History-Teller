#!/usr/bin/env python3
"""Минимальный звук игры: две оркестровые петли и пять эффектов.

Почему так мало: раньше было 25 музыкальных тем (по четыре настроения на главу) и 16 эффектов —
игрок за всю игру слышал часть из них по три раза, а один эффект вообще не был подключён.
Оставляем ровно то, что звучит постоянно.

Только акустические модели движка: смычковый ансамбль, флейта, арфа (щипок), колокол и зальная
реверберация. Аддитивный `pad` не используется намеренно — он и давал синтетический призвук.

Петли бесшовные: источники подмешиваются в буфер по кругу (`place` заворачивает хвост в начало),
поэтому стык не слышен и в плеере не нужен кроссфейд.

Usage: python3 tools/make_audio_min.py [--out Content/audio_v2]
"""
from __future__ import annotations

import argparse
import numpy as np
from pathlib import Path

import audio_engine as ae
from audio_engine import note, SR


def _seal_loop(x: np.ndarray, ms: float = 25.0) -> np.ndarray:
    """Сшить края петли коротким кроссфейдом.

    Источники подмешиваются по кругу, но мастер-цепь фильтрует буфер линейно (не циклически),
    и на стыке остаётся скачок амплитуды — на замере до 8 % от пика, это слышный щелчок.
    Заворачиваем конец в начало на 25 мс: шов пропадает, музыка не меняется.
    """
    n = int(ms * SR / 1000)
    if n * 2 >= len(x):
        return x
    w = np.linspace(0.0, 1.0, n, dtype=np.float32)[:, None]
    head = x[:n] * w + x[-n:] * (1.0 - w)
    out = x.copy()
    out[:n] = head
    return out[:-n]


def _music_master(x: np.ndarray) -> np.ndarray:
    """Мастер для музыки: мягче зарез низа и больше воздуха, чем в общей цепи.

    Общий `master` заточен под эффекты: он рубит ниже 58 Гц и снимает полку на 105 Гц, из-за чего
    контрабас и виолончель пропадали целиком, а трек звучал зажато в середине.
    """
    return ae.master(x, hp=38.0, boom_db=-1.0, mud_db=-2.5, air_db=6.0, peak=0.88)


def _hall(buf: np.ndarray, rt60: float = 2.6, mix: float = 0.26) -> np.ndarray:
    """Зал. convolve_loop сам работает со стерео-буфером и заворачивает хвост в начало петли."""
    return ae.convolve_loop(buf, ae.make_ir(rt60=rt60, predelay=0.022), mix=mix)


def theme() -> np.ndarray:
    """Главная тема: спокойная, ля минор, 68 ударов в минуту, 32 секунды.

    Струнный ансамбль держит гармонию, арфа рисует арпеджио, флейта ведёт мелодию.
    Гармония i–VI–III–VII с заходом на iv и V — обычный классический оборот, без модуляций,
    чтобы петля не «начиналась» на слух каждый круг.
    """
    bar = 4.0                      # 68 bpm, 4/4 → такт ≈ 3.53 с, округляем до 4 для ровной петли
    bars = 8
    total = bar * bars
    n = int(total * SR)
    buf = np.zeros((n, 2), dtype=np.float32)

    # аккорды: Am — F — C — G — Am — Dm — E — Am
    prog = [
        ("A2", ["A3", "C4", "E4"]), ("F2", ["A3", "C4", "F4"]),
        ("C3", ["G3", "C4", "E4"]), ("G2", ["G3", "B3", "D4"]),
        ("A2", ["A3", "C4", "E4"]), ("D3", ["A3", "D4", "F4"]),
        ("E3", ["G#3", "B3", "E4"]), ("A2", ["A3", "C4", "E4"]),
    ]
    for i, (bass, voices) in enumerate(prog):
        t0 = i * bar
        l, r = ae.bowed_chord([note(v) for v in voices], bar * 1.15, bright=0.34, seed=100 + i)
        ae.place_stereo(buf, l, r, t0, gain=0.30)
        low = ae.bowed(note(bass), bar * 1.1, bright=0.22, seed=200 + i)   # виолончель
        ae.place(buf, low, t0, gain=0.24, pan=0.5)
        # контрабас октавой ниже: без него у оркестра нет опоры, трек висит в середине
        ae.place(buf, ae.bowed(note(bass) / 2, bar * 1.15, bright=0.14, seed=250 + i), t0,
                 gain=0.20, pan=0.5)
        # первые скрипки: верхний голос аккорда октавой выше — присутствие в 1–3 кГц
        ae.place(buf, ae.bowed(note(voices[-1]) * 2, bar * 1.05, bright=0.78, seed=260 + i), t0,
                 gain=0.11, pan=0.62)
        # арфа в верхней октаве: даёт «воздух», которого смычковым не хватает
        ae.place(buf, ae.pluck(note(voices[-1]) * 4, 1.2, bright=0.72, body=0.25, seed=270 + i),
                 t0 + 2.0, gain=0.055, pan=0.66)
        # арфа: восходящее арпеджио по аккорду, восьмыми, вторая половина такта
        for k, v in enumerate(voices + [voices[0]]):
            f = note(v) * (2.0 if k == len(voices) else 1.0)
            ae.place(buf, ae.pluck(f, 1.5, bright=0.42, body=0.5, seed=300 + i * 8 + k),
                     t0 + 0.5 * k, gain=0.13, pan=0.38 + 0.06 * k)

    # флейта: две фразы по четыре такта, простая и певучая
    melody = [
        ("E5", 0.0, 1.5), ("C5", 1.6, 1.0), ("D5", 2.7, 1.2), ("E5", 4.1, 2.2),
        ("F5", 6.5, 1.3), ("E5", 8.0, 1.5), ("C5", 9.7, 1.0), ("A4", 11.0, 2.6),
        ("E5", 16.0, 1.5), ("F5", 17.6, 1.0), ("G5", 18.7, 1.4), ("E5", 20.3, 2.0),
        ("D5", 22.6, 1.4), ("C5", 24.2, 1.6), ("B4", 26.0, 1.2), ("A4", 27.4, 3.4),
    ]
    for k, (nm, t0, dur) in enumerate(melody):
        ae.place(buf, ae.flute(note(nm), dur, air=0.16, seed=400 + k), t0, gain=0.20, pan=0.52)

    return _seal_loop(_music_master(_hall(buf, rt60=2.8, mix=0.30)))


def tension() -> np.ndarray:
    """Тревожная тема: тот же оркестр, но ниже, темнее и без мелодии.

    Держится на длинных смычковых и редком пиццикато — под чтение и раздумье, не отвлекает.
    """
    bar = 4.0
    bars = 8
    n = int(bar * bars * SR)
    buf = np.zeros((n, 2), dtype=np.float32)

    prog = [
        ("D2", ["D3", "F3", "A3"]), ("D2", ["D3", "F3", "A3"]),
        ("Bb1", ["D3", "F3", "Bb3"]), ("Bb1", ["D3", "F3", "Bb3"]),
        ("G2", ["Bb2", "D3", "G3"]), ("G2", ["Bb2", "D3", "G3"]),
        ("A2", ["C#3", "E3", "A3"]), ("A2", ["C#3", "E3", "A3"]),
    ]
    for i, (bass, voices) in enumerate(prog):
        t0 = i * bar
        l, r = ae.bowed_chord([note(v) for v in voices], bar * 1.2, bright=0.24, seed=500 + i)
        ae.place_stereo(buf, l, r, t0, gain=0.28)
        ae.place(buf, ae.bowed(note(bass), bar * 1.15, bright=0.16, seed=600 + i), t0, gain=0.26, pan=0.5)
        ae.place(buf, ae.bowed(note(bass) / 2, bar * 1.2, bright=0.12, seed=650 + i), t0, gain=0.22, pan=0.5)
        ae.place(buf, ae.bowed(note(voices[-1]) * 2, bar * 1.1, bright=0.7, seed=660 + i), t0,
                 gain=0.075, pan=0.6)
        # пиццикато на сильную долю: пульс, но без ударных
        ae.place(buf, ae.pluck(note(voices[0]) / 2, 1.1, bright=0.3, body=0.6, seed=700 + i),
                 t0, gain=0.11, pan=0.44)

    # редкий колокол на границах фраз — «часы истории»
    for i, t0 in enumerate((0.0, 16.0)):
        ae.place(buf, ae.bell(note("D4"), 4.0, decay=1.6, seed=800 + i), t0, gain=0.07, pan=0.6)

    return _seal_loop(_music_master(_hall(buf, rt60=3.2, mix=0.34)))


# ─────────────────────────────────────────────────────────── эффекты


def sfx_place() -> np.ndarray:
    """Карточка легла на стол: короткий деревянный щипок без хвоста."""
    m = ae.pluck(note("A3"), 0.28, bright=0.25, body=0.7, seed=11)
    m *= np.linspace(1.0, 0.0, len(m)) ** 2.2
    buf = np.zeros((int(0.32 * SR), 2), dtype=np.float32)
    ae.place(buf, m, 0.0, gain=0.55, pan=0.5)
    return ae.master(buf, peak=0.62)


def sfx_select() -> np.ndarray:
    """Тап по интерфейсу: тише и выше, чтобы не спорить с музыкой."""
    m = ae.pluck(note("E5"), 0.16, bright=0.5, body=0.3, seed=12)
    m *= np.linspace(1.0, 0.0, len(m)) ** 2.6
    buf = np.zeros((int(0.2 * SR), 2), dtype=np.float32)
    ae.place(buf, m, 0.0, gain=0.4, pan=0.5)
    return ae.master(buf, peak=0.5)


def sfx_accent() -> np.ndarray:
    """Событие на доске (любое): струнный акцент с колоколом — заметно, но не крикливо."""
    buf = np.zeros((int(1.5 * SR), 2), dtype=np.float32)
    l, r = ae.bowed_chord(ae.chord("A3", "E4"), 1.1, bright=0.45, seed=13)
    ae.place_stereo(buf, l, r, 0.0, gain=0.42)
    ae.place(buf, ae.bell(note("A5"), 1.3, decay=0.8, seed=14), 0.0, gain=0.16, pan=0.5)
    return ae.master(_hall(buf, rt60=1.6, mix=0.22), peak=0.72)


def sfx_win() -> np.ndarray:
    """Уровень пройден: восходящая арфа по трезвучию плюс колокол."""
    buf = np.zeros((int(2.2 * SR), 2), dtype=np.float32)
    for k, nm in enumerate(("A3", "C4", "E4", "A4")):
        ae.place(buf, ae.pluck(note(nm), 1.6, bright=0.5, body=0.5, seed=20 + k),
                 0.09 * k, gain=0.30, pan=0.42 + 0.05 * k)
    l, r = ae.bowed_chord(ae.chord("A3", "C4", "E4", "A4"), 1.8, bright=0.4, seed=24)
    ae.place_stereo(buf, l, r, 0.12, gain=0.26)
    ae.place(buf, ae.bell(note("A5"), 2.0, decay=1.2, seed=25), 0.1, gain=0.18, pan=0.5)
    return ae.master(_hall(buf, rt60=2.2, mix=0.26), peak=0.84)


def sfx_error() -> np.ndarray:
    """Не сходится: глухой низкий щипок, без музыкального «плача»."""
    m = ae.pluck(note("D2"), 0.5, bright=0.12, body=0.8, seed=30)
    m *= np.linspace(1.0, 0.0, len(m)) ** 1.6
    buf = np.zeros((int(0.6 * SR), 2), dtype=np.float32)
    ae.place(buf, m, 0.0, gain=0.5, pan=0.5)
    return ae.master(buf, peak=0.6)


PIECES = {"theme": theme, "tension": tension,
          "place": sfx_place, "select": sfx_select, "accent": sfx_accent,
          "win": sfx_win, "error": sfx_error}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="Content/audio_v2")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    out = Path(__file__).resolve().parent.parent / a.out
    out.mkdir(parents=True, exist_ok=True)
    names = [x for x in a.only.split(",") if x] or list(PIECES)
    for name in names:
        x = PIECES[name]()
        ae.write_wav(out / f"{name}.wav", x)
        print(f"  {name}.wav  {len(x) / SR:.1f} с")


if __name__ == "__main__":
    main()
