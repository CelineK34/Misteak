"""
pages/2_alerts.py — Plain-language alerts with specific item names
Every alert tells you exactly which item and exactly what to do.
"""
import streamlit as st
import pandas as pd
import json
import os
from html import escape
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ───────────────────── CSS ─────────────────────
for css_file in ("CSS_FIle/style.css", "CSS_FIle/alerts.css"):
    css_path = os.path.join(BASE, css_file)
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ───────────────────── LOAD DATA ─────────────────────
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
glm_data = load_json("glm_payload.json")
glm_result = load_json("glm_result.json")

# ───────────────────── HEADER ─────────────────────
st.markdown("""
<h1 class='page-header-title'>AI Alerts</h1>
<p class='page-header-sub'>Things you should know about your business right now</p>
""", unsafe_allow_html=True)

alerts = []

# ── Precompute item stats ────────────────────────────────────────────────────
if not sales_df.empty and "menu_item_name" in sales_df.columns:
    item_stats = sales_df.groupby("menu_item_name").agg(
        revenue=("revenue", "sum"),
        margin=("profit_margin", "mean"),
        qty=("quantity_sold", "sum"),
        price=("actual_selling_price", "mean"),
        cost=("typical_ingredient_cost", "mean"),
        market=("observed_market_price", "mean"),
    ).reset_index()
else:
    item_stats = pd.DataFrame()

# ───────────────────── 1. INGREDIENTS BEING WASTED (specific items) ──────────
if not inventory_df.empty and "waste_percentage" in inventory_df.columns:
    waste_by_item = inventory_df.groupby("item_name").agg(
        waste_pct=("waste_percentage", "mean"),
        price_per_unit=("price_per_unit", "mean"),
        daily_usage=("daily_usage", "mean"),
        current_stock=("current_stock", "mean"),
        reorder_level=("reorder_level", "mean"),
        lead_time=("lead_time", "mean"),
    ).reset_index().sort_values("waste_pct", ascending=False)

    avg_waste = waste_by_item["waste_pct"].mean()

    # Show top 3 worst waste items
    for _, row in waste_by_item.head(3).iterrows():
        item = row["item_name"]
        waste = row["waste_pct"]
        daily_loss = row["price_per_unit"] * row["daily_usage"] * waste / 100

        if waste > avg_waste:
            # Find which menu items use this ingredient
            related_items = ""
            if not sales_df.empty and "key_ingredients_tags" in sales_df.columns:
                tags_df = sales_df[["menu_item_name", "key_ingredients_tags"]].drop_duplicates("menu_item_name")
                matches = []
                item_lower = item.lower()
                for _, t in tags_df.iterrows():
                    tags = str(t["key_ingredients_tags"]).lower()
                    if item_lower in tags or (item == "Chicken" and "chicken" in tags) or (item == "Eggs" and "egg" in tags) or (item == "Milk" and "milk" in tags) or (item == "Rice" and "rice" in tags) or (item == "Onion" and "onion" in tags):
                        matches.append(t["menu_item_name"])
                if matches:
                    related_items = f" This affects {', '.join(matches[:3])}."

            alerts.append({
                "icon": "🗑️",
                "title": f"Throwing Away Too Much {item}",
                "desc": (
                    f"You waste {waste:.1f}% of {item} every day — "
                    f"that's above your average of {avg_waste:.1f}%. "
                    f"You're losing about RM {daily_loss:.2f} daily just on {item}."
                    f"{related_items} "
                    f"Buy less or use smaller portions to cut the waste."
                ),
                "metric_label": "Wasted",
                "metric_value": f"{waste:.1f}%",
                "impact_label": "Lost Daily",
                "impact_value": f"RM {daily_loss:.2f}",
            })

# ───────────────────── 2. RUNNING LOW ON INGREDIENTS (specific) ──────────────
if not inventory_df.empty and "current_stock" in inventory_df.columns:
    below = inventory_df[inventory_df["current_stock"] < inventory_df["reorder_level"]]
    if not below.empty:
        below_agg = below.groupby("item_name").agg(
            stock=("current_stock", "mean"),
            reorder=("reorder_level", "mean"),
            usage=("daily_usage", "mean"),
            lead=("lead_time", "mean"),
        ).reset_index()
        below_agg["days_left"] = below_agg["stock"] / below_agg["usage"]
        below_agg["ratio"] = below_agg["stock"] / below_agg["reorder"]
        critical = below_agg.nsmallest(3, "days_left")

        for _, r in critical.iterrows():
            days_left = r["days_left"]
            lead = r["lead"]
            urgent = " — ORDER NOW!" if days_left <= lead else ""

            alerts.append({
                "icon": "🚨",
                "title": f"Running Low on {r['item_name']}{urgent}",
                "desc": (
                    f"You only have about {days_left:.0f} days of {r['item_name']} left. "
                    f"But it takes {lead:.0f} days for your supplier to deliver. "
                    f"If you don't order now, you might run out before the next delivery arrives."
                ),
                "metric_label": "Days Left",
                "metric_value": f"{days_left:.0f}",
                "impact_label": "Delivery Takes",
                "impact_value": f"{lead:.0f} days",
            })

