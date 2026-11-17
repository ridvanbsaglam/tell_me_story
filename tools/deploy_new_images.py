import os
from PIL import Image
import numpy as np

src_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\new_images"
dest_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\img"

mapping = {
    # 4 Hats
    "Yellow_propeller_beanie_hat_spin": "lvl_rookie.png",
    "Leather_fedora_with_cyan_belt": "lvl_expert.png",
    "Top_hat_with_ribbon": "lvl_master.png",
    "Purple_wizard_hat_sketch": "lvl_guru.png",
    # 23 Characters
    "Astronaut_wearing_bubble_helmet": "c1_astronaut.png",
    "Basketball_player_spinning_ball": "c1_basketball_player.png",
    "Burglar_carrying_sack_of_loot": "c1_thief.png",
    "Clown_smiling_sketch": "c1_festival.png",
    "Detective_inspecting_clues": "c1_investigate.png",
    "Director_holding_clapperboard": "c1_biography.png",
    "Doctor_wearing_white_coat": "c1_professions_and_jobs.png",
    "Elderly_kung-fu_master": "c1_kung_fu.png",
    "Executive_holding_briefcase": "c1_boss.png",
    "Family_holding_hands": "c1_family.png",
    "Graduate_holding_diploma_scroll": "c1_student.png",
    "Hotel_receptionist_standing_at_desk": "c1_receptionist.png",
    "Martial_arts_fighter_kicking": "c1_kick.png",
    "Mother_cradling_happy_baby": "c1_mother.png",
    "Musician_playing_acoustic_guitar": "c1_rasta.png",
    "Pharmacist_holding_bottle": "c1_pharmacist.png",
    "Princess_wearing_gown_and_tiara": "c1_dress.png",
    "Professional_holding_blueprint": "c1_work.png",
    "Scientist_holding_bubbling_flask": "c1_scientist.png",
    "Singer_singing_into_vintage": "c1_singer.png",
    "Suspicious_character_looking": "c1_suspect.png",
    "Teacher_pointing_at_chalkboard": "c1_teacher.png",
    "Wizard_holding_glowing_staff": "c1_wizards.png",
}

def clean_bg_adaptive(src_path, tol=22, feather=25):
    im = Image.open(src_path).convert("RGBA")
    arr = np.array(im, dtype=np.float32)
    
    # Sample corner pixels (average of 4 corners, 12x12 patches)
    c1 = arr[:12, :12, :3].mean(axis=(0, 1))
    c2 = arr[:12, -12:, :3].mean(axis=(0, 1))
    c3 = arr[-12:, :12, :3].mean(axis=(0, 1))
    c4 = arr[-12:, -12:, :3].mean(axis=(0, 1))
    bg_rgb = (c1 + c2 + c3 + c4) / 4.0
    
    # Distance from background color
    diff = arr[:, :, :3] - bg_rgb
    dist = np.sqrt(np.sum(diff * diff, axis=2))
    
    # Alpha: 0 if dist <= tol, 1 if dist >= tol + feather
    alpha = np.clip((dist - tol) / feather, 0.0, 1.0)
    
    # Ink lines protection (any pixel with low brightness is opaque)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    dark_ink = np.clip((180 - luminance) / 30.0, 0.0, 1.0)
    alpha = np.maximum(alpha, dark_ink)
    
    arr[:, :, 3] = alpha * 255.0
    rgba = Image.fromarray(np.uint8(arr), "RGBA")
    
    # Bounding box crop
    bbox = rgba.getbbox()
    if bbox:
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        pad = int(max(w, h) * 0.03)
        x0 = max(0, bbox[0] - pad)
        y0 = max(0, bbox[1] - pad)
        x1 = min(rgba.width, bbox[2] + pad)
        y1 = min(rgba.height, bbox[3] + pad)
        cropped = rgba.crop((x0, y0, x1, y1))
    else:
        cropped = rgba
        
    # Fit into 512x512
    target_size = 512
    cw, ch = cropped.width, cropped.height
    scale = (target_size * 0.94) / max(cw, ch)
    nw, nh = int(cw * scale), int(ch * scale)
    scaled = cropped.resize((nw, nh), Image.LANCZOS)
    
    canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    ox = (target_size - nw) // 2
    oy = (target_size - nh) // 2
    canvas.paste(scaled, (ox, oy), scaled)
    return canvas

files = os.listdir(src_dir)
count = 0
for f in files:
    for prefix, target in mapping.items():
        if f.startswith(prefix):
            src_p = os.path.join(src_dir, f)
            dest_p = os.path.join(dest_dir, target)
            canvas = clean_bg_adaptive(src_p)
            canvas.save(dest_p, optimize=True)
            print(f"Processed: {target} (from {f[:35]}...)")
            count += 1
            break

print(f"\nSuccessfully converted and deployed {count} images to img/!")
