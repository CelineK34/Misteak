"""
pages/2_alerts.py — Plain-language alerts from sales + inventory + AI
No jargon — written so any restaurant owner can act on them immediately.
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

def load_glm_payload():
    path = os.path.join(BASE, "glm_payload.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

sales_df = load_sales()
inventory_df = load_inventory()
glm_data = load_glm_payload()

# ───────────────────── HEADER ─────────────────────
st.markdown("""
<h1 class='page-header-title'>AI Alerts</h1>
<p class='page-header-sub'>Things you should know about your business right now</p>
""", unsafe_allow_html=True)

alerts = []

# ───────────────────── 1. INGREDIENT SUPPLY PROBLEMS ─────────────────────
if not inventory_df.empty:
    avg_waste = inventory_df["waste_percentage"].mean()
    below_reorder = (inventory_df["current_stock"] < inventory_df["reorder_level"]).sum()
    total_rows = len(inventory_df)
    stockout_pct = below_reorder / total_rows * 100 if total_rows else 0

    waste_by_item = inventory_df.groupby("item_name")["waste_percentage"].mean()
    worst_waste_item = waste_by_item.idxmax()
    worst_waste_pct = waste_by_item.max()

    if avg_waste > 3.0 or stockout_pct > 5:
        alerts.append({
            "icon": "⚠️",
            "title": "Ingredient Supply Problems",
            "desc": (
                f"You're throwing away {avg_waste:.1f}% of ingredients on average. "
                f"{worst_waste_item} has the worst waste at {worst_waste_pct:.1f}%. "
                f"Also, {stockout_pct:.0f}% of your items are running low. "
                f"Order smarter — buy less of what gets wasted, and reorder before you run out."
            ),
            "metric_label": "Ingredients Wasted",
            "metric_value": f"{avg_waste:.1f}%",
            "impact_label": "Running Low",
            "impact_value": f"{stockout_pct:.0f}% of items",
        })

# ───────────────────── 2. PRICES TOO LOW ─────────────────────
pricing_score = glm_data.get("pricing", {}).get("score", 0.5)

if pricing_score < 0.6 and not sales_df.empty and "menu_item_name" in sales_df.columns:
    margin_by_item = sales_df.groupby("menu_item_name")["profit_margin"].mean()
    worst_item = margin_by_item.idxmin()
    worst_margin = margin_by_item.min()
    avg_margin = sales_df["profit_margin"].mean()
    gap = avg_margin - worst_margin

    alerts.append({
        "icon": "💰",
        "title": "Your Prices May Be Too Low",
        "desc": (
            f"Your {worst_item} only keeps {worst_margin:.0f} sen profit for every RM 1 you earn. "
            f"That's {gap:.0%} less than your average ({avg_margin:.0%}). "
            f"You might need to raise its price a bit or find cheaper ingredients."
        ),
        "metric_label": "Pricing Health",
        "metric_value": f"{pricing_score:.0%}",
        "impact_label": "Lowest Profit Item",
        "impact_value": f"{worst_item}",
    })

# ───────────────────── 3. PEOPLE KNOW YOU BUT DON'T REVIEW ─────────────────────
customer_score = glm_data.get("customer", {}).get("score", 0)

if customer_score < 0:
    followers = glm_data.get("customer", {}).get("metrics", {}).get("followers", 0)
    reviews = glm_data.get("customer", {}).get("metrics", {}).get("reviews", 0)
    rpf = reviews / followers if followers else 0

    alerts.append({
        "icon": "💬",
        "title": "Many Followers, Few Reviews",
        "desc": (
            f"You have {followers:,.0f} people following you, but only {reviews:,.0f} left reviews. "
            f"That means almost no one is talking about you after visiting. "
            f"Try offering a small discount for leaving a review — it helps bring in new customers."
        ),
        "metric_label": "Review Rate",
        "metric_value": f"{rpf:.1%}",
        "impact_label": "Followers",
        "impact_value": f"{followers:,.0f}",
    })

# ───────────────────── 4. ITEMS SELLING LESS ─────────────────────
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
            common = last_rev.index.intersection(prev_rev.index)

            for item in common:
                if prev_rev[item] > 0:
                    change = (last_rev[item] - prev_rev[item]) / prev_rev[item] * 100
                    if change < -15:
                        lost = prev_rev[item] - last_rev[item]
                        alerts.append({
                            "icon": "📉",
                            "title": f"{item} Is Selling Less",
                            "desc": (
                                f"Your {item} made RM {last_rev[item]:,.0f} this month, "
                                f"down from RM {prev_rev[item]:,.0f} last month. "
                                f"That's RM {lost:,.0f} less in your pocket. "
                                f"Try a promotion or small price cut to bring customers back."
                            ),
                            "metric_label": "Sales Drop",
                            "metric_value": f"{abs(change):.0f}%",
                            "impact_label": "Money Lost",
                            "impact_value": f"RM {lost:,.0f}/month",
                        })

# ───────────────────── 5. STAR ITEM OPPORTUNITY ─────────────────────
if not sales_df.empty and "menu_item_name" in sales_df.columns:
    top_item = sales_df.groupby("menu_item_name").agg(
        revenue=("revenue", "sum"),
        margin=("profit_margin", "mean"),
        qty=("quantity_sold", "sum"),
    )
    best = top_item.nlargest(1, "revenue")

    for item, row in best.iterrows():
        alerts.append({
            "icon": "🌟",
            "title": f"{item} Is Your Best Seller",
            "desc": (
                f"{item} earned you RM {row['revenue']:,.0f} total — "
                f"your top earner! You keep {row['margin']:.0%} as profit on each one sold. "
                f"You could raise the price a little since people clearly love it."
            ),
            "metric_label": "Total Earned",
            "metric_value": f"RM {row['revenue']:,.0f}",
            "impact_label": "Profit Kept",
            "impact_value": f"{row['margin']:.0%}",
        })

# ───────────────────── 6. TOO MUCH WASTE ON SPECIFIC ITEMS ─────────────────────
if not inventory_df.empty and "waste_percentage" in inventory_df.columns:
    waste_by_item = inventory_df.groupby("item_name").agg(
        waste_pct=("waste_percentage", "mean"),
        price_per_unit=("price_per_unit", "mean"),
        daily_usage=("daily_usage", "mean"),
    )
    avg_waste = waste_by_item["waste_pct"].mean()

    for item, row in waste_by_item.iterrows():
        if row["waste_pct"] > avg_waste * 1.5 and row["waste_pct"] > 3.5:
            daily_loss = row["price_per_unit"] * row["daily_usage"] * row["waste_pct"] / 100
            alerts.append({
                "icon": "🗑️",
                "title": f"Throwing Away Too Much {item}",
                "desc": (
                    f"You waste {row['waste_pct']:.1f}% of {item} every day — "
                    f"that's {row['waste_pct']/avg_waste:.0f}x more than your average. "
                    f"You're losing about RM {daily_loss:.2f} daily just on {item}. "
                    f"Buy less or use smaller portions to cut the waste."
                ),
                "metric_label": "Wasted",
                "metric_value": f"{row['waste_pct']:.1f}%",
                "impact_label": "Lost Daily",
                "impact_value": f"RM {daily_loss:.2f}",
            })

# ───────────────────── 7. RUNNING OUT OF STOCK SOON ─────────────────────
if not inventory_df.empty and "current_stock" in inventory_df.columns:
    below = inventory_df[inventory_df["current_stock"] < inventory_df["reorder_level"]]
    if not below.empty:
        below = below.copy()
        below["ratio"] = below["current_stock"] / below["reorder_level"]
        critical = below.nsmallest(3, "ratio")

        for _, r in critical.iterrows():
            days_left = r["current_stock"] / r["daily_usage"] if r["daily_usage"] > 0 else 999
            lead = r["lead_time"]
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
