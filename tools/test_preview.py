from PIL import Image

bg_color = (246, 241, 229, 255) # #F6F1E5
hat = Image.open(r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\build\test_trans\test_wizard_hat.png")

card = Image.new("RGBA", (hat.width, hat.height), bg_color)
card.paste(hat, (0, 0), hat)

card.save(r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\build\test_trans\test_on_cream.png")
print("Saved preview on cream card")
