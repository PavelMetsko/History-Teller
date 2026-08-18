#!/usr/bin/env python3
"""Сборка аудио: WAV из генераторов → нормализация громкости → AAC в Content/audio.

Зачем нормализация: раньше `theme` была −16.2 LUFS, а музыка глав −23…−24 — при входе в главу
звук проваливался на 8 дБ. Теперь вся музыка приводится к −20 LUFS (EBU R128, двухпроходный
loudnorm), true peak −1.5 dBTP. SFX по громкости выставлены вручную при синтезе (тап тише,
победа громче), поэтому им loudnorm не нужен — он бы сравнял их и сломал баланс.

Usage:
    python3 tools/build_audio.py [--render] [--only name1,name2] [--src DIR] [--dst DIR]
        --render   сначала пересинтезировать WAV (make_music_v2 + make_sfx_v2)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Content" / "audio_v2"
DST = ROOT / "Content" / "audio"

MUSIC_LUFS = -20.0        # фон: тише диалогов и SFX, но одинаково во всех главах
MUSIC_TP = -1.5
MUSIC_BITRATE = "80k"     # стерео LC-AAC; материал тональный, артефактов не слышно
SFX_BITRATE = "96k"

SFX_NAMES = {"place", "remove", "select", "ally", "conspire", "love", "kill", "crown", "envy",
             "win", "error", "clash", "coin", "gavel", "drum", "flee"}


def measure(path: Path) -> dict:
    """Первый проход loudnorm — снять реальные I/TP/LRA файла."""
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af",
         f"loudnorm=I={MUSIC_LUFS}:TP={MUSIC_TP}:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1]
    return json.loads(tail)


def encode_music(src: Path, dst: Path) -> None:
    m = measure(src)
    af = (f"loudnorm=I={MUSIC_LUFS}:TP={MUSIC_TP}:LRA=11"
          f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
          f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
          f":offset={m['target_offset']}:linear=true:print_format=summary")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
                    "-af", af, "-ar", "44100", "-ac", "2", "-c:a", "aac", "-b:a", MUSIC_BITRATE,
                    str(dst)], check=True)


def loop_meta(src_wav: Path, dst_m4a: Path) -> dict:
    """Точка склейки лупа: сколько отсчётов priming добавил AAC-кодер и какова истинная длина.

    iOS этого не требует — AVAudioFile сам применяет edit list из MP4. Android декодирует
    через MediaCodec «как есть», поэтому без обрезки на каждом витке лупа слышен щелчок.
    """
    import wave
    with wave.open(str(src_wav)) as w:
        frames, sr, chans = w.getnframes(), w.getframerate(), w.getnchannels()

    # сырых отсчётов у декодера = AAC-пакетов × 1024; ffmpeg сам срезает priming, поэтому
    # разница между сырой длиной и его выдачей и есть искомый priming.
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-count_packets",
                        "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0",
                        str(dst_m4a)], capture_output=True, text=True)
    raw = int(r.stdout.strip()) * 1024
    dec = subprocess.run(["ffmpeg", "-v", "error", "-i", str(dst_m4a), "-f", "s16le", "-"],
                         capture_output=True)
    decoded = len(dec.stdout) // (2 * chans)
    return {"skip": max(0, raw - decoded), "frames": frames, "sampleRate": sr}


def encode_sfx(src: Path, dst: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
                    "-ar", "44100", "-ac", "2", "-c:a", "aac", "-b:a", SFX_BITRATE, str(dst)],
                   check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--src", default=str(SRC))
    ap.add_argument("--dst", default=str(DST))
    a = ap.parse_args()
    src, dst = Path(a.src), Path(a.dst)
    only = set(x for x in a.only.split(",") if x)

    if a.render:
        for script in ("make_music_v2.py", "make_sfx_v2.py"):
            subprocess.run([sys.executable, str(ROOT / "tools" / script), str(src)], check=True)

    dst.mkdir(parents=True, exist_ok=True)
    wavs = sorted(src.glob("*.wav"))
    if not wavs:
        sys.exit(f"нет WAV в {src} — сначала запусти с --render")

    loops_path = dst / "loops.json"
    loops = json.loads(loops_path.read_text()) if loops_path.exists() else {}

    for w in wavs:
        if only and w.stem not in only:
            continue
        out = dst / f"{w.stem}.m4a"
        if w.stem in SFX_NAMES:
            encode_sfx(w, out)
        else:
            encode_music(w, out)
            loops[w.stem] = loop_meta(w, out)
        print(f"  {out.name:26} {out.stat().st_size/1024:7.0f} KB")

    loops_path.write_text(json.dumps(dict(sorted(loops.items())), indent=1) + "\n")
    print(f"  loops.json  ({len(loops)} треков)")


if __name__ == "__main__":
    main()
