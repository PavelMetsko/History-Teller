#!/usr/bin/env python3
"""Сделать из сгенерированного трека бесшовную петлю.

Генераторы дают музыку с финалом — громкость в конце проваливается на 25–30 дБ, и при
зацикливании слышна яма. Здесь: находим последнюю точку, где трек ещё в полной громкости,
режем там, а хвост (последние N секунд после среза) заворачиваем кроссфейдом в начало,
чтобы стык был гладким по амплитуде и не на пустом месте.
"""
from __future__ import annotations
import sys, subprocess, numpy as np

SR = 44100

def decode(path: str) -> np.ndarray:
    raw = subprocess.run(["ffmpeg","-v","error","-i",path,"-f","f32le","-ac","2","-ar",str(SR),"-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def loopify(x: np.ndarray, fade_s: float = 3.0, drop_db: float = 6.0) -> np.ndarray:
    hop = SR // 10
    env = np.sqrt((x[:len(x)//hop*hop].reshape(-1, hop, 2) ** 2).mean(axis=(1, 2)))
    ref = np.percentile(env, 85)
    thr = ref * 10 ** (-drop_db / 20)
    # последний блок, где ещё громко — после него идёт финальное затухание
    last = int(np.max(np.nonzero(env >= thr)[0]))
    cut = (last + 1) * hop
    body = x[:cut]
    n = int(fade_s * SR)
    w = np.linspace(0, 1, n, dtype=np.float32)[:, None]
    # хвост после среза (затухание) подмешиваем под начало: начало нарастает, хвост угасает
    tail = x[cut:cut + n]
    if len(tail) < n:
        tail = np.vstack([tail, np.zeros((n - len(tail), 2), np.float32)])
    out = body.copy()
    out[:n] = body[:n] * w + tail * (1 - w)
    return out

def write_wav(path: str, x: np.ndarray) -> None:
    import wave
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    x = decode(src); y = loopify(x)
    write_wav(dst, y)
    k = SR
    a = np.sqrt((y[:k]**2).mean()); b = np.sqrt((y[-k:]**2).mean())
    print(f"{dst}: {len(x)/SR:.1f} → {len(y)/SR:.1f} с, стык {20*np.log10(a+1e-9):.1f} / {20*np.log10(b+1e-9):.1f} dB")
