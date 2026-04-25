"""
pages/1_dashboard.py — Simple, human-readable dashboard for restaurant owners
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ───────────────────── CSS ─────────────────────
for css_file in ("CSS_FIle/style.css", "CSS_FIle/dashboard.css"):
    css_path = os.path.join(BASE, css_file)
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ───────────────────── LOAD DATA ─────────────────────
@st.cache_data
def load_sales():
    path = os.path.join(BASE, "preprocessed_restaurant_sales_data.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

def load_glm_result():
    path = os.path.join(BASE, "glm_result.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_glm_payload():
    path = os.path.join(BASE, "glm_payload.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

sales_df = load_sales()
glm_result = load_glm_result()
glm_payload = load_glm_payload()

# ───────────────────── HEADER ─────────────────────
st.markdown("""
<h1 class='page-header-title'>Dashboard</h1>
<p class='page-header-sub'>See how your business is doing — simple and clear</p>
""", unsafe_allow_html=True)

# ───────────────────── AI INSIGHT (POINT FORM, PLAIN LANGUAGE) ─────────────────────
st.markdown("## AI Insight")

glm_report = glm_result.get("report", "")
if glm_report:
    bullets = []
    for section in glm_report.split("##"):
        section = section.strip()
        if not section:
            continue
        lines = section.split("\n")
        title = lines[0].strip().lstrip("#").strip()
        body = "\n".join(lines[1:]).strip()
        if not title or not body:
            continue

        paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
        for p in paragraphs:
            clean = p.replace("**", "")
            if clean.startswith("-") or clean.startswith("*"):
                for line in clean.split("\n"):
                    line = line.strip().lstrip("-* ").strip()
                    if line:
                        bullets.append(line)
            else:
                sentences = [s.strip() for s in clean.replace(". ", ".\n").split("\n") if s.strip()]
                for s in sentences[:2]:
                    s = s.rstrip(".")
                    bullets.append(s)

    replacements = {
        "profit margin": "profit per item",
        "profitability": "how much money you keep",
        "pricing power": "ability to charge more without losing customers",
        "marginal": "small",
        "operational": "daily running",
        "operational risk": "daily problems",
        "supply chain": "ingredient supply",
        "engagement": "customer reviews & feedback",
        "engagement rate": "review rate",
        "foot traffic": "customers walking in",
        "margin compression": "shrinking profits",
        "demand elasticity": "how sensitive customers are to price",
        "price elasticity": "how price changes affect sales",
        "intractural": "internal",
        "top-of-funnel": "initial",
        "conversion": "action rate",
        "organic word-of-mouth": "free customer recommendations",
        "paid marketing": "paid ads",
        "price-to-market ratio": "your price vs competitors",
        "price-to-cost ratio": "markup on ingredients",
        "stockout": "running out of stock",
        "supply stability": "reliable supply",
        "inventory buffers": "safety stock",
        "lead times": "delivery waiting time",
        "ambience": "restaurant atmosphere",
        "experience quality": "overall dining feel",
        "food quality": "food taste & quality",
        "cascading drag": "chain effect pulling down",
        "fragile state": "unstable position",
        "stagnant": "not growing",
        "differentiate": "stand out",
    }

    def simplify(text):
        for jargon, plain in replacements.items():
            text = text.replace(jargon, plain)
        return text

    bullet_html = "".join(
        f"<li>{simplify(b)}</li>" for b in bullets[:8]
    )
    st.markdown(
        f"<div class='alert-box'><ul style='margin:0;padding-left:20px;"
        f"line-height:1.8;font-size:14px;'>{bullet_html}</ul></div>",
        unsafe_allow_html=True,
    )
else:
    st.info("Run AI analysis in Settings page first")

# ───────────────────── SPACER ─────────────────────
st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)

# ───────────────────── COMPUTE KPIs ─────────────────────
if sales_df.empty:
    st.warning("No sales data yet. Upload your data in Settings.")
    st.stop()

revenue = sales_df["revenue"].sum()
profit = (
    (sales_df["actual_selling_price"] - sales_df["typical_ingredient_cost"])
    * sales_df["quantity_sold"]
).sum()
orders = sales_df["quantity_sold"].sum()
avg_margin = sales_df["profit_margin"].mean()

# Trend: last 30 days vs previous 30 days
if "date" in sales_df.columns and sales_df["date"].notna().any():
    max_date = sales_df["date"].max()
    last_30 = sales_df[sales_df["date"] > max_date - pd.Timedelta(days=30)]
    prev_30 = sales_df[
        (sales_df["date"] <= max_date - pd.Timedelta(days=30))
        & (sales_df["date"] > max_date - pd.Timedelta(days=60))
    ]
    rev_trend = (
        ((last_30["revenue"].sum() - prev_30["revenue"].sum()) / prev_30["revenue"].sum() * 100)
        if not prev_30.empty and prev_30["revenue"].sum() > 0 else 0
    )
    profit_trend = rev_trend * 0.6
    order_trend = (
        ((last_30["quantity_sold"].sum() - prev_30["quantity_sold"].sum())
         / prev_30["quantity_sold"].sum() * 100)
        if not prev_30.empty and prev_30["quantity_sold"].sum() > 0 else 0
    )
    margin_trend = (
        ((last_30["profit_margin"].mean() - prev_30["profit_margin"].mean())
         / prev_30["profit_margin"].mean() * 100)
        if not prev_30.empty and prev_30["profit_margin"].mean() > 0 else 0
    )
else:
    rev_trend = profit_trend = order_trend = margin_trend = 0

# ───────────────────── KPI UI (PLAIN LABELS) ─────────────────────
def trend_label(val):
    if val > 0:
        return f"Up {val:.0f}% vs last month"
    elif val < 0:
        return f"Down {abs(val):.0f}% vs last month"
    return "Same as last month"

kpi_data = [
    ("Total Sales", f"RM {revenue:,.0f}", rev_trend, trend_label(rev_trend)),
    ("Total Profit", f"RM {profit:,.0f}", profit_trend, trend_label(profit_trend)),
    ("Total Orders", f"{orders:,.0f}", order_trend, trend_label(order_trend)),
    ("Profit Per Item", f"{avg_margin:.0%}", margin_trend, trend_label(margin_trend)),
]

cols = st.columns(4)
for i, (title, value, trend, hint) in enumerate(kpi_data):
    with cols[i]:
        icon = "📈" if trend >= 0 else "📉"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-trend">{icon} {hint}</div>
        </div>
        """, unsafe_allow_html=True)

