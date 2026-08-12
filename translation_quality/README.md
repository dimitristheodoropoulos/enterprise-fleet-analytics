# Translation Quality Analytics 🌐🔍

Part of the [AI-Driven Operational Analytics Platform](../README.md), this module applies the same **hypothesis-driven analytical methodology** used elsewhere in the repository — including fleet efficiency and forecasting analysis — to a different domain: **LLM translation quality and user edit behavior**.

The objective is not simply to report translation-quality metrics. Instead, the analysis follows an investigative workflow:

```text
Observed pattern
      ↓
Hypothesis
      ↓
Statistical test
      ↓
Alternative explanation
      ↓
Control / adjustment
      ↓
Interpretation
      ↓
Actionable recommendation
```

This design demonstrates how an analyst can move from an observed quality signal to a structured investigation while explicitly distinguishing **statistical evidence from causal claims**.

---

# ❓ The Question

> **Why do users edit some language pairs' translations far more than others?**

The analysis uses **user edit distance** as an observable proxy for post-editing behavior.

A high edit distance may indicate that the machine-generated translation differs substantially from the final user-edited version.

However, edit distance alone does not establish that the machine translation is linguistically incorrect. Users may also make stylistic, preferential, or domain-specific changes.

The analysis therefore treats edit distance as a **diagnostic signal**, not as a direct ground-truth measure of translation quality.

---

# 🎮 Live Interactive Demo

