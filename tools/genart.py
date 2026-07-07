#!/usr/bin/env python3
"""Генерация/раскладка персонажей History Teller через Nano-Banana (Gemini image).

Пайплайн: сгенерить на МАГЕНТА-фоне по стилю-референсу → вырезать магенту в alpha=0 →
положить в Art/source + iOS imageset + Android drawable (имя char_<id>[_<pose>]).

Требует GEMINI_API_KEY (source ~/.zshenv). Ключ НИКОГДА не пишем в файлы.

Программный API:
    from genart import gen, cutout, place, make
    make(char_id, pose, prompt, ref_path)   # всё разом

CLI:
    python3 tools/genart.py <char_id> <pose|base> <ref_path> "<prompt>"
"""
import sys, os, json, base64, urllib.request, pathlib
import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = "gemini-2.5-flash-image"

def gen(ref_path, prompt, out_raw):
    key = os.environ["GEMINI_API_KEY"]
    ref = base64.b64encode(open(ref_path, "rb").read()).decode()
    body = {"contents": [{"parts": [{"text": prompt},
            {"inline_data": {"mime_type": "image/png", "data": ref}}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}"
    body_b = json.dumps(body).encode()
    r = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=body_b, headers={"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=240))
            break
        except Exception as e:
            if attempt == 3:
                raise
            print(f"    retry {attempt+1} ({type(e).__name__})")
    parts = r["candidates"][0]["content"]["parts"]
    imgs = [p.get("inlineData", p.get("inline_data")) for p in parts
            if p.get("inlineData") or p.get("inline_data")]
    if not imgs:
        raise RuntimeError("no image: " + str([p.get("text") for p in parts])[:200])
    open(out_raw, "wb").write(base64.b64decode(imgs[0]["data"]))

def cutout(raw_path, out_path):
    """Магента-фон → прозрачность. Красный/золото/кожу не трогает (у них b≈g)."""
    a = np.array(Image.open(raw_path).convert("RGBA")).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bg = (r - g > 40) & (b - g > 22) & (r > 120)
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    al = np.array(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.8)))
    al = np.where(al < 40, 0, np.where(al > 200, 255, al)).astype(np.uint8)
    out = a.copy(); out[:, :, 3] = al
    Image.fromarray(out.astype(np.uint8)).save(out_path)

def place(png_path, char_id, pose=None):
    name = f"char_{char_id}" + (f"_{pose}" if pose and pose != "base" else "")
    ax = ROOT / "ios/Modules/GameContent/Resources/Assets.xcassets" / f"{name}.imageset"
    ax.mkdir(parents=True, exist_ok=True)
    im = Image.open(png_path)
    im.save(ax / f"{name}.png")
    (ax / "Contents.json").write_text(
        '{\n  "images" : [ { "idiom" : "universal", "filename" : "%s.png" } ],\n'
        '  "info" : { "author" : "xcode", "version" : 1 }\n}\n' % name)
    im.save(ROOT / "android/app/src/main/res/drawable" / f"{name}.png")
    return name

def make(char_id, pose, prompt, ref_path):
    src_dir = ROOT / "Art" / "source"
    stem = f"char_{char_id}" + (f"_{pose}" if pose and pose != "base" else "")
    raw = src_dir / f"{stem}_gen.png"
    final = src_dir / f"{stem}.png"
    gen(ref_path, prompt, raw)
    cutout(raw, final)
    name = place(final, char_id, pose)
    frac = (np.array(Image.open(final))[:, :, 3] == 0).mean()
    print(f"  {name}: прозрачно {frac*100:.0f}%")
    return final

if __name__ == "__main__":
    cid, pose, ref, prompt = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    make(cid, pose, prompt, ref)
