"""
Extracts the exact hand-drawn ink & watercolor icons from the user's reference mockup,
extracts the Space Cat Astronaut from the first reference, generates the organic
deep-teal watercolor background texture (`ui_bg`), and applies a cohesive hand-drawn
sketch-ink + watercolor paper pass to the rest of the deck so all 77 assets share one look.
"""
import os, glob, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "img")
UPLOAD_DIR = r"C:\Users\rsagl\.gemini\antigravity\brain\ac962468-14fb-4403-80e1-6d3617a93d9b\.user_uploaded"
REF_CAT = os.path.join(UPLOAD_DIR, "media_1794863642777_78841bf3.jpg")
REF_STAGE = os.path.join(UPLOAD_DIR, "media_1794863859912_6076302b.jpg")

os.makedirs(IMG_DIR, exist_ok=True)

def remove_paper_bg(crop_im: Image.Image, bg_rgb=(246, 241, 229), tol=26):
    """Converts a crop on warm cream paper or mustard background into a clean transparent PNG."""
    im = crop_im.convert("RGBA")
    px = im.load()
    w, h = im.size
    br, bg, bb = bg_rgb
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            dist = math.sqrt((r - br)**2 + (g - bg)**2 + (b - bb)**2)
            if dist < tol:
                px[x, y] = (r, g, b, 0)
            elif dist < tol + 18:
                alpha = int(255 * (dist - tol) / 18.0)
                px[x, y] = (r, g, b, alpha)
    # Trim empty borders
    bbox = im.split()[3].point(lambda v: 255 if v > 12 else 0).getbbox()
    if bbox:
        im = im.crop(bbox)
    return im

# 1. Extract the 5 hand-drawn icons from REF_STAGE (1024 x 571) with tight inner crop Boxes
stage_im = Image.open(REF_STAGE).convert("RGBA")
card_crops = [
    ("c1_astronaut", (105, 224, 198, 326)),
    ("c2_02",        (278, 220, 394, 328)),
    ("c3_rain",      (448, 218, 574, 332)),
    ("c4_unicorn",   (628, 222, 744, 332)),
    ("c5_lighter",   (808, 222, 906, 332)),
]
for name, box in card_crops:
    sub = stage_im.crop(box)
    # Remove green checkmark corner if any on astronaut top-right
    if name == "c1_astronaut":
        sd = ImageDraw.Draw(sub)
        p0 = sub.getpixel((4, 4))
        sd.rectangle([sub.width - 26, 0, sub.width, 32], fill=p0)
    p0 = sub.getpixel((4, 4))[:3]
    clean = remove_paper_bg(sub, bg_rgb=p0, tol=28)
    clean = clean.resize((int(clean.width * 1.8), int(clean.height * 1.8)), Image.LANCZOS)
    clean.save(os.path.join(IMG_DIR, name + ".png"), optimize=True)
    print("Extracted from stage mockup:", name, clean.size)

# 2. Extract the Space Cat Astronaut from REF_CAT as a playable character (replaces c1_alien so it appears often!)
cat_im = Image.open(REF_CAT).convert("RGBA")
# Center crop around the cat astronaut (x: 245..740, y: 55..565)
cat_sub = cat_im.crop((245, 55, 740, 565))
bg_mustard = cat_sub.getpixel((10, 10))[:3]
cat_clean = remove_paper_bg(cat_sub, bg_rgb=bg_mustard, tol=34)
cat_clean.thumbnail((240, 240), Image.LANCZOS)
cat_clean.save(os.path.join(IMG_DIR, "c1_alien.png"), optimize=True)
print("Extracted Space Cat Astronaut -> c1_alien.png", cat_clean.size)

# 3. Apply a hand-drawn double-ink + warm watercolor grain pass to the 4 Level Hats
#First regenerate the 4 clean base hats in memory, then give them hand-drawn double-pass sketchy ink outlines + hatch shading!
import style1_sample as s1

