# Enterprise Fleet Analytics & AI Copilot 🚢🤖

An enterprise-grade maritime analytics platform and AI assistant that processes multi-million row fleet telemetry data, generates operational insights using a **Text-to-SQL AI Agent**, exposes data via a **FastAPI REST API**, applies a full **Machine Learning suite** (prediction, clustering, classification, optimization, forecasting) to fuel consumption, and visualizes key performance indicators (KPIs) through an interactive **Power BI Dashboard**.

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

## 💰 Finance Reconciliation Extension

The same AI-driven platform generalizes beyond maritime telemetry: the `finance/` module reuses the exact same architecture (PostgreSQL, FastAPI, LLM explanation layer) to solve a cross-system finance-operations problem — automated reconciliation, exception handling, and journal entry generation.

### What it does
* **Cross-system matching:** Reconciles transactions between two independent feeds (e.g. an internal ERP ledger vs. a bank/PMS statement) by reference, flagging amount mismatches, date mismatches, and unmatched entries on either side.
* **Anomaly / exception detection:** Every discrepancy the matching engine can't cleanly resolve is recorded as a `PENDING_REVIEW` exception rather than silently ignored or auto-approved.
* **Human-in-the-loop validation:** A reviewer approves or rejects each exception via a dedicated endpoint; the decision and reviewer are recorded for audit purposes.
* **AI-generated explanations:** Each exception can be explained in natural language (via the same Gemini client used by the AI Copilot) to speed up human review.
* **Automated journal entry generation:** Approving an exception automatically drafts a journal entry (debit/credit/amount/memo), ready for posting.

### New tables
* `erp_transactions` / `bank_transactions` — the two systems being reconciled.
* `reconciliation_exceptions` — every mismatch found, its type, status, and AI explanation.
* `journal_entries` — draft entries generated from approved exceptions.

### Running it
```bash
# 1. Apply the finance schema (in addition to the main schema)
psql -U postgres -d maritime_db -f finance/schema_finance.sql

# 2. Seed mock ERP + bank transactions with intentional discrepancies
python finance/generate_finance_data.py

# 3. Start the API (finance router is mounted automatically in main.py)
python -m uvicorn main:app --reload
```

### API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/finance/reconcile` | Runs a full reconciliation pass, returns a summary |
| GET | `/finance/exceptions?status=PENDING_REVIEW` | Lists exceptions by status |
| GET | `/finance/exceptions/{id}/explain` | AI-generated explanation for one exception |
| POST | `/finance/exceptions/{id}/review` | Records an approve/reject decision (`{"decision": "APPROVED", "reviewed_by": "..."}`) |
| GET | `/finance/journal-entries?status=DRAFT` | Lists generated journal entries |

Example:
```bash
curl -X POST http://localhost:8000/finance/reconcile
curl "http://localhost:8000/finance/exceptions?status=PENDING_REVIEW"
curl -X POST http://localhost:8000/finance/exceptions/1/review \
  -H "Content-Type: application/json" \
  -d '{"decision": "APPROVED", "reviewed_by": "dimitris"}'
```
