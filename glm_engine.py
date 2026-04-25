import json
import anthropic
import os

# =========================
# 1. INIT GLM CLIENT
# =========================
client = anthropic.Anthropic(
    api_key="sk-03b07a1e4b1f8c2b3c407aecdabec8816a182940d2488ec1",
    base_url="https://api.ilmu.ai/anthropic"
)

# =========================
# 2. LOAD INPUT
# =========================
with open("glm_payload.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# =========================
# 3. BUILD PROMPT
# =========================
def build_prompt(data):

    return f"""
You are a senior restaurant business intelligence analyst.

You will analyze 4 modules:

1. Supply (inventory efficiency, waste, risk)
2. Pricing (margin strength, pricing power)
3. Customer (engagement, demand strength)
4. Business (experience quality, overall performance)

---

INPUT DATA:
{json.dumps(data, indent=2)}

---

TASK:
Generate a professional business report in Markdown format.

Your output MUST include:

# 1. Executive Summary
- Overall business health interpretation

# 2. Customer Score Explanation
- Explain in business language
- Include real numbers from input
- Explain cause-effect clearly

# 3. Business Score Explanation
- Explain experience gap or strength

# 4. Pricing Analysis
- Profitability explanation
- Market positioning

# 5. Supply Chain Analysis
- Risk, waste, stability explanation

# 6. Core Issue (VERY IMPORTANT)
- Identify ONE main problem
- Explain root cause relationship between modules

# 7. Recommendations (3 actionable steps)
- Clear business actions
- Must be practical for F&B owner

---

STYLE:
- Simple business English
- No technical ML jargon
- Focus on decisions, not math
- Very structured like consulting report

Return ONLY Markdown text.
"""

# =========================
# 4. CALL GLM
# =========================
def run_glm():

    response = client.messages.create(
        model="ilmu-glm-5.1",
        max_tokens=2500,
        system="You are a professional restaurant business analyst.",
        messages=[
            {
                "role": "user",
                "content": build_prompt(data)
            }
        ]
    )

    # ✅ SAFE TEXT EXTRACTION (works for all GLM formats)
    if hasattr(response.content[0], "text"):
        result = response.content[0].text
    else:
        result = str(response.content)

    return result.strip()

# =========================
# 5. SAVE OUTPUT
# =========================
if __name__ == "__main__":

    print("🚀 Sending data to GLM...")

    report = run_glm()

    # =========================
    # 1. Save Markdown Report
    # =========================
    with open("glm_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    # =========================
    # 2. Save JSON for frontend
    # =========================
    output_json = {
        "report": report,
        "status": "success"
    }

    with open("glm_result.json", "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2, ensure_ascii=False)

    print("✅ GLM report generated successfully!")
    print("📄 glm_report.md ready")
    print("📊 glm_result.json ready for Streamlit")

if not os.path.exists("glm_payload.json"):
    raise FileNotFoundError("glm_payload.json not found. Run glm_payload.py first")