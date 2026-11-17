with open(r'c:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\main.luau', 'r', encoding='utf-8') as f:
    for idx, l in enumerate(f):
        if 'Ridvan' in l or 'Created' in l:
            print(idx+1, l)
