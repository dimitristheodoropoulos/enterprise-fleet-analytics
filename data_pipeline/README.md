# Data Pipeline: Multilingual Wikipedia Pageview Coverage 🌍📥

A small, real (not synthetic) ETL pipeline, kept intentionally lean — no dbt, no orchestrator, just a scheduled script and SQL views — built as a companion to [`translation_quality/`](../translation_quality), which demonstrates the *investigative* side of this OnTheGoSystems posting. This module demonstrates the *data engineering* side: pulling from a live external API, loading into a cloud SQL database, transforming with SQL, and running on a schedule without anyone triggering it by hand.

## Why Wikipedia pageviews

It's a genuinely public, real-time, free, no-API-key data source that is inherently multilingual — the same topic exists as a differently-titled article on each language edition of Wikipedia, and how much attention it gets varies by edition. That's a real cross-language signal, not a stand-in for one.

## What it does

| File | Role |
|---|---|
| `extract_pageviews.py` | Pulls daily pageview counts for a small set of topics, across 6 Wikipedia language editions, from the free Wikimedia REST API |
| `load_to_supabase.py` | Loads the extracted rows into a Postgres table (`raw_pageviews`) hosted on Supabase's free tier |
| `sql/views.sql` | Two SQL views: a daily per-edition ranking, and a `language_coverage_gap` view showing each edition's pageviews as a % of the leading edition per topic |
| `analyze_coverage_gap.py` | Queries the view and prints which language editions lag furthest behind — framed as an open question, not a conclusion (see note below) |
| `.github/workflows/daily_pageview_extract.yml` | Runs extract + load automatically every day via GitHub Actions — no local machine needs to be on |

## Mapping to the job posting

| Posting asks for | Where it's covered |
|---|---|
| Extracting/combining data from SQL, NoSQL, logs, APIs, CSV exports | Live API extraction → raw JSON archived in **MongoDB (NoSQL)** → flattened CSV → cloud **Postgres (SQL)**, plus structured **JSONL run logs** (`logs/extract_runs.jsonl`) parsed by a separate monitoring script (`parse_extract_logs.py`) |
| Comparing results across language pairs / dimensions | `language_coverage_gap` view compares every edition per topic |
| Building repeatable reports, scripts, and monitoring processes | Scheduled GitHub Actions run, idempotent upserts (`ON CONFLICT DO UPDATE`) so re-runs are safe |
| Separating real signals from coincidence | The analysis script explicitly stops short of claiming a cause with only pageview data — flags it as a question instead of overreaching |
| Strong hands-on experience using AI tools / data tooling generally, working independently | dbt models + tests and an Airflow DAG show the same investigative pipeline built with the tooling a data team would actually standardize on |

## Honesty note

This dataset answers "how much attention does each language edition get," not "is the translation quality good" — those are different questions. I did not force a connection to translation-quality that the data doesn't support. If asked to extend this, the natural next step would be joining it against actual edit-history/translation-lag data per article and language, which Wikipedia also exposes via API.

## Two ways to run this

### A. Plain scripts + SQL views (fastest path, always-on via GitHub Actions)

```bash
cd data_pipeline
pip install -r requirements.txt
export DATABASE_URL="postgresql://...supabase connection string..."
python extract_pageviews.py
python load_to_supabase.py
python analyze_coverage_gap.py
```

Then run `sql/views.sql` once in the Supabase SQL editor to create the views. `.github/workflows/daily_pageview_extract.yml` runs steps 1–2 automatically every day — this part is genuinely always-on, since GitHub runs it for you.

### B. dbt + Airflow (same pipeline, orchestrated)

`dbt/` replaces `sql/views.sql` with proper dbt models (staging + marts, with tests), and `airflow/` orchestrates the full sequence — extract → load → `dbt run` → `dbt test` → analyze — as a DAG.

```bash
# one-time: create a local ~/.dbt/profiles.yml from dbt/profiles.yml.example
# (or set DBT_PROFILES_DIR to point at dbt/), then:
cd data_pipeline/dbt
export SUPABASE_HOST=... SUPABASE_USER=... SUPABASE_PASSWORD=... SUPABASE_DBNAME=...
dbt run
dbt test

# to see it as an orchestrated DAG:
cd ../airflow
cp .env.example .env   # fill in your real values
docker compose up airflow-init   # first time only
docker compose up
# open http://localhost:8080 (admin / admin), trigger `translation_pageview_pipeline`
```
## 📊 Live Dashboard (Streamlit)

Beyond the command-line analysis, this module includes a live, interactive dashboard built with **Streamlit** and **Plotly**. It connects directly to the Supabase database and visualizes the `language_coverage_gap` findings as dynamic bar charts.

**Run it locally:**
```bash
pip install streamlit plotly
streamlit run dashboard.py

🤖 AI-Assisted Hypothesis Generation (Gemini)
To demonstrate the "investigative" and "AI-tooling" side of the role, a separate script feeds the pattern discovered by analyze_coverage_gap.py into an LLM (gemini-2.5-flash). The model generates three plausible hypotheses for why the gap exists, suggests specific metrics to test them, and provides a critical evaluation of whether the data could indicate a translation quality issue — all in plain language suitable for a Product Manager or Linguist.

Run it locally:
export GEMINI_API_KEY="your_google_api_key"
python3 llm_coverage_analysis.py

**Honest scope note:** this local Airflow only runs while `docker compose up` is running on this machine — it is not a 24/7 production scheduler the way the GitHub Actions workflow is. It's here to demonstrate DAG design, task dependencies, and dbt orchestration, not to replace the always-on path in option A. Both are kept because they demonstrate different things: A is "this actually runs unattended," B is "I can build and read a DAG."
