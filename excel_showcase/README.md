# Excel Showcase & AI Fine-Tuning Dataset 📊🤖

This directory houses the Excel-based analytical model and dataset exports for the **Enterprise Fleet Analytics** platform.

## 📂 Contents & Structure
* **`Fleet_Telemetry_Analysis_v1.xlsx`**: The core Excel workbook structured with dedicated tabs for raw data, cleaned Power Query datasets, formula analytics, AI training prompt-response pairs, and an **Executive Dashboard** featuring interactive Pivot Tables, Pivot Charts, and Slicers.
* **`convert_to_jsonl.py`**: Python automation script utilizing `pandas` and `openpyxl` to parse the AI training dataset sheet and export records into `.jsonl` format.
* **`fleet_ai_training_data.jsonl`**: Processed training data containing prompt-response pairs, fully formatted for LLM Fine-Tuning and RAG ingestion.
* **`data_dictionary.md`**: Comprehensive data dictionary detailing metrics, data cleaning steps, and prompt-response mapping logic.