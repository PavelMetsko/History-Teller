#!/usr/bin/env python3
"""Оркестровый синтез с нуля. Ничего из старого движка не используется.

Принципы, ради которых написано заново:
- ни одного низкочастотного качания амплитуды и ни одной расстройки голосов —
  именно они давали синтетическое «вувувуву»;
- каждый инструмент — свой гармонический ряд, своя огибающая и своё вибрато,
  как у живого исполнителя: вибрато входит не сразу и не у всех;
- ансамбль строится из независимых голосов с разными фазами и микросдвигами по времени,
  а не из одного голоса, размноженного с расстройкой;
- зал — настоящая свёртка с импульсной характеристикой; петли сшиваются циклически.
"""
from __future__ import annotations

import math
import wave
import numpy as np

SR = 44100
_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def hz(name: str) -> float:
    """'A4' → 440, 'Bb2', 'F#3'."""
    step = _SEMI[name[0].upper()]
    i = 1
    while i < len(name) and name[i] in "#b":
        step += 1 if name[i] == "#" else -1
        i += 1
    return 440.0 * 2.0 ** ((step - 9) / 12.0 + int(name[i:]) - 4)


# ───────────────────────────────────────────── инструменты (моно, нормированы к 1)


def _env(n: int, atk: float, dec: float, sus: float, rel: float) -> np.ndarray:
    """ADSR по времени в секундах; релиз входит внутрь длительности."""
    t = np.arange(n) / SR
    dur = n / SR
    a = np.clip(t / max(atk, 1e-3), 0, 1) ** 1.4
    d = sus + (1 - sus) * np.exp(-np.maximum(t - atk, 0) / max(dec, 1e-3))
    r = np.clip((dur - t) / max(rel, 1e-3), 0, 1) ** 1.2
    return (a * d * r).astype(np.float32)


def _partials(freq: float, n: int, amps, *, vib_hz=0.0, vib_cents=0.0, vib_delay=0.0,
              rng=None) -> np.ndarray:
    """Сумма гармоник с общим (не расстроенным!) вибрато и случайными фазами."""
    t = np.arange(n, dtype=np.float64) / SR
    if vib_hz > 0:
        depth = (vib_cents / 1200.0) * np.clip((t - vib_delay) / 0.5, 0, 1)
        ratio = 2.0 ** (depth * np.sin(2 * np.pi * vib_hz * t))
        phase = 2 * np.pi * freq * np.cumsum(ratio) / SR
    else:
        phase = 2 * np.pi * freq * t
    out = np.zeros(n, dtype=np.float64)
    for h, a in enumerate(amps, start=1):
        if freq * h > 18000 or a <= 0:
            continue
        ph0 = rng.uniform(0, 2 * math.pi) if rng is not None else 0.0
        out += a * np.sin(h * phase + ph0)
    return out.astype(np.float32)


def violin(freq: float, dur: float, *, seed: int = 0, dyn: float = 1.0) -> np.ndarray:
    """Скрипка/альт: яркий ряд с медленным спадом, формант около 3 кГц, вибрато 5.8 Гц."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    amps = []
    for h in range(1, 40):
        f = freq * h
        a = 1.0 / h ** 0.95
        a *= 1.0 + 1.6 * math.exp(-0.5 * ((f - 3000) / 900) ** 2)   # формант корпуса
        a *= 1.0 + 0.5 * math.exp(-0.5 * ((f - 500) / 250) ** 2)
        a *= math.exp(-f / 16000)                                       # естественный спад верха
        amps.append(a * (0.85 + 0.3 * rng.random()))                    # неровность обертонов
    x = _partials(freq, n, amps, vib_hz=5.6 + rng.uniform(-0.3, 0.3), vib_cents=8,
                  vib_delay=0.4, rng=rng)
    x *= _env(n, 0.18, 0.4, 0.85, 0.35)
    # шорох канифоли: слабый шум только в верху, постоянный по уровню
    nz = rng.normal(0, 1, n).astype(np.float32)
    x += 0.02 * dyn * _bp(nz, 2500, 9000)
    return x / (np.max(np.abs(x)) + 1e-9)


def cello(freq: float, dur: float, *, seed: int = 0) -> np.ndarray:
    """Виолончель/контрабас: плотный низ, формант около 250 Гц и 1.2 кГц, вибрато медленнее."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    amps = []
    for h in range(1, 40):
        f = freq * h
        a = 1.0 / h ** 1.0
        a *= 1.0 + 1.0 * math.exp(-0.5 * ((f - 250) / 120) ** 2)
        a *= 1.0 + 0.8 * math.exp(-0.5 * ((f - 1200) / 500) ** 2)
        a *= math.exp(-f / 7000)
        amps.append(a * (0.85 + 0.3 * rng.random()))
    x = _partials(freq, n, amps, vib_hz=4.8 + rng.uniform(-0.3, 0.3), vib_cents=6,
                  vib_delay=0.5, rng=rng)
    x *= _env(n, 0.22, 0.5, 0.88, 0.4)
    nz = rng.normal(0, 1, n).astype(np.float32)
    x += 0.008 * _bp(nz, 1500, 5000)
    return x / (np.max(np.abs(x)) + 1e-9)


