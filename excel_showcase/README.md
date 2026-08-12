# Excel Analytics Showcase & AI Dataset 📊🤖

This directory contains the Excel-based analytical model, dashboard, and AI-oriented dataset exports developed as part of the **Enterprise Fleet Analytics** platform.

The module demonstrates how operational telemetry data can be transformed through spreadsheet-based analysis into structured business insights and machine-readable datasets that can subsequently support AI experimentation.

The Excel workbook is intended as an **analytics and presentation layer**, while the Python export script provides a reproducible bridge from spreadsheet-based AI examples to structured JSONL data.

---

## 📂 Contents & Structure

| File                               | Purpose                                                                                                                                                        |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Fleet_Telemetry_Analysis_v1.xlsx` | Main Excel analytical workbook containing raw data, cleaned datasets, formula-based analysis, AI-oriented prompt/response examples, and an executive dashboard |
| `convert_to_jsonl.py`              | Python utility using `pandas` and `openpyxl` to extract the AI-oriented dataset from Excel and export it as JSONL                                              |
| `fleet_ai_training_data.jsonl`     | Structured prompt/response dataset exported from the workbook for potential use in supervised fine-tuning experiments, evaluation, or other LLM workflows      |
| `data_dictionary.md`               | Documentation of the dataset fields, analytical metrics, cleaning logic, and prompt/response structure                                                         |

---

# 📊 Excel Analytical Model

The workbook brings together several stages of the analytics workflow in a single, inspectable environment.

The main components include:

### Raw Data

Contains the underlying fleet telemetry records used by the analytical model.

Typical operational variables include:

* Vessel identifier.
* Vessel type.
* Speed.
* Fuel consumption.
* Cargo weight.
* Weather conditions.
* Vessel characteristics.

### Cleaned / Transformed Data

Contains the data after the relevant cleaning and transformation steps.

The workbook documents the transformations rather than treating the spreadsheet as a black-box output.

### Formula-Based Analytics

Excel formulas are used to calculate operational KPIs and derived metrics.

This provides a transparent spreadsheet-level view of calculations that can be inspected and reproduced directly within Excel.

### AI-Oriented Prompt/Response Dataset

The workbook also contains structured examples pairing operational questions with corresponding analytical answers.

These examples are designed to demonstrate how structured operational data can be translated into natural-language analytical interactions.

---

# 📈 Executive Dashboard

The workbook includes an executive-oriented dashboard built around:

* Pivot Tables.
* Pivot Charts.
* Slicers.
* Fleet-level KPIs.
* Fuel-consumption analysis.
* Operational comparisons.

The dashboard provides an interactive business-facing layer on top of the underlying telemetry data.

The objective is not to replace the Python/FastAPI analytics backend, but to demonstrate how the same operational dataset can also be consumed by traditional BI and spreadsheet workflows.

---

# 🤖 AI Dataset Export

The `fleet_ai_training_data.jsonl` file is generated from the AI-oriented dataset contained in the Excel workbook.

The conversion pipeline is:

```text
Excel AI Dataset
       │
       ▼
convert_to_jsonl.py
       │
       ▼
Structured JSONL
       │
       ├───────────────┐
       ▼               ▼
Fine-Tuning       Evaluation /
Experiments       AI Workflows
```

The JSONL format provides a convenient machine-readable representation of the prompt/response examples.

However, the dataset should be considered an **AI experimentation dataset**, rather than automatically assuming that it is production-ready fine-tuning data for every model provider.

Different LLM platforms impose different requirements for:

* Message formatting.
* System/user/assistant roles.
* Dataset size.
* Validation splits.
* Token limits.
* Safety filtering.
* Evaluation methodology.

The exported JSONL therefore provides the structured content, while model-specific formatting and validation should be performed as part of the target fine-tuning workflow.

---

# 🔎 Fine-Tuning vs. RAG

The dataset can support more than one AI use case, but **fine-tuning and Retrieval-Augmented Generation (RAG) should not be treated as the same technique**.

### Fine-Tuning

The prompt/response examples can be used as a starting point for supervised fine-tuning experiments where the objective is to teach a model a particular response style, task format, or behavior.

Before actual fine-tuning, the dataset should be evaluated for:

* Correctness.
* Consistency.
* Duplicate examples.
* Prompt/response quality.
* Training/validation separation.
* Potential leakage from evaluation examples.

### RAG

For RAG, the underlying operational knowledge is generally better represented as retrievable documents or structured records rather than simply treating prompt/response pairs as a fine-tuning corpus.

A possible RAG workflow would be:

```text
Operational Data
       │
       ▼
