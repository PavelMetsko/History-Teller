#!/usr/bin/env python3
"""SFX на движке audio_engine: слоями (транзиент + тело + хвост), а не голыми бипами.

Старые звуки были одиночными осцилляторами (`select` — синус 1100→1300 Гц, `error` — меандр),
из-за чего резали ухо и звучали как будильник. Здесь у каждого звука есть материал:
дерево, пергамент, бронза, струна — плюс общий короткий «зал», чтобы SFX жили в том же
пространстве, что и музыка.

Имена файлов совпадают со старыми (`Audio.SFX` в iOS/Android менять не нужно).

Usage: python3 tools/make_sfx_v2.py [out_dir]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_engine import (SR, bell, convolve_loop, drum, fft_filter, make_ir, note, pluck,
                          soft_clip, write_wav)

RNG = np.random.default_rng(20250811)


def buf(dur: float) -> np.ndarray:
    return np.zeros((int(dur * SR), 2), dtype=np.float32)


def add(b: np.ndarray, mono: np.ndarray, t0: float, gain: float = 1.0, pan: float = 0.5) -> None:
    i0 = int(t0 * SR)
    n = min(len(mono), len(b) - i0)
    if n <= 0:
        return
    b[i0:i0 + n, 0] += mono[:n] * float(np.sqrt(1 - pan)) * gain
    b[i0:i0 + n, 1] += mono[:n] * float(np.sqrt(pan)) * gain


def noise_hit(dur: float, lo: float, hi: float, decay: float, seed: int = 0) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    x = np.random.default_rng(seed).normal(0, 1, n).astype(np.float32)
    x = fft_filter(x, SR, lo=lo, hi=hi)
    x *= np.exp(-t * decay) * np.minimum(1.0, t * 3000)
    return (x / (np.max(np.abs(x)) + 1e-9)).astype(np.float32)


def swish(dur: float, f_from: float, f_to: float, seed: int = 0) -> np.ndarray:
    """Шорох с движущейся полосой — «смахнуть фигуру со стола»."""
    n = int(dur * SR)
    x = np.random.default_rng(seed).normal(0, 1, n).astype(np.float32)
    parts = 8
    out = np.zeros(n, dtype=np.float32)
    edges = np.linspace(0, n, parts + 1).astype(int)
    for i in range(parts):
        f = f_from + (f_to - f_from) * (i / (parts - 1))
        seg = np.zeros(n, dtype=np.float32)
        seg[edges[i]:edges[i + 1]] = x[edges[i]:edges[i + 1]]
        out += fft_filter(seg, SR, lo=f * 0.7, hi=f * 1.6)
    t = np.arange(n, dtype=np.float32) / SR
    out *= np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.4
    return (out / (np.max(np.abs(out)) + 1e-9)).astype(np.float32)


def finish(b: np.ndarray, *, room: float = 0.16, rt60: float = 0.9, peak: float = 0.72,
           fade: float = 0.008) -> np.ndarray:
    """Общий хвост-помещение + мягкий лимит + защита от щелчка в конце."""
    ir = make_ir(rt60=rt60, damping=0.6, predelay=0.006, seed=3)
    pad_n = int(rt60 * SR)
    ext = np.vstack([b, np.zeros((pad_n, 2), dtype=np.float32)])
    out = convolve_loop(ext, ir, mix=room)
    # Удары (place, kill) сидели в тех же 60–120 Гц, что и музыка, и складывались с ней в гул.
    for ch in range(2):
        out[:, ch] = fft_filter(out[:, ch], SR, lo=75.0)
    out = soft_clip(out, 1.05)
    out = out * (peak / (np.max(np.abs(out)) + 1e-9))

    # обрезать хвост тише −60 dBFS: иначе половина файла — тишина реверба
    env = np.max(np.abs(out), axis=1)
    live = np.nonzero(env > 10 ** (-60 / 20) * peak)[0]
    end = min(len(out), (live[-1] if len(live) else len(out)) + int(0.02 * SR))
    out = out[:end]
    k = min(int(fade * SR), len(out))
    out[-k:] *= np.linspace(1, 0, k)[:, None]
    return out.astype(np.float32)


# ─────────────────────────────────────────────────────────── звуки


def s_select() -> np.ndarray:
    """Тап по карточке: сухой деревянный тик. Самый частый звук — должен быть тихим и мягким."""
    b = buf(0.10)
    add(b, noise_hit(0.035, 900, 3600, 90, seed=1), 0.0, 0.42)
    add(b, pluck(note("A5"), 0.09, damp=0.986, bright=0.30, body=0.2, seed=2), 0.001, 0.16)
    return finish(b, room=0.10, rt60=0.5, peak=0.42)


def s_place() -> np.ndarray:
    """Фигура опускается на доску: стук дерева о камень + короткое тело."""
    b = buf(0.22)
    add(b, noise_hit(0.05, 300, 2600, 55, seed=3), 0.0, 0.55)
    add(b, drum(0.18, freq=150.0, tight=26.0, snap=0.12, seed=4), 0.0, 0.5)
    add(b, pluck(note("D3"), 0.20, damp=0.988, bright=0.22, body=0.45, seed=5), 0.004, 0.2)
    return finish(b, room=0.14, rt60=0.7, peak=0.62)


def s_remove() -> np.ndarray:
    """Снять фигуру: короткий шорох вверх, будто смахнули."""
    b = buf(0.20)
    add(b, swish(0.14, 700, 2800, seed=6), 0.0, 0.42, pan=0.42)
    add(b, noise_hit(0.03, 400, 1800, 80, seed=7), 0.0, 0.2)
    return finish(b, room=0.12, rt60=0.6, peak=0.46)


def s_error() -> np.ndarray:
    """Запрет: приглушённая малая секунда на низкой струне. Без меандра — не «бип ошибки»."""
    b = buf(0.45)
    add(b, pluck(note("F2"), 0.42, damp=0.9905, bright=0.16, body=0.5, seed=8), 0.0, 0.55, pan=0.44)
    add(b, pluck(note("Gb2"), 0.40, damp=0.9900, bright=0.14, body=0.5, seed=9), 0.012, 0.45, pan=0.56)
    add(b, noise_hit(0.04, 200, 1200, 70, seed=10), 0.0, 0.18)
    return finish(b, room=0.18, rt60=0.9, peak=0.58)


def s_ally() -> np.ndarray:
    """Союз: тёплая квинта на двух струнах, чуть вразбежку — как рукопожатие."""
    b = buf(0.75)
    add(b, pluck(note("G3"), 0.7, damp=0.9955, bright=0.42, body=0.4, seed=11), 0.0, 0.5, pan=0.4)
    add(b, pluck(note("D4"), 0.7, damp=0.9958, bright=0.46, body=0.4, seed=12), 0.028, 0.44, pan=0.6)
    add(b, pluck(note("G4"), 0.6, damp=0.9950, bright=0.5, body=0.3, seed=13), 0.055, 0.2, pan=0.5)
    return finish(b, room=0.22, rt60=1.2, peak=0.6)


def s_conspire() -> np.ndarray:
    """Заговор: низкий шёпот-свелл и приглушённый щипок. Ничего яркого — это шёпот."""
    b = buf(0.7)
    n = int(0.5 * SR)
    t = np.arange(n, dtype=np.float32) / SR
    whisper = fft_filter(RNG.normal(0, 1, n).astype(np.float32), SR, lo=380, hi=2200)
    whisper *= np.sin(np.pi * t / 0.5) ** 2
    add(b, whisper / (np.max(np.abs(whisper)) + 1e-9), 0.0, 0.34, pan=0.38)
    add(b, pluck(note("D2"), 0.6, damp=0.9925, bright=0.12, body=0.55, seed=14), 0.02, 0.42, pan=0.58)
    add(b, pluck(note("A2"), 0.5, damp=0.9915, bright=0.14, body=0.5, seed=15), 0.11, 0.24, pan=0.5)
    return finish(b, room=0.24, rt60=1.1, peak=0.5)


def s_love() -> np.ndarray:
    """Любовь: арфовое арпеджио вверх, мягкое."""
    b = buf(1.0)
    for i, nm in enumerate(("F3", "A3", "C4", "F4")):
        add(b, pluck(note(nm), 0.9 - i * 0.1, damp=0.9968, bright=0.34 + i * 0.04, body=0.4,
                     seed=20 + i), i * 0.055, 0.42 - i * 0.05, pan=0.42 + i * 0.05)
    return finish(b, room=0.26, rt60=1.4, peak=0.58)


def s_envy() -> np.ndarray:
    """Зависть: тритон с расстройкой — биения дают ощущение «что-то не так»."""
    b = buf(0.7)
    add(b, pluck(note("B2"), 0.65, damp=0.9930, bright=0.3, body=0.4, seed=16), 0.0, 0.46, pan=0.4)
    add(b, pluck(note("F3") * 1.006, 0.65, damp=0.9928, bright=0.34, body=0.4, seed=17), 0.018,
        0.42, pan=0.6)
    return finish(b, room=0.2, rt60=1.0, peak=0.54)


def s_crown() -> np.ndarray:
    """Корона: восходящее трезвучие на колоколах + шиммер."""
    b = buf(1.4)
    for i, nm in enumerate(("C4", "E4", "G4")):
        add(b, bell(note(nm), 1.3 - i * 0.15, decay=1.1 + i * 0.2, strike=0.4, seed=30 + i),
            i * 0.085, 0.42 - i * 0.04, pan=0.5 + (i - 1) * 0.12)
    add(b, bell(note("C5"), 1.0, decay=1.6, strike=0.25, seed=34), 0.26, 0.2)
    return finish(b, room=0.3, rt60=1.8, peak=0.62)


def s_kill() -> np.ndarray:
    """Смерть: короткий металлический удар клинка + низкое тело. Без крови в звуке."""
    b = buf(0.6)
    metal = noise_hit(0.25, 1800, 9000, 26, seed=40)
    metal += 0.5 * bell(note("A5"), 0.25, decay=0.28, strike=0.6, seed=41)[:len(metal)]
    add(b, metal / (np.max(np.abs(metal)) + 1e-9), 0.0, 0.4, pan=0.46)
    add(b, drum(0.4, freq=72.0, tight=11.0, snap=0.3, seed=42), 0.006, 0.62)
    add(b, pluck(note("D2"), 0.5, damp=0.9905, bright=0.1, body=0.6, seed=43), 0.01, 0.26)
    return finish(b, room=0.2, rt60=1.1, peak=0.72)


def s_win() -> np.ndarray:
    """Победа уровня: короткая фанфара — струны, колокол, свелл. 2 с, чтобы не мешать переходу."""
    b = buf(2.4)
    for i, nm in enumerate(("C3", "G3", "C4", "E4", "G4")):
        add(b, pluck(note(nm), 2.0 - i * 0.15, damp=0.9962, bright=0.4 + i * 0.03, body=0.42,
                     seed=50 + i), i * 0.07, 0.34 - i * 0.03, pan=0.38 + i * 0.06)
    add(b, bell(note("C5"), 2.2, decay=1.9, strike=0.35, seed=56), 0.34, 0.3)
    add(b, bell(note("G4"), 1.8, decay=2.2, strike=0.2, seed=57), 0.5, 0.18, pan=0.6)
    add(b, drum(0.6, freq=64.0, tight=8.0, snap=0.2, seed=58), 0.0, 0.3)
    return finish(b, room=0.32, rt60=2.0, peak=0.78)


def s_clash() -> np.ndarray:
    """Битва/стояние: два удара стали друг о друга — металл без низкого «тела» смерти."""
    b = buf(0.7)
    for i, (t0, seed) in enumerate(((0.0, 60), (0.13, 61))):
        metal = noise_hit(0.22, 2200, 9500, 30, seed=seed)
        metal += 0.45 * bell(note("E6") * (1.0 + i * 0.03), 0.22, decay=0.22, strike=0.7, seed=seed + 5)[:len(metal)]
        add(b, metal / (np.max(np.abs(metal)) + 1e-9), t0, 0.5 - i * 0.1, pan=0.4 + i * 0.2)
    add(b, drum(0.25, freq=95.0, tight=18.0, snap=0.2, seed=62), 0.13, 0.28)
    return finish(b, room=0.2, rt60=1.0, peak=0.66)


def s_coin() -> np.ndarray:
    """Подкуп: две монеты звякнули о стол — короткие яркие колокольчики."""
    b = buf(0.6)
    add(b, bell(note("E6"), 0.4, decay=0.35, strike=0.8, seed=70), 0.0, 0.42, pan=0.42)
    add(b, bell(note("B6"), 0.35, decay=0.3, strike=0.8, seed=71), 0.07, 0.34, pan=0.58)
    add(b, bell(note("G6"), 0.3, decay=0.28, strike=0.7, seed=72), 0.15, 0.22, pan=0.5)
    add(b, noise_hit(0.03, 3000, 9000, 120, seed=73), 0.0, 0.16)
    return finish(b, room=0.14, rt60=0.7, peak=0.5)


def s_gavel() -> np.ndarray:
    """Суд/обвинение: два сухих удара дерева о дерево + низкая струна приговора."""
    b = buf(0.7)
    for i, t0 in enumerate((0.0, 0.16)):
        add(b, noise_hit(0.05, 250, 2000, 60, seed=80 + i), t0, 0.5)
        add(b, drum(0.14, freq=180.0, tight=30.0, snap=0.15, seed=82 + i), t0, 0.4)
    add(b, pluck(note("A2"), 0.5, damp=0.9915, bright=0.16, body=0.5, seed=84), 0.2, 0.36)
    return finish(b, room=0.18, rt60=0.9, peak=0.58)


def s_drum() -> np.ndarray:
    """Поход/сила/знамя: два удара войскового барабана с трещоткой."""
    b = buf(0.8)
    add(b, drum(0.35, freq=70.0, tight=9.0, snap=0.35, seed=90), 0.0, 0.62)
    add(b, drum(0.35, freq=70.0, tight=9.0, snap=0.35, seed=91), 0.21, 0.5)
    add(b, noise_hit(0.12, 500, 4000, 40, seed=92), 0.21, 0.22)
    add(b, noise_hit(0.08, 500, 4000, 60, seed=93), 0.42, 0.14)
    return finish(b, room=0.22, rt60=1.1, peak=0.62)


def s_flee() -> np.ndarray:
    """Уход/бегство: длинный шорох вниз, будто ушли за дверь."""
    b = buf(0.5)
    add(b, swish(0.36, 2600, 500, seed=95), 0.0, 0.46, pan=0.6)
    add(b, noise_hit(0.05, 200, 1200, 70, seed=96), 0.3, 0.16, pan=0.4)
    return finish(b, room=0.16, rt60=0.8, peak=0.46)


SFX = {
    "select": s_select, "place": s_place, "remove": s_remove, "error": s_error,
    "ally": s_ally, "conspire": s_conspire, "love": s_love, "envy": s_envy,
    "crown": s_crown, "kill": s_kill, "win": s_win,
    "clash": s_clash, "coin": s_coin, "gavel": s_gavel, "drum": s_drum, "flee": s_flee,
}


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "Content" / "audio_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, fn in SFX.items():
        x = fn()
        write_wav(out_dir / f"{name}.wav", x)
        print(f"  {name}.wav  {len(x)/SR:.2f}s  peak {np.max(np.abs(x)):.2f}")


if __name__ == "__main__":
    main()
