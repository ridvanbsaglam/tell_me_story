"""QA screenshots across all 8 screens/states of Tell Me! Rive game."""
import re, subprocess, shutil, os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
main = os.path.join(root, "main.luau")
orig = open(main, encoding="utf-8").read()

shots = [
    ("01_hello", 0, "1.5s"),
    ("02_help_modal", 7, "1.5s"),
    ("03_level1_rookie_closed", 1, "1.5s"),
    ("04_level1_rookie_flipped", 2, "1.5s"),
    ("05_level2_expert_timer", 3, "1.5s"),
    ("06_level3_master_twist", 4, "1.5s"),
    ("07_level4_guru_write", 5, "1.5s"),
    ("08_level4_guru_showcase", 6, "1.5s"),
]

qa_dir = os.path.join(root, "build", "qa")
os.makedirs(qa_dir, exist_ok=True)

try:
    for name, dbg, adv in shots:
        patched = re.sub(r"local DEBUG_MODE = \d+", f"local DEBUG_MODE = {dbg}", orig)
        open(main, "w", encoding="utf-8", newline="\n").write(patched)
        subprocess.run(["rive", ".", "--screenshot", f"--advance={adv}"], cwd=root, capture_output=True)
        shutil.copy(os.path.join(root, "build", "tell_me_story.png"), os.path.join(qa_dir, name + ".png"))
        print("captured:", name)
finally:
    open(main, "w", encoding="utf-8", newline="\n").write(orig)
