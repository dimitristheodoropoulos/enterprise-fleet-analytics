"""
translation_pageview_pipeline DAG

extract_pageviews.py -> load_to_supabase.py -> dbt run -> analyze_coverage_gap.py

All four steps run inside the Airflow worker container, which has
DATABASE_URL available as an environment variable (set via docker-compose),
so each BashOperator inherits it automatically — no per-task secrets wiring
needed for this local setup.
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/data_pipeline"

with DAG(
    dag_id="translation_pageview_pipeline",
    description="Extract multilingual Wikipedia pageviews, load to Postgres, transform with dbt, analyze coverage gaps",
    start_date=datetime(2026, 8, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["translation-quality", "portfolio"],
) as dag:

    extract = BashOperator(
        task_id="extract_pageviews",
        bash_command=f"cd {PROJECT_DIR} && python extract_pageviews.py",
    )

    load = BashOperator(
        task_id="load_to_supabase",
        bash_command=f"cd {PROJECT_DIR} && python load_to_supabase.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            f"cd {PROJECT_DIR}/dbt && "
            "DBT_PROFILES_DIR=. dbt run"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"cd {PROJECT_DIR}/dbt && "
            "DBT_PROFILES_DIR=. dbt test"
        ),
    )

    analyze = BashOperator(
        task_id="analyze_coverage_gap",
        bash_command=f"cd {PROJECT_DIR} && python analyze_coverage_gap.py",
    )

    extract >> load >> dbt_run >> dbt_test >> analyze
