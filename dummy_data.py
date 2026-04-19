import pandas as pd

# 1. KPI Data
kpi_data = {
    "Total Revenue": {"value": "RM 9,293", "trend": 12, "is_positive": True},
    "Total Profit":  {"value": "RM 6,150.2", "trend": 8, "is_positive": True},
    "Total Orders":  {"value": "2,013", "trend": 5, "is_positive": True},
    "Avg Margin":    {"value": "66.2%", "trend": 2, "is_positive": True}
}

# 2. Trend Chart — more points = smoother, more dramatic curve
trend_df = pd.DataFrame({
    "Date": [
        "2024-01-01","2024-01-08","2024-01-15","2024-01-22","2024-01-29",
        "2024-02-05","2024-02-12","2024-02-19","2024-02-26",
        "2024-03-04","2024-03-11","2024-03-18","2024-03-25",
        "2024-04-01","2024-04-08","2024-04-15","2024-04-22",
    ],
    "Revenue": [
        1800,1850,1900,1950,2000,
        2050,2150,2350,2400,
        2200,2000,1900,1870,
        1850,1840,1830,1850,
    ],
    "Profit": [
        1200,1220,1250,1280,1320,
        1350,1400,1480,1520,
        1400,1250,1150,1120,
        1100,1090,1100,1150,
    ]
})

# 3. Item Profit — shorter names, matches image 2
item_profit_df = pd.DataFrame({
    "Item":   ["Nasi Lemak", "Roti Canai", "Teh Tarik", "Mee Goreng", "Satay"],
    "Profit": [1200, 800, 600, 550, 400]
})

# 4. Tables
top_performers_df = pd.DataFrame({
    "Item":    ["Nasi Lemak Special", "Teh Tarik Ais", "Roti Bakar"],
    "Revenue": ["RM 2,343", "RM 1,200", "RM 890"],
    "Margin":  ["62.4%", "70.1%", "65.0%"]
})

needs_attention_df = pd.DataFrame({
    "Item":    ["Roti Canai Special", "Curry Laksa"],
    "Revenue": ["RM 690", "RM 450"],
    "Margin":  ["75.0%", "55.0%"]
})