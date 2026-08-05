#!/usr/bin/env python3
"""WAV (mono 44.1k Int16) → сжатый кодек. Идемпотентно: исходники .wav удаляются после конвертации.

Обе платформы — AAC в .m4a: AVAudioPlayer на iOS, SoundPool/MediaPlayer на Android
(AAC-LC в MP4 поддержан с API 16, у нас minSdk 26). Имя ресурса в res/raw ищется через
getIdentifier без расширения, поэтому код на Android менять не нужно.

Usage:
    python3 tools/optimize_audio.py [--dry-run]
"""
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

IOS_AUDIO = ROOT / "ios/Modules/GameContent/Resources/Audio"
ANDROID_RAW = ROOT / "android/app/src/main/res/raw"

BITRATE = "80k"   # моно-синтезатор, на 80 кбит/с артефактов не слышно


def convert(src: Path, ext: str, codec: list[str], dry: bool):
    dst = src.with_suffix(ext)
    r = subprocess.run(["ffmpeg", "-y", "-i", str(src), *codec, "-ac", "1", str(dst)],
                       capture_output=True)
    if r.returncode != 0:
        print(f"  ! {src.name}: {r.stderr.decode()[-200:]}")
        return None
    before, after = src.stat().st_size, dst.stat().st_size
    if dry:
        dst.unlink()
    else:
        src.unlink()
    return before, after


def run(dry: bool):
    targets = [
        ("iOS", IOS_AUDIO, ".m4a", ["-c:a", "aac", "-b:a", BITRATE]),
        ("Android", ANDROID_RAW, ".m4a", ["-c:a", "aac", "-b:a", BITRATE]),
    ]
    print("dry-run (ничего не записано)\n" if dry else "")
    for tag, d, ext, codec in targets:
        if not d.exists():
            continue
        b = a = n = 0
        for src in sorted(d.glob("*.wav")):
            res = convert(src, ext, codec, dry)
            if res:
                b += res[0]; a += res[1]; n += 1
        if n:
            print(f"{tag}: {n} файлов  {b/1e6:.1f} МБ → {a/1e6:.1f} МБ  (×{b/max(a,1):.2f})")
        else:
            print(f"{tag}: нечего конвертировать")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    run(ap.parse_args().dry_run)
