"""
extract_pageviews.py

Pulls real daily pageview counts for the same underlying topic across several
Wikipedia language editions, using the free, public, no-key-required
Wikimedia REST API.

Why this topic: it's a genuine cross-language data source (not synthetic),
which fits the "SQL databases, NoSQL databases, logs, APIs, and CSV exports"
and "comparing results across language pairs" parts of the job posting,
without depending on any translation vendor's private data.

Each Wikipedia language edition has its own article title for the same
subject (that's a real localization fact, not a coincidence) so the mapping
below is a small hardcoded dictionary. Extend ARTICLES to track more topics.
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta

# Wikimedia requires a descriptive User-Agent identifying the client.
HEADERS = {
    "User-Agent": "translation-quality-pipeline/1.0 (portfolio project; contact: replace-with-your-email)"
}

BASE_URL = (
    "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
    "{project}/all-access/all-agents/{article}/daily/{start}/{end}"
)

# topic -> {language_project: localized article title}
ARTICLES = {
    "machine_translation": {
        "en.wikipedia": "Machine_translation",
        "de.wikipedia": "Maschinelle_Übersetzung",
        "fr.wikipedia": "Traduction_automatique",
        "es.wikipedia": "Traducción_automática",
        "pt.wikipedia": "Tradução_automática",
        "ja.wikipedia": "機械翻訳",
    },
    "artificial_intelligence": {
        "en.wikipedia": "Artificial_intelligence",
        "de.wikipedia": "Künstliche_Intelligenz",
        "fr.wikipedia": "Intelligence_artificielle",
        "es.wikipedia": "Inteligencia_artificial",
        "pt.wikipedia": "Inteligência_artificial",
        "ja.wikipedia": "人工知能",
    },
}


def fetch_pageviews(project: str, article: str, start: str, end: str) -> list[dict]:
    url = BASE_URL.format(project=project, article=article, start=start, end=end)
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code == 404:
        # Article/edition combination has no data for the range — skip, don't crash.
        return []
    resp.raise_for_status()
    return resp.json().get("items", [])


def run(days_back: int = 30) -> pd.DataFrame:
    end_date = datetime.utcnow().date() - timedelta(days=1)  # API lags ~1 day
    start_date = end_date - timedelta(days=days_back)
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    rows = []
    for topic, editions in ARTICLES.items():
        for project, article in editions.items():
            items = fetch_pageviews(project, article, start_str, end_str)
            for item in items:
                rows.append(
                    {
                        "topic": topic,
                        "project": project,
                        "article": article,
                        "date": datetime.strptime(item["timestamp"][:8], "%Y%m%d").date(),
                        "views": item["views"],
                    }
                )
            time.sleep(0.2)  # polite pacing, well under Wikimedia's rate limits

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    df = run(days_back=int(os.environ.get("DAYS_BACK", "30")))
    out_path = os.path.join(os.path.dirname(__file__), "raw_pageviews.csv")
    df.to_csv(out_path, index=False)
    print(f"Extracted {len(df)} rows across {df['project'].nunique()} language editions -> {out_path}")
