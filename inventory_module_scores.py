import pandas as pd
import json
import os
import requests
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# STEP 1: Load preprocessed data
print("Loading preprocessed data...")
df = pd.read_csv(os.path.join(PROJECT_DIR, 'preprocessed_inventory_data.csv'))
print(f"Data: {df.shape[0]} rows, {df['restaurant_id'].nunique()} restaurants")

# STEP 2: Feature engineering
print("Engineering features...")

item_day = df.groupby(
    ['restaurant_id', 'restaurant_type', 'item_id', 'item_name', 'category', 'subcategory', 'date']
).agg(
    current_stock=('current_stock', 'mean'),
    reorder_level=('reorder_level', 'mean'),
    daily_usage=('daily_usage', 'mean'),
    lead_time=('lead_time', 'first'),
    price_per_unit=('price_per_unit', 'first'),
    seasonal_factor=('seasonal_factor', 'mean'),
    waste_pct=('waste_percentage', 'mean'),
    high_demand_flag=('high_demand_flag', 'any'),
    usage_level=('usage_level', 'first'),
    supplier_name=('supplier_name', 'first')
).reset_index()

features = item_day.groupby(
    ['restaurant_id', 'restaurant_type', 'item_id', 'item_name', 'category', 'subcategory']
).agg(
    mean_stock=('current_stock', 'mean'),
    std_stock=('current_stock', 'std'),
    min_stock=('current_stock', 'min'),
    mean_reorder_level=('reorder_level', 'mean'),
    mean_daily_usage=('daily_usage', 'mean'),
    std_daily_usage=('daily_usage', 'std'),
    mean_lead_time=('lead_time', 'mean'),
    mean_waste_pct=('waste_pct', 'mean'),
    max_waste_pct=('waste_pct', 'max'),
    high_demand_pct=('high_demand_flag', 'mean'),
    mean_seasonal_factor=('seasonal_factor', 'mean'),
    mean_price=('price_per_unit', 'mean'),
).reset_index()

# Derived features
features['stock_usage_ratio'] = features['mean_stock'] / features['mean_daily_usage']
features['stock_cv'] = features['std_stock'] / features['mean_stock']
features['usage_cv'] = features['std_daily_usage'] / features['mean_daily_usage']
features['reorder_coverage_days'] = features['mean_reorder_level'] / features['mean_daily_usage']
features['stockout_risk'] = features['mean_reorder_level'] / features['min_stock']
features['waste_to_usage'] = features['mean_waste_pct'] / (features['mean_daily_usage'] * 100)
features['lead_time_demand'] = features['mean_lead_time'] * features['mean_daily_usage']
features['safety_buffer'] = (features['mean_stock'] - features['lead_time_demand']) / features['mean_stock']

sup = item_day.groupby(['restaurant_id', 'item_id'])['supplier_name'].nunique().reset_index()
sup.columns = ['restaurant_id', 'item_id', 'supplier_diversity']
features = features.merge(sup, on=['restaurant_id', 'item_id'])
features['is_perishable'] = features['subcategory'].isin(
    ['Meat', 'Poultry', 'Fish', 'Dairy', 'Vegetable']
).astype(int)

# STEP 3: Score calculation
print("Calculating scores...")
scaler = MinMaxScaler(feature_range=(0, 1))

# Supply Stability
sd = features[['stock_usage_ratio', 'safety_buffer', 'reorder_coverage_days',
               'supplier_diversity', 'stock_cv', 'usage_cv']].copy()
for c in sd.columns:
    sd[c] = scaler.fit_transform(sd[[c]])
sd['stock_cv_inv'] = 1 - sd['stock_cv']
sd['usage_cv_inv'] = 1 - sd['usage_cv']
features['supply_stability_score'] = (
    0.25 * sd['stock_usage_ratio'] + 0.25 * sd['safety_buffer'] +
    0.15 * sd['reorder_coverage_days'] + 0.10 * sd['supplier_diversity'] +
    0.15 * sd['stock_cv_inv'] + 0.10 * sd['usage_cv_inv']
)

# Operational Risk (higher = less risk = better)
rd = features[['mean_waste_pct', 'max_waste_pct', 'stockout_risk',
               'mean_lead_time', 'high_demand_pct', 'is_perishable', 'waste_to_usage']].copy()
for c in rd.columns:
    rd[c] = scaler.fit_transform(rd[[c]])
for c in rd.columns:
    rd[c + '_inv'] = 1 - rd[c]
features['operational_risk_score'] = (
    0.20 * rd['mean_waste_pct_inv'] + 0.15 * rd['max_waste_pct_inv'] +
    0.20 * rd['stockout_risk_inv'] + 0.15 * rd['mean_lead_time_inv'] +
    0.10 * rd['high_demand_pct_inv'] + 0.10 * rd['is_perishable_inv'] +
    0.10 * rd['waste_to_usage_inv']
)

# Stock Efficiency
ed = features[['safety_buffer', 'mean_waste_pct', 'waste_to_usage',
               'mean_seasonal_factor', 'stock_usage_ratio']].copy()
