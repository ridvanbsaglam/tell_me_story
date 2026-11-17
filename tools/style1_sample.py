"""
Lineless Soft-3D / Papercut Vector Icon Generator (Kapı 2 Revize Numunesi: 9 İkon)
SIFIR DIŞ ÇİZGİ (No Stroke/Outline).
Derinlik tamamen:
1) Yumuşak Gaussian alt gölge (ambient drop shadow),
2) Katmanlar arası ince düşen gölge (layer cast shadow),
3) Alt hacim koyulaşması (warm shading) ve üst yumuşak parlaklık (soft specular highlight) ile sağlanır.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "img_style1_test")
os.makedirs(OUT_DIR, exist_ok=True)

def new_canvas():
    return Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))

def add_layer_with_shadow(base: Image.Image, draw_fn, shadow_offset=(0, 18), shadow_blur=22, shadow_alpha=52):
    """Draws shapes onto a sub-layer, casts a soft blurred drop shadow onto `base`, then composites the layer."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d)
    if shadow_alpha > 0 and shadow_blur > 0:
        alpha = layer.split()[3]
        sh = Image.new("RGBA", base.size, (15, 23, 42, 0))
        sh_alpha = alpha.point(lambda a: int(a * (shadow_alpha / 255.0)))
        sh.putalpha(sh_alpha)
        sh = sh.filter(ImageFilter.GaussianBlur(shadow_blur))
        shifted = Image.new("RGBA", base.size, (0, 0, 0, 0))
        shifted.paste(sh, shadow_offset)
        base.alpha_composite(shifted)
    base.alpha_composite(layer)

def add_soft_glow(base: Image.Image, box, color, blur=28):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)

def finish_icon(im: Image.Image, target_px=260):
    alpha = im.split()[3]
    bbox = alpha.point(lambda v: 255 if v > 4 else 0).getbbox()
    if bbox:
        pad = 20
        x0 = max(0, bbox[0] - pad)
        y0 = max(0, bbox[1] - pad)
        x1 = min(im.width, bbox[2] + pad)
        y1 = min(im.height, bbox[3] + pad)
        im = im.crop((x0, y0, x1, y1))
    im.thumbnail((target_px, target_px), Image.LANCZOS)
    return im

# ==============================================================================
# 1. LEVEL BADGES (4 HATS — LINELESS SOFT 3D)
# ==============================================================================

def make_lvl_rookie():
    im = new_canvas()
    # Soft floor shadow
    add_soft_glow(im, [200, 770, 824, 855], (15, 23, 42, 55), blur=24)

    # Propeller stem + blades
    def blades(d):
        d.rounded_rectangle([488, 175, 536, 330], radius=24, fill=(217, 119, 6, 255))
        d.ellipse([205, 145, 505, 228], fill=(203, 213, 225, 255))
        d.ellipse([225, 155, 480, 195], fill=(241, 245, 249, 255))
        d.ellipse([519, 145, 819, 228], fill=(148, 163, 184, 255))
        d.ellipse([540, 155, 795, 195], fill=(226, 232, 240, 255))
        d.ellipse([474, 150, 550, 226], fill=(239, 68, 68, 255))
        d.ellipse([486, 160, 526, 190], fill=(252, 165, 165, 220))
    add_layer_with_shadow(im, blades, (0, 14), 16, 45)

    # Cap Dome (Rich warm yellow + deeper amber bottom rim + panel seams in soft darker gold)
    def dome(d):
        d.pieslice([190, 290, 834, 910], 180, 360, fill=(245, 158, 11, 255))
        d.pieslice([200, 290, 824, 885], 180, 360, fill=(250, 204, 21, 255))
        # Subtle panel ribs (no black lines — warm caramel tone)
        d.arc([345, 295, 679, 895], 180, 360, fill=(217, 119, 6, 160), width=14)
        d.line([512, 295, 512, 600], fill=(217, 119, 6, 160), width=14)
        # Soft glossy highlight on upper-left dome
        d.ellipse([265, 345, 415, 445], fill=(254, 249, 195, 195))
    add_layer_with_shadow(im, dome, (0, 20), 24, 55)

    # Visor / Brim casting a slight upward/downward 3D shadow
    def visor(d):
        d.rounded_rectangle([148, 575, 876, 680], radius=52, fill=(234, 88, 12, 255))
        d.rounded_rectangle([160, 575, 864, 652], radius=44, fill=(249, 115, 22, 255))
        d.rounded_rectangle([210, 588, 814, 618], radius=15, fill=(253, 186, 116, 180))
    add_layer_with_shadow(im, visor, (0, 16), 20, 60)
    return finish_icon(im)

