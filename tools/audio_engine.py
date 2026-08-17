#!/usr/bin/env python3
"""Синтез-движок для музыки и SFX: стерео 44.1 кГц, физмоделируемые тембры, свёрточный реверб.

Заменяет синусный генератор из make_music.py / make_tudor_music.py. Ключевые отличия:
  * щипок — Karplus–Strong (лютня/кифара/арфа), а не sin(2πft)·exp(-t);
  * пад — многоголосный, с расстройкой и спектральной огибающей (движение «фильтра»);
  * колокол/барабан — инегармонические партиалы и модель мембраны;
  * реверб — свёртка с синтезированной IR, у которой ВЧ гаснут быстрее НЧ;
  * луп бесшовный по построению: события пишутся по модулю длины, реверб — ЦИКЛИЧЕСКАЯ свёртка.

Всё векторизовано на numpy (scipy не нужен). Единица времени — секунды, буферы — float32 (N, 2).
"""
from __future__ import annotations

import math
import numpy as np

SR = 44100


# ─────────────────────────────────────────────────────────── ноты

_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note(name: str) -> float:
    """'A3' / 'Bb2' / 'F#4' → частота в Гц (A4 = 440)."""
    step = _SEMI[name[0].upper()]
    i = 1
    while i < len(name) and name[i] in "#bs":
        step += 1 if name[i] in "#s" else -1
        i += 1
    octave = int(name[i:])
    return 440.0 * (2.0 ** ((step - 9) / 12.0 + (octave - 4)))


def chord(*names: str) -> list[float]:
    return [note(n) for n in names]


# ─────────────────────────────────────────────────────────── примитивы фильтрации


def _one_pole_lp(x: np.ndarray, a: float) -> np.ndarray:
    """Однополюсный ФНЧ (рекурсия по короткому массиву — используется только на возбуждении)."""
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = acc * a + x[i] * (1.0 - a)
        y[i] = acc
    return y


def fft_filter(x: np.ndarray, sr: int, lo: float | None = None, hi: float | None = None,
               tilt_db: float = 0.0) -> np.ndarray:
    """Полосовая фильтрация в частотной области + опциональный наклон спектра (dB на декаду)."""
    n = len(x)
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    gain = np.ones_like(freqs)
    if lo:
        gain *= 1.0 / np.sqrt(1.0 + (lo / np.maximum(freqs, 1e-6)) ** 4)
    if hi:
        gain *= 1.0 / np.sqrt(1.0 + (freqs / hi) ** 4)
    if tilt_db:
        gain *= 10.0 ** (tilt_db * np.log10(np.maximum(freqs, 20.0) / 1000.0) / 20.0)
    return np.fft.irfft(spec * gain, n).astype(np.float32)


# ─────────────────────────────────────────────────────────── тембры (моно, float32)


