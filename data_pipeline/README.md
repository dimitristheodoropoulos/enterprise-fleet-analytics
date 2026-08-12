# Data Pipeline: Multilingual Wikipedia Pageview Coverage 🌍📥

A reproducible ETL and analytics pipeline that collects **real multilingual Wikipedia pageview data** from the Wikimedia REST API, stores it in PostgreSQL, transforms it with SQL/dbt, and exposes the results through command-line analysis and an interactive dashboard.

The module demonstrates the **data-engineering and investigative workflow** behind the broader [AI-Driven Operational Analytics Platform](../README.md).

Unlike the synthetic datasets used in some of the machine-learning demonstrations elsewhere in the repository, this pipeline operates on a **live public data source**.

---

# 🎯 Objective

The pipeline investigates a simple descriptive question:

> **How does Wikipedia attention for the same topic differ across language editions?**

The purpose is deliberately narrower than claiming that pageview differences indicate translation quality.

Wikipedia pageviews can reveal differences in audience attention across language editions, but they cannot by themselves establish:

* Translation quality.
* Translation accuracy.
* User satisfaction.
* Linguistic quality.
* Causal relationships between language coverage and user behavior.

The pipeline therefore treats the observed pageview differences as **signals for further investigation**, rather than as conclusions about translation quality.

---

# 🌍 Why Wikipedia Pageviews?

Wikipedia provides a useful public data source for demonstrating multilingual data engineering because:

* The data is publicly accessible.
* The Wikimedia API can be queried without a paid data subscription.
* Multiple language editions are available.
* Pageview data is generated from real user activity.
* The same broad topic can be investigated across different language editions.
* The data can be collected repeatedly over time.

This makes the dataset suitable for demonstrating an end-to-end pipeline involving:

```text
External API
     ↓
Raw Data
     ↓
NoSQL / JSON Archive
     ↓
Flattened Dataset
     ↓
PostgreSQL
     ↓
SQL / dbt Transformations
     ↓
Analytics
     ↓
Dashboard / AI-Assisted Investigation
```

---

# 🏗️ Pipeline Architecture

The repository contains two implementations of the same analytical workflow.

## Path A — Lean Scheduled Pipeline

The simplest implementation uses Python scripts, PostgreSQL/ Supabase, SQL views, and GitHub Actions.

```text
Wikimedia REST API
        │
        ▼
extract_pageviews.py
        │
        ▼
Raw JSON / MongoDB
        │
        ▼
Flattened CSV
        │
        ▼
load_to_supabase.py
        │
        ▼
PostgreSQL / Supabase
        │
        ▼
SQL Views
        │
        ▼
analyze_coverage_gap.py
        │
        ├───────────────┐
        ▼               ▼
CLI Analysis       Streamlit Dashboard
```

GitHub Actions runs the extraction and loading steps automatically on a daily schedule.

This is the **leanest and most operationally simple implementation**.

---

# 🔧 Path B — dbt + Airflow

A second implementation demonstrates how the same workflow can be standardized using common data-engineering tools.

```text
Wikimedia REST API
        │
        ▼
Extraction
        │
        ▼
Raw Data
        │
        ▼
PostgreSQL / Supabase
        │
        ▼
       dbt
   ┌────┴────┐
   ▼         ▼
Staging     Marts
   │         │
   └────┬────┘
        ▼
    dbt tests
        │
        ▼
    Analysis
```

Airflow provides orchestration:

```text
Extract
   ↓
Load
   ↓
dbt run
   ↓
dbt test
   ↓
Analyze
```

The two paths are intentionally kept because they demonstrate different engineering capabilities:

* **Path A:** simple, reproducible, unattended execution.
* **Path B:** dependency management, orchestration, transformation modeling, and data-quality testing.

---

# 📂 Project Structure

| Component                                      | Purpose                                                               |
| ---------------------------------------------- | --------------------------------------------------------------------- |
| `extract_pageviews.py`                         | Extracts daily pageview data from the Wikimedia REST API              |
| `load_to_supabase.py`                          | Loads extracted records into PostgreSQL hosted by Supabase            |
| `sql/views.sql`                                | SQL views used by the lightweight implementation                      |
| `analyze_coverage_gap.py`                      | Calculates and reports pageview differences between language editions |
| `dashboard.py`                                 | Streamlit dashboard for interactive exploration                       |
| `llm_coverage_analysis.py`                     | Uses Gemini to generate hypotheses and investigation suggestions      |
| `parse_extract_logs.py`                        | Parses structured extraction logs for monitoring                      |
| `logs/extract_runs.jsonl`                      | JSONL execution logs for extraction runs                              |
| `dbt/`                                         | dbt models and tests for the orchestrated transformation path         |
| `airflow/`                                     | Airflow DAG and configuration for orchestrated execution              |
| `.github/workflows/daily_pageview_extract.yml` | Scheduled GitHub Actions workflow                                     |

