import anthropic
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import json

client = anthropic.Anthropic(
    auth_token="sk-03b07a1e4b1f8c2b3c407aecdabec8816a182940d2488ec1",
    base_url="https://api.ilmu.ai/anthropic"
)

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

def explain_weights_with_glm(weights, res_df):
    stats = {
        "profit_margin":         {"min": round(res_df['profit_margin'].min(), 2),         "max": round(res_df['profit_margin'].max(), 2),         "mean": round(res_df['profit_margin'].mean(), 2)},
        "quantity_sold":         {"min": round(res_df['quantity_sold'].min(), 2),         "max": round(res_df['quantity_sold'].max(), 2),         "mean": round(res_df['quantity_sold'].mean(), 2)},
        "revenue":               {"min": round(res_df['revenue'].min(), 2),               "max": round(res_df['revenue'].max(), 2),               "mean": round(res_df['revenue'].mean(), 2)},
        "price_to_market_ratio": {"min": round(res_df['price_to_market_ratio'].min(), 2), "max": round(res_df['price_to_market_ratio'].max(), 2), "mean": round(res_df['price_to_market_ratio'].mean(), 2)},
        "price_to_cost_ratio":   {"min": round(res_df['price_to_cost_ratio'].min(), 2),   "max": round(res_df['price_to_cost_ratio'].max(), 2),   "mean": round(res_df['price_to_cost_ratio'].mean(), 2)}
    }

    response = client.messages.create(
        model="ilmu-glm-5.1",
        max_tokens=2048,
        system="You are a restaurant pricing expert.",
        messages=[{
            "role": "user",
            "content": f"""These weights were defined based on business logic for a Malaysian restaurant pricing score:
                {json.dumps(weights, indent=2)}

                Dataset statistics:
                {json.dumps(stats, indent=2)}

                Explain in 2-3 sentences why these weights make business sense for a Malaysian restaurant."""
        }]
    )

    raw = ""
    for block in response.content:
        if block.type == "text":
            raw = block.text
            break
    return raw.strip()

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

    print("Asking GLM to explain weights...")
    explanation = explain_weights_with_glm(weights, res_df)
    print(f"GLM explanation: {explanation}")

    scaler = MinMaxScaler()
    res_df[['norm_profit', 'norm_demand', 'norm_revenue', 'norm_market_ratio', 'norm_cost_ratio']] = scaler.fit_transform(res_df[numeric_cols])

    res_df['pricing_score'] = (
        (weights['profit_margin']         * res_df['norm_profit']) +
        (weights['quantity_sold']         * res_df['norm_demand']) +
        (weights['revenue']               * res_df['norm_revenue']) +
        (weights['price_to_market_ratio'] * res_df['norm_market_ratio']) +
        (weights['price_to_cost_ratio']   * res_df['norm_cost_ratio'])
    ).round(4)

    overall_score=res_df['pricing_score'].mean().round(4)

    return res_df, weights, explanation, overall_score

if __name__ == "__main__":
    df = pd.read_csv(r"C:\Users\User\Documents\misteak\Misteak\preprocessed_restaurant_sales_data.csv")

    res_df, weights, explanation,overall_score = calculate_pricing_score(df)

    print(f"\nTop 5 restaurants:\n{res_df.nlargest(5, 'pricing_score')[['restaurant_id', 'pricing_score']].to_string()}")
    print(f"\nBottom 5 restaurants:\n{res_df.nsmallest(5, 'pricing_score')[['restaurant_id', 'pricing_score']].to_string()}")

    output = res_df.set_index('restaurant_id')['pricing_score'].to_dict()
    output['overall_score'] = float(overall_score)

    with open("pricing_score_output.json", "w") as f:
        json.dump(output, f, indent=2)
