import os
from PIL import Image

src_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\new_images"
files = [f for f in os.listdir(src_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

print(f"Total images found: {len(files)}")
for f in files:
    p = os.path.join(src_dir, f)
    with Image.open(p) as img:
        print(f"{f}: {img.size}, mode={img.mode}")
