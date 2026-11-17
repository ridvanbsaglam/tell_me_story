import json

path = r"C:\Users\rsagl\.gemini\antigravity\brain\ac962468-14fb-4403-80e1-6d3617a93d9b\.system_generated\logs\transcript.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        d = json.loads(line)
        c = str(d.get("content", ""))
        if "prompt" in c.lower() or "tarz" in c.lower() or "dixit" in c.lower() or "stil" in c.lower():
            if idx not in [163, 169, 192, 204, 214]:
                print(f"Step {idx}: {c[:300]}...\n")