def flute(freq: float, dur: float, *, seed: int = 0) -> np.ndarray:
    """Флейта: почти чистый тон, чуть второй и третьей гармоники, дыхание, вибрато 5 Гц."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    amps = [1.0, 0.18, 0.09, 0.03, 0.015]
    x = _partials(freq, n, amps, vib_hz=5.0 + rng.uniform(-0.2, 0.2), vib_cents=10,
                  vib_delay=0.3, rng=rng)
    x *= _env(n, 0.09, 0.3, 0.9, 0.2)
    nz = rng.normal(0, 1, n).astype(np.float32)
    x += 0.05 * _bp(nz, freq * 1.5, 7000) * _env(n, 0.05, 0.3, 0.7, 0.2)
    return x / (np.max(np.abs(x)) + 1e-9)


def oboe(freq: float, dur: float, *, seed: int = 0) -> np.ndarray:
    """Гобой: носовой тембр — сильные средние гармоники и формант около 1.1 кГц."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    amps = []
    for h in range(1, 30):
        f = freq * h
        a = (1.0 if h % 2 else 0.75) / h ** 0.8
        a *= 1.0 + 2.0 * math.exp(-0.5 * ((f - 1100) / 300) ** 2)
        a *= math.exp(-f / 9000)
        amps.append(a)
    x = _partials(freq, n, amps, vib_hz=5.4, vib_cents=7, vib_delay=0.35, rng=rng)
    x *= _env(n, 0.07, 0.3, 0.9, 0.18)
    return x / (np.max(np.abs(x)) + 1e-9)


def horn(freq: float, dur: float, *, seed: int = 0) -> np.ndarray:
    """Валторна: тёплая медь, мягкая атака, спад обертонов, без вибрато."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    amps = [math.exp(-h / 4.0) * (1.0 + 0.6 * math.exp(-0.5 * ((freq * h - 700) / 300) ** 2))
            for h in range(1, 20)]
    x = _partials(freq, n, amps, rng=rng)
    x *= _env(n, 0.12, 0.6, 0.85, 0.3)
    return x / (np.max(np.abs(x)) + 1e-9)


def harp(freq: float, dur: float, *, seed: int = 0) -> np.ndarray:
    """Арфа: щипок — быстрый спад верхних гармоник, долгий основной тон, без вибрато."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float64) / SR
    out = np.zeros(n, dtype=np.float64)
    for h in range(1, 16):
        f = freq * h
        if f > 16000:
            break
        a = 1.0 / h ** 1.6
        tau = 1.8 / (h ** 0.9) * (300.0 / max(freq, 60.0)) ** 0.5   # низкие звенят дольше
        out += a * np.exp(-t / tau) * np.sin(2 * math.pi * f * t + rng.uniform(0, 6.28))
    out *= np.clip(t / 0.004, 0, 1)                                   # мгновенный щипок
    return (out / (np.max(np.abs(out)) + 1e-9)).astype(np.float32)


def timpani(freq: float, dur: float, *, seed: int = 0) -> np.ndarray:
    """Литавра: мембрана — негармонические моды с быстрым спадом верха и глубоким гулом."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float64) / SR
    out = np.zeros(n, dtype=np.float64)
    for ratio, a, tau in ((1.0, 1.0, 0.9), (1.5, 0.5, 0.5), (1.98, 0.35, 0.35),
                          (2.44, 0.2, 0.25), (2.9, 0.12, 0.18)):
        out += a * np.exp(-t / tau) * np.sin(2 * math.pi * freq * ratio * t + rng.uniform(0, 6.28))
    hit = rng.normal(0, 1, n) * np.exp(-t / 0.012)                    # удар колотушки
    out += 0.4 * _bp(hit.astype(np.float32), 200, 3000)
    return (out / (np.max(np.abs(out)) + 1e-9)).astype(np.float32)


def bell(freq: float, dur: float, *, seed: int = 0) -> np.ndarray:
    """Оркестровый колокол/трубчатые: негармонические партиалы с долгим звоном."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float64) / SR
    out = np.zeros(n, dtype=np.float64)
    for ratio, a, tau in ((0.5, 0.5, 2.5), (1.0, 1.0, 2.2), (1.19, 0.6, 1.5), (1.56, 0.5, 1.2),
                          (2.0, 0.6, 1.0), (2.51, 0.35, 0.7), (2.66, 0.25, 0.6), (3.01, 0.2, 0.5)):
        out += a * np.exp(-t / tau) * np.sin(2 * math.pi * freq * ratio * t + rng.uniform(0, 6.28))
    out *= np.clip(t / 0.003, 0, 1)
    return (out / (np.max(np.abs(out)) + 1e-9)).astype(np.float32)


