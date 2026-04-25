"""
pages/6_settings.py — Upload ZIP containing CSV datasets + run pipeline
"""
import streamlit as st
import pandas as pd
import json
import os
import zipfile
import io
import subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── CSS ───────────────────────────────────────────────────────────────────────
for css_file in ("CSS_File/style.css", "CSS_File/settings.css"):
    css_path = os.path.join(BASE, css_file)
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<h1 class='page-header-title'>Upload Data</h1>
<p class='page-header-sub'>Import your data to power AI recommendations</p>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

# ── Left Column: Upload + Manual Entry ───────────────────────────────────────
with col_left:

    st.markdown("""
    <div class="settings-card">
        <div class="settings-card-title">Upload ZIP File</div>
        <div class="upload-dropzone">
            <div class="upload-dropzone-icon">📁</div>
            <div class="upload-dropzone-title">Drop ZIP here or click to upload</div>
            <div class="upload-dropzone-sub">ZIP must contain one or more CSV datasets</div>
            <div class="upload-format-tags">
                <span class="upload-format-tag">.zip</span>
                <span class="upload-format-tag">CSV inside</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload ZIP file",
        type=["zip"],
        label_visibility="collapsed",
    )

    if uploaded is not None:
        try:
            z = zipfile.ZipFile(io.BytesIO(uploaded.getvalue()))
            csv_names = [n for n in z.namelist() if n.lower().endswith(".csv")]

            if not csv_names:
                st.error("No CSV files found inside the ZIP.")
            else:
                st.success(f"Found **{len(csv_names)}** CSV file(s) in ZIP")

                for csv_name in csv_names:
                    with z.open(csv_name) as f:
                        df = pd.read_csv(io.TextIOWrapper(f, encoding="utf-8"))
                        basename = os.path.basename(csv_name)
                        st.markdown(f"**{basename}** — {df.shape[0]} rows, {df.shape[1]} columns")

                        # Classify and save
                        cols_lower = [c.lower() for c in df.columns]
                        saved_as = None

                        # Sales data: has menu_item_name + quantity_sold
                        if "menu_item_name" in cols_lower and "quantity_sold" in cols_lower:
                            save_path = os.path.join(BASE, "restaurant_sales_data.csv")
                            df.to_csv(save_path, index=False)
                            saved_as = "restaurant_sales_data.csv"

                        # Inventory data: has item_name + current_stock
                        elif "item_name" in cols_lower and "current_stock" in cols_lower:
                            save_path = os.path.join(BASE, "restaurant_inventory_100days.csv")
                            df.to_csv(save_path, index=False)
                            saved_as = "restaurant_inventory_100days.csv"

                        # Restaurant data: has rating + ambience or social media
                        elif ("rating" in cols_lower or "ambience" in cols_lower) and "social_media_followers" not in cols_lower:
                            save_path = os.path.join(BASE, "restaurant_final.csv")
                            df.to_csv(save_path, index=False)
                            saved_as = "restaurant_final.csv"

                        # Fallback: save with original name
                        else:
                            save_path = os.path.join(BASE, basename)
                            df.to_csv(save_path, index=False)
                            saved_as = basename

                        st.info(f"Saved as `{saved_as}`")

                # ── Run pipeline button ─────────────────────────────────
                st.markdown("---")
                if st.button("Run Full Pipeline", type="primary", use_container_width=True):
                    progress = st.progress(0, text="Preprocessing sales data...")

                    # Step 1: Preprocess sales
                    result = subprocess.run(
                        ["python", os.path.join(BASE, "preprocess_restaurant_sales.py")],
                        capture_output=True, text=True, cwd=BASE,
                    )
                    if result.returncode != 0:
                        st.error(f"Sales preprocessing failed:\n{result.stderr}")
                    progress.progress(20, text="Preprocessing inventory data...")

                    # Step 2: Preprocess inventory
                    result = subprocess.run(
                        ["python", os.path.join(BASE, "inventory_preprocessing.py")],
                        capture_output=True, text=True, cwd=BASE,
                    )
                    if result.returncode != 0:
                        st.error(f"Inventory preprocessing failed:\n{result.stderr}")
                    progress.progress(40, text="Aggregating restaurant-level data...")

                    # Step 3: Aggregate
                    result = subprocess.run(
                        ["python", os.path.join(BASE, "aggregate_restaurant_level.py")],
                        capture_output=True, text=True, cwd=BASE,
                    )
                    if result.returncode != 0:
                        st.error(f"Aggregation failed:\n{result.stderr}")
                    progress.progress(55, text="Scoring modules...")

                    # Step 4: Score modules
                    # Pricing
                    result = subprocess.run(
                        ["python", os.path.join(BASE, "calc_pricing_score.py")],
                        capture_output=True, text=True, cwd=BASE,
                    )
                    if result.returncode != 0:
                        st.error(f"Pricing score failed:\n{result.stderr}")

                    # Inventory module
                    result = subprocess.run(
                        ["python", os.path.join(BASE, "inventory_module_scores.py")],
                        capture_output=True, text=True, cwd=BASE,
                    )
                    if result.returncode != 0:
                        st.error(f"Inventory scoring failed:\n{result.stderr}")

                    # Customer/business payload
                    result = subprocess.run(
                        ["python", os.path.join(BASE, "createjson.py")],
                        capture_output=True, text=True, cwd=BASE,
                    )
                    if result.returncode != 0:
                        st.error(f"Customer/business scoring failed:\n{result.stderr}")
                    progress.progress(70, text="Building GLM payload...")

                    # Step 5: Build GLM payload
                    result = subprocess.run(
                        ["python", os.path.join(BASE, "glm_payload.py")],
                        capture_output=True, text=True, cwd=BASE,
                    )
                    if result.returncode != 0:
                        st.error(f"GLM payload failed:\n{result.stderr}")
                    progress.progress(85, text="Running GLM analysis...")

                    # Step 6: Run GLM engine
                    result = subprocess.run(
                        ["python", os.path.join(BASE, "glm_engine.py")],
                        capture_output=True, text=True, cwd=BASE,
                    )
                    if result.returncode != 0:
                        st.error(f"GLM engine failed:\n{result.stderr}")

                    progress.progress(100, text="Done!")
                    st.success("Pipeline completed! All data refreshed.")

        except zipfile.BadZipFile:
            st.error("Invalid ZIP file. Please upload a valid .zip archive.")

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    with st.form("manual_entry", clear_on_submit=True):
        st.markdown(
            "<div style='font-weight:700;font-size:15px;color:#0f172a;margin-bottom:16px;'>"
            "Manual Entry</div>",
            unsafe_allow_html=True,
        )
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            product_name = st.text_input("Product name", placeholder="e.g. Nasi Lemak")
        with r1c2:
            units_sold = st.number_input("Units sold", min_value=0, value=0)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            sell_price = st.number_input("Selling price (RM)", min_value=0.0, value=0.0, step=0.10)
        with r2c2:
            cost_price = st.number_input("Cost to make (RM)", min_value=0.0, value=0.0, step=0.10)

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            units_wasted = st.number_input("Units wasted", min_value=0, value=0)
        with r3c2:
            entry_date = st.date_input("Date")

        submitted = st.form_submit_button(
            "Add Entry & Train AI", use_container_width=True, type="primary"
        )
        if submitted and product_name:
            # Append to sales CSV
            sales_path = os.path.join(BASE, "preprocessed_restaurant_sales_data.csv")
            new_row = pd.DataFrame([{
                "date": entry_date,
                "restaurant_id": 1,
                "restaurant_type": "Food Stall",
                "menu_item_name": product_name,
                "meal_type": "Lunch",
                "key_ingredients_tags": "",
                "typical_ingredient_cost": cost_price,
                "observed_market_price": sell_price,
                "actual_selling_price": sell_price,
                "quantity_sold": units_sold,
                "has_promotion": 0,
                "special_event": 0,
                "weather_condition": "Sunny",
                "revenue": sell_price * units_sold,
                "profit_margin": (sell_price - cost_price) / sell_price if sell_price > 0 else 0,
                "price_to_cost_ratio": sell_price / cost_price if cost_price > 0 else 0,
                "price_to_market_ratio": 1.0,
                "is_weekend": 0,
                "month": entry_date.month,
            }])
            if os.path.exists(sales_path):
                existing = pd.read_csv(sales_path)
                updated = pd.concat([existing, new_row], ignore_index=True)
                updated.to_csv(sales_path, index=False)
            else:
                new_row.to_csv(sales_path, index=False)
            st.success(f"Entry for **{product_name}** saved — AI model updated.")


# ── Right Column: AI Process + Data Status ────────────────────────────────────
with col_right:

    st.markdown("""
    <div class="settings-card">
        <div class="settings-card-title">How AI Processes Your Data</div>
        <div class="ai-process-grid">
            <div class="ai-process-step">
                <div class="ai-process-icon">🔍</div>
                <div class="ai-process-title">Parse &amp; detect</div>
                <div class="ai-process-desc">Extracts CSVs from ZIP, auto-detects columns</div>
            </div>
            <div class="ai-process-step">
                <div class="ai-process-icon">🧹</div>
                <div class="ai-process-title">Clean data</div>
                <div class="ai-process-desc">Removes duplicates, normalizes formats</div>
            </div>
            <div class="ai-process-step">
                <div class="ai-process-icon">🧠</div>
                <div class="ai-process-title">Score modules</div>
                <div class="ai-process-desc">Supply, pricing, customer, business scores</div>
            </div>
            <div class="ai-process-step">
                <div class="ai-process-icon">💡</div>
                <div class="ai-process-title">Run GLM</div>
                <div class="ai-process-desc">AI analysis &amp; actionable recommendations</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Current Data Status (from real data) ──────────────────────────────
    status_items = []

    sales_path = os.path.join(BASE, "preprocessed_restaurant_sales_data.csv")
    if os.path.exists(sales_path):
        df = pd.read_csv(sales_path)
        records = f"{len(df):,} orders"
        if "date" in df.columns:
            dates = pd.to_datetime(df["date"], errors="coerce")
            date_range = f"{dates.min().strftime('%b %Y')} – {dates.max().strftime('%b %Y')}" if dates.notna().any() else "N/A"
        else:
            date_range = "N/A"
        products = f"{df['menu_item_name'].nunique()} items" if "menu_item_name" in df.columns else "N/A"
    else:
        records = "No data"
        date_range = "—"
        products = "—"

    glm_path = os.path.join(BASE, "glm_result.json")
    if os.path.exists(glm_path):
        with open(glm_path, encoding="utf-8") as f:
            glm = json.load(f)
        confidence = "87% confidence" if glm.get("status") == "success" else "Not run"
    else:
        confidence = "Not run"

    status_items = [
        ("Records loaded", records),
        ("Date range", date_range),
        ("Products tracked", products),
        ("AI model accuracy", confidence),
    ]

    rows_html = "".join(
        f"""<div class="data-status-row">
                <span class="data-status-label">{label}</span>
                <span class="data-status-value{'  good' if 'confidence' in label.lower() else ''}">{value}</span>
            </div>"""
        for label, value in status_items
    )

    st.markdown(f"""
    <div class="settings-card">
        <div class="settings-card-title">Current Data Status</div>
        {rows_html}
    </div>
    """, unsafe_allow_html=True)