---

# 📥 Extraction

`extract_pageviews.py` queries the public Wikimedia REST API for a predefined set of topics across multiple Wikipedia language editions.

The extraction process produces structured pageview records containing information such as:

* Topic.
* Wikipedia language edition.
* Date.
* Pageview count.

The extraction step is intentionally separated from the loading and transformation layers so that each stage can be tested independently.

---

# 🗄️ Storage

The pipeline can persist raw and processed information through multiple storage layers.

## MongoDB

Raw API responses can be archived as JSON documents in MongoDB.

This demonstrates the ability to work with a **NoSQL document store** when preserving semi-structured external API responses.

## PostgreSQL / Supabase

The flattened analytical records are loaded into PostgreSQL hosted by Supabase.

This provides a relational layer for:

* SQL transformations.
* Aggregations.
* Analytical queries.
* Dashboard access.
* dbt models.

Conceptually:

```text
Wikimedia JSON
      │
      ▼
   MongoDB
   raw JSON
      │
      ▼
Flattened records
      │
      ▼
PostgreSQL
   raw_pageviews
```

The separation between raw API responses and relational analytical records demonstrates a common pattern in data pipelines: **retain the source representation while creating a structured analytical layer**.

---

# 🔄 Data Transformation

The lightweight implementation uses SQL views defined in:

```text
sql/views.sql
```

The orchestrated implementation uses dbt models.

The transformations produce analytical datasets such as:

### Daily Edition Ranking

Ranks language editions by pageviews for each topic and date.

### Language Coverage Gap

Calculates each language edition's pageviews relative to the leading edition for the same topic.

For example:

```text
coverage_ratio =
    edition_pageviews / leading_edition_pageviews
```

and the corresponding percentage can be represented as:

```text
coverage_percentage =
    coverage_ratio × 100
```

This makes relative differences easier to compare across topics with very different absolute traffic levels.

---

# 🧪 Data Quality & Reproducibility

The dbt implementation adds explicit transformation testing.

The objective is not simply to produce a table, but to verify assumptions about the transformed data.

Typical checks can include:

* Required fields are not null.
* Identifiers are unique where expected.
* Relationships between staging and analytical models are valid.
* Derived metrics remain within expected ranges.

The pipeline also uses idempotent loading behavior where appropriate, allowing repeated runs without intentionally creating duplicate analytical records.

This is important for scheduled pipelines because failures and retries are normal operational events.

---

# 📊 Coverage-Gap Analysis

`analyze_coverage_gap.py` queries the transformed data and identifies which language editions have the largest relative pageview gaps.

The analysis is intentionally descriptive.

For example:

```text
Topic A
--------------------------------
English     100%
German       61%
French       47%
Spanish      42%
Greek        18%
```

This indicates that the Greek edition receives substantially fewer pageviews than the leading edition for that topic.

It does **not** establish why that difference exists.

Potential explanations could include:

* Different audience sizes.
* Different levels of interest in the topic.
* Differences in search behavior.
* Differences in article availability.
* Differences in article discoverability.
* Cultural differences in topic relevance.
* Differences in external linking.
* Translation or localization effects.

Those explanations require additional evidence.

---

# 🔬 Investigative Methodology

The analysis deliberately separates:

```text
Observed Pattern
       ↓
Possible Explanations
       ↓
Additional Evidence
       ↓
Hypothesis Testing
       ↓
Conclusion
```

rather than:

```text
Observed Pattern
       ↓
Assumed Cause
```

For example, if one language edition has substantially fewer pageviews, it would be inappropriate to conclude:

> "The translation is worse."

Pageview data alone cannot support that conclusion.

A stronger investigation would combine pageviews with additional signals such as:

* Article edit history.
* Translation timestamps.
* Article completeness.
* Article length.
* Inter-language links.
* Search visibility.
* Content quality indicators.
* User engagement metrics.
* Translation revision history.