for c in ed.columns:
    ed[c] = scaler.fit_transform(ed[[c]])
ed['waste_inv'] = 1 - ed['mean_waste_pct']
ed['waste_usage_inv'] = 1 - ed['waste_to_usage']
ed['seasonal_inv'] = 1 - ed['mean_seasonal_factor']
features['stock_efficiency_score'] = (
    0.25 * ed['safety_buffer'] + 0.25 * ed['waste_inv'] +
    0.20 * ed['waste_usage_inv'] + 0.15 * ed['seasonal_inv'] +
    0.15 * ed['stock_usage_ratio']
)

# Composite per item, then aggregate to final
features['supply_score'] = (
    0.35 * features['supply_stability_score'] +
    0.35 * features['operational_risk_score'] +
    0.30 * features['stock_efficiency_score']
)
features['supply_score'] = scaler.fit_transform(features[['supply_score']])

rest = features.groupby('restaurant_id')['supply_score'].mean().reset_index()
final_score = round(float(rest['supply_score'].mean()), 4)

# Key stats
avg_safety = float(features['safety_buffer'].mean())
avg_waste = float(features['mean_waste_pct'].mean())
avg_lead = float(features['mean_lead_time'].mean())
avg_stockout = float(features['stockout_risk'].mean())
avg_high_demand = float(features['high_demand_pct'].mean())
avg_stability = float(features['supply_stability_score'].mean())
avg_risk = float(features['operational_risk_score'].mean())
avg_efficiency = float(features['stock_efficiency_score'].mean())

# STEP 4: Label & driver
def get_label(s):
    if s >= 0.7: return "strong"
    elif s >= 0.4: return "moderate"
    else: return "weak"

label = get_label(final_score)

if final_score >= 0.7:
    drivers = []
    if avg_safety >= 0.5: drivers.append("adequate stock buffers")
    if avg_waste <= 2.5: drivers.append("low waste")
    if avg_lead <= 2.0: drivers.append("short lead times")
    if avg_stability >= 0.6: drivers.append("stable supply")
    driver = ", ".join(drivers) if drivers else "balanced inventory metrics"
else:
    drivers = []
    if avg_safety < 0.35: drivers.append("thin safety buffer")
    if avg_waste > 3.0: drivers.append("high waste")
    if avg_lead > 2.5: drivers.append("long lead times")
    if avg_stockout > 1.0: drivers.append("stockout risk")
    if avg_high_demand > 0.1: drivers.append("demand volatility")
    if avg_stability < 0.5: drivers.append("unstable supply")
    if avg_risk < 0.5: drivers.append("high operational risk")
    driver = ", ".join(drivers[:3]) if drivers else "below average inventory metrics"

# STEP 5: GLM summary
print(f"Final supply_score: {final_score} ({label})")
print(f"Driver: {driver}")
print("Calling ilmu Z.AI GLM...")

prompt = (
    f"Supply score: {final_score} ({label})\n"
    f"Key drivers: {driver}\n"
    f"Avg safety buffer: {avg_safety:.2f}, "
    f"Avg waste: {avg_waste:.2f}%, "
    f"Avg lead time: {avg_lead:.1f} days, "
    f"Avg stockout risk: {avg_stockout:.2f}, "
    f"Avg high demand days: {avg_high_demand:.1%}\n"
    f"Sub-scores: stability={avg_stability:.3f}, "
    f"risk={avg_risk:.3f}, "
    f"efficiency={avg_efficiency:.3f}\n\n"
    f"Explain why the supply score is {label} in 2-3 sentences, referencing the score value and key metrics."
)

try:
    resp = requests.post(
        'https://api.ilmu.ai/v1/chat/completions',
        headers={
            'Authorization': 'Bearer sk-03b07a1e4b1f8c2b3c407aecdabec8816a182940d2488ec1',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'ilmu-glm-5.1',
            'messages': [
                {'role': 'system', 'content': 'You are a restaurant supply chain analyst. Write ONE concise paragraph (2-3 sentences) explaining why this restaurant supply score is at its level. Be specific and data-driven, referencing the score value and key metrics.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.5,
            'max_tokens': 2000
        }
    )
    data = resp.json()
    glm_summary = data['choices'][0]['message']['content'].strip()
except Exception as e:
    print(f"GLM error: {e}")
    glm_summary = f"The supply score of {final_score} is {label} primarily driven by {driver}."

# STEP 6: Output JSON + CSV
output = {
    "supply_score": final_score,
    "supply_label": label,
    "supply_driver": driver,
    "glm_summary": glm_summary
}

with open(os.path.join(PROJECT_DIR, 'inventory_module_scores.json'), 'w') as f:
    json.dump(output, f, indent=2)

features.to_csv(os.path.join(PROJECT_DIR, 'inventory_feature_engineering_full.csv'), index=False)

print("\n" + "=" * 60)
print("FINAL OUTPUT")
print("=" * 60)
print(json.dumps(output, indent=2))
print(f"\nSaved: inventory_module_scores.json")
print("Saved: inventory_feature_engineering_full.csv")
