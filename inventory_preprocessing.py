import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# STEP 1: Load raw data
print("Loading raw data...")
df = pd.read_csv(os.path.join(PROJECT_DIR, 'restaurant_inventory_100days.csv'))
print(f"Raw data: {df.shape}")

# STEP 2: Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Strip whitespace from string columns
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.strip()

# Format date
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['date'] = df['date'].dt.strftime('%d-%m-%Y')

print(f"After cleaning: {df.shape}")

# STEP 3: Drop duplicates & remove negatives
df = df.drop_duplicates()
print(f"After dedup: {df.shape}")

numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
for col in numeric_cols:
    df = df[df[col] >= 0]
print(f"After removing negatives: {df.shape}")

# STEP 4: Duplicate 8x with variation (same as notebook)
n = 8
df = pd.concat([df] * n, ignore_index=True)
df['current_stock'] *= np.random.uniform(0.9, 1.1, len(df))
df['daily_usage'] *= np.random.uniform(0.9, 1.1, len(df))
df['waste_percentage'] *= np.random.uniform(0.8, 1.2, len(df))

# Shuffle
df = df.sample(frac=1).reset_index(drop=True)
print(f"After 8x duplication with variation: {df.shape}")

# STEP 5: Add high_demand_flag and usage_level
threshold = df['daily_usage'].quantile(0.95)
df['high_demand_flag'] = df['daily_usage'] > threshold

df['usage_level'] = pd.cut(
    df['daily_usage'],
    bins=[-1, 2, 5, threshold, df['daily_usage'].max()],
    labels=['Low', 'Medium', 'High', 'Extreme']
)

print(f"high_demand_flag: {df['high_demand_flag'].sum()} True out of {len(df)}")
print(f"usage_level distribution:\n{df['usage_level'].value_counts()}")

# STEP 6: Expand to 50 restaurants
print("\nExpanding to 50 restaurants...")

N = 50
profiles = pd.DataFrame({
    'restaurant_id': range(1, N + 1),
    'demand_mult': np.random.uniform(0.6, 1.4, N),
    'waste_mult': np.random.uniform(0.5, 2.0, N),
    'stock_mult': np.random.uniform(0.7, 1.3, N),
    'lead_time_shift': np.random.choice([0, 0, 0, 1, 1, 2], N),
})
profiles['restaurant_type'] = np.random.choice(
    ['Fine Dining', 'Casual', 'Fast Food', 'Food Stall', 'Cafe'],
    N, p=[0.1, 0.3, 0.25, 0.25, 0.1]
)

all_data = []
for _, p in profiles.iterrows():
    r = df.copy()
    r['restaurant_id'] = p['restaurant_id']
    r['restaurant_type'] = p['restaurant_type']

    # Apply restaurant-specific variation
    r['current_stock'] = r['current_stock'] * p['stock_mult']
    r['daily_usage'] = r['daily_usage'] * p['demand_mult']
    r['waste_percentage'] = (r['waste_percentage'] * p['waste_mult']).clip(0.01, 9.99)
    r['lead_time'] = (r['lead_time'] + p['lead_time_shift']).clip(1, 7)
    r['reorder_level'] = r['reorder_level'] * p['demand_mult']

    # Adjust high demand flag based on demand multiplier
    if p['demand_mult'] > 1.1:
        boost = (p['demand_mult'] - 1.0) * 0.5
        r['high_demand_flag'] = r['high_demand_flag'] | (np.random.random(len(r)) < boost)
    elif p['demand_mult'] < 0.8:
        r['high_demand_flag'] = r['high_demand_flag'] & (np.random.random(len(r)) < 0.3)

    # Add per-row noise
    r['current_stock'] = (r['current_stock'] * np.random.normal(1.0, 0.05, len(r))).clip(0.5)
    r['daily_usage'] = (r['daily_usage'] * np.random.normal(1.0, 0.05, len(r))).clip(0.1)

    # Recalculate usage_level for this restaurant
    rest_threshold = r['daily_usage'].quantile(0.95)
    r['usage_level'] = pd.cut(
        r['daily_usage'],
        bins=[-1, 2, 5, rest_threshold, r['daily_usage'].max()],
        labels=['Low', 'Medium', 'High', 'Extreme']
    )

    all_data.append(r)

expanded = pd.concat(all_data, ignore_index=True)
print(f"Final: {expanded.shape[0]} rows, {expanded['restaurant_id'].nunique()} restaurants")

# STEP 7: Save
output_path = os.path.join(PROJECT_DIR, 'preprocessed_inventory_data.csv')
expanded.to_csv(output_path, index=False)
print(f"Saved: {output_path}")