# ───────────────────── 3. PRICES TOO LOW (specific menu items) ───────────────
pricing_score = glm_data.get("pricing", {}).get("score", 0.5)
pricing_summary = ""
# Try to get GLM pricing summary
pricing_output = load_json("pricing_score_output.json")
pricing_summary = pricing_output.get("glm_summary", "")

if pricing_score < 0.6 and not item_stats.empty:
    # Show bottom 3 margin items
    low_margin = item_stats.nsmallest(3, "margin")
    avg_margin = item_stats["margin"].mean()

    for _, w in low_margin.iterrows():
        item = w["menu_item_name"]
        margin = w["margin"]
        price = w["price"]
        cost = w["cost"]
        market = w["market"]
        gap = avg_margin - margin

        if price < market:
            hint = f"You're charging RM {price:.2f} but the market average is RM {market:.2f}. You could raise the price."
        else:
            hint = f"You're already priced above market at RM {price:.2f} (market avg RM {market:.2f}). Try finding cheaper suppliers for RM {cost:.2f}/unit ingredients."

        ai_note = f" AI analysis: {pricing_summary}" if pricing_summary else ""

        alerts.append({
            "icon": "💰",
            "title": f"{item} — Low Profit Per Item",
            "desc": (
                f"Your {item} only keeps {margin:.0%} as profit (cost RM {cost:.2f}, sell RM {price:.2f}). "
                f"That's {gap:.0%} below your average of {avg_margin:.0%}. "
                f"{hint}{ai_note}"
            ),
            "metric_label": "Profit Per Item",
            "metric_value": f"{margin:.0%}",
            "impact_label": "Cost",
            "impact_value": f"RM {cost:.2f}",
        })

# ───────────────────── 4. PEOPLE KNOW YOU BUT DON'T REVIEW ───────────────────
customer_score = glm_data.get("customer", {}).get("score", 0)

if customer_score < 0:
    followers = glm_data.get("customer", {}).get("metrics", {}).get("followers", 0)
    reviews = glm_data.get("customer", {}).get("metrics", {}).get("reviews", 0)
    rpf = reviews / followers if followers else 0
    customer_weakness = glm_data.get("customer", {}).get("insight", {}).get("weakness", "")

    ai_note = f" AI finding: {customer_weakness}." if customer_weakness else ""

    alerts.append({
        "icon": "💬",
        "title": "Many Followers, Few Reviews",
        "desc": (
            f"You have {followers:,.0f} people following you, but only {reviews:,.0f} left reviews. "
            f"That means almost no one is talking about you after visiting."
            f"{ai_note} "
            f"Try offering a small discount for leaving a review — it helps bring in new customers."
        ),
        "metric_label": "Review Rate",
        "metric_value": f"{rpf:.1%}",
        "impact_label": "Followers",
        "impact_value": f"{followers:,.0f}",
    })

# ───────────────────── 5. ITEMS SELLING LESS (specific items) ────────────────
if not sales_df.empty and "date" in sales_df.columns and "menu_item_name" in sales_df.columns:
    sales_df["date"] = pd.to_datetime(sales_df["date"], errors="coerce")
    sales_df = sales_df.dropna(subset=["date"])

    if len(sales_df) > 30:
        max_date = sales_df["date"].max()
        last30 = sales_df[sales_df["date"] > max_date - pd.Timedelta(days=30)]
        prev30 = sales_df[
            (sales_df["date"] <= max_date - pd.Timedelta(days=30))
            & (sales_df["date"] > max_date - pd.Timedelta(days=60))
        ]

        if not last30.empty and not prev30.empty:
            last_rev = last30.groupby("menu_item_name")["revenue"].sum()
            prev_rev = prev30.groupby("menu_item_name")["revenue"].sum()
            last_qty = last30.groupby("menu_item_name")["quantity_sold"].sum()
            prev_qty = prev30.groupby("menu_item_name")["quantity_sold"].sum()
            common = last_rev.index.intersection(prev_rev.index)

            for item in common:
                if prev_rev[item] > 0:
                    change = (last_rev[item] - prev_rev[item]) / prev_rev[item] * 100
                    if change < -15:
                        lost = prev_rev[item] - last_rev[item]
                        qty_drop = prev_qty[item] - last_qty[item]
                        alerts.append({
                            "icon": "📉",
                            "title": f"{item} Is Selling Less",
                            "desc": (
                                f"Your {item} made RM {last_rev[item]:,.0f} this month, "
                                f"down from RM {prev_rev[item]:,.0f} last month. "
                                f"That's {qty_drop:,.0f} fewer orders and RM {lost:,.0f} less in your pocket. "
                                f"Try a promotion or small price cut to bring customers back."
                            ),
                            "metric_label": "Sales Drop",
                            "metric_value": f"{abs(change):.0f}%",
                            "impact_label": "Money Lost",
                            "impact_value": f"RM {lost:,.0f}/month",
                        })

