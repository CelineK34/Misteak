"""
dummy_data.py — Central data store for FoodAI
All mock/demo data lives here so pages stay logic-only.
"""
import pandas as pd

# ── 1. KPI Summary ──────────────────────────────────────────────────────────
kpi_data = {
    "Total Revenue": {"value": "RM 9,293",   "trend": 12, "is_positive": True},
    "Total Profit":  {"value": "RM 6,150",   "trend": 8,  "is_positive": True},
    "Total Orders":  {"value": "2,013",       "trend": 5,  "is_positive": True},
    "Avg Margin":    {"value": "66.2%",       "trend": 2,  "is_positive": True},
}

# ── 2. Weekly Revenue & Profit Trend ────────────────────────────────────────
trend_df = pd.DataFrame({
    "Date": [
        "2024-01-01", "2024-01-08", "2024-01-15", "2024-01-22", "2024-01-29",
        "2024-02-05", "2024-02-12", "2024-02-19", "2024-02-26",
        "2024-03-04", "2024-03-11", "2024-03-18", "2024-03-25",
        "2024-04-01", "2024-04-08", "2024-04-15", "2024-04-22",
    ],
    "Revenue": [
        1800, 1850, 1900, 1950, 2000,
        2050, 2150, 2350, 2400,
        2200, 2000, 1900, 1870,
        1850, 1840, 1830, 1850,
    ],
    "Profit": [
        1200, 1220, 1250, 1280, 1320,
        1350, 1400, 1480, 1520,
        1400, 1250, 1150, 1120,
        1100, 1090, 1100, 1150,
    ],
})

# ── 3. Profit by Menu Item (bar chart) ──────────────────────────────────────
item_profit_df = pd.DataFrame({
    "Item":   ["Nasi Lemak", "Roti Canai", "Teh Tarik", "Mee Goreng", "Satay"],
    "Profit": [1200, 800, 600, 550, 400],
})

# ── 4. Top Performers & Needs Attention ─────────────────────────────────────
top_performers_df = pd.DataFrame({
    "Item":    ["Nasi Lemak Special", "Teh Tarik Ais", "Roti Bakar"],
    "Revenue": ["RM 2,343", "RM 1,200", "RM 890"],
    "Margin":  ["62.4%", "70.1%", "65.0%"],
})

needs_attention_df = pd.DataFrame({
    "Item":    ["Roti Canai Special", "Curry Laksa", "Mee Goreng Mamak"],
    "Revenue": ["RM 690", "RM 450", "RM 381"],
    "Margin":  ["75.0% · declining", "55.0% · low volume", "−20% sales drop"],
})

# ── 5. AI Alerts ─────────────────────────────────────────────────────────────
alerts_data = [
    {
        "icon": "⚠️",
        "icon_bg": "#fef3c7",
        "title": "Mee Goreng sales declining",
        "badge": "WARNING",
        "badge_bg": "#f59e0b",
        "badge_color": "white",
        "desc": (
            "Mee Goreng Mamak sales dropped 20% over the past 3 days. "
            "Customer ratings also fell from 4.3 to 4.0. "
            "Consider a recipe refresh or promotion to revive interest."
        ),
        "metric_label": "Metric",
        "metric_value": "−20% sales",
        "impact_label": "Daily loss",
        "impact_value": "RM 58.80/day",
    },
    {
        "icon": "↗️",
        "icon_bg": "#d0f5e8",
        "title": "Teh Tarik is your star performer",
        "badge": "OPPORTUNITY",
        "badge_bg": "#008b5b",
        "badge_color": "white",
        "desc": (
            "Teh Tarik has the highest profit margin (76%) and strongest demand growth. "
            "Consider upselling combos or increasing price by RM 0.30 — demand is inelastic."
        ),
        "metric_label": "Margin",
        "metric_value": "76%",
        "impact_label": "Potential gain",
        "impact_value": "+RM 45/day",
    },
    {
        "icon": "🔥",
        "icon_bg": "#fee2e2",
        "title": "Ais Kacang low weekday demand",
        "badge": "CRITICAL",
        "badge_bg": "#ef4444",
        "badge_color": "white",
        "desc": (
            "Ais Kacang demand drops 33% on weekdays vs weekends. "
            "Over-preparation is causing significant food waste that hurts your bottom line."
        ),
        "metric_label": "Waste risk",
        "metric_value": "33%",
        "impact_label": "Daily waste",
        "impact_value": "RM 22.50/day",
    },
    {
        "icon": "↗️",
        "icon_bg": "#d0f5e8",
        "title": "Weekend surge pattern detected",
        "badge": "OPPORTUNITY",
        "badge_bg": "#008b5b",
        "badge_color": "white",
        "desc": (
            "All items see 15–25% higher demand on weekends. "
            "Prepare extra inventory for Saturday and Sunday — "
            "staffing up on Fridays will help manage the peak."
        ),
        "metric_label": "Demand surge",
        "metric_value": "+25%",
        "impact_label": "Weekend gain",
        "impact_value": "RM 120/weekend",
    },
]

