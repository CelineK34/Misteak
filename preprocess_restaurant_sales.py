import pandas as pd
import os

# =========================
# 1. LOAD DATA (SAFE PATH)
# =========================
FILE_PATH = "restaurant_sales_data.csv"  # same folder as script

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded: {file_path}")
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None


# =========================
# 2. MAIN PIPELINE
# =========================
if __name__ == "__main__":

    df = load_data(FILE_PATH)

    if df is None:
        print("❌ Data loading failed. Stop execution.")
        exit()

    # ─────────────────────────────
    # BASIC CLEANING
    # ─────────────────────────────
    print("Missing values:\n", df.isna().sum())
    print("Duplicates:", df.duplicated().sum())

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    bool_columns = ["has_promotion", "special_event"]
    for col in bool_columns:
        df[col] = df[col].astype(int)

    string_columns = [
        "restaurant_type",
        "menu_item_name",
        "meal_type",
        "key_ingredients_tags",
        "weather_condition"
    ]

    for col in string_columns:
        df[col] = df[col].astype(str).str.strip().str.title()

    float_columns = [
        "typical_ingredient_cost",
        "observed_market_price",
        "actual_selling_price"
    ]

    for col in float_columns:
        df[col] = df[col].astype(float)

    df["quantity_sold"] = df["quantity_sold"].astype(int)

    # ─────────────────────────────
    # FEATURE ENGINEERING (IMPORTANT)
    # ─────────────────────────────
    df["revenue"] = df["actual_selling_price"] * df["quantity_sold"]

    df["profit_margin"] = (
        df["actual_selling_price"] - df["typical_ingredient_cost"]
    ) / df["actual_selling_price"]

    df["price_to_cost_ratio"] = (
        df["actual_selling_price"] / df["typical_ingredient_cost"]
    )

    df["price_to_market_ratio"] = (
        df["actual_selling_price"] / df["observed_market_price"]
    )

    df["is_weekend"] = df["date"].dt.dayofweek.isin([5, 6]).astype(int)
    df["month"] = df["date"].dt.month

    # ─────────────────────────────
    # SAVE OUTPUT
    # ─────────────────────────────
    OUTPUT_PATH = "preprocessed_restaurant_sales_data.csv"
    df.to_csv(OUTPUT_PATH, index=False)

    print("\n✅ PREPROCESSING COMPLETE")
    print("Final shape:", df.shape)
    print("Saved to:", OUTPUT_PATH)