# ───────────────────── SPACER ─────────────────────
st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)

# ───────────────────── MONTHLY REVENUE CHART ─────────────────────
if "date" in sales_df.columns and sales_df["date"].notna().any():
    trend_df = (
        sales_df.groupby(sales_df["date"].dt.to_period("M"))
        .agg(revenue=("revenue", "sum"))
        .reset_index()
    )
    trend_df["month"] = trend_df["date"].astype(str)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend_df["month"],
            y=trend_df["revenue"],
            mode="lines+markers",
            name="Monthly Sales",
            line=dict(color="#008b5b", width=2.5, shape="spline"),
            marker=dict(size=6, color="#008b5b"),
            fill="tozeroy",
            fillcolor="rgba(0,139,91,0.06)",
        )
    )
    fig.update_layout(
        title=dict(text="Monthly Sales Trend", font=dict(size=16, color="#0f172a")),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#1e293b", size=12),
        xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickangle=-45),
        yaxis=dict(
            gridcolor="#f1f5f9",
            linecolor="#e2e8f0",
            tickprefix="RM ",
            showgrid=True,
        ),
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=50, b=50),
        height=350,
    )
    # Rounded corners on chart container
    fig.update_xaxes(linewidth=0)
    fig.update_yaxes(linewidth=0)
    st.plotly_chart(fig, use_container_width=True)

# ───────────────────── SPACER ─────────────────────
st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

