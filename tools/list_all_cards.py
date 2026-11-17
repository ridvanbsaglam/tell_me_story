import re, json

with open(r"c:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\cards_data.luau", "r", encoding="utf-8") as f:
    text = f.read()

# Parse categories and their items
cat_blocks = re.split(r'\{\s*name\s*=\s*"([^"]+)"', text)
# cat_blocks[0] is preamble, then alternating (cat_name, content)
categories = []
for i in range(1, len(cat_blocks), 2):
    cname = cat_blocks[i]
    content = cat_blocks[i+1]
    items = re.findall(r'\{\s*id\s*=\s*"([^"]+)",\s*name\s*=\s*"([^"]+)"\s*\}', content)
    categories.append({
        "category": cname,
        "items": items
    })

total = sum(len(c["items"]) for c in categories)
print(f"Total Categories: {len(categories)}, Total Cards: {total}")
for c in categories:
    print(f"\n### {c['category']} ({len(c['items'])} cards):")
    for cid, name in c["items"]:
        print(f"  - `{cid}`: {name}")
