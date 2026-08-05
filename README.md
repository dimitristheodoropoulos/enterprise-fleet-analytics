# AI-Driven Operational Analytics Platform 🤖📊
### (Enterprise Fleet Analytics, Finance Reconciliation & Translation Quality)

An enterprise-grade AI-driven analytics and automation platform, built around a reusable architecture — Text-to-SQL AI agent, FastAPI REST API, PostgreSQL, and an LLM explanation layer — applied to **three independent operational domains** to demonstrate the platform's generality:

* 🚢 **Maritime Fleet Analytics:** Processes multi-million row fleet telemetry data, generates operational insights using a Text-to-SQL AI Agent, applies a full Machine Learning suite (prediction, clustering, classification, optimization, forecasting) to fuel consumption, and visualizes KPIs through an interactive Power BI Dashboard.
* 💰 **Finance Reconciliation:** Automates cross-system transaction matching (ERP vs. bank/PMS), anomaly/exception detection, human-in-the-loop exception review, and automated journal entry generation. See [`finance/README.md`](finance/README.md) for full details.
* 🌐 **Translation Quality Analytics:** Investigates LLM translation-quality drift across language pairs and model versions using hypothesis-driven root-cause analysis (content-type mix, sentence length, and model-rollout effects), separating genuine signal from confounds rather than reporting raw metrics. Includes a [live interactive demo](https://dimitristheodoropoulos.github.io/enterprise-fleet-analytics/translation_quality/) you can run directly in your browser. See [`translation_quality/README.md`](translation_quality/README.md) for full details.

The sections below cover the original maritime analytics build in depth; jump to [💰 Finance Reconciliation Extension](finance/README.md) or [🌐 Translation Quality Analytics](translation_quality/README.md) for the other domain modules.

## 🌟 Key Features
* **AI Copilot (Text-to-SQL):** Converts natural language queries into safe, production-ready PostgreSQL syntax using the official Google GenAI SDK (`gemini-2.5-flash`).
* **Predictive & Prescriptive Analytics (ML):** A full machine learning suite covering prediction (Random Forest Regressor, R² = 0.998), clustering (K-Means voyage efficiency profiling), classification (fuel-cost risk categorization), speed optimization (recommendation engine), and time-series forecasting — served via live FastAPI endpoints. See [`models/README.md`](models/README.md) for full methodology, including honestly-reported model limitations.
* **Production Guardrail Layer:** Employs explicit SQL injection blocking using regex patterns and structural validation via PostgreSQL `EXPLAIN` query execution planning before execution.
* **Input Validation & Function Calling:** Utilizes Pydantic models for strict type-checking and automated Gemini Function Calling to interface safely with DB backend endpoints.
* **Scalable Data Pipeline:** Custom Python data simulation script utilizing Pandas and NumPy vectorization to efficiently seed **100,000+ telemetry rows** into PostgreSQL.
* **Interactive Power BI Dashboard:** Real-time metrics visualization focusing on vessel fuel efficiency, cargo capacity allocation, and adverse weather impact analysis.
* **MLOps Logging:** Automated performance logging capturing user questions, LLM latency metrics, and execution metadata directly into database transaction logs.

## 🏗️ Architecture & Tech Stack
* **Language:** Python 3.10+
* **Frameworks:** FastAPI, Pydantic
* **AI Ecosystem:** Google GenAI SDK (`gemini-2.5-flash`, `gemini-embedding-2`), OpenAI Compatibility Layer
* **Machine Learning:** scikit-learn (Random Forest, Gradient Boosting, K-Means), statsmodels (Holt-Winters), joblib
* **Database:** PostgreSQL (Hosted via Docker Container)
* **Data Science:** Pandas, NumPy, Psycopg2
* **Business Intelligence:** Microsoft Power BI Desktop

## 📊 Database Schema & Optimization
The solution utilizes a highly optimized relational Star Schema:
* `vessels`: Contains core fleet structural data (ID, Name, Type, DWT, Built Year).
* `telemetry_logs`: Stores 100k+ rows of real-time sensor metrics (Speed, Fuel Consumption, Weather/Beaufort Scale, Cargo Weight, Route Status).
* `ai_chat_logs`: Implements MLOps telemetry, logging LLM user queries, vector embeddings, generated SQL code, and API call latency.

## 🔮 Machine Learning Suite

Beyond a core regression model, this project implements a full range of ML techniques applied to the same maritime telemetry dataset — prediction, clustering, classification, recommendation/optimization, and forecasting — each with its own evaluation and honestly-documented limitations. See [`models/README.md`](models/README.md) for complete details on feature engineering, model selection, evaluation methodology, and findings (including where a method underperformed a baseline and why).

| Technique | Method | Key Result |
|---|---|---|
| Prediction | Random Forest Regressor | R² = 0.9981, RMSE = 0.24 tons/day |
| Clustering | K-Means (voyage efficiency profiles) | Silhouette = 0.27, 3 interpretable profiles |
| Classification | Random Forest Classifier (fuel-cost risk) | 100% accuracy (see caveat in `models/README.md`) |
| Recommendation/Optimization | Speed optimizer using the trained regressor | Identifies fuel-minimizing speed under a time constraint |
| Forecasting | Holt-Winters Exponential Smoothing | Underperformed naive baseline — root cause documented |

**Serving:** The regression model is exposed via a live `POST /predict-fuel-consumption` FastAPI endpoint, returning real-time predictions in JSON.

**Example request:**
```bash
curl -X POST 'http://127.0.0.1:8000/predict-fuel-consumption' \
  -H 'Content-Type: application/json' \
  -d '{"speed": 12.5, "cargo_weight": 60000, "beaufort_scale": 4, "dwt": 105000, "built_year": 2018}'
```

**Reproduce all results:**
```bash
python models/run_training.py          # regression model
python models/compare_models.py        # model comparison
python models/feature_importance.py    # feature importance
python models/cluster_voyages.py       # clustering
python models/speed_optimizer.py       # speed optimization
python models/classify_fuel_risk.py    # classification
python models/forecast_fuel_trend.py   # forecasting
```

## 🚀 How to Run Locally

1. **Clone the repository:**
```bash
   git clone https://github.com/dimitristheodoropoulos/enterprise-fleet-analytics.git
   cd enterprise-fleet-analytics
```

2. **Configure Environment Variables:**
   The application securely fetches the Gemini API credentials using environment variables. Set your key in your terminal before running the application:
```bash
   # On Windows (PowerShell)
   $env:GEMINI_API_KEY="your_actual_api_key_here"
```

3. **Populate the Database:**
   Ensure your PostgreSQL docker container is up and running, then execute the data pipeline script to seed the database with 100,000 production-scale telemetry records:
```bash
   python database/generate_data.py
```

4. **Train the Fuel Prediction Model:**
```bash
   python models/run_training.py
```

5. **Start the FastAPI Backend Server:**
```bash
   python -m uvicorn main:app --reload
```

6. **Execute the AI Chatbot Agent:**
```bash
   python chatbot_agent.py
```

## 📈 Power BI Insights
Open the `Enterprise_Fleet_Analytics.pbix` file in Power BI Desktop and hit Refresh to explore live aggregated data pipelines:
* Fuel efficiency degradation maps against high Beaufort weather states.
* Fuel consumption trends by hull type and asset age profile.

### 🛠️ Data Engineering Showcase (ETL Pipeline)

To complement the investigative analytics showcased above, this repository includes a standalone, real-world ETL pipeline. It extracts live Wikipedia pageview data via a public REST API, loads it into a cloud PostgreSQL database (Supabase), transforms it using **dbt** (SQL modeling), and orchestrates the full workflow with an **Airflow DAG**. See [`data_pipeline/README.md`](data_pipeline/README.md) for the full technical breakdown.

## 💰 Finance Reconciliation Extension

See [`finance/README.md`](finance/README.md) for full details, endpoints, and a verified end-to-end run.
