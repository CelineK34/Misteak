import pandas as pd
import os

# =========================
# 1. PATH FIX (IMPORTANT)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SALES_PATH = os.path.join(BASE_DIR, "preprocessed_restaurant_sales_data.csv")
INV_PATH   = os.path.join(BASE_DIR, "preprocessed_inventory_data.csv")
RES_PATH   = os.path.join(BASE_DIR, "restaurant_final.csv")


# =========================
# 2. SAFE LOADER
# =========================
def load_csv(path):
    try:
        df = pd.read_csv(path)
        print(f"[OK] Loaded: {os.path.basename(path)} | Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"[ERROR] Loading {os.path.basename(path)} failed: {e}")
        return None


# =========================
# 3. LOAD FILES
# =========================
sales = load_csv(SALES_PATH)
inv   = load_csv(INV_PATH)
res   = load_csv(RES_PATH)

if sales is None or inv is None or res is None:
    print("Missing dataset(s). Stop execution.")
    exit()


# =========================
# 4. SALES AGGREGATION
# =========================
sales_agg = sales.groupby("restaurant_id").agg({
    "profit_margin": "mean",
    "quantity_sold": "sum",
    "revenue": "sum",
    "price_to_cost_ratio": "mean",
    "price_to_market_ratio": "mean"
}).reset_index()


# =========================
# 5. INVENTORY AGGREGATION
# =========================
inv_agg = inv.groupby("restaurant_id").agg({
    "waste_percentage": "mean",
    "lead_time": "mean",
    "daily_usage": "mean",
    "current_stock": "mean"
}).reset_index()


# =========================
# 6. RESTAURANT LEVEL DATA
# =========================
if "restaurant_id" not in res.columns:
    res["restaurant_id"] = range(1, len(res) + 1)

res_agg = res[[
    "restaurant_id",
    "business_score",
    "customer_score",
    "Revenue"
]]


# =========================
# 7. MERGE ALL
# =========================
df = sales_agg.merge(inv_agg, on="restaurant_id", how="left")
df = df.merge(res_agg, on="restaurant_id", how="left")

df = df.dropna()


# =========================
# 8. OUTPUT
# =========================
OUTPUT_PATH = os.path.join(BASE_DIR, "final_master_dataset.csv")
df.to_csv(OUTPUT_PATH, index=False)

print("[DONE] Final dataset created:", df.shape)
print("[SAVED]", OUTPUT_PATH)