# ───────────────────────────────────────────── фильтры, зал, сведение


def _bp(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    F = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = 1.0 / np.sqrt(1 + (lo / np.maximum(f, 1e-6)) ** 4) / np.sqrt(1 + (f / hi) ** 4)
    return np.fft.irfft(F * g, len(x)).astype(np.float32)


def hall_ir(rt60: float = 2.4, seed: int = 7) -> np.ndarray:
    """Импульсная характеристика зала: ранние отражения + экспоненциальный диффузный хвост,
    верх затухает быстрее низа — как в настоящем зале."""
    rng = np.random.default_rng(seed)
    n = int(rt60 * 1.3 * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2), dtype=np.float32)
    for ch in range(2):
        tail = rng.normal(0, 1, n) * np.exp(-6.91 * t / rt60)
        # частотно-зависимое затухание: сначала уходит верх
        F = np.fft.rfft(tail)
        f = np.fft.rfftfreq(n, 1 / SR)
        F *= np.exp(-f / 9000.0)
        tail = np.fft.irfft(F, n)
        for k in range(12):                                            # ранние отражения
            d = int(rng.uniform(0.008, 0.06) * SR)
            tail[d] += rng.uniform(0.15, 0.4) * (1 if rng.random() < 0.5 else -1)
        ir[:, ch] = tail
    ir[0, :] = 0.0
    ir[int(0.02 * SR), :] += 0.0
    return ir / (np.max(np.abs(ir)) + 1e-9)


def reverb_loop(x: np.ndarray, ir: np.ndarray, mix: float) -> np.ndarray:
    """Циклическая свёртка: хвост зала заворачивается в начало петли — шва нет."""
    n = len(x)
    wet = np.zeros_like(x)
    for ch in range(2):
        h = np.zeros(n, dtype=np.float32)
        m = min(n, len(ir))
        h[:m] = ir[:m, ch]
        wet[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch]) * np.fft.rfft(h), n)
    wet *= (np.max(np.abs(x)) + 1e-9) / (np.max(np.abs(wet)) + 1e-9)
    return ((1 - mix) * x + mix * wet).astype(np.float32)


def put(buf: np.ndarray, mono: np.ndarray, t0: float, gain: float, pan: float = 0.5) -> None:
    """Подмешать голос в стерео-буфер по кругу (для петель) с постоянной мощностью панорамы."""
    n = len(buf)
    idx = (np.arange(len(mono)) + int(t0 * SR)) % n
    np.add.at(buf[:, 0], idx, mono * gain * math.sqrt(1 - pan))
    np.add.at(buf[:, 1], idx, mono * gain * math.sqrt(pan))


def finish(x: np.ndarray, peak: float = 0.9) -> np.ndarray:
    """Мастер: убрать инфраниз ниже 30 Гц, мягкое ограничение, нормировка."""
    out = np.empty_like(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = 1.0 / np.sqrt(1 + (30.0 / np.maximum(f, 1e-6)) ** 6)
    for ch in range(2):
        out[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch]) * g, len(x))
    out = np.tanh(out * 1.05) / math.tanh(1.05)
    return (out * peak / (np.max(np.abs(out)) + 1e-9)).astype(np.float32)


def seal(x: np.ndarray, ms: float = 30.0) -> np.ndarray:
    """Кроссфейд конца в начало: линейная фильтрация мастера оставляет микрошов — сшиваем."""
    n = int(ms * SR / 1000)
    w = np.linspace(0, 1, n, dtype=np.float32)[:, None]
    out = x.copy()
    out[:n] = x[:n] * w + x[-n:] * (1 - w)
    return out[:-n]


def write(path, x: np.ndarray) -> None:
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
