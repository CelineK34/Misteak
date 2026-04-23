import anthropic
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import json

client = anthropic.Anthropic(
    auth_token="sk-03b07a1e4b1f8c2b3c407aecdabec8816a182940d2488ec1",
    base_url="https://api.ilmu.ai/anthropic"
)

def get_weights_from_glm(df):
    stats = {
        "profit_margin":         {"min": round(df['profit_margin'].min(), 2),         "max": round(df['profit_margin'].max(), 2),         "mean": round(df['profit_margin'].mean(), 2)},
        "quantity_sold":         {"min": round(df['quantity_sold'].min(), 2),         "max": round(df['quantity_sold'].max(), 2),         "mean": round(df['quantity_sold'].mean(), 2)},
        "revenue":               {"min": round(df['revenue'].min(), 2),               "max": round(df['revenue'].max(), 2),               "mean": round(df['revenue'].mean(), 2)},
        "price_to_market_ratio": {"min": round(df['price_to_market_ratio'].min(), 2), "max": round(df['price_to_market_ratio'].max(), 2), "mean": round(df['price_to_market_ratio'].mean(), 2)},
        "price_to_cost_ratio":   {"min": round(df['price_to_cost_ratio'].min(), 2),   "max": round(df['price_to_cost_ratio'].max(), 2),   "mean": round(df['price_to_cost_ratio'].mean(), 2)}
    }

    response = client.messages.create(
        model="ilmu-glm-5.1",
        max_tokens=2048,
        system="You are a restaurant pricing expert. Determine optimal weights for a pricing score formula. Weights must sum to exactly 1.0. Return ONLY valid JSON, no explanation outside JSON.",
        messages=[{
            "role": "user",
            "content": f"""Given these dataset statistics for a Malaysian restaurant:
{json.dumps(stats, indent=2)}

Return ONLY this JSON:
{{
    "weights": {{
        "profit_margin": 0.00,
        "quantity_sold": 0.00,
        "revenue": 0.00,
        "price_to_market_ratio": 0.00,
        "price_to_cost_ratio": 0.00
    }},
    "reasoning": "brief explanation"
}}"""
        }]
    )

    raw = ""
    for block in response.content:
        if block.type == "text":
            raw = block.text
            break
    raw = raw.strip().replace("```json", "").replace("```", "").strip()
    print(f"GLM raw response: '{raw}'")
    return json.loads(raw)

def calculate_pricing_score(df):
    numeric_cols = ['profit_margin', 'quantity_sold', 'revenue', 'price_to_market_ratio', 'price_to_cost_ratio']

    item_df = df.groupby('menu_item_name').agg({
        'profit_margin':         'mean',
        'quantity_sold':         'sum',
        'revenue':               'sum',
        'price_to_market_ratio': 'mean',
        'price_to_cost_ratio':   'mean'
    }).reset_index()

    item_df[numeric_cols] = item_df[numeric_cols].astype(float)

    # Apply log transformation to large range columns only
    item_df['quantity_sold'] = np.log1p(item_df['quantity_sold'])
    item_df['revenue']       = np.log1p(item_df['revenue'])

    # Rest stays the same
    print("Asking GLM to determine optimal weights...")
    glm_output = get_weights_from_glm(item_df)
    weights = glm_output["weights"]
    print(f"GLM reasoning: {glm_output['reasoning']}")
    print(f"Weights: {weights}")

    scaler = MinMaxScaler()
    item_df[['norm_profit', 'norm_demand', 'norm_revenue', 'norm_market_ratio', 'norm_cost_ratio']] = scaler.fit_transform(item_df[numeric_cols])

    item_df['pricing_score'] = (
        (weights['profit_margin']         * item_df['norm_profit']) +
        (weights['quantity_sold']         * item_df['norm_demand']) +
        (weights['revenue']               * item_df['norm_revenue']) +
        (weights['price_to_market_ratio'] * item_df['norm_market_ratio']) +
        (weights['price_to_cost_ratio']   * item_df['norm_cost_ratio'])
    ) * 100

    item_df['pricing_score'] = item_df['pricing_score'].round(2)
    overall_score = round(item_df['pricing_score'].mean(), 2)

    return item_df, overall_score, glm_output

if __name__ == "__main__":
    df = pd.read_csv(r"C:\Users\User\Documents\misteak\Misteak\preprocessed_restaurant_sales_data.csv")

    item_df, overall_score, glm_output = calculate_pricing_score(df)

    print(f"\nFinal Pricing Score: {overall_score}/100")
    print(f"\nTop 5 items:\n{item_df.nlargest(5, 'pricing_score')[['menu_item_name', 'pricing_score']].to_string()}")
    print(f"\nBottom 5 items:\n{item_df.nsmallest(5, 'pricing_score')[['menu_item_name', 'pricing_score']].to_string()}")

    output = {
        "overall_pricing_score": overall_score,
        "reasoning": glm_output["reasoning"]
    }

    with open("pricing_score_output.json", "w") as f:
        json.dump(output, f, indent=2)