import anthropic
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import json
import time

client = anthropic.Anthropic(
    auth_token="sk-03b07a1e4b1f8c2b3c407aecdabec8816a182940d2488ec1",
    base_url="https://api.ilmu.ai/anthropic"
)

def build_prompt(payload):
    return f"""You are a restaurant pricing analyst.

Overall pricing performance across all restaurants:
- Pricing Score: {payload['pricing_score']}
- Pricing Label: {payload['pricing_label']}
- Pricing Driver: {payload['pricing_driver']}

Context:
- Avg Profit Margin: {payload['context']['avg_profit_margin']}
- Avg Price to Market Ratio: {payload['context']['avg_price_to_market_ratio']}
- Avg Price to Cost Ratio: {payload['context']['avg_price_to_cost_ratio']}
- Avg Quantity Sold: {payload['context']['avg_quantity_sold']}
- Avg Revenue: {payload['context']['avg_revenue']}

Interpretation:
- Score > 0.7 = strong pricing
- Score 0.5-0.7 = moderate pricing
- Score < 0.5 = weak pricing

Tasks:
1. Explain WHY the pricing score is high or low based on the context

Be specific and data-driven.

Return ONLY this JSON:
{{
    "glm_summary": "2-3 sentence explanation covering all key metrics
}}"""

def get_pricing_signal(score):
    if score >= 0.7:
        return "strong"
    elif score >= 0.5:
        return "moderate"
    else:
        return "weak"

def get_pricing_driver_overall(res_df):
    return get_pricing_driver({
        'norm_profit': res_df['norm_profit'].mean(),
        'norm_market_ratio': res_df['norm_market_ratio'].mean(),
        'norm_cost_ratio': res_df['norm_cost_ratio'].mean()
    })

def get_pricing_driver(row):
    drivers = []
    if row['norm_profit'] >= 0.7:
        drivers.append("high margin")
    elif row['norm_profit'] <= 0.3:
        drivers.append("low margin")
    else:
        drivers.append("average margin")

    if row['norm_market_ratio'] >= 0.7:
        drivers.append("above-market pricing")
    elif row['norm_market_ratio'] <= 0.3:
        drivers.append("below-market pricing")
    else:
        drivers.append("competitive market pricing")

    if row['norm_cost_ratio'] >= 0.7:
        drivers.append("strong markup")
    elif row['norm_cost_ratio'] <= 0.3:
        drivers.append("weak markup")

    return ", ".join(drivers)

def get_weights():
    weights = {
        "profit_margin":         0.35,
        "quantity_sold":         0.25,
        "revenue":               0.20,
        "price_to_market_ratio": 0.10,
        "price_to_cost_ratio":   0.10
    }
    print(f"Business logic weights: {weights}")
    return weights

def get_summary_with_glm(res_df, overall_score, df_original):
    original_stats = df_original.groupby('restaurant_id').agg({
        'quantity_sold': 'sum',
        'revenue':       'sum'
    })

    payload = {
        "pricing_score": float(overall_score),
        "pricing_label": get_pricing_signal(float(overall_score)),
        "pricing_driver": get_pricing_driver_overall(res_df),
        "context": {
            "avg_profit_margin":         round(float(res_df['profit_margin'].mean()), 2),
            "avg_price_to_market_ratio": round(float(res_df['price_to_market_ratio'].mean()), 2),
            "avg_price_to_cost_ratio":   round(float(res_df['price_to_cost_ratio'].mean()), 2),
            "avg_quantity_sold":         round(float(original_stats['quantity_sold'].mean()), 2),
            "avg_revenue":               round(float(original_stats['revenue'].mean()), 2)
        }
    }

    response = client.messages.create(
        model="ilmu-glm-5.1",
        max_tokens=2048,
        system="You are a restaurant pricing analyst. Return ONLY valid JSON.",
        messages=[{"role": "user", "content": build_prompt(payload)}]
    )

    raw = ""
    for block in response.content:
        if block.type == "text":
            raw = block.text
            break
    raw = raw.strip().replace("```json", "").replace("```", "").strip()
    print(f"GLM raw: '{raw}'")
    return json.loads(raw)["glm_summary"]

def calculate_pricing_score(df):
    numeric_cols = ['profit_margin', 'quantity_sold', 'revenue', 'price_to_market_ratio', 'price_to_cost_ratio']

    res_df = df.groupby('restaurant_id').agg({
        'profit_margin':         'mean',
        'quantity_sold':         'sum',
        'revenue':               'sum',
        'price_to_market_ratio': 'mean',
        'price_to_cost_ratio':   'mean'
    }).reset_index()

    res_df[numeric_cols] = res_df[numeric_cols].astype(float)

    res_df['quantity_sold'] = np.log1p(res_df['quantity_sold'])
    res_df['revenue']       = np.log1p(res_df['revenue'])

    weights = get_weights()

    scaler = MinMaxScaler()
    res_df[['norm_profit', 'norm_demand', 'norm_revenue', 'norm_market_ratio', 'norm_cost_ratio']] = scaler.fit_transform(res_df[numeric_cols])

    res_df['pricing_score'] = (
        (weights['profit_margin']         * res_df['norm_profit']) +
        (weights['quantity_sold']         * res_df['norm_demand']) +
        (weights['revenue']               * res_df['norm_revenue']) +
        (weights['price_to_market_ratio'] * res_df['norm_market_ratio']) +
        (weights['price_to_cost_ratio']   * res_df['norm_cost_ratio'])
    ).round(4)

    overall_score = round(float(res_df['pricing_score'].mean()), 4)

    return res_df, overall_score

if __name__ == "__main__":
    df = pd.read_csv(r"C:\Users\User\Documents\misteak\Misteak\preprocessed_restaurant_sales_data.csv")

    res_df, overall_score = calculate_pricing_score(df)

    print("Asking GLM to generate overall summary...")
    summary = get_summary_with_glm(res_df, overall_score, df)
    print(f"GLM summary: {summary}")

    output = {
        "pricing_score": overall_score,
        "pricing_label": get_pricing_signal(overall_score),
        "pricing_driver": get_pricing_driver_overall(res_df),
        "glm_summary": summary
    }

    with open("pricing_score_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)