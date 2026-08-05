"""
load_to_supabase.py

Loads raw_pageviews.csv into a Supabase (hosted Postgres) table.
Reads the connection string from the DATABASE_URL environment variable —
never hardcode credentials in the script or commit them to git.

Get DATABASE_URL from: Supabase project -> Settings -> Database -> Connection string (URI).
Locally, put it in a .env file (add .env to .gitignore) or export it in your shell.
In GitHub Actions, set it as a repository secret (see the workflow file).
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. Export it or put it in a local .env file."
        )
    return psycopg2.connect(DATABASE_URL)


def ensure_schema(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_pageviews (
                topic   TEXT NOT NULL,
                project TEXT NOT NULL,
                article TEXT NOT NULL,
                date    DATE NOT NULL,
                views   INTEGER NOT NULL,
                PRIMARY KEY (topic, project, date)
            );
            """
        )
    conn.commit()


def load(csv_path: str):
    df = pd.read_csv(csv_path, parse_dates=["date"])
    conn = get_connection()
    try:
        ensure_schema(conn)
        records = list(
            df[["topic", "project", "article", "date", "views"]].itertuples(
                index=False, name=None
            )
        )
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO raw_pageviews (topic, project, article, date, views)
                VALUES %s
                ON CONFLICT (topic, project, date) DO UPDATE
                    SET views = EXCLUDED.views, article = EXCLUDED.article;
                """,
                records,
            )
        conn.commit()
        print(f"Loaded/updated {len(records)} rows into raw_pageviews.")
    finally:
        conn.close()


if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), "raw_pageviews.csv")
    load(csv_path)
