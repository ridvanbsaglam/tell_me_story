import os, re

base_dir = r"c:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story"
rml_path = os.path.join(base_dir, "scene.rml")

with open(rml_path, "r", encoding="utf-8") as f:
    content = f.read()

files = re.findall(r'file="([^"]+)"', content)
missing = []
for rel in files:
    full = os.path.join(base_dir, rel)
    if not os.path.exists(full):
        missing.append(rel)

print(f"Total assets referenced in scene.rml: {len(files)}")
print(f"Missing assets: {len(missing)}")
if missing:
    for m in missing:
        print("  -", m)
else:
    print("ALL assets are present and accounted for!")
