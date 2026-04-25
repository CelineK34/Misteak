import json

with open("glm_payload.json") as f:
    data = json.load(f)

print(json.dumps(data, indent=2))