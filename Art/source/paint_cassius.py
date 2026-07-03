import os
from PIL import Image, ImageDraw, ImageFilter

def paint_feature(img, draw, coords, color, width):
    # Draw thick line with anti-aliasing (by drawing on a 4x canvas and resizing back)
    # But since Pillow line can be aliased, we can draw a series of overlapping circles or use simple lines.
    # Actually, drawing lines with width is fine, or we can use small ellipses to make smooth rounded caps.
    for i in range(len(coords) - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i+1]
        draw.line([x1, y1, x2, y2], fill=color, width=width)
        # Rounded caps
        draw.ellipse([x1-width/2, y1-width/2, x1+width/2, y1+width/2], fill=color)
        draw.ellipse([x2-width/2, y2-width/2, x2+width/2, y2+width/2], fill=color)

def main():
    brutus_path = "/Users/volhametsko/.gemini/antigravity/brain/9f64cc2e-3373-4946-9817-9ee405040037/char_brutus_1783069372578.png"
    img = Image.open(brutus_path).convert("RGBA")
    
    width, height = img.size
    
    # 1. Modify Brutus's sash from purple to olive
    # Lighter olive: #6e6f4a (110, 111, 74)
    # Darker olive: #585a3a (88, 90, 58)
    for x in range(width):
        for y in range(height):
            r, g, b, a = img.getpixel((x, y))
            # Detect purple pixels (high R & B, low G)
            if r > 90 and b > 90 and g < 130 and r > g + 20 and b > g + 20:
                avg_rb = (r + b) / 2.0
                if avg_rb < 130:
                    img.putpixel((x, y), (88, 90, 58, a))
                else:
                    img.putpixel((x, y), (110, 111, 74, a))
                    
    # 2. Erase Brutus's eyes, eyebrows, and mouth
    # We will cover them with the skin tone. Since the face has a light gradient, we can
    # fill the areas and apply a slight blur to blend them seamlessly.
    # Skin tone is around (249, 211, 188)
    draw = ImageDraw.Draw(img)
    
    # Erase Left Eye/Eyebrow: x=390 to 480, y=320 to 380
    left_skin = (248, 207, 185, 255)
    draw.rectangle([390, 310, 480, 380], fill=left_skin)
    
    # Erase Right Eye/Eyebrow: x=540 to 630, y=320 to 380
    right_skin = (251, 215, 191, 255)
    draw.rectangle([540, 310, 630, 380], fill=right_skin)
    
    # Erase Mouth: x=440 to 580, y=410 to 445
    mouth_skin = (250, 209, 181, 255)
    draw.rectangle([440, 410, 580, 445], fill=mouth_skin)
    
    # Blend the erased areas using a soft blur filter on a patch
    # We can crop the face area, blur it, and blend it back.
    face_box = (380, 300, 640, 450)
    face_patch = img.crop(face_box)
    # Blur the patch to smooth out the hard edges of the rectangles
    blurred_patch = face_patch.filter(ImageFilter.GaussianBlur(radius=3))
    
    # We only want to blur the erased regions, so we use a mask
    mask = Image.new("L", face_patch.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    # Draw soft white rectangles in the mask where we erased
    mask_draw.rectangle([390-380, 310-300, 480-380, 380-300], fill=255)
    mask_draw.rectangle([540-380, 310-300, 630-380, 380-300], fill=255)
    mask_draw.rectangle([440-380, 410-300, 580-380, 445-300], fill=255)
    # Blur the mask to make the blend seamless
    mask = mask.filter(ImageFilter.GaussianBlur(radius=5))
    
    # Paste blurred patch using the mask
    face_patch.paste(blurred_patch, (0, 0), mask)
    img.paste(face_patch, face_box)
    
    # 3. Draw Cassius's new features
    # Outline color: #2b2419 (RGB 43, 36, 25)
    outline_color = (43, 36, 25, 255)
    
    # Devious slanted eyebrows (pointing down towards the nose)
    # Left eyebrow: M 400 325 Q 435 328 470 338
    # Right eyebrow: M 624 325 Q 589 328 554 338
    # We draw them as quadratic bezier curves or straight lines. Since they are small, 
    # two-segment lines will look very organic and hand-drawn.
    left_eyebrow = [(400, 320), (435, 324), (465, 334)]
    right_eyebrow = [(624, 320), (589, 324), (559, 334)]
    paint_feature(img, draw, left_eyebrow, outline_color, 8)
    paint_feature(img, draw, right_eyebrow, outline_color, 8)
    
    # Squinting sly eyes (thin horizontal-ish lines)
    # Left eye: M 415 352 L 455 352
    # Right eye: M 609 352 L 569 352
    left_eye = [(415, 350), (455, 350)]
    right_eye = [(609, 350), (569, 350)]
    paint_feature(img, draw, left_eye, outline_color, 8)
    paint_feature(img, draw, right_eye, outline_color, 8)
    
    # Cunning smirk mouth (curving up on one side)
    # M 470 422 Q 512 422 554 414
    mouth = [(475, 422), (512, 424), (549, 414)]
    paint_feature(img, draw, mouth, outline_color, 7)
    
    # 4. Save the raw composite
    img.save("char_cassius_raw.png", "PNG")
    print("Saved composite to char_cassius_raw.png")

if __name__ == "__main__":
    main()
