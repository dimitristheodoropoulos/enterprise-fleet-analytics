# AI-Driven Operational Analytics Platform 🤖📊

### Enterprise Fleet Analytics, Finance Reconciliation & Translation Quality

An AI-driven analytics and automation platform built around a reusable, enterprise-oriented architecture — combining a **Text-to-SQL AI agent, FastAPI REST API, PostgreSQL, machine learning services, and an LLM explanation layer**.

The same architectural approach is applied to **three independent operational domains** to demonstrate the platform's generality:

* 🚢 **Maritime Fleet Analytics:** Processes 100,000+ synthetic fleet telemetry records, generates operational insights through a Text-to-SQL AI agent, and applies a range of supervised, unsupervised, optimization, and time-series methods to fuel-consumption analysis. Operational KPIs are visualized through an interactive Power BI dashboard.
* 💰 **Finance Reconciliation:** Automates cross-system transaction matching (ERP vs. bank/PMS), anomaly and exception detection, human-in-the-loop exception review, and automated journal-entry generation. See `finance/README.md` for the complete implementation and validation details.
* 🌐 **Translation Quality Analytics:** Investigates LLM translation-quality drift across language pairs and model versions using hypothesis-driven root-cause analysis. The analysis examines content-type mix, sentence length, and model-rollout effects to distinguish genuine quality signals from potential confounding factors. Includes a [live interactive demo](https://dimitristheodoropoulos.github.io/enterprise-fleet-analytics/translation_quality/) that runs directly in the browser. See `translation_quality/README.md` for full details.

The sections below describe the original maritime analytics implementation in depth. For the additional domains, see [💰 Finance Reconciliation Extension](finance/README.md) and [🌐 Translation Quality Analytics](translation_quality/README.md).

---

## 🌟 Key Features

### 🤖 AI Copilot — Text-to-SQL

* Converts natural-language analytical questions into PostgreSQL queries using the official **Google GenAI SDK** (`gemini-2.5-flash`).
* Uses structured function calling to interface with database-backed operations.
* Applies explicit SQL-safety guardrails before query execution.
* Validates generated queries structurally through PostgreSQL `EXPLAIN` before execution.
* Logs user questions, generated SQL, model latency, and execution metadata for observability and analysis.

The system is designed to demonstrate how an LLM can act as a controlled analytical interface over structured operational data rather than providing unrestricted database access.

### 📊 Predictive & Prescriptive Analytics

The maritime module implements a range of analytical methods covering:

* **Prediction:** Random Forest Regression for fuel-consumption estimation.
* **Clustering:** K-Means for voyage-efficiency profiling.
* **Classification:** Random Forest classification for fuel-cost risk categorization.
* **Optimization:** Speed recommendation based on the trained fuel-consumption model and voyage-time constraints.
* **Forecasting:** Holt-Winters exponential smoothing for fuel-consumption trends.

Model results are evaluated quantitatively and documented together with their limitations. In particular, the forecasting experiment explicitly compares the statistical model against a naive baseline rather than assuming that a more sophisticated method will necessarily perform better.

### 🛡️ SQL Safety & Validation Layer

The Text-to-SQL pipeline includes multiple controls before generated SQL is executed:

1. Explicit pattern-based blocking of common SQL-injection constructs.
2. Structural validation of generated SQL.
3. PostgreSQL `EXPLAIN` validation before execution.
4. Pydantic-based input validation at the API layer.

These mechanisms provide an explicit safety boundary around the LLM-generated query workflow. They are intended as application-level safeguards and should not be interpreted as a substitute for a comprehensive security assessment or production penetration test.

### 🔬 Reproducible Data Pipeline

A custom Python data-generation pipeline uses Pandas and NumPy vectorization to efficiently generate and load **100,000+ synthetic telemetry records** into PostgreSQL.

The dataset is designed to exercise the analytical architecture at a meaningful operational data volume while keeping the project fully reproducible without requiring access to proprietary maritime datasets.

### 📈 Interactive Power BI Dashboard

The project includes an interactive Power BI dashboard covering operational KPIs such as:

* Vessel fuel efficiency.
* Fuel-consumption trends.
* Cargo utilization.
* Weather impact.
* Vessel age and hull-type comparisons.

### 📝 Observability & MLOps Logging

The platform records analytical interaction metadata, including:

* User questions.
* Generated SQL.
* LLM latency.
* API execution metadata.
* Database interaction information.

This provides an operational foundation for monitoring the behavior of the AI analytics layer.

---

# 🏗️ Architecture & Tech Stack

## Core Technology

* **Language:** Python 3.10+
* **API Framework:** FastAPI
* **Validation:** Pydantic
* **Database:** PostgreSQL
* **Database Driver:** Psycopg2
* **Data Processing:** Pandas, NumPy
* **Containerization:** Docker

## AI / LLM

* **Google GenAI SDK**
* `gemini-2.5-flash`
* `gemini-embedding-2`
* OpenAI-compatible interfaces where applicable
* Function calling for structured interaction with backend capabilities

## Machine Learning

* **scikit-learn**

  * Random Forest Regressor
  * Random Forest Classifier
  * K-Means
  * Gradient Boosting
* **statsmodels**

  * Holt-Winters Exponential Smoothing
* **joblib**

  * Model persistence

## Business Intelligence

* Microsoft Power BI Desktop

---

# 🏛️ Platform Architecture

At a high level, the platform follows the following flow:

```text
                         ┌─────────────────────┐
                         │   User / Analyst    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    AI Copilot       │
                         │   Text-to-SQL LLM    │
                         └──────────┬──────────┘
                                    │
                          Generated SQL / Calls
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Safety & Validation  │
                         │  - Input validation │
                         │  - SQL checks        │
                         │  - PostgreSQL EXPLAIN│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     PostgreSQL      │
                         │ Operational Dataset │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐      ┌──────────────┐      ┌──────────────┐
       │   FastAPI   │      │ ML Analytics │      │  Power BI    │
       │   Services  │      │   Pipeline   │      │  Dashboard   │
       └─────────────┘      └──────────────┘      └──────────────┘
              │                     │
              ▼                     ▼
       REST Predictions       Models / Insights
              │                     │
              └──────────┬──────────┘
                         ▼
                ┌───────────────────┐
                │ Observability /   │
                │ AI Interaction Log│
                └───────────────────┘
```

The architecture intentionally separates the **LLM interaction layer**, **data access layer**, **analytical models**, and **presentation/API layer**, making the approach reusable across different operational domains.

---

# 📊 Database Schema & Optimization

The maritime analytics module uses a relational schema centered around vessel and telemetry data.

### `vessels`

Contains core fleet information:

* Vessel ID
* Vessel name
* Vessel type
* Deadweight tonnage (DWT)
* Built year

### `telemetry_logs`

Stores synthetic operational telemetry including:

* Vessel ID
* Speed
* Fuel consumption
* Beaufort weather scale
* Cargo weight
* Route status
* Operational timestamps

The dataset contains **100,000+ synthetic telemetry records** generated through a reproducible Python data-generation pipeline.

### `ai_chat_logs`

Provides observability for the AI analytics layer, recording information such as:

* User analytical questions
* Generated SQL
* Vector embeddings where applicable
* LLM metadata
* API latency
* Execution metadata

---

# 🔮 Machine Learning Suite

The maritime module evaluates several complementary analytical approaches rather than relying on a single predictive model.

| Technique                     | Method                                  | Result / Observation                                                    |
| ----------------------------- | --------------------------------------- | ----------------------------------------------------------------------- |
| Prediction                    | Random Forest Regressor                 | Test R² = 0.9981, RMSE = 0.24 tons/day                                  |
| Clustering                    | K-Means                                 | Silhouette score = 0.27; 3 interpretable operational profiles           |
| Classification                | Random Forest Classifier                | 100% test accuracy on the synthetic dataset; see documented limitations |
| Recommendation / Optimization | Speed optimizer using trained regressor | Identifies fuel-minimizing speed subject to a time constraint           |
| Forecasting                   | Holt-Winters Exponential Smoothing      | Underperformed a naive baseline; root-cause analysis documented         |

## Important Interpretation Note

The maritime dataset used by this project is **synthetic**.

Therefore, the reported model metrics measure performance on the generated dataset and **should not be interpreted as evidence of equivalent performance on real-world maritime operations**.

In particular, the very high regression R² reflects the structure of the simulated relationships between operational variables and fuel consumption. Real-world vessel data would contain additional sources of uncertainty, measurement noise, environmental variation, vessel-specific behavior, and potentially non-stationary operating conditions.

The purpose of these experiments is therefore to demonstrate:

* ML pipeline construction.
* Feature engineering.
* Model comparison.
* Evaluation methodology.
* Model serving.
* Analytical interpretation.
* Failure analysis.
* Reproducibility.

rather than to claim production-level predictive accuracy for real vessels.

---

# 📈 1. Fuel Consumption Prediction

### Model

**Random Forest Regressor**

### Evaluation

```text
Test R²   = 0.9981
Test RMSE = 0.24 tons/day
```

The model estimates daily fuel consumption using operational and vessel characteristics such as:

* Speed
* Cargo weight
* Beaufort scale
* DWT
* Vessel age / built year

The model is exposed through a FastAPI endpoint for on-demand inference.

### Example API Request

```bash
curl -X POST 'http://127.0.0.1:8000/predict-fuel-consumption' \
  -H 'Content-Type: application/json' \
  -d '{"speed": 12.5, "cargo_weight": 60000, "beaufort_scale": 4, "dwt": 105000, "built_year": 2018}'
```

### Example Conceptual Response

```json
{
  "predicted_fuel_consumption": 25.4
}
```

The endpoint demonstrates how a trained ML model can be integrated into an operational REST API and consumed by downstream applications.

---

# 🔬 2. Voyage Efficiency Clustering

### Method

**K-Means clustering**

The clustering pipeline groups operational records into voyage-efficiency profiles using selected operational features.

### Result

```text
Silhouette Score = 0.27
Number of clusters = 3
```

The relatively moderate silhouette score indicates that the clusters should not be interpreted as strongly separated natural categories.

Their value is primarily exploratory and operational: they provide interpretable profiles that can be used to investigate differences in vessel operating behavior.

This is intentionally presented as an exploratory segmentation rather than as evidence of a highly separable underlying population.

---

# ⚠️ 3. Fuel-Cost Risk Classification

### Method

**Random Forest Classifier**

The classification model categorizes operational observations into fuel-cost risk groups.

### Result

```text
Test accuracy = 100%
```

The result is reported specifically for the synthetic evaluation dataset.

The unusually high accuracy is treated as a limitation rather than as evidence that an equivalent classifier would achieve perfect accuracy on real-world data.

Potential contributors include:

* Synthetic feature relationships.
* Deterministic or highly structured target-generation logic.
* Limited variability compared with real operational data.
* Potential class separability introduced by the simulation process.

The repository documents these limitations and keeps the result separate from claims about real-world generalization.

---

# ⚙️ 4. Speed Optimization

The project also demonstrates a simple prescriptive analytics layer.

Instead of only predicting fuel consumption, the system searches for a speed that minimizes predicted fuel consumption while satisfying an operational time constraint.

Conceptually:

```text
Minimize:
    predicted_fuel_consumption(speed)

Subject to:
    voyage_time(speed) <= maximum_allowed_time
```

The optimization layer therefore demonstrates the transition from:

```text
Descriptive Analytics
        ↓
Predictive Analytics
        ↓
Prescriptive Analytics
```

The optimizer uses the trained regression model as its predictive component.

Because the underlying model is trained on synthetic data, the optimization recommendations should likewise be interpreted as **demonstrations of the methodology**, not as operational recommendations for real vessels.

---

# 📉 5. Fuel-Consumption Forecasting

### Method

**Holt-Winters Exponential Smoothing**

Unlike the other ML experiments, the forecasting model did **not** outperform a simpler naive baseline.

This result is intentionally retained in the project.

Rather than selecting the best-looking metric or removing an underperforming experiment, the analysis investigates why the more sophisticated model failed to provide additional predictive value.

This illustrates an important principle of applied analytics:

> A more sophisticated model is not automatically a better model.

The documented analysis examines the characteristics of the available time-series data and the suitability of the forecasting assumptions.

---

# 🧪 Reproducibility

The major analytical experiments can be reproduced using the following scripts:

```bash
python models/run_training.py
python models/compare_models.py
python models/feature_importance.py
python models/cluster_voyages.py
python models/speed_optimizer.py
python models/classify_fuel_risk.py
python models/forecast_fuel_trend.py
```

### Main experiments

| Script                   | Purpose                                     |
| ------------------------ | ------------------------------------------- |
| `run_training.py`        | Train the fuel-consumption regression model |
| `compare_models.py`      | Compare candidate regression models         |
| `feature_importance.py`  | Analyze feature contributions               |
| `cluster_voyages.py`     | Perform voyage-efficiency clustering        |
| `speed_optimizer.py`     | Perform speed recommendation / optimization |
| `classify_fuel_risk.py`  | Train and evaluate the risk classifier      |
| `forecast_fuel_trend.py` | Evaluate time-series forecasting            |

---

# 🚀 How to Run Locally

## 1. Clone the repository

```bash
git clone https://github.com/dimitristheodoropoulos/enterprise-fleet-analytics.git
cd enterprise-fleet-analytics
```

## 2. Configure Environment Variables

The application uses environment variables for Gemini API credentials.

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="your_actual_api_key_here"
```

### Linux / macOS

```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

Do not commit API keys or other credentials to the repository.

---

## 3. Start PostgreSQL

Ensure the PostgreSQL Docker container is running according to the repository's database configuration.

---

## 4. Generate the Dataset

Run the reproducible synthetic data-generation pipeline:

```bash
python database/generate_data.py
```

This generates and loads **100,000+ synthetic telemetry records** into PostgreSQL.

---

## 5. Train the Fuel Prediction Model

```bash
python models/run_training.py
```

---

## 6. Start the FastAPI Backend

```bash
python -m uvicorn main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

---

## 7. Run the AI Chatbot Agent

```bash
python chatbot_agent.py
```

The chatbot provides a natural-language interface for analytical queries over the operational database.

---

# 📊 Power BI Dashboard

The repository includes:

```text
Enterprise_Fleet_Analytics.pbix
```

Open the file using **Power BI Desktop** and refresh the data sources according to the local environment configuration.

The dashboard focuses on operational questions such as:

* Fuel-efficiency degradation under adverse weather conditions.
* Fuel-consumption trends by vessel type.
* Fuel-consumption patterns across vessel age.
* Cargo utilization.
* Operational KPI comparisons.

The dashboard complements the programmatic analytics layer by providing an interactive business-facing visualization interface.

---

# 🛠️ Data Engineering Showcase — ETL Pipeline

The repository also includes a standalone ETL/data-engineering workflow.

The pipeline:

```text
Wikipedia Pageview API
        ↓
Extraction
        ↓
PostgreSQL / Supabase
        ↓
dbt transformations
        ↓
Airflow orchestration
        ↓
Analytical dataset
```

The pipeline demonstrates integration between:

* Public REST APIs
* Python-based extraction
* PostgreSQL
* Supabase
* dbt SQL transformations
* Apache Airflow orchestration

See:

```text
data_pipeline/README.md
```

for the complete technical description.

---

# 💰 Finance Reconciliation Extension

The finance module extends the same general architecture into a financial operations workflow.

It addresses:

* Cross-system transaction reconciliation.
* ERP vs. bank/PMS matching.
* Exception detection.
* Anomaly identification.
* Human-in-the-loop exception review.
* Automated journal-entry generation.

The objective is to demonstrate how the same AI/automation architecture can be adapted from operational fleet analytics to financial operations.

See:

```text
finance/README.md
```

for:

* Architecture
* Data model
* API endpoints
* Matching methodology
* Exception workflow
* Validation results
* End-to-end execution

---

# 🌐 Translation Quality Analytics

The translation-quality module applies the platform's analytical methodology to LLM translation systems.

Rather than reporting only aggregate translation-quality metrics, the analysis investigates **why quality changes**.

The analysis examines:

* Language-pair differences.
* Model-version changes.
* Content-type composition.
* Sentence-length effects.
* Model rollout effects.
* Potential confounding variables.

The goal is to distinguish:

```text
Observed metric change
        ↓
Potential confounders
        ↓
Hypothesis testing
        ↓
Root-cause analysis
        ↓
Actionable interpretation
```

### Live Demo

The interactive browser-based demonstration is available here:

https://dimitristheodoropoulos.github.io/enterprise-fleet-analytics/translation_quality/

See:

```text
translation_quality/README.md
```

for the methodology and detailed findings.

---

# 🧠 Design Principles

The platform follows several principles intended to make analytical AI systems more reliable and interpretable.

### 1. Separate LLM reasoning from database execution

The LLM generates analytical intent and SQL, but database execution remains behind an explicit validation layer.

### 2. Validate generated artifacts

Generated SQL is not treated as trusted code. It passes through application-level safety checks and PostgreSQL structural validation.

### 3. Evaluate models quantitatively

Models are evaluated using appropriate metrics rather than qualitative claims.

### 4. Compare against baselines

Where appropriate, more complex models are compared against simpler baselines.

### 5. Document failure cases

Underperforming methods are retained and analyzed rather than hidden.

### 6. Distinguish synthetic evaluation from real-world claims

Synthetic datasets are useful for demonstrating architecture and methodology, but model metrics obtained from them are not presented as evidence of real-world operational accuracy.

### 7. Keep the architecture reusable

The same core approach can support different operational domains:

```text
                  Reusable AI Analytics Architecture
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
       Maritime            Finance          Translation
       Analytics          Reconciliation      Quality
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                    Shared Engineering Principles
                    - AI agents
                    - APIs
                    - Databases
                    - Validation
                    - Analytics
                    - Observability
```

---

# ⚠️ Limitations

This project is primarily an **engineering and analytical demonstration** rather than a production maritime decision-support system.

Important limitations include:

### Synthetic Data

The maritime telemetry dataset is generated programmatically. It does not represent a proprietary real-world vessel fleet.

### Model Generalization

Reported ML metrics describe performance on the project's evaluation dataset and should not be extrapolated directly to real-world maritime operations.

### Synthetic Relationships

The simulated data-generation process can produce relationships that are cleaner and more predictable than those found in real operational data.

### Security

The SQL guardrail layer provides application-level protections but does not constitute a complete security assessment.

Production deployment would require additional controls such as:

* Database role separation.
* Least-privilege credentials.
* Query allowlisting.
* Network isolation.
* Rate limiting.
* Authentication and authorization.
* Comprehensive adversarial testing.
* Monitoring and alerting.

### Operational Deployment

The FastAPI endpoints demonstrate model serving and analytical integration. They are not intended to represent a complete production MLOps deployment.

A production implementation would additionally require:

* Model versioning.
* Automated model validation.
* CI/CD.
* Drift monitoring.
* Centralized observability.
* Automated rollback.
* Load testing.
* Secrets management.

---

# 🔬 Scientific & Engineering Positioning

The project deliberately emphasizes **methodology, reproducibility, and critical evaluation** rather than presenting unusually high model scores as evidence of real-world superiority.

The main objective is to demonstrate an end-to-end architecture that connects:

```text
Natural Language
       ↓
LLM Reasoning
       ↓
Validated SQL / Function Calls
       ↓
Operational Database
       ↓
Analytics / ML
       ↓
Optimization / Forecasting
       ↓
REST APIs / BI
       ↓
Observability
```

The additional Finance and Translation Quality modules demonstrate that the underlying architecture can be adapted to substantially different operational problems while preserving the same engineering principles.

---

# 📁 Repository Structure

A simplified view of the repository:

```text
enterprise-fleet-analytics/
│
├── chatbot_agent.py
├── main.py
│
├── database/
│   └── generate_data.py
│
├── models/
│   ├── run_training.py
│   ├── compare_models.py
│   ├── feature_importance.py
│   ├── cluster_voyages.py
│   ├── speed_optimizer.py
│   ├── classify_fuel_risk.py
│   └── forecast_fuel_trend.py
│
├── finance/
│   └── README.md
│
├── translation_quality/
│   └── README.md
│
├── data_pipeline/
│   └── README.md
│
├── Enterprise_Fleet_Analytics.pbix
│
└── README.md
```

---

# 🎯 Project Objectives

The project demonstrates practical experience across several areas:

* AI agents and LLM integration.
* Text-to-SQL systems.
* Function calling.
* REST API development.
* PostgreSQL data engineering.
* Machine learning.
* Statistical forecasting.
* Prescriptive analytics.
* Data visualization.
* ETL orchestration.
* dbt-based transformations.
* Airflow workflows.
* Financial reconciliation.
* Translation-quality analysis.
* AI system observability.
* Reproducible analytical experimentation.

The broader objective is to demonstrate how **AI agents, data engineering, machine learning, and operational analytics can be combined into reusable software architectures rather than isolated proof-of-concept scripts.**
