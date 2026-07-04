#!/usr/bin/env python3
"""Фоновые лупы для глав Революция / Империя / Борджиа (по 4 настроения).

Движок тот же, что в make_tudor_music.py (пад с кроссфейдом аккордов + щипковое арпеджио,
+ опц. колокол/барабан). Сигнатура эпохи: Революция — марш с барабаном; Империя — русские
колокола и глубокий минор; Борджиа — придворная лютня (яркий щипок).

Usage: python3 tools/make_epoch_music.py [out_dir]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_tudor_music import render  # переиспользуем движок и рендер

# ---- ноты (низкий регистр, Гц) ----
N = {"C2":65.41,"D2":73.42,"E2":82.41,"F2":87.31,"G2":98.00,"A2":110.00,"B2":123.47,
     "Bb2":116.54,"Ab2":103.83,"Db3":138.59,"Eb3":155.56,"Gb2":92.50,"Fs2":92.50,
     "C3":130.81,"D3":146.83,"E3":164.81,"F3":174.61,"G3":196.00,"A3":220.00,"B3":246.94,
     "Bb3":233.08,"Cs3":138.59,"Fs3":185.00}
def ch(*names): return [N[n] for n in names]

TRACKS = {
 # ===== РЕВОЛЮЦИЯ: марш и барабаны, имперский пафос =====
 "revolution_tension": dict(  # Dm–Bb–Gm–A, тревожный марш дред
   chords=[ch("D3","F3","A3"),ch("Bb2","D3","F3"),ch("G2","Bb2","D3"),ch("A2","Db3","E3")],
   chord_dur=4.0, step_dur=1.0, pattern=[0,2,1,2], octave=1.0, decay=3.0, bright=0.15,
   pad_gain=0.55, arp_gain=0.20, bell=None, drum=dict(period=1.0, freq=55.0, gain=0.22)),
 "revolution_battle": dict(  # Am–F–C–G, гонит вперёд, барабанный пульс
   chords=[ch("A2","C3","E3"),ch("F2","A2","C3"),ch("C3","E3","G3"),ch("G2","B2","D3")],
   chord_dur=2.0, step_dur=0.25, pattern=[0,1,2,1,0,2,1,2], octave=2.0, decay=9.0, bright=0.5,
   pad_gain=0.40, arp_gain=0.30, bell=None, drum=dict(period=0.5, freq=60.0, gain=0.5)),
 "revolution_ceremony": dict(  # C–G–Am–F, парадная коронация Наполеона
   chords=[ch("C3","E3","G3"),ch("G2","B2","D3"),ch("A2","C3","E3"),ch("F2","A2","C3")],
   chord_dur=4.0, step_dur=0.5, pattern=[0,2,1,2,0,1,2,1], octave=2.0, decay=6.0, bright=0.4,
   pad_gain=0.50, arp_gain=0.32, bell=None),
 "revolution_romance": dict(  # F–Dm–Bb–C, тёплая (Жозефина)
   chords=[ch("F2","A2","C3"),ch("D3","F3","A3"),ch("Bb2","D3","F3"),ch("C3","E3","G3")],
   chord_dur=4.0, step_dur=1.0, pattern=[0,1,2,1], octave=2.0, decay=4.0, bright=0.25,
   pad_gain=0.58, arp_gain=0.26, bell=None),

 # ===== ИМПЕРИЯ: русские колокола, глубокий минор, хоральность =====
 "empire_tension": dict(  # Am–Dm–E–F, мрачно, редкий низкий колокол (опричнина)
   chords=[ch("A2","C3","E3"),ch("D3","F3","A3"),ch("E2","B2","E3"),ch("F2","A2","C3")],
   chord_dur=5.0, step_dur=2.5, pattern=[0,2], octave=1.0, decay=3.0, bright=0.12,
   pad_gain=0.55, arp_gain=0.20, bell=dict(period=5.0, freq=82.41, gain=0.26)),
 "empire_battle": dict(  # Em–C–G–D, тяжёлый марш + барабан (Полтава/Казань)
   chords=[ch("E3","G3","B3"),ch("C3","E3","G3"),ch("G3","B3","D3"),ch("D3","Fs3","A3")],
   chord_dur=2.0, step_dur=0.25, pattern=[0,1,2,1,0,2,1,2], octave=1.0, decay=8.0, bright=0.42,
   pad_gain=0.44, arp_gain=0.28, bell=None, drum=dict(period=0.5, freq=58.0, gain=0.52)),
 "empire_ceremony": dict(  # C–Am–F–G, венчание на царство, БОЛЬШОЙ колокол
   chords=[ch("C3","E3","G3"),ch("A2","C3","E3"),ch("F2","A2","C3"),ch("G2","B2","D3")],
   chord_dur=4.0, step_dur=0.5, pattern=[0,2,1,2,0,1,2,1], octave=2.0, decay=6.0, bright=0.32,
   pad_gain=0.55, arp_gain=0.30, bell=dict(period=4.0, freq=98.00, gain=0.34)),
 "empire_romance": dict(  # Bb–Gm–Eb–F, тёплая (Екатерина/Потёмкин)
   chords=[ch("Bb2","D3","F3"),ch("G2","Bb2","D3"),ch("Eb3","G3","Bb3"),ch("F2","A2","C3")],
   chord_dur=4.0, step_dur=1.0, pattern=[0,1,2,1], octave=2.0, decay=4.0, bright=0.22,
   pad_gain=0.58, arp_gain=0.24, bell=None),

 # ===== БОРДЖИА: придворная лютня, ренессанс, изящно-зловеще =====
 "borgia_tension": dict(  # Am–Dm–E–Am, тёмный придворный минор, мягкая лютня (яд, интрига)
   chords=[ch("A2","C3","E3"),ch("D3","F3","A3"),ch("E2","B2","E3"),ch("A2","C3","E3")],
   chord_dur=4.0, step_dur=0.5, pattern=[0,2,1,2], octave=2.0, decay=6.5, bright=0.35,
   pad_gain=0.50, arp_gain=0.30, bell=None),
 "borgia_battle": dict(  # Dm–A–Gm–A, походы Чезаре, лёгкий барабан
   chords=[ch("D3","F3","A3"),ch("A2","Db3","E3"),ch("G2","Bb2","D3"),ch("A2","Db3","E3")],
   chord_dur=2.0, step_dur=0.25, pattern=[0,1,2,1,0,2,1,2], octave=2.0, decay=9.0, bright=0.48,
   pad_gain=0.42, arp_gain=0.30, bell=None, drum=dict(period=0.5, freq=62.0, gain=0.44)),
 "borgia_ceremony": dict(  # C–G–F–C, папское величие, яркая лютня
   chords=[ch("C3","E3","G3"),ch("G2","B2","D3"),ch("F2","A2","C3"),ch("C3","E3","G3")],
   chord_dur=4.0, step_dur=0.5, pattern=[0,2,1,2,0,1,2,1], octave=2.0, decay=6.5, bright=0.45,
   pad_gain=0.50, arp_gain=0.34, bell=None),
 "borgia_romance": dict(  # F–Dm–Bb–C, тёплый консорт
   chords=[ch("F2","A2","C3"),ch("D3","F3","A3"),ch("Bb2","D3","F3"),ch("C3","E3","G3")],
   chord_dur=4.0, step_dur=1.0, pattern=[0,1,2,1], octave=2.0, decay=4.0, bright=0.28,
   pad_gain=0.58, arp_gain=0.26, bell=None),

 # ===== ВИЗАНТИЯ: православная модальность (фригийский), дрон, колокола =====
 "byzantium_tension": dict(  # Em–F–Em–Dm, фригийский сумрак, низкий колокол
   chords=[ch("E3","G3","B3"),ch("F2","A2","C3"),ch("E2","B2","E3"),ch("D3","F3","A3")],
   chord_dur=5.0, step_dur=2.5, pattern=[0,2], octave=1.0, decay=3.0, bright=0.14,
   pad_gain=0.56, arp_gain=0.18, bell=dict(period=5.0, freq=82.41, gain=0.24)),
 "byzantium_battle": dict(  # Em–C–G–D, тяжёлый марш + барабан
   chords=[ch("E3","G3","B3"),ch("C3","E3","G3"),ch("G3","B3","D3"),ch("D3","Fs3","A3")],
   chord_dur=2.0, step_dur=0.25, pattern=[0,1,2,1,0,2,1,2], octave=1.0, decay=8.0, bright=0.4,
   pad_gain=0.44, arp_gain=0.28, bell=None, drum=dict(period=0.5, freq=58.0, gain=0.5)),
 "byzantium_ceremony": dict(  # C–Am–F–G, сакральное величие Св. Софии, БОЛЬШОЙ колокол
   chords=[ch("C3","E3","G3"),ch("A2","C3","E3"),ch("F2","A2","C3"),ch("G2","B2","D3")],
   chord_dur=4.0, step_dur=0.5, pattern=[0,2,1,2,0,1,2,1], octave=2.0, decay=6.0, bright=0.30,
   pad_gain=0.56, arp_gain=0.28, bell=dict(period=4.0, freq=98.00, gain=0.36)),
 "byzantium_romance": dict(  # Dm–Bb–F–C, тёплая, с тёплым отзвуком колокола (Феодора)
   chords=[ch("D3","F3","A3"),ch("Bb2","D3","F3"),ch("F2","A2","C3"),ch("C3","E3","G3")],
   chord_dur=4.0, step_dur=1.0, pattern=[0,1,2,1], octave=2.0, decay=4.0, bright=0.24,
   pad_gain=0.58, arp_gain=0.24, bell=dict(period=8.0, freq=146.83, gain=0.14)),
}

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        root / "ios/Modules/GameContent/Resources/Audio"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, cfg in TRACKS.items():
        render(cfg, out_dir / f"{name}.wav")
