import os, re

src_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\new_images"
files = [f for f in os.listdir(src_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# Comprehensive mapping dictionary
# Match keywords in file names to target IDs
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
    ("Carnival_carousel", "c2_01.png"),                     # Atlıkarınca
    ("Theater_stage_with_drama_masks", "c2_02.png"),        # Tiyatro Sahnesi
    ("Circus_tent_with_pennants", "c2_03.png"),             # Sirk Çadırı
    ("Victorian_haunted_mansion", "c2_04.png"),             # Perili Ev
    ("Palm_tree_on_desert_island", "c2_05.png"),            # Tropik Ada
    ("Medieval_stone_castle", "c2_06.png"),                 # Ortaçağ Kalesi
    ("Space_station_floating", "c2_07.png"),                # Uzay İstasyonu
    ("Neoclassical_building", "c2_government.png"),          # Hükümet / Mahkeme
    ("Steel_bank_vault_door", "c2_mortgage_loan.png"),      # Banka Kasası
    ("Sports_stadium", "c2_stadium.png"),                   # Stadyum

    # Weather & Atmosphere (14)
    ("Smiling_sun_radiating_rays", "c3_01.png"),            # Güneş
    ("Rainbow_curving_over_cloud", "c3_02.png"),            # Gökkuşağı
    ("Snow-covered_mountain", "c3_03.png"),                 # Karlı Gece & Dağ
    ("Shooting_stars_streaking", "c3_04.png"),              # Meteor Yağmuru
    ("Beach_umbrella_towel", "c3_beach.png"),               # Plaj
    ("Desert_sandstorm_whirlwind", "c3_dust.png"),          # Kum Fırtınası
    ("Ground_fissure_splitting", "c3_earthquake.png"),      # Deprem
    ("River_flood_waters", "c3_flood.png"),                 # Sel
    ("Wooden_bench_under_tree", "c3_park.png"),             # Park
    ("Rain_falling_from_cloud", "c3_rain.png"),             # Yağmur
    ("Lightning_striking_from_rain_cloud", "c3_storm.png"), # Fırtına
    ("Smiling_sun_wearing_sunglasses", "c3_sun.png"),       # Gözlüklü Güneş
    ("Tsunami_wave_with_white_crest", "c3_tsunami.png"),    # Tsunami
    ("Swords_clashing_with_sparks", "c3_war.png"),          # Savaş / Kılıçlar

    # Twist (10)
    ("Drama_masks_sketch", "c4_bipolar.png"),               # Tiyatro Maskeleri
    ("Crocodile_floating_in_water", "c4_crocodile.png"),    # Timsah
    ("Cartoon_Grim_Reaper", "c4_death.png"),                # Azrail
    ("Crystal_ball_on_stand", "c4_fortune_telling.png"),    # Kristal Küre
    ("Desert_scorpion_with_stinger", "c4_scorpion.png"),    # Akrep
    ("Tent_pitched_by_campfire", "c4_tent.png"),            # Kamp Çadırı
    ("Lightning_shock_with_glowing_sparks", "c4_thyroid.png"), # Elektrik Şoku
    ("Unicorn_head_sketch", "c4_unicorn.png"),              # Unicorn
    ("Voodoo_doll_with_pins", "c4_voodoo.png"),             # Voodoo Bebeği
    ("Blue_whale_swimming", "c4_whale.png"),                # Mavi Balina

    # Object (10)
    ("Crossed_vintage_mechanic_tools", "c5_construction_and_tools.png"), # Aletler
    ("Magnifying_glass_inspecting", "c5_evidences.png"),    # Büyüteç & Parmak İzi
    ("Police_handcuffs_linked", "c5_handcuff.png"),         # Kelepçe
    ("Blue_lighter_with_flickering_flame", "c5_lighter.png"), # Çakmak
    ("Rolled_treasure_map", "c5_mat.png"),                  # Hazine Haritası
    ("Glowing_DNA_strand", "c5_mutation.png"),              # DNA Sarmalı
    ("Vintage_tailor_craft_scissors", "c5_scissors.png"),   # Makas
    ("Antique_sewing_machine", "c5_sewing_machine.png"),    # Dikiş Makinesi
    ("Ice_cream_sundae_with_cherry", "c5_sundae.png"),      # Dondurma
    ("Glass_vial_with_cyan_liquid", "c5_vaccine.png"),      # İksir / Aşı
]

matched = {}
for pattern, target in mapping_rules:
    for f in files:
        if pattern.lower() in f.lower():
            if target not in matched:
                matched[target] = f
                break

print(f"Total Rules: {len(mapping_rules)}")
print(f"Total Matched Targets: {len(matched)}")

missing = [target for _, target in mapping_rules if target not in matched]
if missing:
    print("MISSING TARGETS:", missing)
else:
    print("ALL 71 TARGETS MATCHED PERFECTLY!")

# Check unmapped files in folder
mapped_files = set(matched.values())
unmapped = [f for f in files if f not in mapped_files]
print(f"Unmapped / Duplicate files ({len(unmapped)}):", unmapped)
