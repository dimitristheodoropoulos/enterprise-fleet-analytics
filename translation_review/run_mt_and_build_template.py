"""
run_mt_and_build_template.py

For each sampled EN sentence, gets a real machine-translation output
(free, no API key, via the `deep-translator` package's Google Translate
backend), pairs it with the real Tatoeba human reference translation, and
writes a CSV template with empty judgment columns for you to fill in by
hand -- meaning, tone/formality, grammar/pronouns, overall verdict.

Install once: pip install deep-translator
"""

import csv
import json
import os
import time

from deep_translator import GoogleTranslator

IN_PATH = os.path.join(os.path.dirname(__file__), "sampled_pairs.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "review_template.csv")

FIELDS = [
    "id",
    "en_source",
    "el_human_reference",
    "el_machine_translation",
    "meaning_correct",       # fill in: yes / no / partially
    "tone_formality_notes",  # fill in: your notes
    "grammar_pronoun_notes", # fill in: your notes
    "overall_verdict",       # fill in: good / needs review / wrong
    "your_comment",          # fill in: free text
]


def main():
    with open(IN_PATH, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    translator = GoogleTranslator(source="en", target="el")

    rows = []
    for i, pair in enumerate(pairs, 1):
        en = pair["en"]
        try:
            mt_output = translator.translate(en)
        except Exception as e:
            mt_output = f"[MT FAILED: {e}]"
        rows.append(
            {
                "id": i,
                "en_source": en,
                "el_human_reference": pair["el_reference"],
                "el_machine_translation": mt_output,
                "meaning_correct": "",
                "tone_formality_notes": "",
                "grammar_pronoun_notes": "",
                "overall_verdict": "",
                "your_comment": "",
            }
        )
        print(f"{i}/{len(pairs)} translated")
        time.sleep(0.3)  # polite pacing against the free endpoint

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nTemplate written -> {OUT_PATH}")
    print("Open it in a spreadsheet app (or VS Code) and fill in the judgment columns by hand.")


if __name__ == "__main__":
    main()
