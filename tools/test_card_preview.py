from PIL import Image

# Load card base or compose a mock card
card_w, card_h = 200, 270
bg_color = (246, 241, 229, 255) # cream

test_icons = [
    ("Doctor", "c1_professions_and_jobs.png"),
    ("Princess", "c1_dress.png"),
    ("Kung Fu", "c1_kung_fu.png"),
    ("Wizard", "c1_wizards.png"),
]

sheet = Image.new("RGBA", (card_w * 4 + 50, card_h + 40), (19, 107, 133, 255)) # teal bg
for idx, (label, icon_file) in enumerate(test_icons):
    card = Image.new("RGBA", (card_w, card_h), bg_color)
    icon_path = rf"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\img\{icon_file}"
    icon = Image.open(icon_path).convert("RGBA")
    # scale icon to fit ~140x140
    icon_scaled = icon.resize((140, 140), Image.LANCZOS)
    card.paste(icon_scaled, (30, 60), icon_scaled)
    
    sheet.paste(card, (10 + idx * (card_w + 10), 20), card)

out_p = r"C:\Users\rsagl\.gemini\antigravity\brain\ac962468-14fb-4403-80e1-6d3617a93d9b\new_char_cards_preview.png"
sheet.save(out_p)
print("Saved card preview to:", out_p)
