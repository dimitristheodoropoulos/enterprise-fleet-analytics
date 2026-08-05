"""
load_to_supabase.py

Loads raw_pageviews.csv into a Supabase (hosted Postgres) table.
Reads the connection string from the DATABASE_URL environment variable.
This script now automatically loads from the .env file using python-dotenv.
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv  # <-- Η βιβλιοθήκη που χρειαζόμαστε

# Φόρτωση του αρχείου .env που βρίσκεται στον ίδιο φάκελο
load_dotenv()

def get_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Make sure .env file exists in this folder "
            "and contains DATABASE_URL=postgresql://..."
        )
    return psycopg2.connect(db_url, sslmode='require')


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