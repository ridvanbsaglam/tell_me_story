from PIL import Image
import numpy as np

def clean_bg_adaptive(src_path, tol=22, feather=25):
    im = Image.open(src_path).convert("RGBA")
    arr = np.array(im, dtype=np.float32)
    
    # Sample corner pixels (average of 4 corners, 10x10 patches)
    c1 = arr[:10, :10, :3].mean(axis=(0, 1))
    c2 = arr[:10, -10:, :3].mean(axis=(0, 1))
    c3 = arr[-10:, :10, :3].mean(axis=(0, 1))
    c4 = arr[-10:, -10:, :3].mean(axis=(0, 1))
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
    res = Image.fromarray(np.uint8(arr), "RGBA")
    return res, bg_rgb

test_path = r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\new_images\Purple_wizard_hat_sketch_4e58888f.jpg"
res, bg = clean_bg_adaptive(test_path)
print("Sampled background RGB:", bg)

# Paste on cream card
card = Image.new("RGBA", (res.width, res.height), (246, 241, 229, 255))
card.paste(res, (0, 0), res)
card.save(r"C:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\build\test_trans\test_adaptive_wizard.png")
print("Saved adaptive test")
