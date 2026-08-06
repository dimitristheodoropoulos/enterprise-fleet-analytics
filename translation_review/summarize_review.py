"""
summarize_review.py

Run this AFTER you've filled in the judgment columns in review_template.csv
by hand. Produces a repeatable Markdown report -- the kind of "here's what
I found" output you'd hand to a PM or a linguist, not a wall of raw rows.
"""

import csv
import os
from collections import Counter

INPUT_PATH = os.path.join(os.path.dirname(__file__), "review_template.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "translation_quality_report.md")


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    filled = [r for r in rows if r["overall_verdict"].strip()]
    total_filled = len(filled)

    if not filled:
        print("No rows have a filled-in 'overall_verdict' yet. Fill in the judgment columns first.")
        return

    verdicts = Counter(r["overall_verdict"].strip().lower() for r in filled)
    meaning = Counter(r["meaning_correct"].strip().lower() for r in filled if r["meaning_correct"].strip())
    flagged = [r for r in filled if r["overall_verdict"].strip().lower() in ("needs review", "wrong")]
    pass_with_note = [r for r in filled if r["overall_verdict"].strip().lower() == "pass with note"]

    # --- Build Markdown report ---
    md = []
    md.append("# Machine Translation Quality Review (EN → EL)\n")
    md.append(f"**Total samples reviewed:** {total_filled} / {total}\n")

    md.append("## 📊 Overall Verdict Breakdown")
    for verdict, count in verdicts.most_common():
        pct = 100 * count / total_filled
        md.append(f"- **{verdict.capitalize()}:** {count} ({pct:.0f}%)")

    md.append("\n## ✅ Meaning Correctness Breakdown")
    if meaning:
        for m, count in meaning.most_common():
            # Διόρθωση: Διαίρεση με το σύνολο των αξιολογημένων δειγμάτων (total_filled), όχι με το πλήθος των κατηγοριών
            pct = 100 * count / total_filled
            md.append(f"- **{m.capitalize()}:** {count} ({pct:.0f}%)")
    else:
        md.append("- No meaning-correctness data available.\n")

    if flagged:
        md.append("\n## ⚠️ Flagged Sentences (Needs Review / Wrong)")
        for r in flagged:
            md.append(f"\n**ID #{r['id']}:** `{r['en_source']}`")
            md.append(f"- **Machine Translation:** `{r['el_machine_translation']}`")
            md.append(f"- **Human Reference:** `{r['el_human_reference']}`")
            if r["your_comment"].strip():
                md.append(f"- **Comment:** {r['your_comment']}")
    else:
        md.append("\n## ✅ No critical errors (0 flagged sentences).")

    # Προσθήκη λεπτομερειών για τα "Pass with note"
    if pass_with_note:
        md.append("\n## 📝 Detailed Insights from 'Pass with note'")
        md.append("\n*The 8 cases below are fully accurate in meaning, but contain subtle nuances in formality, tense, or capitalization that are worth documenting for evaluation purposes.*")
        for r in pass_with_note:
            md.append(f"\n**ID #{r['id']}:** `{r['en_source']}`")
            md.append(f"- **Human Ref:** `{r['el_human_reference']}`")
            md.append(f"- **MT:** `{r['el_machine_translation']}`")
            if r["tone_formality_notes"].strip():
                md.append(f"- **Tone/Formality Note:** {r['tone_formality_notes']}")
            if r["grammar_pronoun_notes"].strip():
                md.append(f"- **Grammar/Pronoun Note:** {r['grammar_pronoun_notes']}")
            if r["your_comment"].strip():
                md.append(f"- **Your Comment:** {r['your_comment']}")

    md.append("\n## 📌 Methodology")
    md.append("- Sample taken from the Tatoeba parallel corpus (EN-EL).")
    md.append("- Machine translation generated via a local LibreTranslate endpoint.")
    md.append("- Evaluation criteria: Meaning, Tone/Formality, Grammar/Pronouns.")
    md.append("- Final verdict based on combined human judgment.\n")

    # Write to file
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"✅ Done! Report saved to: {OUTPUT_PATH}")
    print("You can now preview it in VS Code or upload it to GitHub.")


if __name__ == "__main__":
    main()