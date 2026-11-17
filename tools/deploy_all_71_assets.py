import os, shutil
from PIL import Image
import numpy as np

src_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\new_images"
dest_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\img"
backup_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\img_backup_full_set"

# Backup
if not os.path.exists(backup_dir):
    shutil.copytree(dest_dir, backup_dir)
    print(f"Backed up {dest_dir} to {backup_dir}")

mapping_rules = [
    # Hats (4)
    ("Yellow_propeller_beanie", "lvl_rookie.png"),
    ("Leather_fedora_with_cyan_belt", "lvl_expert.png"),
    ("Top_hat_with_ribbon", "lvl_master.png"),
    ("Purple_wizard_hat_sketch", "lvl_guru.png"),
    
    # Characters (23)
    ("Astronaut_wearing_bubble_helmet", "c1_astronaut.png"),
    ("Basketball_player_spinning_ball", "c1_basketball_player.png"),
    ("Burglar_carrying_sack_of_loot", "c1_thief.png"),
    ("Clown_smiling_sketch", "c1_festival.png"),
    ("Detective_inspecting_clues", "c1_investigate.png"),
    ("Director_holding_clapperboard", "c1_biography.png"),
    ("Doctor_wearing_white_coat", "c1_professions_and_jobs.png"),
    ("Elderly_kung-fu_master", "c1_kung_fu.png"),
    ("Executive_holding_briefcase", "c1_boss.png"),
    ("Family_holding_hands", "c1_family.png"),
    ("Graduate_holding_diploma_scroll", "c1_student.png"),
    ("Hotel_receptionist_standing_at_desk", "c1_receptionist.png"),
    ("Martial_arts_fighter_kicking", "c1_kick.png"),
    ("Mother_cradling_happy_baby", "c1_mother.png"),
    ("Musician_playing_acoustic_guitar", "c1_rasta.png"),
    ("Pharmacist_holding_bottle", "c1_pharmacist.png"),
    ("Princess_wearing_gown_and_tiara", "c1_dress.png"),
    ("Professional_holding_blueprint", "c1_work.png"),
    ("Scientist_holding_bubbling_flask", "c1_scientist.png"),
    ("Singer_singing_into_vintage", "c1_singer.png"),
    ("Suspicious_character_looking", "c1_suspect.png"),
    ("Teacher_pointing_at_chalkboard", "c1_teacher.png"),
    ("Wizard_holding_glowing_staff", "c1_wizards.png"),

    # Place (10)
    ("Carnival_carousel", "c2_01.png"),
    ("Theater_stage_with_drama_masks", "c2_02.png"),
    ("Circus_tent_with_pennants", "c2_03.png"),
    ("Victorian_haunted_mansion", "c2_04.png"),
    ("Palm_tree_on_desert_island", "c2_05.png"),
    ("Medieval_stone_castle", "c2_06.png"),
    ("Space_station_floating", "c2_07.png"),
    ("Neoclassical_building", "c2_government.png"),
    ("Steel_bank_vault_door", "c2_mortgage_loan.png"),
    ("Sports_stadium", "c2_stadium.png"),

    # Weather & Atmosphere (14)
    ("Smiling_sun_radiating_rays", "c3_01.png"),
    ("Rainbow_curving_over_cloud", "c3_02.png"),
    ("Snow-covered_mountain", "c3_03.png"),
    ("Shooting_stars_streaking", "c3_04.png"),
    ("Beach_umbrella_towel", "c3_beach.png"),
    ("Desert_sandstorm_whirlwind", "c3_dust.png"),
    ("Ground_fissure_splitting", "c3_earthquake.png"),
    ("River_flood_waters", "c3_flood.png"),
    ("Wooden_bench_under_tree", "c3_park.png"),
    ("Rain_falling_from_cloud", "c3_rain.png"),
    ("Lightning_striking_from_rain_cloud", "c3_storm.png"),
    ("Smiling_sun_wearing_sunglasses", "c3_sun.png"),
    ("Tsunami_wave_with_white_crest", "c3_tsunami.png"),
    ("Swords_clashing_with_sparks", "c3_war.png"),

    # Twist (10)
    ("Drama_masks_sketch", "c4_bipolar.png"),
    ("Crocodile_floating_in_water", "c4_crocodile.png"),
    ("Cartoon_Grim_Reaper", "c4_death.png"),
    ("Crystal_ball_on_stand", "c4_fortune_telling.png"),
    ("Desert_scorpion_with_stinger", "c4_scorpion.png"),
    ("Tent_pitched_by_campfire", "c4_tent.png"),
    ("Lightning_shock_with_glowing_sparks", "c4_thyroid.png"),
    ("Unicorn_head_sketch", "c4_unicorn.png"),
    ("Voodoo_doll_with_pins", "c4_voodoo.png"),
    ("Blue_whale_swimming", "c4_whale.png"),

    # Object (10)
    ("Crossed_vintage_mechanic_tools", "c5_construction_and_tools.png"),
    ("Magnifying_glass_inspecting", "c5_evidences.png"),
    ("Police_handcuffs_linked", "c5_handcuff.png"),
    ("Blue_lighter_with_flickering_flame", "c5_lighter.png"),
    ("Rolled_treasure_map", "c5_mat.png"),
    ("Glowing_DNA_strand", "c5_mutation.png"),
    ("Vintage_tailor_craft_scissors", "c5_scissors.png"),
    ("Antique_sewing_machine", "c5_sewing_machine.png"),
    ("Ice_cream_sundae_with_cherry", "c5_sundae.png"),
    ("Glass_vial_with_cyan_liquid", "c5_vaccine.png"),
]

def clean_bg_adaptive(src_path, tol=22, feather=25):
    im = Image.open(src_path).convert("RGBA")
    arr = np.array(im, dtype=np.float32)
    
    # 4 corners average (12x12)
    c1 = arr[:12, :12, :3].mean(axis=(0, 1))
    c2 = arr[:12, -12:, :3].mean(axis=(0, 1))
    c3 = arr[-12:, :12, :3].mean(axis=(0, 1))
    c4 = arr[-12:, -12:, :3].mean(axis=(0, 1))
    bg_rgb = (c1 + c2 + c3 + c4) / 4.0
    
    diff = arr[:, :, :3] - bg_rgb
    dist = np.sqrt(np.sum(diff * diff, axis=2))
    
    alpha = np.clip((dist - tol) / feather, 0.0, 1.0)
    
    # Dark ink lines protection
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    dark_ink = np.clip((180 - luminance) / 30.0, 0.0, 1.0)
    alpha = np.maximum(alpha, dark_ink)
    
    arr[:, :, 3] = alpha * 255.0
    rgba = Image.fromarray(np.uint8(arr), "RGBA")
    
    # Bounding box
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
matched_count = 0
for pattern, target in mapping_rules:
    for f in files:
        if pattern.lower() in f.lower():
            src_p = os.path.join(src_dir, f)
            dest_p = os.path.join(dest_dir, target)
            canvas = clean_bg_adaptive(src_p)
            canvas.save(dest_p, optimize=True)
            matched_count += 1
            print(f"[{matched_count}/71] Converted: {target:30} <- {f[:35]}...")
            break

print(f"\nALL {matched_count} IMAGES CONVERTED AND DEPLOYED SUCCESSFULLY TO {dest_dir}!")
