# Fuel Consumption Prediction & Fleet Analytics Models 🚢📊

This module implements a collection of supervised, unsupervised, optimization, and time-series methods for analyzing **synthetic maritime fleet telemetry**.

The main components are:

* Fuel-consumption regression.
* Regression-model comparison.
* Feature-importance analysis.
* Voyage-efficiency clustering.
* Speed recommendation / optimization.
* Fuel-cost risk classification.
* Fleet-wide time-series forecasting.
* FastAPI model serving.

The module is designed to demonstrate an end-to-end analytical workflow:

```text id="8w8e3n"
Operational Data
      ↓
Feature Engineering
      ↓
Model Training
      ↓
Evaluation
      ↓
Error / Limitation Analysis
      ↓
Operational Recommendation
      ↓
API Serving
```

The dataset is **synthetic** and is intentionally structured to provide a reproducible environment for demonstrating the methodology. The reported metrics therefore describe performance on this generated dataset and should not be interpreted as expected accuracy on real-world vessel operations.

---

# 🎯 Problem Framing

Fuel consumption is an important variable operating cost in maritime fleet management and is influenced by multiple measurable operational and vessel characteristics.

This module frames fuel consumption as a **supervised regression problem**, predicting a continuous quantity:

```text
Fuel consumption → metric tons / day
```

Regression is appropriate for this formulation because the resulting prediction can be used as an input to downstream analytical tasks such as:

* Fuel-consumption estimation.
* Voyage comparison.
* Bunker-cost analysis.
* Speed optimization.
* Operational scenario analysis.

The same underlying prediction problem is subsequently reused for classification and optimization experiments.

---

# 🧮 Feature Engineering

The regression model uses the following features:

| Feature                    | Source                             | Rationale                                                            |
| -------------------------- | ---------------------------------- | -------------------------------------------------------------------- |
| `speed` (knots)            | `telemetry_logs.speed_knots`       | Fuel consumption generally increases non-linearly with vessel speed  |
| `cargo_weight` (tons)      | `telemetry_logs.cargo_weight_tons` | Cargo/load affects displacement and therefore resistance             |
| `beaufort_scale`           | `telemetry_logs.wind_beaufort`     | Higher wind/weather severity can increase resistance and engine load |
| `dwt` (deadweight tonnage) | `vessels.capacity_dwt`             | Represents vessel carrying capacity and structural scale             |
| `built_year`               | `vessels.year_built`               | Proxy for vessel age and generation of vessel/engine technology      |

The features are loaded directly from the relational database through a joined SQL query implemented in `models/run_training.py`.

This keeps the training workflow reproducible:

```text id="g3k6bx"
PostgreSQL
    ↓
SQL join
    ↓
Feature dataset
    ↓
Train/test split
    ↓
Model training
    ↓
Evaluation
```

No manual spreadsheet-based data preparation is required.

---

# 🌲 Model Selection: Random Forest Regressor

Three regression approaches were evaluated:

* Linear Regression.
* Random Forest Regression.
* Gradient Boosting Regression.

Random Forest was selected as the primary model for serving because it provides:

### Non-linear modeling

Tree ensembles can capture non-linear relationships between operational variables without requiring explicit polynomial transformations.

### No feature scaling requirement

Random Forest does not require standardized input features in the same way as many distance- or coefficient-based models.

### Feature-importance analysis

The trained ensemble provides a straightforward mechanism for extracting relative feature-importance estimates.

### Practical baseline

Random Forest provides a strong non-linear baseline with relatively little hyperparameter tuning.

The model configuration used for the primary experiment is:

```text id="zq7n9j"
n_estimators = 100
random_state = 42
```

Hyperparameter optimization was not performed exhaustively. The selected configuration should therefore be considered a **baseline model configuration**, not a fully optimized production model.

---

# 🔬 Model Comparison

Three regression algorithms were evaluated using the same train/test split:

| Model             |         R² | RMSE (tons/day) |
| ----------------- | ---------: | --------------: |
| Linear Regression |     0.9741 |            0.88 |
| **Random Forest** | **0.9981** |        **0.24** |
| Gradient Boosting | **0.9982** |        **0.23** |

The results show that both tree-based ensemble methods substantially outperform Linear Regression on this synthetic dataset.

This is consistent with the non-linear relationship encoded in the generated telemetry.

Gradient Boosting achieves a marginally better result than Random Forest:

```text id="ubf3io"
ΔR² = 0.0001
```

Random Forest was retained as the primary model because the accuracy difference is negligible in this experiment while the Random Forest configuration provides a simple, reproducible baseline for model serving.

