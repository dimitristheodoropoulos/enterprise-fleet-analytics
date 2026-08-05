"""
analyze_coverage_gap.py

Queries language_coverage_gap (see sql/views.sql) and reports which language
editions lag furthest behind the leading edition for each topic — a real,
data-backed starting point for a "why" investigation (content gap? smaller
reader base? translation lag?), in the same spirit as the hypothesis-driven
walkthrough in ../translation_quality/.

This script deliberately stops at "here's the pattern and the open
questions it raises" rather than asserting a cause — with only pageview
counts (no edit/translation-quality signal in this dataset), asserting a
root cause here would be overreach. That's a judgment call, not a
limitation to gloss over.
"""

import os
import psycopg2

def main():
    # Διαβάζουμε το DATABASE_URL τη στιγμή που καλείται η main
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set. Export it or put it in a local .env file.")
    
    # Σύνδεση με sslmode='require' για τη Supabase
    conn = psycopg2.connect(db_url, sslmode='require')
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT topic, project, total_views, pct_of_top_edition
                FROM language_coverage_gap
                ORDER BY topic, pct_of_top_edition DESC;
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    current_topic = None
    for topic, project, total_views, pct in rows:
        if topic != current_topic:
            print(f"\n== {topic} ==")
            current_topic = topic
        flag = "  <- lagging edition, worth investigating" if pct < 20 else ""
        print(f"  {project:15s} {total_views:>8} views  ({pct}% of leading edition){flag}")

    print(
        "\nNote: pageview share alone doesn't say *why* an edition lags — "
        "smaller reader population, less complete translation of the article, "
        "or genuinely lower interest are all plausible and untested here. "
        "Flagging it as a question, not a conclusion."
    )


if __name__ == "__main__":
    main()