with open(r'c:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\main.luau', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i in range(275, 315):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")