This should not be interpreted as evidence that Random Forest is universally preferable to Gradient Boosting. A model choice for a real deployment would also consider:

* Validation methodology.
* Prediction latency.
* Training cost.
* Hyperparameter optimization.
* Model stability.
* Dataset size.
* Drift.
* Interpretability requirements.

---

# 📈 Training & Evaluation

## Dataset

```text id="5ckl4j"
100,000 synthetic telemetry records
```

The telemetry records are joined with vessel metadata before model training.

## Train/Test Split

```text id="5fzrjo"
80% training
20% testing

random_state = 42
```

The current regression experiment uses a standard random train/test split.

Because the data is synthetic and does not represent a true temporal operational stream, this is appropriate for the demonstration. A real production telemetry system would require additional consideration of temporal splitting and vessel-level leakage.

---

# 📊 Regression Results

| Metric |       Test Result |
| ------ | ----------------: |
| R²     |        **0.9981** |
| RMSE   | **0.24 tons/day** |

The very high R² should be interpreted carefully.

The synthetic data-generation process creates a relatively clean relationship between the operational variables and fuel consumption. This makes the prediction task substantially easier than a real-world maritime deployment, where additional sources of variability would be expected.

Examples include:

* Sensor noise.
* Measurement errors.
* Ocean currents.
* Hull fouling.
* Propeller condition.
* Engine condition.
* Sea state.
* Wind direction.
* Wave characteristics.
* Route differences.
* Operational behavior.
* Loading configuration.

Therefore:

> **R² = 0.9981 demonstrates strong predictive performance on the generated dataset, not 99.81% real-world predictive accuracy.**

The result is useful for validating the end-to-end ML pipeline and model-serving architecture, but it should not be extrapolated directly to production vessel operations.

---

# 🔍 Feature Importance

The trained Random Forest produced the following relative feature-importance values:

| Feature          | Importance |
| ---------------- | ---------: |
| `speed`          |     0.9504 |
| `beaufort_scale` |     0.0483 |
| `cargo_weight`   |     0.0012 |
| `dwt`            |     0.0001 |
| `built_year`     |     0.0001 |

Speed dominates the model's feature-importance distribution, while weather severity contributes a smaller but measurable share.

This is broadly consistent with the structure of the synthetic fuel-consumption relationship.

However, feature importance should **not** be interpreted as causal importance.

In particular:

* A high feature importance does not prove causality.
* A low feature importance does not prove that a variable is physically irrelevant.
* Correlated variables can distribute importance in unintuitive ways.
* Tree-based feature importance can be affected by the structure of the dataset.

The results should therefore be treated as a model diagnostic rather than as a causal analysis of vessel fuel consumption.

---

# 🎯 Voyage Efficiency Clustering — K-Means

Beyond predicting fuel consumption, the module performs unsupervised clustering to identify operational efficiency profiles.

## Method

```text id="z7h5ra"
Algorithm: K-Means
Number of clusters: k = 3
Features standardized before clustering
```

### Features

* Speed.
* Fuel consumption.
* Beaufort scale.
* Cargo weight.

### Silhouette Score

```text id="1g5w2q"
0.27
```

The resulting profiles are:

| Profile     | Avg Speed | Avg Fuel (tons/day) | Avg Beaufort | Avg Cargo (tons) | Records |
| ----------- | --------: | ------------------: | -----------: | ---------------: | ------: |
| Efficient   |     11.52 |               12.28 |         2.41 |           57,388 |  23,068 |
| Inefficient |     10.33 |               14.14 |         6.63 |           57,297 |  24,228 |
| Moderate    |     12.92 |               16.14 |         4.37 |           57,842 |  27,800 |

---

## Interpretation

A silhouette score of `0.27` indicates **moderate/weak cluster separation**, rather than three sharply distinct natural populations.

This is expected given that fuel consumption is modeled as a continuous function of variables such as speed and weather.

K-Means therefore acts primarily as an **operational segmentation technique**, partitioning a continuous space into interpretable profiles.

The profiles provide useful descriptive distinctions:

* **Efficient:** lower average speed, lower weather severity, lower fuel consumption.
* **Inefficient:** relatively severe weather conditions despite lower average speed.
* **Moderate:** highest average speed and corresponding higher fuel consumption.

The analysis should not be interpreted as proving that these three categories represent naturally occurring vessel classes.

---

# ⚙️ Speed Optimization & Recommendation

The trained regression model is also used as an evaluation function inside a simple optimization procedure.

