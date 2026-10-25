#!/usr/bin/env python3
"""Фоны главы «США» через Nano Banana — по стилю существующей сцены, тот же рецепт, что poland_bg.py.

    source ~/.zshenv; /usr/bin/python3 tools/batches/usa_bg.py [name ...]
Исходники PNG → Art/source/usa_bg/<name>.png. Раздача по сценам — usa_bg_apply.py.
"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(pathlib.Path(__file__).parent))
from genart import gen
from poland_bg import STYLE, REF
from PIL import Image

BG = {
    "congress_hall": "the Assembly Room of Independence Hall in Philadelphia, 18th century: rows of tables with green cloth, "
                     "Windsor chairs, a raised president's desk with a high-backed chair, tall white-framed windows, grey walls.",
    "supreme_court": "an old American courtroom of the Supreme Court, 19th century: a raised dark wooden bench for the justices, "
                     "red velvet curtains, columns, a gallery railing, gas lamps.",
    "colonial_boston": "a street in colonial Boston, 1770s: red brick Georgian houses, the Old State House with its lion and unicorn "
                       "on the roof, cobblestones, a tavern sign, a big elm tree.",
    "woodland_village": "an Eastern Woodlands Native American village: bark-covered longhouses and domed wigwams, a cornfield with "
                        "squash, a cooking fire, a palisade of sticks, deciduous forest around.",
    "great_plains": "the Great Plains of America: endless golden grass under a huge sky, a camp of white painted tipis by a winding "
                    "river, distant buttes, a few bison far away.",
    "colonial_fort": "an early English colonial fort in Virginia, 1600s: a triangular log palisade, thatched wooden houses, a small "
                     "church, a watchtower, a river with a moored ship.",
    "ship_harbor": "an 18th-century American harbor: tall-masted sailing ships at a wooden wharf, crates and barrels of cargo, brick "
                   "warehouses, seagulls, calm water.",
    "battlefield": "an American Civil War and Revolution era battlefield: rolling green hills, split-rail wooden fences, a stone "
                   "farmhouse, abandoned cannons, smoke drifting in the distance, dramatic clouds.",
    "plantation": "an antebellum Southern plantation: a white-columned big house far away, rows of rough wooden slave cabins, a "
                  "cotton field with white bolls in the foreground, Spanish moss on oak trees, hot hazy light.",
    "southwest": "the American Southwest desert: red mesas, cacti, an old adobe Spanish mission church with a bell wall, dry "
                 "dusty ground, bright sun.",
    "factory_city": "a 19th-century American industrial town: red brick textile mill and steel works with tall smokestacks, a canal "
                    "with a bridge, coal smoke, gas street lamps, cobblestone yard.",
    "railroad_west": "the Western railroad frontier, 1860s: a new railroad track across the plain toward snowy mountains, wooden "
                     "trestle, a steam locomotive with a big funnel smokestack, telegraph poles.",
    "city_street": "a New York City street around 1900: tall brick tenements with fire escapes, shop signs, a horse tram and an "
                   "early automobile, laundry lines, the Brooklyn Bridge far away.",
    "legend_forest": "an autumn forest in the Hudson Valley: orange and red trees, a dirt road leading to a small covered wooden "
                     "bridge over a stream, a lonely church in the distance, a jack-o'-lantern pumpkin on a fence post, misty dusk.",
    "president_office": "an American president's office in the 19th century: a big wooden desk with papers and an inkwell, a US "
                        "flag on a pole, bookshelves, a portrait of George Washington on the wall, tall window with curtains.",
}

if __name__ == "__main__":
    names = sys.argv[1:] or list(BG)
    out = ROOT / "Art/source/usa_bg"; out.mkdir(parents=True, exist_ok=True)
    ref = out / "_ref.png"
    Image.open(REF).convert("RGB").resize((768, 768)).save(ref)
    for n in names:
        p = out / f"{n}.png"
        if p.exists():
            print("skip", n); continue
        gen(ref, STYLE + BG[n], p)
        print("ok", n)
