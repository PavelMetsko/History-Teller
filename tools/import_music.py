#!/usr/bin/env python3
"""Превратить готовый трек (например, из Suno) в бесшовный игровой луп.

Зачем нужен отдельный шаг: сервисы генерации отдают песню — со вступлением, развитием и
затуханием в конце. Движок же крутит трек по кругу без пауз, и «просто зациклить» песню
нельзя: на стыке слышен обрыв. Здесь из середины трека вырезается кусок нужной длины,
причём длина подбирается так, чтобы конец максимально походил на начало, и хвост
подмешивается в голову равномощным кроссфейдом — стык становится неслышным.

    python3 tools/import_music.py ~/Downloads/song.mp3 --as tension
    python3 tools/import_music.py song.mp3 --as theme --intro 12 --len 75 --dry-run
    python3 tools/import_music.py --list          какие имена треков ждёт игра

После записи WAV прогоняется обычная сборка аудио (нормализация −20 LUFS, AAC, loops.json),
поэтому результат сразу играбелен: python3 tools/build_audio.py --only <имя>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "Content" / "audio_v2"
SR = 44100


def track_names() -> list[str]:
    """Имена, которые уровни просят полем `music`."""
    names = {"theme"}
    for p in (ROOT / "Content").glob("*/levels/*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        if m := d.get("music"):
            names.add(m)
    return sorted(names)


def load(path: Path) -> np.ndarray:
    """Любой формат → float32 стерео 44.1 кГц через ffmpeg."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le",
                        "-acodec", "pcm_s16le", "-ar", str(SR), "-ac", "2", "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        sys.exit(f"ffmpeg не смог прочитать {path}: {r.stderr.decode()[-200:]}")
    return np.frombuffer(r.stdout, dtype="<i2").reshape(-1, 2).astype(np.float32) / 32768.0


def trim_silence(x: np.ndarray, thresh_db: float = -45.0) -> np.ndarray:
    env = np.max(np.abs(x), axis=1)
    live = np.nonzero(env > 10 ** (thresh_db / 20))[0]
    return x[live[0]:live[-1] + 1] if len(live) else x


def best_length(x: np.ndarray, start: int, want: int, search: int, win: int) -> tuple[int, float]:
    """Подобрать длину петли так, чтобы её конец был похож на начало.

    Считаем нормированную корреляцию окна в начале петли с окном-кандидатом в конце.
    Чем выше, тем незаметнее кроссфейд: музыка «возвращается в ту же точку такта».
    """
    head = x[start:start + win].mean(axis=1)
    head = head - head.mean()
    hn = np.linalg.norm(head) + 1e-9
    best, score = want, -2.0
    lo, hi = max(win * 2, want - search), want + search
    for length in range(lo, hi, max(1, SR // 100)):        # шаг 10 мс
        e = start + length
        if e + win >= len(x):
            break
        tail = x[e:e + win].mean(axis=1)
        tail = tail - tail.mean()
        s = float(np.dot(head, tail) / (hn * (np.linalg.norm(tail) + 1e-9)))
        if s > score:
            score, best = s, length
    return best, score


def make_loop(x: np.ndarray, intro: float, want: float, fade: float, search: float) -> tuple[np.ndarray, float]:
    start = int(intro * SR)
    if start + int((want + fade) * SR) >= len(x):
        start = max(0, len(x) - int((want + fade + 1) * SR))
    length, score = best_length(x, start, int(want * SR), int(search * SR), int(0.35 * SR))
    f = int(fade * SR)
    if start + length + f > len(x):
        f = max(0, len(x) - start - length)
    body = x[start:start + length].copy()
    if f > 0:
        tail = x[start + length:start + length + f]
        t = np.linspace(0, 1, f, dtype=np.float32)[:, None]
        # равномощный кроссфейд: сумма квадратов постоянна, громкость на стыке не проседает
        body[:f] = body[:f] * np.sqrt(t) + tail * np.sqrt(1 - t)
    return body, score


def seam_quality(x: np.ndarray) -> tuple[float, float]:
    """Скачок на стыке против типичного скачка между соседними отсчётами."""
    edge = float(np.abs(x[0] - x[-1]).max())
    typical = float(np.percentile(np.abs(np.diff(x[:, 0])), 99))
    return edge, typical


def write_wav(path: Path, x: np.ndarray) -> None:
    import wave
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", help="скачанный файл (mp3/wav/m4a)")
    ap.add_argument("--as", dest="name", help="имя трека в игре (см. --list)")
    ap.add_argument("--intro", type=float, default=10.0, help="сколько секунд вступления пропустить")
    ap.add_argument("--len", dest="length", type=float, default=70.0, help="желаемая длина петли, с")
    ap.add_argument("--search", type=float, default=6.0, help="в каких пределах подбирать длину, с")
    ap.add_argument("--fade", type=float, default=0.8, help="длина кроссфейда на стыке, с")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="только показать качество стыка")
    a = ap.parse_args()

    if a.list:
        have = {p.stem for p in RAW.glob("*.wav")}
        for n in track_names():
            print(f"  {n:22} {'есть' if n in have else '—'}")
        return
    if not a.source or not a.name:
        sys.exit("нужны файл и --as <имя трека>; список имён: --list")
    if a.name not in track_names():
        sys.exit(f"игра не знает трека «{a.name}». Доступные: {', '.join(track_names())}")

    x = trim_silence(load(Path(a.source)))
    print(f"исходник: {len(x)/SR:.1f} с")
    loop, score = make_loop(x, a.intro, a.length, a.fade, a.search)
    edge, typical = seam_quality(loop)
    print(f"петля: {len(loop)/SR:.1f} с | похожесть конца на начало {score:+.2f} "
          f"| скачок на стыке {edge:.4f} против типичного {typical:.4f}")
    # Щелчок на стыке лечит кроссфейд (смотрим на «скачок»); похожесть же говорит о другом —
    # попала ли петля в ту же долю такта. Низкая похожесть на ритмичном треке слышна как сбой.
    if edge > typical * 0.5:
        print("  ! слышимый обрыв на стыке — увеличь --fade")
    elif score < 0.2:
        print("  ! петля не попала в долю такта — подвигай --len на пару секунд")
    if a.dry_run:
        return

    RAW.mkdir(parents=True, exist_ok=True)
    write_wav(RAW / f"{a.name}.wav", loop)
    print(f"записано {RAW / (a.name + '.wav')}")
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_audio.py"), "--only", a.name], check=True)


if __name__ == "__main__":
    main()