def pluck(freq: float, dur: float, *, sr: int = SR, damp: float = 0.9955,
          bright: float = 0.5, body: float = 0.35, seed: int = 0) -> np.ndarray:
    """Щипковая струна (Karplus–Strong). bright — яркость медиатора, body — резонанс корпуса.

    Рекурсия y[n] = damp·½(y[n-L] + y[n-L-1]) считается блоками по L отсчётов: внутри блока
    все зависимости лежат в предыдущем блоке, поэтому шаг векторизуется.
    """
    L = max(2, int(round(sr / freq)))
    n = int(dur * sr)
    rng = np.random.default_rng(seed)
    exc = rng.uniform(-1.0, 1.0, L).astype(np.float32)
    exc = _one_pole_lp(exc, 1.0 - min(0.95, max(0.05, bright)))
    exc *= np.linspace(1.0, 0.3, L)          # медиатор гасит хвост возбуждения
    exc -= exc.mean()

    total = n + 2 * L
    y = np.zeros(total, dtype=np.float32)
    y[:L] = exc
    for k in range(1, total // L):
        s, e = k * L, min((k + 1) * L, total)
        prev = y[s - L:e - L]
        prevm1 = y[s - L - 1:e - L - 1] if s - L - 1 >= 0 else np.concatenate(([0.0], y[:e - L - 1]))
        y[s:e] = damp * 0.5 * (prev + prevm1[:len(prev)])
    y = y[:n]

    if body > 0:                              # резонанс деки: короткая гребёнка + подчёркнутый низ
        d = int(sr * 0.011)
        y[d:] += body * y[:-d] * 0.5
        y = fft_filter(y, sr, lo=freq * 0.5, hi=9000.0)
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def bowed(freq: float, dur: float, *, sr: int = SR, damp: float = 0.9988, drive: float = 0.010,
          bright: float = 0.4, seed: int = 0) -> np.ndarray:
    """Тянущаяся струна: та же модель, что у щипка, но смычок подпитывает её всё время.

    Зачем: пад из расстроенных синусов давал ровные биения на постоянной частоте — то самое
    «вувувуву», которое слышно как синтезатор. Здесь звук рождается из шума в петле задержки,
    поэтому призвуки нерегулярные, как у настоящей струны, и тембр совпадает со щипком.
    """
    L = max(2, int(round(sr / freq)))
    n = int(dur * sr)
    rng = np.random.default_rng(seed)
    total = n + 2 * L

    # Шум смычка держим широким: если резать его по кратности основному тону, у низких нот
    # весь верх пропадает и трек уезжает в середину (замер: 90 % энергии в 250 Гц–2 кГц, «в нос»).
    bow = rng.normal(0, 1, total).astype(np.float32)
    bow = fft_filter(bow, sr, lo=freq * 0.8, hi=1200 + 4800 * bright)
    press = 0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(0.11, 0.19) * np.arange(total) / sr
                               + rng.uniform(0, 6.28))          # неровность нажима — живость
    bow *= drive * press

    # Веса петли: ровное 0.5/0.5 — сильный ФНЧ, за пару витков он срезает всё выше пары кГц.
    # Смещение в сторону текущего отсчёта оставляет струне верх и «канифоль».
    w = 0.72
    y = np.zeros(total, dtype=np.float32)
    y[:L] = bow[:L] * 20.0
    for k in range(1, total // L):
        s, e = k * L, min((k + 1) * L, total)
        prev = y[s - L:e - L]
        prevm1 = y[s - L - 1:e - L - 1] if s - L - 1 >= 0 else np.concatenate(([0.0], y[:e - L - 1]))
        y[s:e] = damp * (w * prev + (1.0 - w) * prevm1[:len(prev)]) + bow[s:e]
    y = y[:n]

    t = np.arange(n, dtype=np.float32) / sr
    atk = np.clip(t / 0.28, 0, 1) ** 1.5                        # смычок входит мягко
    rel = np.clip((dur - t) / 0.45, 0, 1) ** 1.2
    y *= atk * rel
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def bowed_chord(freqs: list[float], dur: float, *, sr: int = SR, spread: float = 0.035,
                bright: float = 0.4, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Аккорд смычковых: голоса вступают вразнобой и слегка разной высоты — как живой ансамбль.

    Расстройка задаётся случайно на голос (±4 цента), а не фиксированной сеткой: именно ровная
    сетка расстройки и порождала механическое биение.
    """
    n = int(dur * sr)
    rng = np.random.default_rng(seed)
    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(freqs):
        cents = rng.uniform(-4.0, 4.0)
        delay = int(rng.uniform(0, spread) * sr)
        v = bowed(f * 2.0 ** (cents / 1200.0), max(0.2, dur - delay / sr),
                  bright=bright, seed=int(rng.integers(1 << 30)))
        pan = 0.5 + 0.34 * (i - (len(freqs) - 1) / 2.0) / max(1.0, (len(freqs) - 1) / 2.0)
        m = min(len(v), n - delay)
        left[delay:delay + m] += v[:m] * math.sqrt(1.0 - pan)
        right[delay:delay + m] += v[:m] * math.sqrt(pan)
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-9)
    return (left / peak).astype(np.float32), (right / peak).astype(np.float32)


def pad(freqs: list[float], dur: float, *, sr: int = SR, harmonics: int = 9,
        detune: float = 6.0, voices: int = 3, open_from: float = 0.35, open_to: float = 1.0,
        breath: float = 0.12, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Хоральный/струнный пад: расстроенные голоса + спектральная огибающая (эффект открытия фильтра).

    Возвращает (L, R): голоса панорамируются, фазы рандомны — отсюда стереоширина без эффектов.
    """
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    rng = np.random.default_rng(seed)
    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)

    # медленное «открытие» тембра: верхние гармоники въезжают позже
    openness = open_from + (open_to - open_from) * (0.5 - 0.5 * np.cos(np.pi * np.minimum(t / dur, 1.0)))
    vib = 1.0 + 0.0025 * np.sin(2 * np.pi * 4.7 * t + rng.uniform(0, 6.28))

    for vi in range(voices):
        cents = detune * (vi - (voices - 1) / 2.0)
        ratio = 2.0 ** (cents / 1200.0)
        panl = 0.5 + 0.42 * (vi - (voices - 1) / 2.0) / max(1, (voices - 1) / 2.0)
        gl, gr = math.sqrt(1.0 - panl), math.sqrt(panl)
        for f in freqs:
            for h in range(1, harmonics + 1):
                amp = 1.0 / (h ** 1.7)
                # Аккорды взяты в низком регистре (C2–C3), и основной тон падал прямо в 60–120 Гц,
                # где пад и наливал гул. Гасим всё, что ниже 140 Гц: тепло держат обертоны.
                amp *= min(1.0, (f * ratio * h / 140.0) ** 1.4)
                if h > 1:
                    amp *= np.clip(openness * harmonics / h - 0.2, 0.0, 1.0)
                ph = rng.uniform(0, 2 * np.pi)
                s = (amp * np.sin(2 * np.pi * f * ratio * h * t * vib + ph)).astype(np.float32)
                left += s * gl
                right += s * gr

    if breath > 0:                            # дыхание/смычок: узкополосный шум по контуру пада
        nz = rng.normal(0, 1, n).astype(np.float32)
        nz = fft_filter(nz, sr, lo=freqs[0] * 1.5, hi=4200.0)
        nz *= breath * (0.6 + 0.4 * openness)
        left += nz
        right += np.roll(nz, 137)             # декорреляция → ширина

    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-9)
    return (left / peak).astype(np.float32), (right / peak).astype(np.float32)


