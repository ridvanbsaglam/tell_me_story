import json

path = r"C:\Users\rsagl\.gemini\antigravity\brain\ac962468-14fb-4403-80e1-6d3617a93d9b\.system_generated\logs\transcript.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if idx == 168:
            d = json.loads(line)
            print(d.get("content"))