# ───────────────────── 6. STAR ITEM OPPORTUNITY (specific top 3) ─────────────
if not item_stats.empty:
    top3 = item_stats.nlargest(3, "revenue")

    for _, t in top3.iterrows():
        item = t["menu_item_name"]
        # Check if priced below market → can raise
        if t["price"] < t["market"]:
            hint = f"You charge RM {t['price']:.2f} but market average is RM {t['market']:.2f} — you could raise the price."
        elif t["margin"] < 0.80:
            hint = f"You keep {t['margin']:.0%} profit per item — a small price bump could boost that further."
        else:
            hint = f"People clearly love it — keep the quality up and it will keep selling."

        alerts.append({
            "icon": "🌟",
            "title": f"{item} Is a Top Earner",
            "desc": (
                f"{item} earned you RM {t['revenue']:,.0f} total, "
                f"selling {t['qty']:,.0f} units at RM {t['price']:.2f} each. "
                f"You keep {t['margin']:.0%} as profit. {hint}"
            ),
            "metric_label": "Total Earned",
            "metric_value": f"RM {t['revenue']:,.0f}",
            "impact_label": "Profit Kept",
            "impact_value": f"{t['margin']:.0%}",
        })

# ───────────────────── 7. ITEMS PRICED BELOW MARKET (specific) ───────────────
if not item_stats.empty:
    underpriced = item_stats[item_stats["price"] < item_stats["market"]].sort_values("margin")
    for _, u in underpriced.head(3).iterrows():
        gap = u["market"] - u["price"]
        alerts.append({
            "icon": "🏷️",
            "title": f"{u['menu_item_name']} Is Underpriced",
            "desc": (
                f"Your {u['menu_item_name']} sells at RM {u['price']:.2f} but the market average is RM {u['market']:.2f}. "
                f"That's RM {gap:.2f} per item you're not collecting. "
                f"With {u['qty']:,.0f} units sold, raising the price by just RM {gap * 0.5:.2f} could add RM {gap * 0.5 * u['qty']:,.0f} in revenue."
            ),
            "metric_label": "Your Price",
            "metric_value": f"RM {u['price']:.2f}",
            "impact_label": "Market Avg",
            "impact_value": f"RM {u['market']:.2f}",
        })

# ───────────────────── 8. WEAK ATMOSPHERE ────────────────────────────────────
business_score = glm_data.get("business", {}).get("score", 0)
business_weakness = glm_data.get("business", {}).get("insight", {}).get("weakness", "")

if business_score < 0 and business_weakness:
    alerts.append({
        "icon": "🍽️",
        "title": "Restaurant Atmosphere Needs Work",
        "desc": (
            f"AI finding: {business_weakness}. "
            f"Customers enjoy the food but the overall experience falls flat. "
            f"Even small improvements like better lighting, music, or table setup can make customers stay longer and spend more."
        ),
        "metric_label": "Experience Score",
        "metric_value": "Weak",
        "impact_label": "Fix",
        "impact_value": "Atmosphere",
    })

# ───────────────────── RENDER ─────────────────────
def safe(val):
    if val is None:
        return ""
    return escape(str(val))

def render(alert):
    icon = alert["icon"]
    return (
        '<div class="alert-card">'
        '<div class="alert-card-inner">'
        f'<div class="alert-icon">{icon}</div>'
        '<div style="flex:1;">'
        '<div class="alert-badge-row">'
        f'<span class="alert-title">{safe(alert["title"])}</span>'
        '</div>'
        f'<p class="alert-desc">{safe(alert["desc"])}</p>'
        '<div class="alert-metrics-row">'
        '<div class="alert-metric-box">'
        f'<div class="alert-metric-label">{safe(alert["metric_label"])}</div>'
        f'<div class="alert-metric-value">{safe(alert["metric_value"])}</div>'
        '</div>'
        '<div class="alert-metric-box">'
        f'<div class="alert-metric-label">{safe(alert["impact_label"])}</div>'
        f'<div class="alert-metric-value">{safe(alert["impact_value"])}</div>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )

if alerts:
    for a in alerts:
        try:
            st.markdown(render(a), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Alert render failed: {e}")
else:
    st.success("No critical alerts detected — everything looks good!")
