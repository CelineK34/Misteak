import json

with open("pricing_score_output.json") as f:
    pricing = json.load(f)

with open("inventory_module_scores.json") as f:
    supply = json.load(f)

with open("zai_payload.json") as f:
    customer_business = json.load(f)

glm_input = {
    "supply": {
        "score": supply["supply_score"],
        "label": supply["supply_label"],
        "driver": supply["supply_driver"]
    },
    "pricing": {
        "score": pricing["pricing_score"],
        "label": pricing["pricing_label"],
        "driver": pricing["pricing_driver"]
    },
    "customer": customer_business["customer"],
    "business": customer_business["business"]
}

with open("glm_payload.json", "w") as f:
    json.dump(glm_input, f, indent=2)

print("GLM input ready")