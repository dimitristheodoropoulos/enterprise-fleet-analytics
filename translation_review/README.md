# Translation Review: Real EN→EL Sentence Evaluation 🇬🇧🇬🇷

The other modules in this repo ([`translation_quality/`](../translation_quality) and [`data_pipeline/`](../data_pipeline)) demonstrate investigative methodology and data engineering. This module is different on purpose: it's **real sentences, a real machine translation, and my own real linguistic judgment** — not synthetic data and not something a script can do on its own.

The job posting is explicit that this matters:

> *"Evaluating multilingual AI output for meaning, terminology, tone, formality, grammar, pronouns, and consistency... using AI tools, dictionaries, and other resources to investigate languages you don't speak, while recognizing when expert linguistic input is needed."*

I'm a native Greek speaker, so for the EN↔EL pair specifically, I can do this evaluation directly rather than needing a third-party linguist — which is exactly the situation the posting describes for "at least one additional language (preferably European)."

## What's in here

| File | Role |
|---|---|
| `fetch_tatoeba_pairs.py` | Downloads real English sentences with real human Greek translations from [Tatoeba](https://tatoeba.org) — a genuine, community-contributed multilingual sentence corpus |
| `run_mt_and_build_template.py` | Runs each English sentence through a real, free machine-translation engine (Google Translate, via `deep-translator`, no API key), and builds `review_template.csv` with the MT output next to the human reference |
| `review_template.csv` | Generated file: id, English source, human reference translation, MT output, and empty columns for my own judgment |
| `summarize_review.py` | Once the judgment columns are filled in by hand, produces a short repeatable summary — verdict breakdown, flagged sentences for follow-up |

## The evaluation columns (filled in by hand, not by a script)

- **meaning_correct** — does the MT output actually say the same thing as the source? (yes / no / partially)
- **tone_formality_notes** — did the MT preserve register (formal/informal), or flatten it?
- **grammar_pronoun_notes** — Greek has grammatical gender and case agreement that English doesn't; this is where MT engines most often slip
- **overall_verdict** — good / needs review / wrong
- **your_comment** — free-text, the kind of note I'd actually hand to an engineer or PM

## Why this design

The posting draws a real distinction between "reporting a metric" and "investigating and evaluating." A script can compute edit distance or BLEU score between two strings, but it can't tell you *why* a translation feels unnatural, or whether a grammatical case was wrong versus just unusual style. That judgment call is the actual skill being asked for — so I built the pipeline to get real sentences and a real MT output in front of me, and did the evaluation myself rather than faking it with another automated score.

## Running it

```bash
cd translation_review
pip install requests deep-translator

python3 fetch_tatoeba_pairs.py        # downloads real EN-EL pairs, samples 20
python3 run_mt_and_build_template.py  # gets real MT output, builds the CSV template

# open review_template.csv, fill in the 5 judgment columns by hand

python3 summarize_review.py           # summarizes your completed review
```

## Honesty note

The sentence sample size (20) is small on purpose — this demonstrates the *process* end-to-end, not a large-scale evaluation. In a real role, this same pipeline would scale to hundreds or thousands of sentences, likely with a sampling strategy targeting the language pairs and content types flagged as problematic by the investigation in [`translation_quality/`](../translation_quality).