def bell(freq: float, dur: float, *, sr: int = SR, decay: float = 1.0,
         strike: float = 0.5, seed: int = 0) -> np.ndarray:
    """Колокол: инегармонические партиалы, у каждого свой спад + шумовой удар языка."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    partials = [(0.5, 0.30, 0.55), (1.0, 1.00, 0.75), (1.19, 0.45, 1.0), (1.56, 0.35, 1.4),
                (2.0, 0.55, 1.1), (2.61, 0.22, 2.0), (3.42, 0.16, 2.6), (4.51, 0.10, 3.4),
                (5.43, 0.07, 4.2)]
    rng = np.random.default_rng(seed)
    out = np.zeros(n, dtype=np.float32)
    for mult, amp, rate in partials:
        env = np.exp(-t * rate / max(decay, 1e-3))
        out += amp * env * np.sin(2 * np.pi * freq * mult * t + rng.uniform(0, 6.28))
    if strike > 0:
        k = int(sr * 0.03)
        nz = rng.normal(0, 1, k).astype(np.float32) * np.exp(-np.arange(k) / (k * 0.25))
        out[:k] += strike * fft_filter(nz, sr, lo=freq * 2, hi=7000.0)
    out *= np.minimum(1.0, t * 500)           # снять щелчок на атаке
    return (out / (np.max(np.abs(out)) + 1e-9)).astype(np.float32)


def drum(dur: float, *, sr: int = SR, freq: float = 62.0, tight: float = 8.0,
         snap: float = 0.35, seed: int = 0) -> np.ndarray:
    """Маршевый/церемониальный барабан: шумовой транзиент + мембрана с питч-огибающей."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    rng = np.random.default_rng(seed)
    pitch = freq * (1.0 + 2.2 * np.exp(-t * 45.0))
    phase = 2 * np.pi * np.cumsum(pitch) / sr
    body = np.sin(phase) * np.exp(-t * tight)
    body += 0.35 * np.sin(phase * 1.59) * np.exp(-t * tight * 2.2)   # обертон мембраны
    nz = rng.normal(0, 1, n).astype(np.float32) * np.exp(-t * 55.0)
    nz = fft_filter(nz, sr, lo=250.0, hi=6500.0)
    out = body + snap * nz
    out *= np.minimum(1.0, t * 1200)
    return (out / (np.max(np.abs(out)) + 1e-9)).astype(np.float32)


