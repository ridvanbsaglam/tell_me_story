import os
from PIL import Image

src_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\img"
art_dir = r"C:\Users\rsagl\.gemini\antigravity\brain\ac962468-14fb-4403-80e1-6d3617a93d9b"
bg_cream = (246, 241, 229)

def make_grid(file_list, cols, rows, cell_size, out_path):
    w = cols * cell_size
    h = rows * cell_size
    grid = Image.new("RGB", (w, h), bg_cream)
    for idx, fname in enumerate(file_list):
        if idx >= cols * rows: break
        c = idx % cols
        r = idx // cols
        p = os.path.join(src_dir, fname)
        if os.path.exists(p):
            with Image.open(p) as im:
                im_rgba = im.convert("RGBA")
                # scale keeping aspect
                scale = (cell_size * 0.88) / max(im_rgba.width, im_rgba.height)
                nw, nh = int(im_rgba.width * scale), int(im_rgba.height * scale)
                scaled = im_rgba.resize((nw, nh), Image.LANCZOS)
                ox = c * cell_size + (cell_size - nw) // 2
                oy = r * cell_size + (cell_size - nh) // 2
                grid.paste(scaled, (ox, oy), scaled)
    grid.save(out_path, quality=92)
    print("Saved grid to:", out_path)

# 1. Places (10) -> 5x2 grid
places = ["c2_01.png", "c2_02.png", "c2_03.png", "c2_04.png", "c2_05.png",
          "c2_06.png", "c2_07.png", "c2_government.png", "c2_mortgage_loan.png", "c2_stadium.png"]
make_grid(places, 5, 2, 220, os.path.join(art_dir, "showcase_places.jpg"))

# 2. Weather (14) -> 5x3 grid
weather = ["c3_01.png", "c3_02.png", "c3_03.png", "c3_04.png", "c3_beach.png",
           "c3_dust.png", "c3_earthquake.png", "c3_flood.png", "c3_park.png", "c3_rain.png",
           "c3_storm.png", "c3_sun.png", "c3_tsunami.png", "c3_war.png"]
make_grid(weather, 5, 3, 200, os.path.join(art_dir, "showcase_weather.jpg"))

# 3. Twists (10) -> 5x2 grid
twists = ["c4_bipolar.png", "c4_crocodile.png", "c4_death.png", "c4_fortune_telling.png", "c4_scorpion.png",
          "c4_tent.png", "c4_thyroid.png", "c4_unicorn.png", "c4_voodoo.png", "c4_whale.png"]
make_grid(twists, 5, 2, 220, os.path.join(art_dir, "showcase_twists.jpg"))

# 4. Objects (10) -> 5x2 grid
objects = ["c5_construction_and_tools.png", "c5_evidences.png", "c5_handcuff.png", "c5_lighter.png", "c5_mat.png",
           "c5_mutation.png", "c5_scissors.png", "c5_sewing_machine.png", "c5_sundae.png", "c5_vaccine.png"]
make_grid(objects, 5, 2, 220, os.path.join(art_dir, "showcase_objects.jpg"))