def make_lvl_expert():
    im = new_canvas()
    add_soft_glow(im, [145, 755, 879, 845], (15, 23, 42, 55), blur=24)

    # Wide Safari Brim (back/base)
    def brim(d):
        d.ellipse([96, 545, 928, 720], fill=(146, 64, 14, 255))
        d.ellipse([112, 545, 912, 695], fill=(180, 83, 9, 255))
        d.ellipse([145, 555, 879, 670], fill=(217, 119, 6, 255))
    add_layer_with_shadow(im, brim, (0, 22), 26, 60)

    # Fedora Crown
    def crown(d):
        d.polygon([(272, 585), (338, 250), (455, 295), (569, 295), (686, 250), (752, 585)], fill=(180, 83, 9, 255))
        d.polygon([(278, 575), (342, 255), (455, 295), (555, 295), (650, 260), (705, 575)], fill=(217, 119, 6, 255))
        # Left sunlit face
        d.polygon([(295, 560), (348, 268), (450, 302), (430, 560)], fill=(245, 158, 11, 255))
        # Crown pinch shadow
        d.ellipse([435, 275, 589, 345], fill=(146, 64, 14, 150))
    add_layer_with_shadow(im, crown, (0, 16), 18, 50)

    # Ribbon + Golden Buckle
    def ribbon(d):
        d.rounded_rectangle([266, 500, 758, 592], radius=26, fill=(3, 105, 161, 255))
        d.rounded_rectangle([272, 500, 752, 574], radius=22, fill=(14, 165, 233, 255))
        d.rounded_rectangle([454, 488, 570, 602], radius=22, fill=(245, 158, 11, 255))
        d.rounded_rectangle([460, 488, 564, 590], radius=20, fill=(250, 204, 21, 255))
        d.rounded_rectangle([484, 516, 540, 570], radius=10, fill=(2, 132, 199, 255))
    add_layer_with_shadow(im, ribbon, (0, 12), 14, 50)
    return finish_icon(im)

def make_lvl_master():
    im = new_canvas()
    add_soft_glow(im, [155, 765, 869, 855], (15, 23, 42, 55), blur=24)

    # Curved Brim
    def brim(d):
        d.ellipse([115, 560, 909, 726], fill=(30, 41, 59, 255))
        d.ellipse([135, 560, 889, 700], fill=(51, 65, 85, 255))
        d.ellipse([175, 570, 849, 675], fill=(71, 85, 105, 255))
    add_layer_with_shadow(im, brim, (0, 22), 26, 65)

    # Top Hat Cylinder
    def cylinder(d):
        d.polygon([(252, 210), (772, 210), (718, 608), (306, 608)], fill=(30, 41, 59, 255))
        d.polygon([(258, 210), (745, 210), (695, 600), (312, 600)], fill=(51, 65, 85, 255))
        # Soft glossy vertical reflection
        d.polygon([(290, 225), (410, 225), (390, 590), (330, 590)], fill=(100, 116, 139, 255))
        # Top ellipse crown
        d.ellipse([248, 162, 776, 262], fill=(71, 85, 105, 255))
        d.ellipse([268, 170, 756, 248], fill=(100, 116, 139, 255))
    add_layer_with_shadow(im, cylinder, (0, 18), 20, 55)

    # Silk Magenta Band + Gold Emblem
    def band(d):
        d.rounded_rectangle([296, 502, 728, 598], radius=24, fill=(190, 24, 93, 255))
        d.rounded_rectangle([302, 502, 722, 580], radius=20, fill=(236, 72, 153, 255))
        d.ellipse([466, 504, 558, 596], fill=(245, 158, 11, 255))
        d.ellipse([472, 504, 552, 586], fill=(250, 204, 21, 255))
        d.ellipse([486, 516, 518, 544], fill=(254, 249, 195, 200))
    add_layer_with_shadow(im, band, (0, 12), 14, 50)
    return finish_icon(im)