Structured Documents / Records
       │
       ▼
Embedding / Indexing
       │
       ▼
Vector or Hybrid Search
       │
       ▼
Relevant Context
       │
       ▼
LLM Response
```

Therefore, the JSONL export is useful as a structured AI dataset, while the appropriate downstream architecture depends on whether the objective is **behavior adaptation (fine-tuning)** or **knowledge retrieval (RAG)**.

---

# 🐍 Reproducible Export Pipeline

The JSONL dataset can be regenerated from the Excel workbook using:

```bash
python excel_showcase/convert_to_jsonl.py
```

The script reads the relevant worksheet, validates the expected fields, and serializes the records into JSONL format.

This keeps the dataset export reproducible rather than relying on a manually maintained JSONL file.

---

# 🧹 Data Quality Considerations

The Excel workbook is part of a broader analytics pipeline, so the AI-oriented dataset should inherit the same emphasis on data quality used elsewhere in the repository.

Before using the exported examples for model training or evaluation, relevant checks include:

* Missing-value detection.
* Duplicate prompt detection.
* Invalid response detection.
* Inconsistent terminology.
* Numerical consistency with the underlying telemetry data.
* Separation between training and evaluation examples.
* Detection of examples that expose information that should not be present in model training data.

The `data_dictionary.md` file documents the expected structure and transformation logic.

---

# 🏗️ Role Within the Overall Platform

The Excel module complements the project's Python, database, ML, API, and BI components.

Conceptually:

```text
                    Fleet Telemetry
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
       Python / PostgreSQL       Excel Analytics
              │                       │
              ▼                       ▼
       ML + FastAPI              KPIs + Dashboard
              │                       │
              └───────────┬───────────┘
                          ▼
                  Operational Insights
                          │
                          ▼
                   AI Dataset Export
                          │
                          ▼
                    JSONL Dataset
```

This demonstrates the ability to move between:

* Operational data engineering.
* Spreadsheet analytics.
* Business intelligence.
* Machine learning.
* API-based analytics.
* AI-oriented data preparation.

---

# 🎯 What This Demonstrates

This module demonstrates practical skills across both traditional analytics and AI workflows:

* Excel-based data analysis.
* Power BI / dashboard-oriented thinking.
* Pivot Tables and Pivot Charts.
* Interactive filtering with Slicers.
* Data cleaning and transformation.
* Python automation.
* Structured dataset generation.
* JSONL serialization.
* AI dataset preparation.
* Understanding of fine-tuning versus RAG.
* Reproducible data-export workflows.

The broader objective is to demonstrate that the platform is not limited to an AI interface: the same operational data can be transformed into **business-facing analytics, machine-learning inputs, API outputs, and AI-ready datasets**.

---

# ⚠️ Important Scope Note

The AI dataset contained in this directory is a **demonstration and experimentation dataset**.

Its existence in JSONL format does not by itself demonstrate that a fine-tuned model has been trained, nor that fine-tuning would necessarily be the optimal approach for the underlying analytics problem.

For production AI systems, dataset quality, evaluation methodology, model selection, retrieval architecture, privacy, and deployment constraints should be assessed independently.

The purpose of this module is to demonstrate the **data preparation and integration workflow** connecting spreadsheet analytics with downstream AI experimentation.
