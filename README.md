🍽️ AI-Powered Restaurant Intelligence System

An end-to-end data-driven decision support system for restaurants that transforms raw operational data into actionable business insights using preprocessing pipelines and AI-powered modeling.

🚀 Overview

This system allows users to upload restaurant datasets and automatically generates:

📊 Business performance dashboards
🚨 Operational alerts
💡 Strategy recommendations
📈 Pricing simulations
🧠 AI-generated decision insights

Built using Streamlit, data pipelines, and AI-driven modeling (GLM + scoring modules).

🧠 Key Features
1. Automated Data Pipeline
Upload a ZIP file containing CSV datasets
System auto-detects and classifies files
Runs full preprocessing and modeling pipeline
2. Smart Dashboard
KPIs: Sales, Profit, Orders
Monthly trends & comparisons
Top & bottom performing items
AI-generated insights
3. Alerts System
Supply risk detection
Pricing inefficiencies
Declining product performance
Stockout warnings
4. Strategy Generator
AI-generated business strategies:
Pricing optimization
Bundle offers
Waste reduction
Promotion planning
5. Simulator
What-if analysis using price & cost sliders
Real elasticity modeling (log-log regression)
Profit and demand prediction
6. Decision Engine
Ranks strategies based on:
Profit impact
Risk level
Confidence score
Provides explainable AI insights
🏗️ System Architecture
ZIP Upload (CSV files)
    │
    ├── Sales Data → Preprocessing → Sales Features
    ├── Inventory Data → Expansion → Inventory Insights
    ├── Customer Data → Scoring → Customer Insights
    │
    ├── Pricing Model → pricing_score_output.json
    ├── Inventory Model → inventory_module_scores.json
    │
    └── GLM Engine → glm_result.json + report
            │
            ├── Dashboard
            ├── Alerts
            ├── Strategies
            ├── Simulator
            └── Decision Page
📂 Project Structure
├── app.py
├── pages/
│   ├── 1_dashboard.py
│   ├── 2_alerts.py
│   ├── 3_strategies.py
│   ├── 4_simulator.py
│   ├── 5_decision.py
│   └── 6_settings.py
│
├── pipeline/
│   ├── preprocess_restaurant_sales.py
│   ├── inventory_preprocessing.py
│   ├── aggregate_restaurant_level.py
│   ├── calc_pricing_score.py
│   ├── inventory_module_scores.py
│   ├── createjson.py
│   ├── glm_payload.py
│   └── glm_engine.py
│
├── data/
├── outputs/
└── README.md
📥 Input Data Format

Upload a .zip file containing CSV files. The system auto-detects based on columns:

Data Type	Required Columns
Sales Data	menu_item_name, quantity_sold
Inventory Data	item_name, current_stock
Customer Data	rating, ambience
⚙️ How to Run
1. Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2. Install dependencies
pip install -r requirements.txt
3. Run the app
streamlit run app.py
🧪 Demo Flow
Launch the application
Navigate to Settings page
Upload dataset ZIP
Click Run Full Pipeline
Explore insights across all pages
📊 Data Flow
Raw CSV → Preprocessing → Feature Engineering → Scoring Models → GLM Engine → Insights

All pages use processed data only (no raw data dependency).

🧩 Tech Stack
Frontend: Streamlit
Data Processing: Pandas, NumPy
Modeling: scikit-learn
Statistical Modeling: GLM (Generalized Linear Model)
Language: Python
🎯 Use Cases
Restaurant performance analysis
Pricing optimization
Inventory planning
Business decision support
AI-powered consulting tools
⚠️ Notes
System runs on file-based pipeline (no database required)
Designed for flexibility and rapid deployment
Suitable for hackathons, prototypes, and analytics tools
🔮 Future Improvements
Database integration (PostgreSQL / Firebase)
Multi-user support
Real-time dashboard updates
API deployment
Model optimization
👨‍💻 Authors
Your Name
Team Name (if applicable)
📜 License

This project is for educational and demonstration purposes.