def make_lvl_guru():
    im = new_canvas()
    add_soft_glow(im, [145, 770, 879, 860], (15, 23, 42, 55), blur=24)

    # Wide Mystical Brim
    def brim(d):
        d.ellipse([105, 575, 919, 742], fill=(88, 28, 135, 255))
        d.ellipse([125, 575, 899, 718], fill=(109, 40, 217, 255))
        d.ellipse([160, 585, 864, 695], fill=(139, 92, 246, 255))
    add_layer_with_shadow(im, brim, (0, 22), 26, 60)

    # Pointed Wizard Cone
    def cone(d):
        d.polygon([(262, 610), (475, 135), (695, 235), (585, 275), (758, 610)], fill=(109, 40, 217, 255))
        d.polygon([(270, 602), (475, 142), (675, 232), (572, 272), (725, 602)], fill=(139, 92, 246, 255))
        # Sunlit left ridge
        d.polygon([(295, 590), (476, 165), (545, 235), (425, 590)], fill=(167, 139, 250, 255))
        # Golden stars embedded on cone
        d.ellipse([420, 360, 472, 412], fill=(250, 204, 21, 255))
        d.ellipse([562, 412, 604, 454], fill=(250, 204, 21, 255))
    add_layer_with_shadow(im, cone, (0, 18), 20, 55)

    # Belt & Gold Buckle
    def belt(d):
        d.rounded_rectangle([252, 520, 772, 614], radius=28, fill=(162, 28, 175, 255))
        d.rounded_rectangle([260, 520, 764, 596], radius=24, fill=(217, 70, 239, 255))
        d.rounded_rectangle([450, 504, 574, 628], radius=24, fill=(245, 158, 11, 255))
        d.rounded_rectangle([456, 504, 568, 616], radius=22, fill=(250, 204, 21, 255))
        d.rounded_rectangle([482, 534, 542, 596], radius=10, fill=(88, 28, 135, 255))
    add_layer_with_shadow(im, belt, (0, 12), 14, 50)
    return finish_icon(im)

# ==============================================================================
# 2. SAMPLE CARDS (5 CATEGORIES — LINELESS SOFT 3D)
# ==============================================================================

def make_c1_astronaut():
    im = new_canvas()
    # Suit Shoulders
    def suit(d):
        d.rounded_rectangle([210, 655, 814, 915], radius=115, fill=(203, 213, 225, 255))
        d.rounded_rectangle([222, 655, 802, 885], radius=105, fill=(241, 245, 249, 255))
        d.rounded_rectangle([410, 735, 614, 850], radius=30, fill=(14, 165, 233, 255))
        d.ellipse([445, 772, 488, 815], fill=(239, 68, 68, 255))
        d.ellipse([536, 772, 579, 815], fill=(250, 204, 21, 255))
    add_layer_with_shadow(im, suit, (0, 20), 24, 55)

    # Helmet Ears & Antenna + Sphere
    def helmet(d):
        # Antenna
        d.rounded_rectangle([498, 105, 526, 205], radius=14, fill=(148, 163, 184, 255))
        d.ellipse([472, 65, 552, 145], fill=(239, 68, 68, 255))
        d.ellipse([484, 75, 520, 105], fill=(252, 165, 165, 220))
        # Side ear pods
        d.rounded_rectangle([125, 360, 235, 540], radius=45, fill=(234, 88, 12, 255))
        d.rounded_rectangle([135, 360, 225, 515], radius=40, fill=(249, 115, 22, 255))
        d.rounded_rectangle([789, 360, 899, 540], radius=45, fill=(234, 88, 12, 255))
        d.rounded_rectangle([799, 360, 889, 515], radius=40, fill=(249, 115, 22, 255))
        # Outer white helmet sphere with soft slate bottom shading
        d.ellipse([212, 150, 812, 750], fill=(203, 213, 225, 255))
        d.ellipse([218, 150, 806, 722], fill=(248, 250, 252, 255))
    add_layer_with_shadow(im, helmet, (0, 22), 26, 65)

    # Visor + Cute Character Face inside
    def visor(d):
        d.rounded_rectangle([275, 265, 749, 615], radius=165, fill=(3, 105, 161, 255))
        d.rounded_rectangle([290, 275, 734, 595], radius=155, fill=(14, 165, 233, 255))
        # Cute warm face
        d.ellipse([372, 320, 652, 590], fill=(253, 186, 116, 255))
        d.ellipse([378, 320, 646, 572], fill=(254, 215, 170, 255))
        # Cheeks & Eyes
        d.ellipse([402, 462, 450, 496], fill=(251, 113, 133, 210))
        d.ellipse([574, 462, 622, 496], fill=(251, 113, 133, 210))
        d.ellipse([438, 415, 474, 451], fill=(30, 41, 59, 255))
        d.ellipse([550, 415, 586, 451], fill=(30, 41, 59, 255))
        d.arc([474, 448, 550, 512], 15, 165, fill=(30, 41, 59, 255), width=16)
        # Glossy reflection on glass
        d.rounded_rectangle([325, 305, 465, 348], radius=21, fill=(255, 255, 255, 195))
    add_layer_with_shadow(im, visor, (0, 12), 16, 45)
    return finish_icon(im)