def flute(freq: float, dur: float, *, sr: int = SR, air: float = 0.22, seed: int = 0) -> np.ndarray:
    """Духовая (авлос/най/сиринкс): мягкие нечётные гармоники + шум дыхания."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    rng = np.random.default_rng(seed)
    vib = 1.0 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t / 0.4, 0, 1)
    out = np.zeros(n, dtype=np.float32)
    for h, a in ((1, 1.0), (2, 0.22), (3, 0.3), (4, 0.08), (5, 0.1)):
        out += a * np.sin(2 * np.pi * freq * h * t * vib + rng.uniform(0, 6.28))
    nz = fft_filter(rng.normal(0, 1, n).astype(np.float32), sr, lo=freq * 1.2, hi=8000.0)
    out += air * nz
    atk, rel = int(sr * 0.09), int(sr * 0.18)
    env = np.ones(n, dtype=np.float32)
    env[:atk] = np.linspace(0, 1, atk) ** 1.4
    env[-rel:] *= np.linspace(1, 0, rel) ** 1.6
    out *= env
    return (out / (np.max(np.abs(out)) + 1e-9)).astype(np.float32)


def choir(freqs: list[float], dur: float, *, sr: int = SR, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Голосовой ансамбль: формантная окраска смычковых (для сакральных тем).

    Раньше строился на синусном паде и звучал так же механически, как он.
    """
    l, r = bowed_chord(freqs, dur, sr=sr, spread=0.06, bright=0.55, seed=seed)
    # форманты «а/о» — два резонанса
    out = []
    for ch in (l, r):
        spec = np.fft.rfft(ch)
        fr = np.fft.rfftfreq(len(ch), 1.0 / sr)
        g = np.ones_like(fr)
        for fc, q, boost in ((720.0, 90.0, 2.2), (1180.0, 130.0, 1.7), (2600.0, 400.0, 0.7)):
            g += boost * np.exp(-0.5 * ((fr - fc) / q) ** 2)
        g /= 1.0 + 0.9 * np.clip((fr - 3200.0) / 3200.0, 0, 3)
        out.append(np.fft.irfft(spec * g, len(ch)).astype(np.float32))
    peak = max(np.max(np.abs(out[0])), np.max(np.abs(out[1])), 1e-9)
    return (out[0] / peak).astype(np.float32), (out[1] / peak).astype(np.float32)


# ─────────────────────────────────────────────────────────── реверб


def make_ir(*, sr: int = SR, rt60: float = 2.2, predelay: float = 0.018,
            damping: float = 0.55, width: float = 1.0, seed: int = 7) -> np.ndarray:
    """Синтезированная стерео-IR зала: ранние отражения + диффузный хвост с ВЧ-затуханием."""
    n = int(rt60 * sr)
    t = np.arange(n, dtype=np.float32) / sr
    rng = np.random.default_rng(seed)
    ir = np.zeros((n, 2), dtype=np.float32)

    for ch in range(2):
        nz = rng.normal(0, 1, n).astype(np.float32)
        # три полосы с разным RT60: ВЧ гаснут быстрее — так звучит настоящее помещение.
        # Низу удлинять хвост нельзя: он смазывается в сплошной гул (было rt60 × 1.25).
        low = fft_filter(nz, sr, hi=500.0) * np.exp(-6.9 * t / rt60)
        mid = fft_filter(nz, sr, lo=500.0, hi=3000.0) * np.exp(-6.9 * t / rt60)
        high = fft_filter(nz, sr, lo=3000.0) * np.exp(-6.9 * t / (rt60 * (1.0 - 0.55 * damping)))
        tail = low * 0.65 + mid * 0.9 + high * 0.55
        tail *= np.clip(t / 0.03, 0, 1)       # плавный вход диффузии
        ir[:, ch] = tail

    ir[:, 1] = np.roll(ir[:, 1], int(sr * 0.0011 * width))   # микро-сдвиг → ширина

    for tap, g in ((0.011, 0.5), (0.019, -0.38), (0.031, 0.3), (0.043, -0.22), (0.057, 0.16)):
        i = int((predelay + tap) * sr)
        if i < n:
            ir[i, 0] += g
            ir[min(i + int(sr * 0.0013), n - 1), 1] += g * 0.85

    d = int(predelay * sr)
    ir = np.vstack([np.zeros((d, 2), dtype=np.float32), ir])
    ir[0, :] += 1.0                            # прямой сигнал
    return ir / np.max(np.abs(ir))


