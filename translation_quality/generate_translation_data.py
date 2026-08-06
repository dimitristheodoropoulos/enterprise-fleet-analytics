"""
generate_translation_data.py

Generates a synthetic-but-realistic dataset of LLM translation events for
the translation_quality analytics module.

Design intent (deliberately mirrors real production dynamics, not random noise):
  1. Some language pairs are structurally more distant from English
     (word order, script, honorific systems) -> higher baseline edit distance.
  2. Some content types (legal, marketing) require more post-editing due to
     tone/idiom/terminology sensitivity, independent of language pair.
  3. Longer source sentences are harder to translate cleanly -> a genuine
     confound that must be controlled for before blaming language pair alone.
  4. An AI model upgrade ("v2") is rolled out on day 45. It meaningfully
     reduces edit distance for most language pairs, but NOT for en-ja,
     because v2's training data under-represented that pair. This is the
     root cause an analyst is expected to uncover -- not something visible
     from a single aggregate metric.
  5. Genuine random noise is layered on top of all of the above so no
     signal is perfectly clean.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RNG = np.random.default_rng(42)

N_DAYS = 90
MODEL_SWITCH_DAY = 45  # v2 deployed on this day
START_DATE = datetime(2026, 4, 1)

LANGUAGE_PAIRS = ["en-el", "en-es", "en-fr", "en-de", "en-ja", "en-zh", "en-pt", "en-it"]

# Structural distance from English (word order, script, morphology).
# Higher = harder to translate cleanly => higher baseline edit distance.
STRUCTURAL_DISTANCE = {
    "en-el": 0.35, "en-es": 0.15, "en-fr": 0.18, "en-de": 0.25,
    "en-ja": 0.70, "en-zh": 0.65, "en-pt": 0.15, "en-it": 0.17,
}

# How much the v2 model upgrade reduces edit distance, per language pair.
# en-ja and en-zh get much smaller benefit -- v2's training mix under-weighted
# CJK data. en-ja is the worst case (near zero improvement).
V2_IMPROVEMENT = {
    "en-el": 0.28, "en-es": 0.32, "en-fr": 0.30, "en-de": 0.27,
    "en-ja": 0.03, "en-zh": 0.14, "en-pt": 0.31, "en-it": 0.29,
}

CONTENT_TYPES = ["marketing", "documentation", "support_ticket", "legal"]

# Extra edit burden by content type (idiom/tone/terminology sensitivity).
CONTENT_TYPE_EFFECT = {
    "marketing": 0.12, "documentation": 0.03, "support_ticket": 0.02, "legal": 0.16,
}

# Content type is not uniformly distributed across language pairs in real
# platforms (e.g. more legal content flows through higher-resource languages).
# Skew it slightly so a naive analyst might initially blame content mix.
CONTENT_TYPE_WEIGHTS = {
    "en-el": [0.30, 0.35, 0.25, 0.10],
    "en-es": [0.30, 0.30, 0.30, 0.10],
    "en-fr": [0.28, 0.32, 0.28, 0.12],
    "en-de": [0.25, 0.30, 0.25, 0.20],
    "en-ja": [0.20, 0.35, 0.30, 0.15],
    "en-zh": [0.22, 0.33, 0.30, 0.15],
    "en-pt": [0.32, 0.30, 0.28, 0.10],
    "en-it": [0.30, 0.32, 0.28, 0.10],
}

# --- ΝΕΕΣ ΔΙΑΣΤΑΣΕΙΣ ΓΙΑ ΤΗΝ ΑΓΓΕΛΙΑ ---
PROVIDERS = ["Gemini", "OpenAI", "Internal"]
CUSTOMER_TIERS = ["free", "premium", "enterprise"]
TRAFFIC_VOLUMES = ["low", "medium", "high"]
# ---------------------------------------

rows = []
row_id = 1

for day in range(N_DAYS):
    date = START_DATE + timedelta(days=day)
    model_version = "v2" if day >= MODEL_SWITCH_DAY else "v1"
    # daily volume varies a bit
    n_events_today = RNG.integers(35, 55)

    for _ in range(n_events_today):
        lang_pair = RNG.choice(LANGUAGE_PAIRS)
        content_type = RNG.choice(CONTENT_TYPES, p=CONTENT_TYPE_WEIGHTS[lang_pair])

        # --- ΤΥΧΑΙΑ ΕΠΙΛΟΓΗ ΝΕΩΝ ΔΙΑΣΤΑΣΕΩΝ ---
        provider = RNG.choice(PROVIDERS)
        customer_tier = RNG.choice(CUSTOMER_TIERS, p=[0.4, 0.35, 0.25]) # More free users
        traffic_volume = RNG.choice(TRAFFIC_VOLUMES, p=[0.2, 0.5, 0.3]) # Mostly medium traffic
        # ---------------------------------------

        # Source sentence length (words) -- log-normal, content-type dependent
        base_len = {"marketing": 18, "documentation": 35, "support_ticket": 22, "legal": 48}[content_type]
        sentence_length = max(5, int(RNG.lognormal(mean=np.log(base_len), sigma=0.35)))

        # --- Build edit distance (normalized 0-1: fraction of tokens edited) ---
        baseline = 0.10
        structural = STRUCTURAL_DISTANCE[lang_pair]
        content_effect = CONTENT_TYPE_EFFECT[content_type]
        length_effect = min(0.20, sentence_length / 400)  # longer -> harder, capped

        v2_reduction = V2_IMPROVEMENT[lang_pair] if model_version == "v2" else 0.0

        noise = RNG.normal(0, 0.045)

        edit_distance = baseline + structural + content_effect + length_effect - v2_reduction + noise
        edit_distance = float(np.clip(edit_distance, 0.01, 0.95))

        latency_ms = int(RNG.normal(420 if model_version == "v1" else 380, 60))
        latency_ms = max(120, latency_ms)

        quality_score = float(np.clip(1.0 - edit_distance + RNG.normal(0, 0.03), 0.05, 1.0))

        rows.append({
            "event_id": row_id,
            "timestamp": date.strftime("%Y-%m-%d"),
            "language_pair": lang_pair,
            "ai_model_version": model_version,
            "ai_model_provider": provider,        # Νέο πεδίο
            "customer_tier": customer_tier,      # Νέο πεδίο
            "traffic_volume": traffic_volume,    # Νέο πεδίο
            "content_type": content_type,
            "sentence_length_words": sentence_length,
            "latency_ms": latency_ms,
            "user_edit_distance": round(edit_distance, 4),
            "quality_score": round(quality_score, 4),
        })
        row_id += 1

df = pd.DataFrame(rows)
df.to_csv("translation_events.csv", index=False)
print(f"Generated {len(df)} rows across {N_DAYS} days -> translation_events.csv")
print(df.head())
print("\nRows per language pair:")
print(df["language_pair"].value_counts())
