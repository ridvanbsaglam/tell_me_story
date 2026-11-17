import os

src_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\new_images"
files = os.listdir(src_dir)

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

found = {}
unmapped = []
for f in files:
    matched = False
    for prefix, target in mapping.items():
        if f.startswith(prefix):
            found[target] = f
            matched = True
            break
    if not matched:
        unmapped.append(f)

print(f"Mapped {len(found)} / {len(mapping)} files:")
for target, f in sorted(found.items()):
    print(f"  {target:30} <- {f}")

if unmapped:
    print("\nUnmapped files:", unmapped)
