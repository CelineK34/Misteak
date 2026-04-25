"""
pages/5_decision.py — Final AI recommendation page
Data-connected: picks best strategy from real data + GLM analysis.
Shows ranked strategies with GLM-specific "why" for each.
"""
import streamlit as st
import pandas as pd
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── CSS ───────────────────────────────────────────────────────────────────────
for css_file in ("CSS_FIle/style.css", "CSS_FIle/decision.css"):
    css_path = os.path.join(BASE, css_file)
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_sales():
    path = os.path.join(BASE, "preprocessed_restaurant_sales_data.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

@st.cache_data
def load_inventory():
    path = os.path.join(BASE, "preprocessed_inventory_data.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

def load_json(filename):
    path = os.path.join(BASE, filename)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

sales_df = load_sales()
inventory_df = load_inventory()
glm_payload = load_json("glm_payload.json")
glm_result = load_json("glm_result.json")
pricing_output = load_json("pricing_score_output.json")
inventory_scores = load_json("inventory_module_scores.json")

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<h1 class='page-header-title'>Final Decision</h1>
<p class='page-header-sub'>AI's best recommended action based on your data</p>
""", unsafe_allow_html=True)

# ── RISK BADGE COLORS ────────────────────────────────────────────────────────
def risk_color(risk: str) -> str:
    if "High" in risk:
        return "#ef4444"
    if "Medium" in risk:
        return "#f59e0b"
    return "#008b5b"

def risk_badge_colors(risk: str) -> tuple[str, str]:
    if "Medium" in risk:
        return "#fef3c7", "#92400e"
    if "High" in risk:
        return "#fee2e2", "#991b1b"
    return "#d0f5e8", "#005c3e"

# ── GLM INSIGHT EXTRACTOR ─────────────────────────────────────────────────────
def extract_glm_section(report, heading):
    if not report:
        return ""
    pattern = rf"##\s*\d*\.?\s*{re.escape(heading)}.*?\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, report, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1).strip().replace("**", "")
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return " ".join(sentences[:2])
    return ""

glm_report = glm_result.get("report", "")
pricing_summary = pricing_output.get("glm_summary", "")
supply_summary = inventory_scores.get("glm_summary", "")
supply_driver = glm_payload.get("supply", {}).get("driver", "")
pricing_driver = glm_payload.get("pricing", {}).get("driver", "")
customer_insight = glm_payload.get("customer", {}).get("insight", {})
customer_weakness = customer_insight.get("weakness", "")
customer_strength = customer_insight.get("strength", "")
business_insight = glm_payload.get("business", {}).get("insight", {})
business_weakness = business_insight.get("weakness", "")
core_issue = extract_glm_section(glm_report, "Core Issue")

# ── STRATEGY ENGINE (same as 3_strategies) ───────────────────────────────────
def generate_strategies(sales_df, inventory_df, glm_payload, glm_report,
                        pricing_summary, supply_summary):
    strategies = []
    pricing_score = glm_payload.get("pricing", {}).get("score", 0.5)
    supply_score = glm_payload.get("supply", {}).get("score", 0.5)
    customer_score = glm_payload.get("customer", {}).get("score", 0)
    business_score = glm_payload.get("business", {}).get("score", 0)

    if sales_df.empty:
        return strategies

    item_stats = sales_df.groupby("menu_item_name").agg(
        total_revenue=("revenue", "sum"),
        avg_margin=("profit_margin", "mean"),
        total_qty=("quantity_sold", "sum"),
        avg_price=("actual_selling_price", "mean"),
        avg_cost=("typical_ingredient_cost", "mean"),
        avg_market_price=("observed_market_price", "mean"),
    ).reset_index()

    # ── 1. Bundle Strategy ─────────────────────────────────────────────────
    top2 = item_stats.nlargest(2, "total_revenue")
    if len(top2) >= 2:
        item_a, item_b = top2.iloc[0], top2.iloc[1]
        bundle_price = (item_a["avg_price"] + item_b["avg_price"]) * 0.9
        combined_margin = (item_a["avg_margin"] + item_b["avg_margin"]) / 2
        profit_uplift = round(combined_margin * 22, 1)
        confidence = min(95, int(70 + pricing_score * 25))
        risk = "High Risk" if pricing_score < 0.4 else "Medium Risk"

        pricing_section = extract_glm_section(glm_report, "Pricing")
        if pricing_section:
            desc = (
                f"Create a combo at RM {bundle_price:.2f} (vs RM {item_a['avg_price'] + item_b['avg_price']:.2f} separate). "
                f"Both are top performers with combined margin of {combined_margin:.0%}. "
                f"AI insight: {pricing_section}"
            )
        elif pricing_summary:
            desc = (
                f"Create a combo at RM {bundle_price:.2f} (vs RM {item_a['avg_price'] + item_b['avg_price']:.2f} separate). "
                f"Both are top performers with combined margin of {combined_margin:.0%}. "
                f"AI analysis: {pricing_summary}"
            )
        else:
            desc = (
                f"Create a combo at RM {bundle_price:.2f} (vs RM {item_a['avg_price'] + item_b['avg_price']:.2f} separate). "
                f"Both are top performers with combined margin of {combined_margin:.0%}. "
                f"Bundling increases average order value and drives volume for two proven items."
            )

        actions = []
        rec_section = extract_glm_section(glm_report, "Recommendation")
        if rec_section:
            for line in rec_section.split("\n"):
                clean = line.strip().lstrip("-*0123456789. ").strip()
                if clean and len(clean) > 10:
                    actions.append(clean)
        if len(actions) < 3:
            actions = ["Create combo menu signage", "Train staff on bundle offer", "Track combo vs individual sales"]

        # Strategy-specific "why" from GLM
        why = (
            f"Your top 2 earners are {item_a['menu_item_name']} and {item_b['menu_item_name']}. "
            f"Bundling them targets your strongest revenue drivers. "
        )
        if pricing_driver:
            why += f"AI notes your pricing is {pricing_driver}, so a bundle deal adds value without relying on price increases."

        strategies.append({
            "title": f"Bundle {item_a['menu_item_name']} + {item_b['menu_item_name']}",
            "risk": risk,
            "profit_impact": f"+{profit_uplift:.0f}%",
            "desc": desc,
            "confidence": confidence,
            "actions": actions[:3],
            "why": why,
        })

    # ── 2. Price Optimization ──────────────────────────────────────────────
    if pricing_score < 0.6:
        weak_margin = item_stats.nsmallest(1, "avg_margin")
        if not weak_margin.empty:
            w = weak_margin.iloc[0]
            price_gap = w["avg_market_price"] - w["avg_price"]
            if price_gap > 0:
                new_price = w["avg_price"] + price_gap * 0.5
                profit_uplift = round((1 - w["avg_margin"]) * 15, 1)
                if pricing_summary:
                    desc = (
                        f"{w['menu_item_name']} is priced RM {w['avg_price']:.2f} but market average is RM {w['avg_market_price']:.2f}. "
                        f"Raising to RM {new_price:.2f} would boost margins. "
                        f"AI analysis: {pricing_summary}"
                    )
                else:
                    desc = (
                        f"{w['menu_item_name']} is priced RM {w['avg_price']:.2f} but market average is RM {w['avg_market_price']:.2f}. "
                        f"A partial price correction to RM {new_price:.2f} would boost margins with minimal demand loss, "
                        f"since your current margin is only {w['avg_margin']:.0%}."
                    )

                why = (
                    f"{w['menu_item_name']} has your lowest margin at {w['avg_margin']:.0%} and is priced below market. "
                )
                if pricing_driver:
                    why += f"AI identifies your pricing as {pricing_driver}, meaning you have room to adjust upward without losing customers."

                strategies.append({
                    "title": f"Raise {w['menu_item_name']} price to RM {new_price:.2f}",
                    "risk": "Low Risk",
                    "profit_impact": f"+{profit_uplift:.0f}%",
                    "desc": desc,
                    "confidence": min(90, int(65 + pricing_score * 30)),
                    "actions": ["Gradual price increase over 2 weeks", "Monitor customer feedback", "Compare revenue before/after"],
                    "why": why,
                })
            else:
                if pricing_summary:
                    desc = (
                        f"{w['menu_item_name']} has a margin of only {w['avg_margin']:.0%}. "
                        f"Since pricing is already at market level, focus on reducing ingredient cost. "
                        f"AI analysis: {pricing_summary}"
                    )
                else:
                    desc = (
                        f"{w['menu_item_name']} has a margin of only {w['avg_margin']:.0%}. "
                        f"Since pricing is already at market level, focus on reducing ingredient cost "
                        f"or adjusting portion size to improve profitability."
                    )

                why = f"{w['menu_item_name']} has your lowest margin at {w['avg_margin']:.0%}. "
                if pricing_driver:
                    why += f"AI identifies pricing as {pricing_driver} — cost reduction is the safer path than price increases."

                strategies.append({
                    "title": f"Optimize {w['menu_item_name']} cost structure",
                    "risk": "Medium Risk",
                    "profit_impact": "+12%",
                    "desc": desc,
                    "confidence": min(85, int(60 + pricing_score * 30)),
                    "actions": ["Review supplier contracts", "Optimize portion sizes", "Track cost per serving"],
                    "why": why,
                })

    # ── 3. Waste Reduction ─────────────────────────────────────────────────
    if not inventory_df.empty and "waste_percentage" in inventory_df.columns:
        avg_waste = inventory_df["waste_percentage"].mean()
        high_waste = inventory_df[inventory_df["waste_percentage"] > avg_waste]
        if not high_waste.empty and avg_waste > 2.0:
            worst = high_waste.nlargest(1, "waste_percentage").iloc[0]
            waste_pct = worst["waste_percentage"]
            daily_save = worst.get("price_per_unit", 10) * worst.get("daily_usage", 1) * waste_pct / 100 * 0.5

            if supply_summary:
                desc = (
                    f"{worst['item_name']} has {waste_pct:.1f}% waste — above your average of {avg_waste:.1f}%. "
                    f"Reducing waste by half would save RM {daily_save:,.0f}/day. "
                    f"AI analysis: {supply_summary}"
                )
            else:
                desc = (
                    f"{worst['item_name']} has {waste_pct:.1f}% waste — above your average of {avg_waste:.1f}%. "
                    f"Reducing waste by half would save RM {daily_save:,.0f}/day. "
                    f"Adjust prep quantities and monitor daily usage patterns."
                )

            why = f"{worst['item_name']} waste at {waste_pct:.1f}% is draining RM {daily_save:,.0f}/day. "
            if supply_driver:
                why += f"AI identifies your supply as having {supply_driver} — cutting waste directly improves this."

            strategies.append({
                "title": f"Reduce {worst['item_name']} waste ({waste_pct:.1f}%)",
                "risk": "Low Risk",
                "profit_impact": f"+{round(waste_pct * 2)}%",
                "desc": desc,
                "confidence": min(90, int(70 + supply_score * 20)),
                "actions": ["Reduce prep quantity by 15-20%", "Track daily waste levels", "Adjust reorder based on demand"],
                "why": why,
            })

    # ── 4. Customer Engagement ─────────────────────────────────────────────
    top_item = item_stats.nlargest(1, "total_revenue")
    if not top_item.empty and customer_score < 0.1:
        t = top_item.iloc[0]
        if customer_weakness:
            desc = (
                f"{t['menu_item_name']} is your top seller (RM {t['total_revenue']:,.0f} revenue, "
                f"{t['avg_margin']:.0%} margin) but customer engagement is low. "
                f"AI finding: {customer_weakness}. "
                f"Leverage social media to turn followers into active reviewers."
            )
        else:
            desc = (
                f"{t['menu_item_name']} is your top seller (RM {t['total_revenue']:,.0f} revenue, "
                f"{t['avg_margin']:.0%} margin) but customer engagement is low. "
                f"Leverage social media to drive reviews and word-of-mouth."
            )

        why = f"Your top seller {t['menu_item_name']} could bring in even more customers through reviews. "
        if customer_weakness:
            why += f"AI finds that {customer_weakness.lower()}. Fixing this unlocks free word-of-mouth growth."

        strategies.append({
            "title": f"Promote {t['menu_item_name']} on social media",
            "risk": "Low Risk",
            "profit_impact": f"+{round(t['avg_margin'] * 10)}%",
            "desc": desc,
            "confidence": min(85, int(60 + max(0, customer_score + 1) * 20)),
            "actions": ["Create social media posts featuring this item", "Run review incentive campaign", "Track engagement and foot traffic"],
            "why": why,
        })

    # ── 5. Business Experience ─────────────────────────────────────────────
    business_score = glm_payload.get("business", {}).get("score", 0)
    if business_score < 0.1 and business_weakness:
        why = f"AI identifies that {business_weakness.lower()}. "
        if core_issue:
            why += f"This is linked to your core issue: {core_issue}"

        strategies.append({
            "title": "Improve restaurant atmosphere",
            "risk": "Medium Risk",
            "profit_impact": "+20%",
            "desc": (
                f"AI finding: {business_weakness}. "
                f"Improving the dining atmosphere lets you charge more and keeps customers coming back. "
                f"Even small changes like better lighting, music, or table setup can make a big difference."
            ),
            "confidence": min(80, int(65 + max(0, business_score + 1) * 15)),
            "actions": ["Refresh lighting and decor", "Add background music", "Collect customer feedback on atmosphere"],
            "why": why,
        })

    # ── Fallback ───────────────────────────────────────────────────────────
    if not strategies:
        strategies.append({
            "title": "Analyze business performance",
            "risk": "Low Risk",
            "profit_impact": "+10%",
            "desc": "Run the AI analysis in Settings to generate data-driven strategies.",
            "confidence": 60,
            "actions": ["Go to Settings page", "Run AI analysis", "Return here for strategies"],
            "why": "No AI analysis has been run yet. Complete the analysis to get personalized recommendations.",
        })

    return strategies

# ── GENERATE & RANK ──────────────────────────────────────────────────────────
all_strategies = generate_strategies(
    sales_df, inventory_df, glm_payload, glm_report,
    pricing_summary, supply_summary
)

def strategy_score(s):
    profit_val = float(s["profit_impact"].replace("+", "").replace("%", ""))
    risk_mult = {"Low Risk": 1.0, "Medium Risk": 0.8, "High Risk": 0.5}.get(s["risk"], 0.7)
    return s["confidence"] * profit_val * risk_mult

ranked = sorted(all_strategies, key=strategy_score, reverse=True)
best = ranked[0] if ranked else None

if not best:
    st.warning("No strategies available. Run AI analysis in Settings first.")
    st.stop()

# ── COMPUTE EXPECTED RESULTS ─────────────────────────────────────────────────
total_revenue = sales_df["revenue"].sum() if not sales_df.empty else 0
total_profit = (
    (sales_df["actual_selling_price"] - sales_df["typical_ingredient_cost"])
    * sales_df["quantity_sold"]
).sum() if not sales_df.empty else 0
total_orders = sales_df["quantity_sold"].sum() if not sales_df.empty else 0

profit_pct_val = float(best["profit_impact"].replace("+", "").replace("%", ""))
expected_revenue = total_revenue * (1 + profit_pct_val / 100 * 0.4)
expected_profit = total_profit * (1 + profit_pct_val / 100)
expected_orders = total_orders * (1 + profit_pct_val / 100 * 0.3)

# ── HERO CARD (#1 RECOMMENDATION) ────────────────────────────────────────────
steps_html = ""
for a in best["actions"]:
    steps_html += (
        '<div style="display:flex;align-items:center;gap:10px;padding:9px 0;'
        'border-bottom:1px solid rgba(0,0,0,0.05);">'
        '<span style="color:#008b5b;font-size:16px;font-weight:700;">&#10003;</span>'
        '<span style="font-size:14px;color:#0f172a;">' + a + '</span>'
        '</div>'
    )

risk_clr = risk_color(best["risk"])
metric_html = (
    '<div class="decision-metric-card">'
    '<div class="decision-metric-value" style="color:#008b5b;">' + best['profit_impact'] + '</div>'
    '<div class="decision-metric-label">Profit Impact</div>'
    '</div>'
    '<div class="decision-metric-card">'
    '<div class="decision-metric-value" style="color:' + risk_clr + ';">' + best['risk'] + '</div>'
    '<div class="decision-metric-label">Risk Level</div>'
    '</div>'
    '<div class="decision-metric-card">'
    '<div class="decision-metric-value">' + str(best['confidence']) + '%</div>'
    '<div class="decision-metric-label">AI Confidence</div>'
    '</div>'
)

hero_html = (
    '<div class="decision-hero">'
    '<div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">'
    '<div style="background:#d0f5e8;border-radius:12px;width:50px;height:50px;'
    'display:flex;align-items:center;justify-content:center;font-size:24px;">🏆</div>'
    '<div>'
    '<div class="decision-rec-label">#1 Recommended Strategy</div>'
    '<div class="decision-title">' + best['title'] + '</div>'
    '</div>'
    '</div>'
    '<p class="decision-desc">' + best['desc'] + '</p>'
    '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;">'
    + metric_html +
    '</div>'
    '<div style="font-size:10px;font-weight:600;color:#94a3b8;'
    'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px;">'
    'Implementation Steps</div>'
    + steps_html +
    '<div class="decision-why">'
    '<div class="decision-why-label">Why this strategy?</div>'
    '<div class="decision-why-text">' + best['why'] + '</div>'
    '</div>'
    '</div>'
)

st.markdown(hero_html, unsafe_allow_html=True)

# ── Expected Results ──────────────────────────────────────────────────────────
e1, e2, e3, e4 = st.columns(4)

for col, label, value in zip(
    [e1, e2, e3, e4],
    ["Expected Revenue", "Expected Profit", "Expected Orders", "Timeline"],
    [
        f"RM {expected_revenue:,.0f}",
        f"RM {expected_profit:,.0f}",
        f"{expected_orders:,.0f}",
        "2 weeks",
    ],
):
    with col:
        st.markdown(
            '<div class="decision-expected-card">'
            '<div class="decision-expected-val">' + value + '</div>'
            '<div class="decision-expected-lbl">' + label + '</div>'
            '</div>',
            unsafe_allow_html=True
        )

# ── OTHER RANKED STRATEGIES (each with its own why) ──────────────────────────
other_strategies = [s for s in ranked if s["title"] != best["title"]]

if other_strategies:
    other_rows_html = ""
    for idx, opt in enumerate(other_strategies, start=2):
        bg, fg = risk_badge_colors(opt["risk"])
        risk_label = opt["risk"].replace(" Risk", "")
        other_rows_html += (
            '<div class="other-option-row">'
            '<div style="flex:1;">'
            '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
            f'<span style="background:#f1f5f9;color:#64748b;font-size:11px;font-weight:700;'
            f'width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;'
            f'justify-content:center;">#{idx}</span>'
            f'<span class="other-option-name">{opt["title"]}</span>'
            '</div>'
            f'<div style="font-size:12px;color:#64748b;margin-bottom:6px;">'
            f'<span class="risk-badge" style="background:{bg};color:{fg};">{risk_label}</span>'
            f' &middot; {opt["confidence"]}% confidence &middot; {opt["profit_impact"]} profit</div>'
            f'<div style="font-size:13px;color:#475569;line-height:1.5;">{opt["why"]}</div>'
            '</div>'
            '</div>'
        )

    st.markdown(
        '<div class="other-options-card">'
        '<div class="other-options-label">Other Strategies Considered</div>'
        + other_rows_html +
        '</div>',
        unsafe_allow_html=True
    )

# ── Back Button ───────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
if st.button("← Back to Strategies"):
    st.switch_page("pages/3_strategies.py")
