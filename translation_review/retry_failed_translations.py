"""
retry_failed_translations.py

Finds rows in review_template.csv where the MT call failed (marked as
"[MT FAILED: ...]") and retries just those, with a longer pause between
calls. Free MT endpoints occasionally rate-limit closely-spaced requests --
this is a real, worth-documenting limitation of relying on a free tool
without an API key, not a bug in the pipeline itself.
"""

import csv
import os
import time

from deep_translator import GoogleTranslator

PATH = os.path.join(os.path.dirname(__file__), "review_template.csv")


def main():
    with open(PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    translator = GoogleTranslator(source="en", target="el")
    retried = 0

    for row in rows:
        if row["el_machine_translation"].startswith("[MT FAILED"):
            print(f"Retrying #{row['id']}: {row['en_source']}")
            time.sleep(2.0)  # longer pause than the first pass
            try:
                row["el_machine_translation"] = translator.translate(row["en_source"])
                print(f"  -> {row['el_machine_translation']}")
                retried += 1
            except Exception as e:
                row["el_machine_translation"] = f"[MT FAILED AGAIN: {e}]"
                print(f"  -> still failed: {e}")

    with open(PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nRetried {retried} row(s). File updated -> {PATH}")


if __name__ == "__main__":
    main()