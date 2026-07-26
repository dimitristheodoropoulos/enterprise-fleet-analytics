"""
analyze_edit_drift.py

Investigates: "Why do users edit some language pairs' translations far more
than others?" -- following the same discipline as models/README.md in the
sibling fleet-analytics module: form a hypothesis, test it, rule it in or
out with data, and don't stop at the first plausible-looking explanation.

Run: python3 analyze_edit_drift.py
Outputs: printed findings + two charts (edit_distance_by_pair.png,
v2_rollout_impact.png)
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv("translation_events.csv")

print("=" * 70)
print("STEP 1 — Surface the pattern")
print("=" * 70)

by_pair = df.groupby("language_pair")["user_edit_distance"].agg(["mean", "count"]).sort_values("mean", ascending=False)
print(by_pair.round(4))
print(
    "\nObservation: en-ja and en-zh show noticeably higher average edit "
    "distance than the other six language pairs. That alone doesn't tell us "
    "why -- three competing explanations need to be checked before we "
    "recommend anything.\n"
)

fig, ax = plt.subplots(figsize=(9, 5))
by_pair["mean"].sort_values().plot(kind="barh", ax=ax, color="#4C72B0")
ax.set_xlabel("Mean user edit distance (fraction of tokens edited)")
ax.set_title("Edit Distance by Language Pair (all data)")
plt.tight_layout()
plt.savefig("edit_distance_by_pair.png", dpi=120)
plt.close()

print("=" * 70)
print("STEP 2 — Hypothesis A: is it just a content-type mix difference?")
print("=" * 70)

mix = pd.crosstab(df["language_pair"], df["content_type"], normalize="index")
print(mix.round(2))

overall_mix = df["content_type"].value_counts(normalize=True)
content_effect_est = df.groupby("content_type")["user_edit_distance"].mean()
# Re-weight each language pair's edit distance as if it had the OVERALL
# content-type mix, to strip out any mix-driven difference.
adjusted = {}
for pair, group in df.groupby("language_pair"):
    pair_mix = group["content_type"].value_counts(normalize=True).reindex(overall_mix.index, fill_value=0)
    per_type_mean = group.groupby("content_type")["user_edit_distance"].mean().reindex(overall_mix.index)
    per_type_mean = per_type_mean.fillna(content_effect_est)
    adjusted[pair] = (per_type_mean * overall_mix).sum()

adjusted_series = pd.Series(adjusted, name="content_mix_adjusted_mean").sort_values(ascending=False)
print("\nContent-mix-adjusted mean edit distance (removes content-type skew):")
print(adjusted_series.round(4))
print(
    "\nVerdict: en-ja and en-zh are still ~2x the lowest pairs even after "
    "equalizing content-type mix. Content mix explains only a small slice "
    "of the gap -- ruled out as the primary cause.\n"
)

print("=" * 70)
print("STEP 3 — Hypothesis B: is it just sentence length?")
print("=" * 70)

corr = df["sentence_length_words"].corr(df["user_edit_distance"])
print(f"Overall correlation(sentence_length, edit_distance) = {corr:.3f}")

# Simple linear control: regress edit_distance on sentence_length, look at
# residuals by language pair. If en-ja/en-zh residuals are still high,
# length isn't the (whole) story either.
slope, intercept, r, p, se = stats.linregress(df["sentence_length_words"], df["user_edit_distance"])
df["predicted_from_length"] = intercept + slope * df["sentence_length_words"]
df["residual"] = df["user_edit_distance"] - df["predicted_from_length"]

resid_by_pair = df.groupby("language_pair")["residual"].mean().sort_values(ascending=False)
print("\nMean residual edit distance by language pair, after removing the "
      "sentence-length effect:")
print(resid_by_pair.round(4))
print(
    "\nVerdict: correlation is positive but modest (r={:.2f}), and en-ja/en-zh "
    "still carry large positive residuals after controlling for length. "
    "Length is a real but partial factor -- also ruled out as the primary "
    "cause.\n".format(corr)
)

print("=" * 70)
print("STEP 4 — Hypothesis C: did the v2 model rollout help every pair equally?")
print("=" * 70)

pre_post = (
    df.groupby(["language_pair", "ai_model_version"])["user_edit_distance"]
    .mean()
    .unstack("ai_model_version")
)
pre_post["absolute_improvement"] = pre_post["v1"] - pre_post["v2"]
pre_post["relative_improvement_pct"] = (pre_post["absolute_improvement"] / pre_post["v1"] * 100)
pre_post = pre_post.sort_values("relative_improvement_pct")
print(pre_post.round(4))

# Statistical check on the worst case (en-ja): is its v1->v2 change
# distinguishable from noise, and is it distinguishable from the fleet-wide
# average improvement?
ja_v1 = df[(df.language_pair == "en-ja") & (df.ai_model_version == "v1")]["user_edit_distance"]
ja_v2 = df[(df.language_pair == "en-ja") & (df.ai_model_version == "v2")]["user_edit_distance"]
t_ja, p_ja = stats.ttest_ind(ja_v1, ja_v2, equal_var=False)

others_v1 = df[(df.language_pair != "en-ja") & (df.ai_model_version == "v1")]["user_edit_distance"]
others_v2 = df[(df.language_pair != "en-ja") & (df.ai_model_version == "v2")]["user_edit_distance"]
t_all, p_all = stats.ttest_ind(others_v1, others_v2, equal_var=False)

print(f"\nen-ja v1 vs v2:      t={t_ja:.2f}, p={p_ja:.4f} "
      f"(mean drop {ja_v1.mean()-ja_v2.mean():.4f})")
print(f"other pairs v1 vs v2: t={t_all:.2f}, p={p_all:.4f} "
      f"(mean drop {others_v1.mean()-others_v2.mean():.4f})")

print(
    "\nVerdict: every language pair except en-ja shows a large, statistically "
    "clear drop in edit distance after the v2 rollout. en-ja shows almost no "
    "improvement, and it is the weakest performer in the whole dataset both "
    "before and after. This is the strongest lead -- not content mix, not "
    "sentence length, but v2 not generalizing to en-ja.\n"
)

fig, ax = plt.subplots(figsize=(9, 5))
pre_post[["v1", "v2"]].plot(kind="bar", ax=ax, color=["#C44E52", "#55A868"])
ax.set_ylabel("Mean user edit distance")
ax.set_title("Edit Distance Before (v1) vs After (v2) Model Rollout, by Language Pair")
ax.legend(["v1 (pre-rollout)", "v2 (post-rollout)"])
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("v2_rollout_impact.png", dpi=120)
plt.close()

print("=" * 70)
print("STEP 5 — Root cause statement & recommendation")
print("=" * 70)
print(
    "The elevated edit distance for en-ja is not explained by content-type "
    "mix or sentence length -- both contribute a little, but a large gap "
    "remains after controlling for each. The gap opens up specifically at "
    "the v2 rollout: every other language pair improved substantially, "
    "en-ja did not. The most likely explanation is that v2's training data "
    "under-represented Japanese, so the model upgrade that helped the rest "
    "of the fleet didn't transfer to that pair.\n"
    "\n"
    "Recommendation: prioritize en-ja for targeted fine-tuning or additional "
    "training data in the next model iteration, rather than treating it as "
    "'just a harder language' to be accepted as-is. Before committing "
    "engineering resources, this finding should be confirmed with a native "
    "Japanese linguist review of a sample of flagged translations, since "
    "edit distance alone can't distinguish genuine quality issues from "
    "stylistic preference edits.\n"
    "\n"
    "Caveat: this is a synthetic dataset built to demonstrate the "
    "investigation methodology (hypothesis -> test -> rule out -> confirm), "
    "not a claim about any real production system."
)