# ── 6. Strategy Options ───────────────────────────────────────────────────────
strategies_data = [
    {
        "title": "Bundle Nasi Lemak + Teh Tarik",
        "risk": "Medium Risk",
        "profit_impact": "+22%",
        "desc": (
            "Create a combo meal at RM 9.90 (vs RM 11.00 separate). "
            "Increases average order value and moves two top items together."
        ),
        "confidence": 85,
        "actions": [
            "Create combo menu signage",
            "Train staff on bundle offer",
            "Track combo vs individual sales",
        ],
    },
    {
        "title": "Reduce Mee Goreng price to RM 6.50",
        "risk": "Low Risk",
        "profit_impact": "+15%",
        "desc": (
            "A small price reduction to revive demand. "
            "Based on price elasticity analysis, a 7% cut could boost volume by 15%."
        ),
        "confidence": 78,
        "actions": [
            "Update menu pricing",
            "Announce via social media",
            "Monitor for 2 weeks",
        ],
    },
    {
        "title": "Weekend Ais Kacang promotion",
        "risk": "High Risk",
        "profit_impact": "+30%",
        "desc": (
            "Run 'Buy 1 free 1' on weekdays to clear excess inventory and reduce waste. "
            "Weekend price stays the same."
        ),
        "confidence": 72,
        "actions": [
            "Prepare weekday promo materials",
            "Reduce weekday prep by 20%",
            "Track daily waste levels",
        ],
    },
    {
        "title": "Roti Canai price increase to RM 2.50",
        "risk": "Low Risk",
        "profit_impact": "+18%",
        "desc": (
            "With 75% margin and stable demand, a RM 0.50 increase would "
            "significantly boost profit with minimal volume loss."
        ),
        "confidence": 82,
        "actions": [
            "Gradual price increase",
            "Add value with extra dhal",
            "Monitor customer response",
        ],
    },
]

# ── 7. Best Recommendation (Decision page) ───────────────────────────────────
best_recommendation = {
    "title": "Bundle Nasi Lemak + Teh Tarik",
    "risk": "Medium",
    "risk_color": "#f59e0b",
    "profit_impact": "+22%",
    "desc": (
        "Create a combo meal at RM 9.90 (vs RM 11.00 separate). "
        "Increases average order value and moves two top items together."
    ),
    "confidence": 85,
    "actions": [
        "Create combo menu signage",
        "Train staff on bundle offer",
        "Track combo vs individual sales",
    ],
    "why": (
        "This strategy has the best balance of profit impact and risk. "
        "Nasi Lemak Special and Teh Tarik are already your top 2 performers — "
        "bundling them requires zero new inventory and minimal staff training."
    ),
    "expected_revenue": "RM 11,200",
    "expected_profit": "RM 7,500",
    "expected_orders": "2,300",
    "timeline": "2 weeks",
    "other_options": [
        {"title": "Reduce Mee Goreng price to RM 6.50",  "risk": "Low",  "confidence": 78, "profit_impact": "+15%"},
        {"title": "Weekend Ais Kacang promotion",          "risk": "High", "confidence": 72, "profit_impact": "+30%"},
        {"title": "Roti Canai price increase to RM 2.50",  "risk": "Low",  "confidence": 82, "profit_impact": "+18%"},
    ],
}

# ── 8. Simulator Item Data ────────────────────────────────────────────────────
simulator_items = {
    "Nasi Lemak Special": {"price": 8.50, "cost": 3.20, "qty": 450, "elasticity": -1.2},
    "Teh Tarik":          {"price": 2.50, "cost": 0.60, "qty": 380, "elasticity": -0.8},
    "Roti Canai":         {"price": 2.00, "cost": 0.50, "qty": 520, "elasticity": -1.0},
    "Mee Goreng Mamak":   {"price": 7.00, "cost": 2.80, "qty": 310, "elasticity": -1.3},
    "Ais Kacang":         {"price": 4.50, "cost": 1.50, "qty": 280, "elasticity": -0.9},
}

# ── 9. Current Data Status (Settings page) ────────────────────────────────────
data_status = {
    "Records loaded":   "2,013 orders",
    "Date range":       "Jan 2024 – Apr 2024",
    "Products tracked": "5 items",
    "AI model accuracy":"87% confidence",
}
