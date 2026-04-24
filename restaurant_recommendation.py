import json
import os
import anthropic

# =========================
# 1. LOAD PAYLOAD
# =========================
with open("zai_payload.json", "r") as f:
    payload = json.load(f)

print("✅ Loaded payload")

# =========================
# 2. BUILD PROMPT (UPDATED)
# =========================
def build_user_prompt(p):
    return f"""
You are a senior restaurant business analyst.

This represents ONE restaurant.

==================================================
CUSTOMER PERFORMANCE
==================================================
- Score: {p['customer']['score']:+.4f}
- Label: {p['customer']['label']}

Metrics:
- Followers: {p['customer']['metrics']['followers']:,.0f}
- Reviews: {p['customer']['metrics']['reviews']:,.0f}

Derived:
- Reviews per follower: {p['customer']['derived']['reviews_per_follower']:.4f}
- Engagement Level: {p['customer']['derived']['engagement_level']}
- Interpretation: {p['customer']['derived']['engagement_interpretation']}

Insight:
- Strength: {p['customer']['insight']['strength']}
- Weakness: {p['customer']['insight']['weakness']}

==================================================
BUSINESS PERFORMANCE
==================================================
- Score: {p['business']['score']:+.4f}
- Label: {p['business']['label']}

Metrics:
- Rating: {p['business']['metrics']['rating']:.2f}
- Ambience: {p['business']['metrics']['ambience']:.2f}

Derived:
- Experience Level: {p['business']['derived']['experience_level']}
- Interpretation: {p['business']['derived']['experience_interpretation']}

Insight:
- Strength: {p['business']['insight']['strength']}
- Weakness: {p['business']['insight']['weakness']}

==================================================
TASKS
==================================================

1. CUSTOMER SCORE EXPLANATION
Explain WHY the score occurs:
- Use metrics + derived + insight
- Explain trade-offs (reach vs engagement)

2. BUSINESS SCORE EXPLANATION
Explain WHY the score occurs:
- Use rating vs ambience
- Explain experience gap

3. CORE ISSUE
Identify the MAIN limiting factor

==================================================
OUTPUT FORMAT
==================================================

Customer Score Explanation:
...

Business Score Explanation:
...

Core Issue:
...
"""

# =========================
# 3. GENERATE PROMPT
# =========================
user_prompt = build_user_prompt(payload)

print("\n🧠 Prompt preview:\n")
print(user_prompt[:800])

# =========================
# 4. SETUP CLIENT (IMPORTANT)
# =========================
client = anthropic.Anthropic(
    api_key="sk-03b07a1e4b1f8c2b3c407aecdabec8816a182940d2488ec1",
    base_url="https://api.ilmu.ai/anthropic"
)

# =========================
# 5. CALL MODEL
# =========================
response = client.messages.create(
    model="ilmu-glm-5.1",   # or claude-3-sonnet if needed
    max_tokens=1200,
    messages=[
        {
            "role": "user",
            "content": user_prompt
        }
    ]
)

# =========================
# 6. EXTRACT OUTPUT
# =========================
ai_output = response.content[0].text

print("\n=== AI ANALYSIS ===\n")
print(ai_output)

# =========================
# 7. SAVE OUTPUT
# =========================
with open("zai_recommendation.txt", "w") as f:
    f.write(ai_output)

with open("zai_recommendation.json", "w") as f:
    json.dump({
        "input": payload,
        "analysis": ai_output
    }, f, indent=2)

print("\n✅ Recommendation saved!")