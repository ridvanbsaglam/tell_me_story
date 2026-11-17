import os
from PIL import Image
import numpy as np

def make_transparent_sketch(img_path, tol=245):
    im = Image.open(img_path).convert("RGBA")
    arr = np.array(im, dtype=np.float32)
    # R, G, B, A
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    # Brightness / whiteness
    # White is (255, 255, 255)
    # Calculate distance from white
    # If all channels > 250, alpha -> 0
    # For channels between 220 and 255, feather alpha
    min_c = np.minimum(np.minimum(r, g), b)
    max_c = np.maximum(np.maximum(r, g), b)
    
    # Saturation
    sat = (max_c - min_c) / np.maximum(max_c, 1.0)
    
    # Whiteness: high brightness AND low saturation
    whiteness = (min_c / 255.0) * (1.0 - sat * 0.8)
    
    # Map whiteness to alpha:
    # whiteness >= 0.98 -> alpha 0
    # whiteness <= 0.85 -> alpha 1
    alpha = np.clip((0.98 - whiteness) / (0.98 - 0.85), 0.0, 1.0)
    
    # For dark ink lines, ensure full opacity
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    dark_mask = luminance < 180
    alpha = np.maximum(alpha, np.clip((220 - luminance) / 40.0, 0.0, 1.0))
    
    arr[:, :, 3] = alpha * 255.0
    out = Image.fromarray(np.uint8(arr), "RGBA")
    return out

# Test on wizard hat
test_path = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\new_images\Purple_wizard_hat_sketch_4e58888f.jpg"
res = make_transparent_sketch(test_path)
out_dir = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\build\test_trans"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "test_wizard_hat.png")
res.save(out_file)
print("Saved test transparent image to:", out_file)
