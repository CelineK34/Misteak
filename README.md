# 🍽️ AI-Powered Restaurant Intelligence System

An end-to-end data analytics and AI decision-making platform built with **Streamlit**.  
This system transforms raw restaurant data into actionable insights, alerts, and strategies using a full preprocessing + GLM-based pipeline.

---

## 🚀 Features

- 📦 Upload ZIP dataset (multi-CSV support)
- ⚙️ Automated preprocessing pipeline
- 📊 Interactive dashboard with KPIs & trends
- 🚨 Smart alerts (supply, pricing, engagement)
- 💡 AI-generated business strategies
- 🎯 Decision engine with ranked recommendations
- 🧪 Price & demand simulator (what-if analysis)

---

## 🧠 System Architecture

### Step 1: Data Upload
Upload a `.zip` file containing CSV datasets:

| Dataset Type | Required Columns |
|-------------|------------------|
| Sales Data | `menu_item_name`, `quantity_sold` |
| Inventory Data | `item_name`, `current_stock` |
| Customer/Restaurant Data | `rating`, `ambience` |

The system auto-detects and classifies each file.

---

### Step 2: Data Pipeline

| Step | Script | Output |
|------|--------|--------|
| 1 | `preprocess_restaurant_sales.py` | `preprocessed_restaurant_sales_data.csv` |
| 2 | `inventory_preprocessing.py` | `preprocessed_inventory_data.csv` |
| 3 | `aggregate_restaurant_level.py` | `final_master_dataset.csv` |
| 4a | `calc_pricing_score.py` | `pricing_score_output.json` |
| 4b | `inventory_module_scores.py` | `inventory_module_scores.json` |
| 4c | `createjson.py` | `zai_payload.json` |
| 5 | `glm_payload.py` | `glm_payload.json` |
| 6 | `glm_engine.py` | `glm_result.json`, `glm_report.md` |

---

### Step 3: Application Pages

| Page | Description |
|------|------------|
| 📊 Dashboard | KPIs, trends, top/bottom items, AI insights |
| 🚨 Alerts | Risk detection (stockout, pricing, waste) |
| 💡 Strategies | AI-generated improvement strategies |
| 🧪 Simulator | Price elasticity & profit simulation |
| 🎯 Decision | Best strategy ranked with explanation |
| ⚙️ Settings | Data upload & pipeline execution |

---

## 🔄 Data Flow

ZIP Upload

- Sales Data  
  → Preprocessing  
  → Dashboard / Alerts / Strategies / Simulator / Decision  

- Inventory Data  
  → Preprocessing  
  → Alerts / Strategies / Decision  

- Customer Data  
  → JSON Generation  
  → GLM Engine  
  → AI Insights  

---

## 🖥️ How to Run

### 1. Clone Repository
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```
### 2. Run Application
```bash
streamlit run app.py
```

---

## 🛠️ Tech Stack
- Frontend: Streamlit
- Backend: Python
- Data Processing: Pandas, NumPy
- Machine Learning: Scikit-learn, GLM
- Visualization: Matplotlib / Plotly
