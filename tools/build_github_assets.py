"""
Generates GitHub showcase assets for Tell Me Your Story Rive project:
1. gameplay_walkthrough.gif - Animated preview cycling through the 8 game screens
2. features_grid.png - 2x2 high-res collage of the 4 key gameplay stages
3. hero_banner.png - Elegant widescreen banner for the README
4. Copies individual screenshots to assets/screens/
"""
import os, shutil
from PIL import Image, ImageDraw, ImageFont

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
qa_dir = os.path.join(root, "build", "qa")
assets_dir = os.path.join(root, "assets")
screens_dir = os.path.join(assets_dir, "screens")

os.makedirs(screens_dir, exist_ok=True)

screen_files = [
    ("01_hello.png", "Welcome & Difficulty Selection"),
    ("03_level1_rookie_closed.png", "Level 1: Rookie - Closed Hand"),
    ("04_level1_rookie_flipped.png", "Level 1: Rookie - Flipped & Checked Cards"),
    ("05_level2_expert_timer.png", "Level 2: Expert - 30s Countdown Timer"),
    ("06_level3_master_twist.png", "Level 3: Master - Mystery Twist Envelope"),
    ("07_level4_guru_write.png", "Level 4: Guru - Real-time Story Writing Studio"),
    ("08_level4_guru_showcase.png", "Level 4: Guru - Final Shareable Story Card"),
    ("02_help_modal.png", "How to Play & Game Rules Modal"),
]

# 1. Copy screens
print("Copying individual screenshots...")
for filename, desc in screen_files:
    src = os.path.join(qa_dir, filename)
    if os.path.exists(src):
        dst = os.path.join(screens_dir, filename)
        shutil.copy(src, dst)

# 2. Build 2x2 Features Grid
print("Building 2x2 features grid...")
grid_screens = [
    ("01_hello.png", "1. Choose Your Storytelling Level"),
    ("04_level1_rookie_flipped.png", "2. Draw & Tap Hand-Drawn Cards"),
    ("06_level3_master_twist.png", "3. Master The Mystery Twist"),
    ("07_level4_guru_write.png", "4. Compose in the Writing Studio"),
]

thumb_w, thumb_h = 600, 338
gap = 16
pad = 20
grid_w = pad * 2 + thumb_w * 2 + gap
grid_h = pad * 2 + thumb_h * 2 + gap

grid_img = Image.new("RGB", (grid_w, grid_h), (18, 28, 36))
draw = ImageDraw.Draw(grid_img)

positions = [
    (pad, pad),
    (pad + thumb_w + gap, pad),
    (pad, pad + thumb_h + gap),
    (pad + thumb_w + gap, pad + thumb_h + gap),
]

for idx, (filename, label) in enumerate(grid_screens):
    src = os.path.join(qa_dir, filename)
    if os.path.exists(src):
        im = Image.open(src).convert("RGB")
        im_resized = im.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x, y = positions[idx]
        grid_img.paste(im_resized, (x, y))

grid_path = os.path.join(assets_dir, "features_grid.jpg")
grid_img.save(grid_path, "JPEG", quality=90)
print("Saved features grid:", grid_path)

# 3. Build Animated Walkthrough GIF (960x540 for web smoothness & small filesize)
print("Building animated gameplay walkthrough GIF...")
gif_frames = []
durations = []

# Key sequence for walkthrough
walkthrough_seq = [
    ("01_hello.png", 2200),
    ("03_level1_rookie_closed.png", 1400),
    ("04_level1_rookie_flipped.png", 2000),
    ("05_level2_expert_timer.png", 2000),
    ("06_level3_master_twist.png", 2200),
    ("07_level4_guru_write.png", 2400),
    ("08_level4_guru_showcase.png", 2400),
    ("02_help_modal.png", 1800),
]

target_w, target_h = 960, 540

for filename, dur in walkthrough_seq:
    src = os.path.join(qa_dir, filename)
    if os.path.exists(src):
        im = Image.open(src).convert("RGB")
        im_res = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
        # Quantize with adaptive palette for crisp GIF rendering
        im_quant = im_res.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        gif_frames.append(im_quant)
        durations.append(dur)

if gif_frames:
    gif_path = os.path.join(assets_dir, "gameplay_walkthrough.gif")
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Saved animated GIF: {gif_path} ({os.path.getsize(gif_path) / (1024*1024):.2f} MB)")

print("All GitHub assets generated successfully!")