The optimizer searches over candidate cruising speeds and selects the speed that minimizes predicted fuel consumption while satisfying a voyage-time constraint.

Conceptually:

```text id="sn0jmx"
Minimize:
    predicted_fuel_consumption(speed)

Subject to:
    voyage_distance / speed <= maximum_allowed_time
```

## Example Scenario

```text id="r6n0n6"
Voyage distance:       1,000 nautical miles
Maximum travel time:   90 hours
Weather:               Beaufort 4
```

The optimizer evaluates candidate speeds and identifies the lowest predicted fuel-consumption solution that satisfies the time constraint.

Run:

```bash id="b5b2d8"
python models/speed_optimizer.py
```

---

# ⚠️ Optimization Limitation: Model Extrapolation

The optimizer exposed an important limitation during testing.

For speeds approaching or exceeding the upper end of the training distribution, the Random Forest prediction can plateau instead of continuing to increase.

This is a fundamental property of tree-based models:

> Random Forests generally interpolate within the regions represented by their training data but do not extrapolate smoothly beyond the observed feature range.

The training data generated by `database/generate_data.py` contains a limited operating-speed range.

As a result, an optimizer searching too far toward the boundary can produce recommendations that reflect **model behavior rather than physical reality**.

This is particularly important because optimization amplifies model errors:

```text id="0esxkz"
Prediction error
      ↓
Optimization search
      ↓
Potentially misleading recommendation
```

The recommendation should therefore be constrained to the model's validated operating domain.

### Recommended production safeguards

A real implementation should use one or more of:

1. Explicit feature-range validation.
2. Optimization bounds derived from validated training data.
3. A wider and representative training dataset.
4. Physical constraints.
5. Independent validation of recommended operating points.
6. Human/operator approval for high-impact decisions.

This limitation is deliberately documented because a model that performs well on prediction does not automatically produce reliable optimization recommendations.

---

# 🏷️ Fuel-Cost Risk Classification

The regression problem is also reframed as a three-class classification problem:

```text id="y8z3y7"
Low
Medium
High
```

The goal is to demonstrate a classification workflow suitable for dashboards or alerting systems where a category may be easier to consume than a continuous fuel estimate.

## Model

```text id="1v2t6p"
Random Forest Classifier
```

## Labels

The labels are created using terciles of `fuel_consumption`:

```text id="r6t6tg"
Low    ≤ 11.72 tons/day
Medium ≤ 14.58 tons/day
High   > 14.58 tons/day
```

## Features

The classifier uses the same input features as the regression model:

* Speed.
* Cargo weight.
* Beaufort scale.
* DWT.
* Built year.

---

# 📊 Classification Results

| Class        | Precision | Recall | F1-score |
| ------------ | --------: | -----: | -------: |
| Low          |      1.00 |   1.00 |     1.00 |
| Medium       |      1.00 |   1.00 |     1.00 |
| High         |      1.00 |   1.00 |     1.00 |
| **Accuracy** |           |        | **1.00** |

---

# ⚠️ Interpreting the Perfect Classification Score

The perfect score should **not** be interpreted as evidence of exceptional classification performance.

The reason is structural.

The class labels are derived directly from the target variable:

```text id="0x7h1n"
fuel_consumption
       ↓
quantile thresholds
       ↓
Low / Medium / High
```

The classifier then receives features that already predict `fuel_consumption` with extremely high accuracy:

```text id="gy8r3q"
Operational Features
       ↓
Random Forest
       ↓
Approximate fuel consumption
       ↓
Tercile category
```

Consequently, discretizing a nearly deterministic target relationship produces a classification problem that is inherently easy.

This is an important limitation of the experiment.

The result demonstrates that the pipeline can perform classification successfully, but it does **not** establish that the classifier would achieve 100% accuracy on an independently defined real-world risk label.

---

# 💡 Better Production Formulation

A more realistic production classification task would define the target independently of the same telemetry features.

For example:

```text id="7kqjbf"
Actual bunker cost
       +
Financial threshold
       ↓
Low / Medium / High cost risk
```

or:

```text id="s5c2bq"
Actual voyage cost
       +
Budget threshold
       ↓
Cost-risk category
```

Such labels would provide a more meaningful test of generalization.

The current experiment is therefore best understood as a **pipeline demonstration and methodological exercise**, not as evidence of a production-ready risk classifier.

Reproduce:

```bash id="t0h1wb"
python models/classify_fuel_risk.py
```

---

# 📉 Fleet-Wide Fuel Consumption Forecasting

The module also evaluates fleet-wide time-series forecasting.

Daily fleet fuel consumption is modeled using:

```text id="2v0jks"
Holt-Winters Exponential Smoothing
Additive trend
Weekly seasonality
```

## Dataset

```text id="2ctd3q"
901 daily observations
```

## Evaluation

The last 14 days are held out as the test period.

Importantly, the data is split **chronologically rather than randomly**:

```text id="m8e0k2"
Historical observations
───────────────────────────────┬──────────
                               │
                            14-day test
                               │
                               ▼
                         Future observations
```

This prevents future observations from being mixed into the training set.

The model is compared against a naive baseline:

> Predict today's value as yesterday's observed value.

---

# 📊 Forecasting Results

| Method                | MAE (tons/day) |
| --------------------- | -------------: |
| Holt-Winters forecast |         104.43 |
| **Naive baseline**    |      **98.15** |

The naive baseline performs better.

This is an important negative result and is retained deliberately.

---

# ⚠️ Why the Forecast Underperforms

The synthetic data-generation process provides an important explanation.

Telemetry dates are sampled randomly across a 60-day window rather than generated as a genuinely sequential time series with structured daily observations.

Consequently, the aggregated fleet-level series does not contain a reliable weekly seasonal pattern for Holt-Winters to learn.

The forecasting model can therefore fit a seasonal component that does not correspond to a genuine underlying signal.

The resulting model performs worse than simply using the previous day's value.

This demonstrates an important principle:

> **A sophisticated forecasting model cannot compensate for a dataset that does not contain the temporal structure the model assumes.**

---

# 🔧 Improving the Forecasting Experiment

A more realistic synthetic time-series generator would produce sequential observations such as:

```text id="n0w9h6"
Vessel A — Day 1
Vessel A — Day 2
Vessel A — Day 3
...
Vessel B — Day 1
Vessel B — Day 2
...
```

and explicitly model:

* Weekly seasonality.
* Long-term trend.
* Weather variation.
* Vessel-specific effects.
* Operational cycles.

The forecasting model could then be evaluated against stronger baselines and alternative methods.

Potential future models include:

* Seasonal Naive.
* Exponential Smoothing variants.
* ARIMA / SARIMA.
* Gradient-boosted time-series models.
* Temporal cross-validation.

---

# 🔌 Model Serving

The trained regression model is serialized as:

```text id="o6u8t7"
fuel_model.pkl
```

and loaded by the FastAPI application.

The model is exposed through:

```http
POST /predict-fuel-consumption
```

## Request

```json id="y8h1w4"
{
  "speed": 12.5,
  "cargo_weight": 60000,
  "beaufort_scale": 4,
  "dwt": 105000,
  "built_year": 2018
}
```

## Response

```json id="9ydv2u"
{
  "predicted_fuel_consumption_tons_per_day": 15.13,
  "unit": "Metric Tons / Day",
  "status": "success"
}
```

This demonstrates model integration into a REST API and provides an on-demand prediction interface.

The endpoint should not be interpreted as a complete production MLOps deployment. Production deployment would require additional controls such as:

* Model versioning.
* Input distribution monitoring.
* Model drift detection.
* Authentication and authorization.
* Rate limiting.
* Health checks.
* Automated model validation.
* CI/CD.
* Observability.
* Model rollback mechanisms.

---

# 📁 Files in This Module

| File                                        | Purpose                                                                               |
| ------------------------------------------- | ------------------------------------------------------------------------------------- |
| `run_training.py`                           | Entry point: loads data from PostgreSQL and calls the training pipeline               |
| `train_model.py`                            | Defines features, target, train/test split, model fitting, and evaluation             |
| `compare_models.py`                         | Compares Linear Regression, Random Forest, and Gradient Boosting on the same split    |
| `feature_importance.py`                     | Extracts and visualizes feature-importance estimates                                  |
| `cluster_voyages.py`                        | Performs K-Means clustering of operational records                                    |
| `speed_optimizer.py`                        | Searches for a fuel-minimizing cruising speed under a voyage-time constraint          |
| `classify_fuel_risk.py`                     | Trains the Low/Medium/High fuel-cost classifier                                       |
| `forecast_fuel_trend.py`                    | Performs fleet-wide Holt-Winters forecasting                                          |
| `fuel_predictor.py`                         | Lightweight `FuelPredictor` class for loading and serving predictions outside FastAPI |
| `fuel_model.pkl`                            | Serialized trained regression model                                                   |
| `voyage_clusters.pkl` / `voyage_scaler.pkl` | Serialized clustering model and feature scaler                                        |
| `fuel_risk_classifier.pkl`                  | Serialized trained classification model                                               |
| `feature_importance.png`                    | Generated feature-importance visualization                                            |
| `voyage_clusters.png`                       | Generated clustering visualization                                                    |
| `speed_optimization.png`                    | Generated speed-optimization visualization                                            |
| `confusion_matrix.png`                      | Generated classification confusion matrix                                             |
| `fuel_forecast.png`                         | Generated forecast-vs-actual visualization                                            |