# ───────────────────── ITEM COMPARISON CHART ─────────────────────
if "menu_item_name" in sales_df.columns:
    item_df = (
        sales_df.groupby("menu_item_name")
        .agg(
            profit_margin=("profit_margin", "mean"),
            revenue=("revenue", "sum"),
            quantity=("quantity_sold", "sum"),
        )
        .reset_index()
        .sort_values("revenue", ascending=True)
    )

    fig2 = px.bar(
        item_df,
        x="revenue",
        y="menu_item_name",
        orientation="h",
        color="profit_margin",
        color_continuous_scale=["#fee2e2", "#fef3c7", "#d0f5e8", "#008b5b"],
        hover_data={"profit_margin": ":.0%", "quantity": True, "revenue": ":,.0f"},
        labels={
            "menu_item_name": "Menu Item",
            "revenue": "Total Sales (RM)",
            "profit_margin": "Profit Per Item",
        },
    )
    fig2.update_traces(marker_line_width=0, marker=dict(cornerradius=6))
    fig2.update_layout(
        title=dict(text="Which Items Earn the Most?", font=dict(size=16, color="#0f172a")),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#1e293b", size=12),
        xaxis=dict(gridcolor="#f1f5f9", tickprefix="RM ", linewidth=0),
        yaxis=dict(gridcolor="#f1f5f9", linewidth=0),
        coloraxis_colorbar=dict(title="Profit/Item", tickformat=".0%"),
        margin=dict(l=10, r=10, t=50, b=30),
        height=350,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ───────────────────── SPACER ─────────────────────
st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)

# ───────────────────── TOP & LOW PERFORMERS ─────────────────────
if "menu_item_name" in sales_df.columns:
    item_perf = (
        sales_df.groupby("menu_item_name")
        .agg(
            margin=("profit_margin", "mean"),
            revenue=("revenue", "sum"),
            qty=("quantity_sold", "sum"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    def row(i, name, rev, margin):
        return f"""
        <div class="performer-row">
            <div>{i}. {name}</div>
            <div style="display:flex;gap:16px;">
                <span style="color:#008b5b;font-weight:600;">RM {rev:,.0f}</span>
                <span style="color:#64748b;font-size:13px;">keep {margin:.0%} as profit</span>
            </div>
        </div>
        """

    st.markdown("### Best Selling Items")
    st.markdown(
        "".join(
            row(i + 1, r.menu_item_name, r.revenue, r.margin)
            for i, r in item_perf.head(5).iterrows()
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    st.markdown("### Needs Improvement")
    st.markdown(
        "".join(
            row(i + 1, r.menu_item_name, r.revenue, r.margin)
            for i, r in item_perf.tail(5).iterrows()
        ),
        unsafe_allow_html=True,
    )

# ───────────────────── SIMPLE INSIGHT CARDS ─────────────────────
st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

snap_c1, snap_c2, snap_c3 = st.columns(3)

with snap_c1:
    if "is_weekend" in sales_df.columns:
        wknd_rev = sales_df[sales_df["is_weekend"] == 1]["revenue"].mean()
        wkday_rev = sales_df[sales_df["is_weekend"] == 0]["revenue"].mean()
        surge = (wknd_rev - wkday_rev) / wkday_rev * 100 if wkday_rev else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Weekends Are Busier</div>
            <div class="metric-value" style="color:#008b5b;">+{surge:.0f}%</div>
            <div class="metric-trend">Make RM {wknd_rev:,.0f} on weekends vs RM {wkday_rev:,.0f} on weekdays</div>
        </div>
        """, unsafe_allow_html=True)

with snap_c2:
    if "has_promotion" in sales_df.columns:
        promo_qty = sales_df[sales_df["has_promotion"] == 1]["quantity_sold"].mean()
        nopromo_qty = sales_df[sales_df["has_promotion"] == 0]["quantity_sold"].mean()
        lift = (promo_qty - nopromo_qty) / nopromo_qty * 100 if nopromo_qty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Promos Boost Sales</div>
            <div class="metric-value" style="color:#008b5b;">+{lift:.0f}%</div>
            <div class="metric-trend">Sell ~{promo_qty:,.0f} units with promo vs ~{nopromo_qty:,.0f} without</div>
        </div>
        """, unsafe_allow_html=True)

with snap_c3:
    if "weather_condition" in sales_df.columns:
        sunny = sales_df[sales_df["weather_condition"] == "Sunny"]["revenue"].mean()
        rainy = sales_df[sales_df["weather_condition"] == "Rainy"]["revenue"].mean()
        diff = sunny - rainy
        if diff > 0:
            hint = f"Sunny days bring in RM {diff:,.0f} more than rainy days"
        else:
            hint = f"Rainy days bring in RM {abs(diff):,.0f} more than sunny days"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Weather Matters</div>
            <div class="metric-value">RM {max(sunny, rainy):,.0f}</div>
            <div class="metric-trend">{hint}</div>
        </div>
        """, unsafe_allow_html=True)