def make_c2_02():
    """Place: Grand Theater Stage (Lineless layered paper-3D)"""
    im = new_canvas()
    # Backdrop
    def backdrop(d):
        d.rounded_rectangle([130, 155, 894, 855], radius=65, fill=(15, 23, 42, 255))
        d.rounded_rectangle([142, 155, 882, 835], radius=60, fill=(30, 58, 138, 255))
        for sx, sy in [(380, 360), (640, 340), (512, 285), (420, 505), (610, 495)]:
            d.ellipse([sx - 14, sy - 14, sx + 14, sy + 14], fill=(250, 204, 21, 220))
    add_layer_with_shadow(im, backdrop, (0, 24), 28, 65)

    # Comedy & Tragedy Masks floating in center with soft drop shadow
    def masks(d):
        d.ellipse([355, 365, 535, 545], fill=(250, 204, 21, 255))
        d.arc([410, 440, 480, 500], 10, 170, fill=(146, 64, 14, 255), width=16)
        d.ellipse([500, 395, 680, 575], fill=(56, 189, 248, 255))
        d.arc([555, 495, 625, 550], 195, 345, fill=(3, 105, 161, 255), width=16)
    add_layer_with_shadow(im, masks, (0, 16), 18, 60)

    # Red Velvet Curtains & Top Valance + Stage Floor
    def curtains(d):
        d.polygon([(130, 180), (355, 180), (285, 720), (130, 720)], fill=(190, 18, 60, 255))
        d.polygon([(140, 180), (335, 180), (270, 705), (140, 705)], fill=(225, 29, 72, 255))
        d.polygon([(894, 180), (669, 180), (739, 720), (894, 720)], fill=(190, 18, 60, 255))
        d.polygon([(884, 180), (689, 180), (754, 705), (884, 705)], fill=(225, 29, 72, 255))
        for cx in [220, 365, 512, 659, 804]:
            d.ellipse([cx - 95, 115, cx + 95, 305], fill=(244, 63, 94, 255))
        d.rounded_rectangle([120, 138, 904, 220], radius=40, fill=(245, 158, 11, 255))
        d.rounded_rectangle([130, 138, 894, 202], radius=35, fill=(250, 204, 21, 255))
        # Stage deck & seats
        d.rounded_rectangle([112, 690, 912, 855], radius=48, fill=(180, 83, 9, 255))
        d.rounded_rectangle([122, 690, 902, 830], radius=42, fill=(217, 119, 6, 255))
        for sx in [230, 442, 654]:
            d.rounded_rectangle([sx, 742, sx + 140, 882], radius=32, fill=(244, 63, 94, 255))
            d.rounded_rectangle([sx + 10, 742, sx + 130, 855], radius=26, fill=(251, 113, 133, 255))
    add_layer_with_shadow(im, curtains, (0, 16), 20, 55)
    return finish_icon(im)