---

# 🚀 Reproducing the Results

From the project root, with the PostgreSQL container running and the database populated:

## Train the regression model

```bash id="ik75aj"
python models/run_training.py
```

## Compare regression models

```bash id="q6jskm"
python models/compare_models.py
```

## Generate feature-importance analysis

```bash id="av1poc"
python models/feature_importance.py
```

## Run voyage clustering

```bash id="y4v0f7"
python models/cluster_voyages.py
```

## Run speed optimization

```bash id="h3o7ex"
python models/speed_optimizer.py
```

## Run fuel-cost classification

```bash id="w9m2kf"
python models/classify_fuel_risk.py
```

## Run fleet-wide forecasting

```bash id="6n1zri"
python models/forecast_fuel_trend.py
```

The training script reports the regression performance on the held-out test set and writes the trained model to:

```text id="9k5j0r"
models/fuel_model.pkl
```

---

# ⚠️ Overall Scientific Limitations

The experiments in this module are intended primarily as **reproducible demonstrations of analytical methodology and software integration**.

The most important limitations are:

### 1. Synthetic Data

The maritime telemetry is generated programmatically rather than collected from a real fleet.

### 2. Simplified Relationships

The data generator contains relatively clean relationships between variables such as speed, weather, and fuel consumption.

### 3. Limited External Validity

Model metrics obtained from synthetic data cannot be assumed to transfer to real-world vessel operations.

### 4. Random Train/Test Split

The regression experiment uses a random split because the generated dataset is not a genuine temporal telemetry stream.

Real deployment would require careful consideration of:

* Temporal validation.
* Vessel-level leakage.
* Cross-vessel generalization.
* Out-of-distribution conditions.

### 5. Optimization Depends on Prediction Quality

The speed optimizer inherits the assumptions and limitations of the regression model.

### 6. Classification Target Construction

The risk labels are derived from the same target variable the regression model predicts, making the classification task substantially easier than an independently defined operational risk problem.

### 7. Forecasting Data Generation

The current synthetic time series lacks the temporal structure required to demonstrate a realistic seasonal forecasting problem.

### 8. No Extensive Hyperparameter Optimization

The primary models use reasonable baseline configurations rather than exhaustive hyperparameter search.

---

# 🔬 Scientific Interpretation

The experiments should therefore be interpreted at three different levels.

## What the experiments demonstrate

They demonstrate that the project can:

* Build reproducible ML pipelines.
* Extract structured features from PostgreSQL.
* Train and compare multiple model families.
* Evaluate models quantitatively.
* Perform unsupervised segmentation.
* Connect prediction to optimization.
* Expose models through FastAPI.
* Identify model limitations.
* Compare complex models against simple baselines.

## What the experiments do not demonstrate

They do not establish:

* Production-level maritime prediction accuracy.
* Generalization to unseen real vessels.
* Causal relationships between individual features and fuel consumption.
* Production-ready optimization recommendations.
* Real-world translation of the 100% classification accuracy.
* Superiority of Holt-Winters over other forecasting approaches.

This distinction is intentional.

A strong applied ML workflow should report not only where a model performs well, but also **where the data, evaluation design, or model assumptions limit the conclusions that can be drawn**.

---

# 🎯 Summary

The module demonstrates a complete progression from prediction to decision support:

```text id="xw8s2q"
                    Synthetic Fleet Telemetry
                              │
                              ▼
                     Feature Engineering
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        Regression        Clustering       Classification
             │                │                │
             ▼                ▼                ▼
      Fuel Prediction   Efficiency       Risk Categories
             │             Profiles             │
             │                                   │
             └───────────────┬───────────────────┘
                             │
                             ▼
                      Speed Optimization
                             │
                             ▼
                      Decision Support
                             │
                             ▼
                         FastAPI
                             │
                             ▼
                       Model Serving
```

A separate forecasting workflow evaluates fleet-wide temporal behavior and demonstrates why baseline comparison and data-generation quality are critical to time-series modeling.

The overall emphasis is not on maximizing headline metrics, but on demonstrating a complete analytical process:

> **Build → Evaluate → Challenge → Interpret → Document limitations → Serve responsibly**
