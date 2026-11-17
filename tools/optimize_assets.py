import os
from PIL import Image

dest_dir = r"c:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\img"
files = [f for f in os.listdir(dest_dir) if f.endswith(".png") and f != "ui_bg.png"]

print(f"Optimizing {len(files)} card & hat icons to 280x280...")
total_before = 0
total_after = 0

for f in files:
    p = os.path.join(dest_dir, f)
    total_before += os.path.getsize(p)
    with Image.open(p) as im:
        if im.width > 280 or im.height > 280:
            # Resize keeping aspect ratio, max dimension 280
            scale = 280.0 / max(im.width, im.height)
            nw, nh = int(im.width * scale), int(im.height * scale)
            resized = im.resize((nw, nh), Image.LANCZOS)
            resized.save(p, optimize=True)
    total_after += os.path.getsize(p)

print(f"Total size before: {total_before // 1024} KB ({total_before / (1024*1024):.1f} MB)")
print(f"Total size after:  {total_after // 1024} KB ({total_after / (1024*1024):.1f} MB)")
print(f"Savings: {(total_before - total_after) // 1024} KB ({(1.0 - total_after/total_before)*100:.1f}% reduction!)")
