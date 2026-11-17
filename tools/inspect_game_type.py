with open(r'c:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\main.luau', 'r', encoding='utf-8') as f:
    text = f.read()

# Check Game type definition
idx = text.find('type Game = {')
print(text[idx:idx+500])