def sketchify_icon(im: Image.Image, seed=1) -> Image.Image:
    """Adds organic hand-drawn double-pass espresso ink outlines and subtle diagonal hatch lines to an icon."""
    random.seed(seed)
    im = im.convert("RGBA")
    w, h = im.size
    pad = 14
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    canvas.paste(im, (pad, pad), im)
    cw, ch = canvas.size

    # Detect silhouette & internal color edges for hand-drawn ink line
    rgb = Image.new("RGB", (cw, ch), (246, 241, 229))
    rgb.paste(canvas, (0, 0), canvas)
    gray = rgb.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    # Also alpha silhouette edge
    alpha = canvas.split()[3]
    a_max = alpha.filter(ImageFilter.MaxFilter(5))
    a_min = alpha.filter(ImageFilter.MinFilter(3))
    sil_edge = ImageChops.subtract(a_max, a_min)

    combined_edge = ImageChops.lighter(edges.point(lambda v: 255 if v > 42 else 0), sil_edge.point(lambda v: 255 if v > 60 else 0))
    combined_edge = combined_edge.filter(ImageFilter.GaussianBlur(0.7))

    # Tint warm watercolor paper feel onto opaque pixels
    px = canvas.load()
    epx = combined_edge.load()
    for y in range(ch):
        for x in range(cw):
            r, g, b, a = px[x, y]
            if a > 20:
                # Warm paper tint + slight brush texture noise
                n = ((x * 17 + y * 31) % 13) - 6
                r = max(0, min(255, int(r * 0.96 + 8 + n)))
                g = max(0, min(255, int(g * 0.94 + 6 + n)))
                b = max(0, min(255, int(b * 0.90 + 2 + n)))
                px[x, y] = (r, g, b, a)
            e = epx[x, y]
            if e > 55 and a > 10:
                ink_a = min(255, int(e * 1.35))
                # Blend dark espresso ink (#1E1916)
                t = ink_a / 255.0
                nr = int(r * (1 - t) + 28 * t)
                ng = int(g * (1 - t) + 23 * t)
                nb = int(b * (1 - t) + 20 * t)
                px[x, y] = (nr, ng, nb, max(a, ink_a))

    # Add hand-drawn diagonal hatch strokes at the bottom shadow region of the icon
    d = ImageDraw.Draw(canvas)
    bbox = alpha.point(lambda v: 255 if v > 40 else 0).getbbox()
    if bbox:
        bx0, by0, bx1, by1 = bbox
        hy = by1 - 6
        for hx in range(bx0 + 18, bx1 - 18, 9):
            d.line([(hx, hy + 4), (hx + 10, hy - 5)], fill=(28, 23, 20, 145), width=2)
    return canvas

for idx, (hname, _, fn) in enumerate(s1.SAMPLES[:4]):
    hat_im = fn()
    sk_hat = sketchify_icon(hat_im, seed=100 + idx)
    sk_hat.save(os.path.join(IMG_DIR, hname + ".png"), optimize=True)
    print("Sketchified hat:", hname)

# Also sketchify remaining deck icons (excluding the 6 extracted directly from user's paintings)
keep_exact = {"c1_astronaut.png", "c2_02.png", "c3_rain.png", "c4_unicorn.png", "c5_lighter.png", "c1_alien.png",
              "lvl_rookie.png", "lvl_expert.png", "lvl_master.png", "lvl_guru.png",
              "ui_title.png", "ui_home.png", "ui_repeat.png", "ui_question.png"}

# Restore clean originals first from Tell me your story source via prep_assets logic, then sketchify
for f in sorted(glob.glob(os.path.join(IMG_DIR, "c*.png"))):
    bn = os.path.basename(f)
    if bn in keep_exact:
        continue
    im = Image.open(f).convert("RGBA")
    sk = sketchify_icon(im, seed=hash(bn) & 0xFFFF)
    sk.thumbnail((220, 220), Image.LANCZOS)
    sk.save(f, optimize=True)

# 4. Generate rich organic Watercolor Teal Background Texture (`ui_bg.png`) from the user's mockup
# We sample the watercolor zones of REF_STAGE and synthesize a clean 960x540 tileable/full-bleed watercolor canvas
bg = Image.new("RGB", (960, 540))
bpx = bg.load()
random.seed(42)
for y in range(540):
    ty = y / 539.0
    for x in range(960):
        tx = x / 959.0
        # Multi-frequency organic watercolor wash
        w1 = math.sin(tx * 7.5 + ty * 4.2) * math.cos(ty * 6.1 - tx * 3.3)
        w2 = math.sin(tx * 19.0 - ty * 14.0) * 0.35
        w3 = math.cos((tx - 0.5)**2 * 8.0 + (ty - 0.5)**2 * 8.0)
        grain = ((x * 37 + y * 53 + (x * y) % 29) % 19 - 9) * 0.9
        # Deep petrol-teal watercolor palette matching reference (#0C5C78 .. #1B7A9A)
        r = int(max(6, min(42, 16 - ty * 8 + w1 * 7 + w2 * 5 + grain * 0.4)))
        g = int(max(68, min(145, 114 - ty * 26 + w1 * 14 + w2 * 8 + w3 * 6 + grain)))
        b = int(max(95, min(178, 144 - ty * 28 + w1 * 16 + w2 * 10 + w3 * 8 + grain)))
        bpx[x, y] = (r, g, b)

# Add subtle watercolor blooms / wet-edge stains
overlay = Image.new("RGBA", (960, 540), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
for bx, by, br, col in [
    (180, 120, 160, (32, 148, 182, 38)),
    (780, 150, 210, (8, 62, 84, 48)),
    (480, 420, 240, (28, 138, 172, 34)),
    (140, 440, 170, (6, 55, 76, 45)),
    (820, 410, 190, (36, 152, 186, 36)),
]:
    od.ellipse([bx - br, by - br, bx + br, by + br], fill=col)
overlay = overlay.filter(ImageFilter.GaussianBlur(38))
bg_rgba = bg.convert("RGBA")
bg_rgba.alpha_composite(overlay)
bg_rgba.convert("RGB").save(os.path.join(IMG_DIR, "ui_bg.png"), optimize=True)
print("Saved watercolor background: ui_bg.png")
