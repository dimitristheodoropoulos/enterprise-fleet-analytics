"""
parse_extract_logs.py

Reads the structured JSONL log file that extract_pageviews.py writes on
every run (logs/extract_runs.jsonl) and produces a monitoring summary:
success rate, rate-limit/404 counts, per-edition breakdown.

This is deliberately a separate script from the extraction itself -- it
demonstrates working with logs as a data source in their own right (the
job posting names "logs" explicitly alongside SQL/NoSQL/APIs/CSV), not
just printing to the console during a run.
"""

import json
import os
from collections import Counter

LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "extract_runs.jsonl")


def load_log_lines():
    if not os.path.exists(LOG_PATH):
        print(f"No log file yet at {LOG_PATH} -- run extract_pageviews.py first.")
        return []
    lines = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                lines.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # skip any malformed line rather than crashing
    return lines


def main():
    entries = load_log_lines()
    if not entries:
        return

    print(f"Parsed {len(entries)} log entries from {LOG_PATH}\n")

    status_counts = Counter(e["status"] for e in entries)
    print("Status breakdown:")
    for status, count in status_counts.most_common():
        pct = 100 * count / len(entries)
        print(f"  {status:10s} {count:4d}  ({pct:.0f}%)")

    by_project = Counter(e["project"] for e in entries if e["status"] == "ok")
    print("\nSuccessful calls by language edition:")
    for project, count in by_project.most_common():
        print(f"  {project:15s} {count}")

    rate_limited = [e for e in entries if e["status"] == "rate_limited"]
    if rate_limited:
        print(f"\n{len(rate_limited)} call(s) were rate-limited during the most recent runs:")
        for e in rate_limited[-5:]:
            print(f"  {e['timestamp']}  {e['project']}/{e['article']}")

    total_items = sum(e.get("item_count", 0) for e in entries if e["status"] == "ok")
    print(f"\nTotal pageview data points ingested across all logged runs: {total_items}")


if __name__ == "__main__":
    main()