👉 **[Run the investigation live in your browser](https://dimitristheodoropoulos.github.io/enterprise-fleet-analytics/translation_quality/)**

No local setup is required for the interactive demonstration.

The demo generates the synthetic dataset, executes the investigation through Hypotheses A, B, and C, and displays the corresponding statistical evidence, including:

* Mean edit distance.
* Correlations.
* Residuals.
* t-statistics.
* p-values.
* Pre/post model-rollout comparisons.

The browser implementation reproduces the analytical logic of `analyze_edit_drift.py` client-side.

---

# 🔬 What This Module Does

## `generate_translation_data.py`

Generates a **synthetic but structured dataset of approximately 4,000 translation events over 90 days**.

The generated records include:

* Language pair.
* Content type.
* Sentence length.
* Model version.
* AI model provider.
* Customer tier.
* Traffic volume.
* User edit distance.
* Translation latency.
* Quality score.

The synthetic dataset contains an intentional signal representing a potential language-pair-specific response to a model rollout.

This is deliberate: the dataset is constructed so that the investigation has a known pattern to recover.

Additional fields such as provider, customer tier, and traffic volume are included to support potential extensions involving comparisons across:

* Language pairs.
* AI models.
* Providers.
* Customers.
* Traffic levels.

The current investigation focuses primarily on **language pair, content type, sentence length, and model version**.

---

# `analyze_edit_drift.py`

The analysis is structured as a sequence of hypotheses rather than a single aggregate report.

## Step 1 — Surface the Pattern

Calculate mean user edit distance by language pair.

This identifies language pairs that exhibit substantially different levels of post-editing.

---

## Step 2 — Hypothesis A: Content-Type Mix

### Question

Could the observed language-pair difference simply be caused by different proportions of easy and difficult content types?

For example, a language pair receiving more technical or complex content might naturally have a higher edit distance.

### Test

Each language pair is re-weighted to a common content-type distribution.

### Result

The adjustment produces only a very small change in the observed `en-ja` mean:

```text
Before adjustment: 0.899
After adjustment:  0.901
```

The small change suggests that **content-type composition is unlikely to explain most of the observed language-pair difference in this synthetic dataset**.

This does not prove that content type has no effect. It indicates that the particular composition difference tested here does not account for the main gap.

---

# 📏 Step 3 — Hypothesis B: Sentence Length

### Question

Could longer sentences explain the higher edit distance?

### Test

The analysis examines:

1. Correlation between sentence length and edit distance.
2. Residual edit distance after controlling for sentence length using a linear model.

### Result

The synthetic data produces:

```text
Pearson correlation: r = 0.16
```

This represents a **weak positive relationship** between sentence length and edit distance.

However, after controlling for sentence length, the `en-ja` residual remains elevated.

Therefore:

> Sentence length appears to contribute to edit distance, but it does not explain the majority of the language-pair difference observed in this synthetic experiment.

This distinction is important: a variable can have a genuine relationship with the outcome without being the primary explanation for a group-level difference.

---

# 🚀 Step 4 — Hypothesis C: Model Rollout

### Question

Did the model-version change affect the language pairs differently?

The synthetic dataset contains a model rollout from:

```text
v1 → v2
```

at approximately day 45.

The analysis compares edit distance before and after the rollout for each language pair.

A statistical test is used to assess whether the observed pre/post difference is unlikely to be explained by sampling variation alone under the test assumptions.

### Observed Result

In the generated dataset, edit distance decreases substantially after the v2 rollout for most language pairs.

The reported reductions are approximately:

```text
Other language pairs: 47–80%
en-ja:                 1.5%
```

The corresponding statistical results include:

```text
en-ja:  t = 3.06,  p = 0.002
Others: t = 37.78, p < 0.0001
```

These results provide evidence of a **statistically significant pre/post difference** in the synthetic data.

However, the statistical test alone does not establish that the model rollout was the causal mechanism responsible for the observed change.

Potential alternative explanations would need to be investigated in a real production dataset, including:

* Traffic composition changes.
* User population changes.
* Content distribution changes.
* Temporal effects.
* Provider changes.
* Customer-mix changes.
* Other simultaneous system changes.

---

# 📊 Key Finding

In the synthetic dataset, `en-ja` (English → Japanese) exhibits approximately **3–4× the average edit distance of the best-performing language pairs**.

Two candidate explanations were investigated:

| Hypothesis                                         | Result                                                                                                                  |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Content-type mix differs by language pair          | Standardizing the content-type distribution barely changes the `en-ja` mean (`0.899 → 0.901`)                           |
| Longer sentences are harder to translate           | Weak positive correlation (`r = 0.16`), but the `en-ja` residual remains elevated after controlling for sentence length |
| Model rollout affects all language pairs similarly | Not supported by the synthetic data; most pairs improve substantially after v2 while `en-ja` changes only slightly      |

The strongest explanation **supported by the simulated experiment** is therefore a **language-pair-specific response to the model rollout**.

The dataset was intentionally generated with this type of signal.

---

# 🧠 Interpreting the Root Cause

A plausible real-world hypothesis would be that the new model has insufficient representation of Japanese-specific linguistic patterns in its training or adaptation data.

However, this project **does not establish that explanation empirically**.

The synthetic experiment can show that:

```text
Language-pair difference
        +
Model-version interaction
        +
Weak effect of tested confounders
```

is consistent with a language-pair-specific model effect.

It cannot determine why the model behaves differently internally.

Therefore, the hypothesis:

> **“Japanese was under-represented in the model's training data.”**

should be treated as a **follow-up hypothesis**, not as a demonstrated root cause.

In a real production investigation, this would require additional evidence such as:

* Training-data composition analysis.
* Evaluation by linguistic phenomenon.
* Native-speaker review.
* Error-category analysis.
* Terminology coverage analysis.
* Model-level diagnostics.
* Controlled A/B evaluation.

---

# 🎯 Recommendation

Based on the simulated investigation, `en-ja` would be a reasonable candidate for **targeted investigation and additional evaluation**.

Before allocating significant engineering resources to fine-tuning or additional training data, the recommended next step would be:

### 1. Native-speaker linguistic review

Inspect a representative sample of the high-edit-distance `en-ja` cases.

Determine whether the edits represent:

* Genuine semantic errors.
* Grammar problems.
* Terminology problems.
* Register differences.
* Stylistic preferences.
* Benign rewrites.

### 2. Error categorization

Group the observed errors into linguistic categories.

### 3. Training-data investigation

If genuine systematic errors are confirmed, investigate whether relevant Japanese linguistic phenomena or domain terminology are under-represented in the model's training/adaptation data.

### 4. Controlled evaluation

Run a controlled evaluation comparing the existing model against candidate improvements before deploying additional training or fine-tuning.

This sequence reduces the risk of spending engineering resources optimizing a metric that may partly reflect user style preferences rather than genuine translation errors.

---

# ⚠️ Correlation vs. Causation

A central principle of this analysis is that **statistical association is not automatically causal evidence**.

For example:

```text
v2 rollout
      ↓
lower edit distance
```

may be consistent with a model improvement, but the observed relationship could also be affected by other variables that changed around the same time.

The analysis therefore uses language such as:

* “associated with”
* “consistent with”
* “supports the hypothesis”
* “suggests”
* “candidate explanation”

rather than claiming that the statistical tests alone prove causation.

A production investigation would require stronger experimental or quasi-experimental designs, such as:

* Randomized A/B testing.
* Controlled holdout groups.
* Difference-in-differences analysis.
* Interrupted time-series analysis.
* Stratification or matching.
* Multivariable regression.

---

# 🧪 Statistical Interpretation

The statistical results should be interpreted within the context of the synthetic dataset and the assumptions of the tests used.

A low p-value indicates that the observed difference would be relatively unlikely under the null hypothesis represented by the chosen test.

It does **not** by itself establish:

* Practical significance.
* Causality.
* Translation correctness.
* Generalization to real users.
* Superiority of one model in all linguistic contexts.

For this reason, the analysis combines statistical evidence with residual analysis, alternative-hypothesis testing, and a proposed human-review stage.

---

# 📈 Why Edit Distance?

User edit distance is useful because it provides an observable signal of how much a generated translation changes before reaching the user's final version.

However, it is an imperfect proxy.

A high edit distance can arise from:

* Genuine translation errors.
* Terminology corrections.
* Grammar corrections.
* Style preferences.
* Rephrasing.
* Localization choices.
* Changes unrelated to translation quality.

Therefore:

> **Edit distance is treated as an investigation trigger, not as a definitive quality metric.**

This distinction is central to the design of the module.

---

# 🔗 Relationship to `translation_review/`

The [`translation_review/`](../translation_review) module complements this quantitative investigation by performing manual EN→EL evaluation on individual translation examples.

The two modules therefore operate at different levels:

```text
translation_quality/
        │
        ▼
Aggregate quantitative signal
        │
        ▼
Identify anomalous language pairs
        │
        ▼
Form hypotheses
        │
        ▼
Test alternative explanations
        │
        ▼
translation_review/
        │
        ▼
Inspect individual translations
        │
        ▼
Human linguistic assessment
        │
        ▼
Determine whether the signal
represents genuine quality issues
```

This provides a more complete evaluation workflow:

### Quantitative analysis

Answers:

> **Where is the problem and when did it appear?**

### Qualitative review

Answers:

> **What does the problem actually look like?**

Together, they help distinguish measurable behavioral changes from genuine linguistic-quality problems.

---

# 🧭 Investigation Summary

The complete investigation can be summarized as:

```text
Observed:
en-ja has substantially higher edit distance
                    │
                    ▼
Hypothesis A:
Content-type composition explains the difference
                    │
                    ▼
              Not supported
                    │
                    ▼
Hypothesis B:
Sentence length explains the difference
                    │
                    ▼
Weak effect, but residual remains
                    │
                    ▼
Hypothesis C:
Model rollout affects language pairs differently
                    │
                    ▼
Supported by the simulated data
                    │
                    ▼
Candidate explanation:
language-pair-specific model behavior
                    │
                    ▼
Next step:
native-speaker review + controlled evaluation
```

The important analytical outcome is not simply the final `en-ja` number.

It is the **investigative chain from observation → hypothesis → test → alternative explanation → interpretation → action**.

---

# 🧪 Synthetic Data & Honesty Note

The dataset used by this module is **synthetic** and was generated specifically to demonstrate the investigative methodology.

It is **not** a dataset from a real translation production system, and the reported results should not be interpreted as evidence about the actual performance of any language pair, model provider, or commercial translation system.

The generator intentionally embeds a known pattern so that the analysis has a meaningful signal to investigate.

This means the experiment demonstrates the **analytical process**, not empirical evidence about real-world translation quality.

The project therefore deliberately avoids presenting the `en-ja` finding as a real production discovery.

The same methodology could be applied to real production data where appropriate access, privacy controls, sampling procedures, and statistical methodology are available.

---

# 📏 Limitations

## Synthetic Dataset

The strongest limitation is that the underlying observations are simulated.

Real production data would contain additional factors such as:

* User behavior differences.
* Domain-specific terminology.
* Customer-specific traffic.
* Temporal changes.
* Translation-provider differences.
* Linguistic complexity.
* Product changes.
* Model updates.
* Sampling bias.

## Small Experimental Scope

The current investigation focuses on a limited set of hypotheses.

Additional variables could be incorporated into a larger analysis.

## Observational Rollout Analysis

The v1/v2 comparison is not a randomized controlled experiment.

Therefore, the observed pre/post differences should not be interpreted as definitive causal estimates of the model rollout effect.

## Edit Distance as a Proxy

Edit distance is not equivalent to translation quality.

Human review is required to determine whether observed edits correspond to genuine translation errors.

## Multiple Testing

When many language pairs or hypotheses are tested simultaneously, a larger production analysis should account for multiple comparisons using an appropriate correction or statistical framework.

## Single Synthetic Data-Generating Process

The findings depend on the assumptions encoded in the synthetic data generator.

Different simulated relationships could lead to different conclusions.

---

# 🚀 Running the Analysis

From the repository root:

```bash
cd translation_quality

python3 generate_translation_data.py
python3 analyze_edit_drift.py
```

The analysis will:

1. Generate the synthetic translation dataset.
2. Calculate language-pair edit-distance statistics.
3. Test the content-type hypothesis.
4. Analyze sentence-length effects.
5. Calculate residuals.
6. Compare pre/post model versions.
7. Perform the relevant statistical tests.
8. Produce the investigation summary.

---

# 📁 Module Structure

```text
translation_quality/
│
├── generate_translation_data.py
├── analyze_edit_drift.py
├── README.md
└── ...
```

The module is intentionally lightweight so that the entire investigation can be reproduced locally.

---

# 🎯 What This Demonstrates

This module demonstrates practical experience with:

* Hypothesis-driven data analysis.
* Exploratory data analysis.
* Confounder investigation.
* Statistical testing.
* Correlation analysis.
* Residual analysis.
* Pre/post model comparison.
* AI/LLM quality analytics.
* User-behavior analysis.
* Synthetic-data experimentation.
* Root-cause investigation.
* Human-in-the-loop validation.
* Evidence-based recommendations.
* Explicit distinction between association and causation.

More broadly, it demonstrates an analytical workflow in which the objective is not merely to produce a dashboard or metric, but to answer:

> **What changed, why might it have changed, which explanations can be ruled out, what evidence supports the remaining hypotheses, and what should be investigated next?**

---

# 🔬 Scientific Positioning

This module is intentionally positioned as a **methodology demonstration** rather than a claim about real-world translation-system performance.

The key principle is:

```text
Metric
  ≠
Explanation
  ≠
Causation
  ≠
Business Action
```

A robust analytical workflow connects these stages carefully:

```text
Metric
  ↓
Investigation
  ↓
Hypotheses
  ↓
Statistical Evidence
  ↓
Human / Domain Validation
  ↓
Actionable Recommendation
```

That distinction is the central purpose of this module.