The pipeline therefore treats pageview differences as a **starting point for investigation**.

---

# 🤖 AI-Assisted Hypothesis Generation

The repository also contains:

```text
llm_coverage_analysis.py
```

This script sends the observed pattern to a Gemini model (`gemini-2.5-flash`) and asks the model to:

1. Generate plausible explanations.
2. Suggest measurable variables that could test those explanations.
3. Identify evidence that would support or contradict each hypothesis.
4. Evaluate whether the current pageview data is sufficient to claim a translation-quality problem.

The conceptual workflow is:

```text
Observed Data
     │
     ▼
Descriptive Analysis
     │
     ▼
Candidate Pattern
     │
     ▼
LLM Hypothesis Generation
     │
     ▼
Candidate Explanations
     │
     ▼
Human / Data-Driven Validation
```

The LLM is therefore used as a **hypothesis-generation and investigation-assistance tool**, not as the source of truth.

An LLM-generated hypothesis is not considered a finding until it is tested against appropriate data.

---

# 📈 Live Dashboard

The module includes an interactive Streamlit dashboard using Plotly.

The dashboard connects to the analytical PostgreSQL data and visualizes the `language_coverage_gap` results.

It provides an interactive way to explore:

* Topics.
* Language editions.
* Relative pageview coverage.
* Cross-language differences.

## Run locally

Install the dashboard dependencies:

```bash
pip install streamlit plotly
```

Then:

```bash
streamlit run dashboard.py
```

The dashboard can then be accessed through the local Streamlit URL displayed by the application.

---

# ⏰ Automated Execution with GitHub Actions

The repository includes:

```text
.github/workflows/daily_pageview_extract.yml
```

which schedules the extraction and loading workflow.

The intended execution path is:

```text
Scheduled GitHub Actions Run
            │
            ▼
     Extract Wikimedia Data
            │
            ▼
       Load PostgreSQL
            │
            ▼
       Updated Dataset
```

This means the scheduled version does not depend on the developer's local computer remaining online.

The GitHub Actions workflow should be understood as the **unattended execution mechanism** for the lean pipeline.

Secrets such as database credentials should be stored through GitHub Actions Secrets rather than committed to the repository.

---

# 🛠️ Running the Lean Pipeline

## Install dependencies

```bash
cd data_pipeline
pip install -r requirements.txt
```

## Configure the database

Set the PostgreSQL/Supabase connection string:

```bash
export DATABASE_URL="postgresql://...supabase-connection-string..."
```

On Windows PowerShell:

```powershell
$env:DATABASE_URL="postgresql://...supabase-connection-string..."
```

## Extract data

```bash
python extract_pageviews.py
```

## Load data

```bash
python load_to_supabase.py
```

## Create SQL views

Run:

```text
sql/views.sql
```

once in the Supabase SQL editor.

## Analyze the results

```bash
python analyze_coverage_gap.py
```

## Run the dashboard

```bash
streamlit run dashboard.py
```

---

# 🌱 Running the dbt Pipeline

The dbt implementation replaces the standalone SQL views with version-controlled transformation models.

Configure the required environment variables:

```bash
export SUPABASE_HOST=...
export SUPABASE_USER=...
export SUPABASE_PASSWORD=...
export SUPABASE_DBNAME=...
```

Then:

```bash
cd data_pipeline/dbt
dbt run
dbt test
```

A local `profiles.yml` can be created from:

```text
dbt/profiles.yml.example
```

Alternatively, `DBT_PROFILES_DIR` can be configured to point to the appropriate directory.

---

# 🌬️ Running Airflow Locally

The Airflow implementation demonstrates orchestration of the complete pipeline.

From the Airflow directory:

```bash
cd data_pipeline/airflow
cp .env.example .env
```

Populate the required environment variables.

Initialize Airflow:

```bash
docker compose up airflow-init
```

Then start the services:

```bash
docker compose up
```

Open the Airflow web interface at:

```text
http://localhost:8080
```

and trigger:

```text
translation_pageview_pipeline
```

The DAG represents the dependency chain:

```text
Extract
  ↓
Load
  ↓
dbt Run
  ↓
dbt Test
  ↓
Analyze
```

### Important scope note

This local Airflow deployment is **not a 24/7 production scheduler**.

The DAG only runs while the local Docker Compose environment is active.

