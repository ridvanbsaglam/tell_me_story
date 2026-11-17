import os
from PIL import Image, ImageDraw, ImageFont

src_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\new_images"
art_dir = r"C:\Users\rsagl\.gemini\antigravity\brain\ac962468-14fb-4403-80e1-6d3617a93d9b"

files = [f for f in os.listdir(src_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
files.sort()

# Separate hats and characters
hats = [f for f in files if "hat" in f.lower() or "fedora" in f.lower() or "beanie" in f.lower()]
chars = [f for f in files if f not in hats]

print(f"Hats: {len(hats)}, Characters: {len(chars)}")

# Create a 2x2 grid for the 4 hats
hat_grid = Image.new("RGB", (1024, 1024), (246, 241, 229)) # #F6F1E5
for i, hf in enumerate(hats[:4]):
    x = (i % 2) * 512
    y = (i // 2) * 512
    with Image.open(os.path.join(src_dir, hf)) as im:
        im_resized = im.resize((480, 480), Image.LANCZOS)
        hat_grid.paste(im_resized, (x + 16, y + 16))

hat_grid.save(os.path.join(art_dir, "new_hats_showcase.jpg"), quality=92)
print("Saved new_hats_showcase.jpg")

# Create a 4x3 grid for 12 character samples
char_grid = Image.new("RGB", (1200, 900), (246, 241, 229))
for i, cf in enumerate(chars[:12]):
    x = (i % 4) * 300
    y = (i // 4) * 300
    with Image.open(os.path.join(src_dir, cf)) as im:
        im_resized = im.resize((270, 270), Image.LANCZOS)
        char_grid.paste(im_resized, (x + 15, y + 15))

char_grid.save(os.path.join(art_dir, "new_chars_sample1.jpg"), quality=92)
print("Saved new_chars_sample1.jpg")

# Create a 4x3 grid for the remaining 11 character samples
char_grid2 = Image.new("RGB", (1200, 900), (246, 241, 229))
for i, cf in enumerate(chars[12:24]):
    x = (i % 4) * 300
    y = (i // 4) * 300
    with Image.open(os.path.join(src_dir, cf)) as im:
        im_resized = im.resize((270, 270), Image.LANCZOS)
        char_grid2.paste(im_resized, (x + 15, y + 15))

char_grid2.save(os.path.join(art_dir, "new_chars_sample2.jpg"), quality=92)
print("Saved new_chars_sample2.jpg")