def make_c3_rain():
    """Weather: Warm Sun + Fluffy Soft-3D Cloud + Glossy Raindrops"""
    im = new_canvas()
    # Glowing Sun behind cloud
    def sun(d):
        d.ellipse([165, 145, 455, 435], fill=(245, 158, 11, 255))
        d.ellipse([180, 145, 440, 410], fill=(250, 204, 21, 255))
        d.ellipse([215, 175, 335, 265], fill=(254, 249, 195, 200))
    add_layer_with_shadow(im, sun, (0, 16), 22, 50)

    # Fluffy Cloud (darker sky-blue base + pure white upper puffs)
    def cloud(d):
        puffs = [(330, 450, 150), (505, 375, 180), (685, 455, 145), (420, 505, 135), (600, 505, 135)]
        for cx, cy, r in puffs:
            d.ellipse([cx - r, cy - r + 22, cx + r, cy + r + 22], fill=(186, 230, 253, 255))
        d.rounded_rectangle([205, 460, 810, 622], radius=80, fill=(186, 230, 253, 255))
        for cx, cy, r in puffs:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 249, 255, 255))
        d.rounded_rectangle([215, 450, 800, 595], radius=75, fill=(240, 249, 255, 255))
        for cx, cy, r in puffs[:3]:
            d.ellipse([cx - r + 24, cy - r + 16, cx + r - 24, cy + r - 36], fill=(255, 255, 255, 255))
    add_layer_with_shadow(im, cloud, (0, 22), 26, 60)

    # Rounded Teardrop Raindrops
    def drops(d):
        for dx, dy in [(310, 735), (465, 775), (620, 735), (755, 775)]:
            d.ellipse([dx - 44, dy - 10, dx + 44, dy + 78], fill=(2, 132, 199, 255))
            d.polygon([(dx - 42, dy + 22), (dx, dy - 62), (dx + 42, dy + 22)], fill=(14, 165, 233, 255))
            d.ellipse([dx - 38, dy - 6, dx + 38, dy + 68], fill=(56, 189, 248, 255))
            d.ellipse([dx - 20, dy + 10, dx - 4, dy + 36], fill=(224, 242, 254, 210))
    add_layer_with_shadow(im, drops, (0, 14), 16, 50)
    return finish_icon(im)

def make_c4_unicorn():
    """Twist: Magical Lineless Soft-3D Unicorn"""
    im = new_canvas()
    # Rainbow Mane puffs (back layer)
    def mane(d):
        mane_cols = [(244, 63, 94, 255), (250, 204, 21, 255), (52, 211, 153, 255), (56, 189, 248, 255), (168, 85, 247, 255)]
        for i, col in enumerate(mane_cols):
            cx = 665 + (i % 2) * 28
            cy = 360 + i * 95
            d.ellipse([cx - 92, cy - 92, cx + 92, cy + 92], fill=col)
        # Golden Horn
        d.polygon([(365, 325), (180, 110), (470, 260)], fill=(245, 158, 11, 255))
        d.polygon([(375, 315), (195, 120), (445, 265)], fill=(250, 204, 21, 255))
    add_layer_with_shadow(im, mane, (0, 18), 22, 55)

    # Unicorn Head & Neck (pure white with soft lavender-grey bottom shading)
    def head(d):
        d.polygon([(348, 845), (390, 315), (652, 315), (686, 845)], fill=(226, 232, 240, 255))
        d.polygon([(356, 845), (395, 315), (632, 315), (662, 845)], fill=(248, 250, 252, 255))
        d.rounded_rectangle([180, 285, 652, 565], radius=130, fill=(226, 232, 240, 255))
        d.rounded_rectangle([185, 275, 646, 545], radius=125, fill=(255, 255, 255, 255))
        # Pink Muzzle
        d.rounded_rectangle([175, 310, 340, 540], radius=98, fill=(244, 114, 182, 255))
        d.rounded_rectangle([180, 310, 332, 520], radius=92, fill=(251, 207, 232, 255))
        d.ellipse([232, 382, 264, 414], fill=(236, 72, 153, 255))
        # Ear
        d.polygon([(505, 285), (575, 138), (638, 295)], fill=(244, 114, 182, 255))
        d.polygon([(525, 280), (575, 170), (618, 285)], fill=(251, 207, 232, 255))
        # Eye & Rosy Cheek
        d.ellipse([412, 372, 460, 420], fill=(30, 41, 59, 255))
        d.ellipse([420, 380, 436, 396], fill=(255, 255, 255, 255))
        d.ellipse([398, 445, 468, 485], fill=(251, 113, 133, 195))
    add_layer_with_shadow(im, head, (0, 20), 24, 60)
    return finish_icon(im)