def convolve_loop(x: np.ndarray, ir: np.ndarray, mix: float = 0.3) -> np.ndarray:
    """ЦИКЛИЧЕСКАЯ свёртка стерео-буфера с IR: хвост реверба заворачивается в начало лупа.

    Именно это делает луп бесшовным — на стыке нет обрыва реверберационного хвоста.
    """
    n = len(x)
    wet = np.zeros_like(x)
    for ch in range(2):
        h = np.zeros(n, dtype=np.float32)
        m = min(n, len(ir))
        h[:m] = ir[:m, ch]
        wet[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch]) * np.fft.rfft(h), n)
    wet /= np.max(np.abs(wet)) + 1e-9
    wet *= np.max(np.abs(x)) + 1e-9
    return ((1.0 - mix) * x + mix * wet).astype(np.float32)


# ─────────────────────────────────────────────────────────── микширование


def place(buf: np.ndarray, mono: np.ndarray, t0: float, *, sr: int = SR,
          gain: float = 1.0, pan: float = 0.5) -> None:
    """Подмешать моно-источник в стерео-буфер со сдвигом t0, ПО КРУГУ (хвост уходит в начало лупа)."""
    n = len(buf)
    i0 = int(t0 * sr) % n
    idx = (np.arange(len(mono)) + i0) % n
    gl, gr = math.sqrt(1.0 - pan) * gain, math.sqrt(pan) * gain
    np.add.at(buf[:, 0], idx, mono * gl)
    np.add.at(buf[:, 1], idx, mono * gr)


def place_stereo(buf: np.ndarray, l: np.ndarray, r: np.ndarray, t0: float, *,
                 sr: int = SR, gain: float = 1.0) -> None:
    n = len(buf)
    i0 = int(t0 * sr) % n
    idx = (np.arange(len(l)) + i0) % n
    np.add.at(buf[:, 0], idx, l * gain)
    np.add.at(buf[:, 1], idx, r * gain)


def soft_clip(x: np.ndarray, drive: float = 1.15) -> np.ndarray:
    return np.tanh(x * drive).astype(np.float32) / math.tanh(drive)


def master(x: np.ndarray, *, sr: int = SR, hp: float = 58.0, air_db: float = 1.5,
           mud_db: float = -3.0, boom_db: float = -3.5, peak: float = 0.89) -> np.ndarray:
    """Мастер-цепь: срезать подвал, придавить бубнёж, добавить воздух, мягко ограничить.

    Первая версия резала только ниже 32 Гц, и в полосе 60–120 Гц оставалось до 38 % всей
    энергии трека — на телефоне это читалось как давящий гул. Телефонный динамик ниже ~70 Гц
    всё равно ничего не воспроизводит, а в наушниках этот низ бил по ушам, поэтому режем
    круто и дополнительно снимаем полку 70–140 Гц.
    """
    out = np.empty_like(x)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    g = 1.0 / np.sqrt(1.0 + (hp / np.maximum(f, 1e-6)) ** 8)
    g *= 10 ** (boom_db * np.exp(-0.5 * ((f - 105.0) / 55.0) ** 2) / 20.0)   # бубнёж
    g *= 10 ** (mud_db * np.exp(-0.5 * ((f - 260.0) / 170.0) ** 2) / 20.0)   # мутность
    g *= 10 ** (air_db * np.clip((f - 6000.0) / 6000.0, 0, 1) / 20.0)        # воздух
    for ch in range(2):
        out[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch]) * g, len(x))
    out = soft_clip(out, 1.1)
    return (out * (peak / (np.max(np.abs(out)) + 1e-9))).astype(np.float32)


def write_wav(path, x: np.ndarray, sr: int = SR) -> None:
    import wave
    data = np.clip(x, -1.0, 1.0)
    pcm = (data * 32767.0).astype("<i2")
    with wave.open(str(path), "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