The GitHub Actions workflow is the unattended scheduled implementation in this repository.

The Airflow setup exists to demonstrate:

* DAG construction.
* Task dependencies.
* Orchestration.
* Transformation integration.
* Data-quality testing.

---

# 📝 Monitoring & Run Logs

The extraction process also produces structured JSONL execution logs:

```text
logs/extract_runs.jsonl
```

These records can be parsed by:

```text
parse_extract_logs.py
```

The logging layer captures execution information useful for monitoring repeated extraction runs.

Using structured JSONL rather than only human-readable console output makes the logs easier to process programmatically.

A production implementation could extend this with:

* Failure alerts.
* Retry metrics.
* Data freshness monitoring.
* Row-count anomaly detection.
* API latency monitoring.
* Schema-change detection.

---

# 🔐 Security Considerations

The repository intentionally avoids committing credentials.

Database and API-related secrets should be provided through environment variables or the relevant secret-management mechanism.

For example:

```bash
export DATABASE_URL="..."
export GEMINI_API_KEY="..."
```

For GitHub Actions, secrets should be configured through the repository's Actions Secrets rather than hard-coded in workflow files.

A production implementation would additionally require:

* Credential rotation.
* Least-privilege database users.
* Network restrictions.
* Encryption in transit.
* Secret-management infrastructure.
* Monitoring and alerting.

---

# ⚠️ Limitations

This pipeline is intentionally a compact engineering demonstration rather than a production-scale data platform.

Important limitations include:

### Limited topic set

Only a small predefined set of topics and language editions is collected.

### Pageviews are not translation-quality metrics

Pageview volume measures attention, not linguistic quality.

A lower pageview count does not imply that an article is poorly translated.

### Potential confounding variables

Differences between language editions may result from many factors unrelated to translation.

For example:

* Population and language reach.
* Cultural interest.
* Search behavior.
* Article discoverability.
* External referrals.
* Topic popularity.
* Media coverage.
* Differences in Wikipedia usage patterns.

### No causal inference

The pipeline is observational.

It does not use an experimental design or causal-identification methodology, so causal conclusions should not be drawn from the pageview differences alone.

### Public API dependency

The extraction process depends on the availability and behavior of the Wikimedia API.

A production implementation would require stronger retry, backoff, rate-limit handling, and data-quality monitoring.

### Local Airflow is not always-on

The Docker-based Airflow environment only operates while the local services are running.

The scheduled GitHub Actions implementation provides the unattended execution path.

---

# 🧭 Natural Next Step

If the objective were to investigate whether translation quality contributes to differences in language-edition engagement, pageview data would need to be combined with additional article-level evidence.

A possible extension would be:

```text
Wikipedia Pageviews
        +
Article Metadata
        +
Edit History
        +
Translation / Localization History
        +
Article Length / Completeness
        +
Language Pair
        │
        ▼
Multivariate Analysis
        │
        ▼
Hypothesis Testing
        │
        ▼
Evidence-Based Conclusion
```

This would allow the analysis to move beyond:

> "Language X receives fewer pageviews."

toward questions such as:

> "After accounting for topic popularity, article availability, article age, and content characteristics, is there evidence that translation/localization quality is associated with engagement differences?"

That would require substantially stronger data and statistical controls than the current demonstration.

---

# 🎯 What This Module Demonstrates

This module demonstrates practical data-engineering and analytical capabilities across the full pipeline:

* External REST API integration.
* Real-world data extraction.
* NoSQL document storage.
* Relational database loading.
* PostgreSQL/Supabase.
* SQL transformations.
* dbt modeling.
* dbt data-quality tests.
* Airflow orchestration.
* GitHub Actions scheduling.
* Idempotent data loading.
* Structured JSONL logging.
* Monitoring-oriented design.
* Streamlit dashboards.
* Plotly visualization.
* Hypothesis-driven analysis.
* LLM-assisted hypothesis generation.
* Explicit separation of correlation from causation.

The broader design principle is:

> **Collect real data, transform it reproducibly, validate the resulting dataset, investigate patterns systematically, and distinguish observed evidence from hypotheses that still require testing.**

This makes the module complementary to the other parts of the repository: the fleet analytics and machine-learning components demonstrate predictive analytics, while this pipeline demonstrates how a data analyst or data engineer can build the infrastructure required to obtain, transform, monitor, and investigate real operational data.