def make_c5_lighter():
    """Object: Retro Flame Lighter (Lineless Soft-3D)"""
    im = new_canvas()
    # Glowing Teardrop Flame
    add_soft_glow(im, [430, 80, 690, 410], (251, 146, 60, 95), blur=36)
    def flame(d):
        d.ellipse([455, 180, 665, 390], fill=(249, 115, 22, 255))
        d.polygon([(460, 255), (560, 90), (660, 255)], fill=(249, 115, 22, 255))
        d.ellipse([498, 235, 622, 370], fill=(250, 204, 21, 255))
        d.polygon([(502, 285), (560, 175), (618, 285)], fill=(250, 204, 21, 255))
        d.ellipse([528, 285, 592, 355], fill=(254, 249, 195, 240))
    add_layer_with_shadow(im, flame, (0, 12), 16, 40)

    # Silver Chimney + Flip Lid
    def chimney(d):
        d.rounded_rectangle([425, 385, 695, 525], radius=26, fill=(148, 163, 184, 255))
        d.rounded_rectangle([432, 385, 688, 505], radius=24, fill=(226, 232, 240, 255))
        for hx in [485, 560, 635]:
            d.ellipse([hx - 16, 432, hx + 16, 464], fill=(71, 85, 105, 255))
        d.rounded_rectangle([155, 265, 388, 515], radius=42, fill=(29, 78, 216, 255))
        d.rounded_rectangle([165, 265, 378, 495], radius=38, fill=(59, 130, 246, 255))
    add_layer_with_shadow(im, chimney, (0, 16), 18, 50)

    # Main Lighter Body
    def body(d):
        d.rounded_rectangle([355, 500, 765, 895], radius=58, fill=(29, 78, 216, 255))
        d.rounded_rectangle([365, 500, 755, 870], radius=52, fill=(37, 99, 235, 255))
        d.rounded_rectangle([415, 555, 705, 830], radius=36, fill=(56, 189, 248, 255))
        d.rounded_rectangle([442, 585, 482, 775], radius=20, fill=(224, 242, 254, 195))
    add_layer_with_shadow(im, body, (0, 22), 26, 65)
    return finish_icon(im)

SAMPLES = [
    ("lvl_rookie", "LEVEL 1: ROOKIE", make_lvl_rookie),
    ("lvl_expert", "LEVEL 2: EXPERT", make_lvl_expert),
    ("lvl_master", "LEVEL 3: MASTER", make_lvl_master),
    ("lvl_guru",   "LEVEL 4: GURU",   make_lvl_guru),
    ("c1_astronaut", "CHARACTER: ASTRONAUT", make_c1_astronaut),
    ("c2_02",        "PLACE: THEATER STAGE", make_c2_02),
    ("c3_rain",      "WEATHER: RAIN CLOUD",  make_c3_rain),
    ("c4_unicorn",   "TWIST: UNICORN",       make_c4_unicorn),
    ("c5_lighter",   "OBJECT: LIGHTER",      make_c5_lighter),
]

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    orig_dir = os.path.join(root, "img")
    board = Image.new("RGBA", (1620, 780), (15, 98, 128, 255))
    bd = ImageDraw.Draw(board)
    for idx, (name, title, fn) in enumerate(SAMPLES):
        icon = fn()
        icon.save(os.path.join(OUT_DIR, name + ".png"))
        icon.save(os.path.join(orig_dir, name + ".png"))
        col = idx % 3
        row = idx // 3
        x0 = 30 + col * 525
        y0 = 30 + row * 245
        bd.rounded_rectangle([x0, y0, x0 + 500, y0 + 225], radius=24, fill=(255, 255, 255, 255))
        bd.rounded_rectangle([x0, y0, x0 + 500, y0 + 40], radius=20, fill=(20, 82, 110, 255))
        bd.text((x0 + 20, y0 + 12), title + "   (Lineless Soft-3D + Ambient Shadow)", fill=(255, 255, 255, 255))
        new_im = icon.copy()
        new_im.thumbnail((165, 165), Image.LANCZOS)
        board.paste(new_im, (x0 + (500 - new_im.width)//2, y0 + 48 + (165 - new_im.height)//2), new_im)
    board_path = os.path.join(OUT_DIR, "lineless_soft3d_board.png")
    board.save(board_path)
    print("Saved lineless soft-3D board:", board_path)
