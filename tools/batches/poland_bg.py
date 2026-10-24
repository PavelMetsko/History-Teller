#!/usr/bin/env python3
"""Фоны главы «Польша» через Nano Banana (gemini-2.5-flash-image), по стилю существующей сцены.

    source ~/.zshenv; /usr/bin/python3 tools/batches/poland_bg.py [name ...]
Исходники PNG → Art/source/poland_bg/<name>.png. Раздача по сценам — poland_bg_apply.py.
"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from genart import gen
from PIL import Image

REF = ROOT / "Content/art/scene_court_favour.webp"
STYLE = ("Using EXACTLY the art style of the reference image (flat 2D storybook illustration, warm muted palette, "
         "clean brown line work, soft cel shading, same rendering and colors), draw a NEW empty background scene, "
         "square 1:1, eye-level view, NO people, NO animals, NO text, NO letters. Leave the lower third open floor/ground "
         "so characters can stand there. Scene: ")
BG = {
    "sejm_hall": "the Senators' Hall of the Polish-Lithuanian Sejm in a royal castle: rows of wooden benches facing a raised "
                 "royal throne under a red canopy with a white crowned eagle, coats of arms on the coffered ceiling, tall windows.",
    "krakow_rynek": "the Main Market Square of medieval Kraków: the long arcaded Cloth Hall in the middle, the two unequal "
                    "Gothic brick towers of St. Mary's Basilica on the side, colorful burgher houses, cobblestones, daylight.",
    "wawel_courtyard": "the Renaissance arcaded courtyard of Wawel Royal Castle in Kraków: three storeys of light stone "
                       "arcades with slim columns, red tile roof, golden dome of a chapel visible above, sunny.",
    "polish_field": "a wide open battlefield on the Polish plain: green and yellow meadow, a line of birch trees, distant "
                    "forest, cloudy dramatic sky, abandoned lances and a torn red-and-white banner on the ground.",
    "gdansk_harbor": "the old harbor of Gdańsk on the Motława river: the huge medieval wooden Crane gate, Hanseatic brick "
                     "granaries, a moored sailing cog loaded with grain sacks, wooden quay in the foreground.",
    "manor_interior": "the main room of an old Polish nobleman's manor house (dwór): dark wooden beams, white-washed walls "
                      "with crossed sabres and a family coat of arms, a tiled stove, a long oak table with candles, a window "
                      "onto birch trees.",
    "warsaw_castle_square": "Castle Square in Warsaw: the red-brick Royal Castle with its clock tower, the tall Sigismund "
                            "Column with the bronze king holding a cross and sabre, old town houses, cobblestones, 19th century.",
    "polish_village": "a Polish countryside village: thatched wooden cottages, a small wooden church with onion-less shingle "
                      "roof, golden wheat fields, a stork nest on a pole, dirt road in the foreground.",
    "jasna_gora": "the fortified Jasna Góra monastery in Częstochowa on a hill: white baroque church with a very tall "
                  "slender tower, star-shaped brick bastion walls, snowy winter ground in front, grey sky.",
    "malbork": "the huge red-brick Gothic castle of Malbork of the Teutonic Order on the Nogat river: high walls, "
               "towers with steep roofs, a moat and wooden bridge in the foreground.",
    "vistula_bank": "the sandy bank of the wide Vistula river near old Warsaw: reeds, a fisherman's wooden boat pulled "
                    "ashore, nets drying on poles, the old town skyline far on the other bank, calm evening light.",
    "gniezno_cathedral": "inside the Romanesque-Gothic cathedral of Gniezno: stone pillars, a high altar with a silver "
                         "reliquary of St. Adalbert, candles, stained-glass windows, banners with a white eagle.",
    "wieliczka_mine": "an underground hall of the Wieliczka salt mine: walls and floor of grey-green rock salt, wooden "
                      "beams and ladders, a salt-carved altar, hanging lanterns, warm torch light.",
    "forest_camp": "a clearing in a dark Polish pine forest: a smoldering campfire, rifles leaning on a fallen log, "
                   "a rolled red-and-white flag, a dugout shelter, early morning mist.",
    "royal_chamber": "a Polish royal private chamber in the Wawel castle: a canopied bed, a carved writing desk with "
                     "letters and a quill, leather-covered walls with gold patterns, a portrait, tall window.",
}

if __name__ == "__main__":
    names = sys.argv[1:] or list(BG)
    out = ROOT / "Art/source/poland_bg"; out.mkdir(parents=True, exist_ok=True)
    ref = out / "_ref.png"
    Image.open(REF).convert("RGB").resize((768, 768)).save(ref)
    for n in names:
        p = out / f"{n}.png"
        if p.exists():
            print("skip", n); continue
        gen(ref, STYLE + BG[n], p)
        print("ok", n, Image.open(p).size)
