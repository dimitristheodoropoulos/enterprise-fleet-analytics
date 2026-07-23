# 📊 Maritime Telemetry Data Dictionary & AI Fine-Tuning Specs

## Dataset Overview
- **Source:** Fleet Telemetry Simulation
- **Volume:** 5,000 Records
- **Target Use Case:** Data Cleaning, Excel KPIs Analysis & LLM/AI Training Prompt Dataset

## Data Schema
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `telemetry_id` | Text (Unique Key) | Primary identifier for each telemetry entry |
| `vessel_name` | Text | Name of the vessel (e.g., MV Fleet_01) |
| `vessel_type` | Categorical | Vessel category (`Container`, `Bulk Carrier`, `Tanker`, `LNG Carrier`) |
| `speed_knots` | Float | Vessel speed in knots |
| `beaufort_scale` | Integer | Weather condition on Beaufort scale (1 to 9) |
| `cargo_weight_tons` | Integer | Loaded cargo weight in metric tons |
| `route_status` | Categorical | Current status (`Underway`, `Anchored`, `Moored`) |
| `fuel_consumption_mt` | Float | Fuel consumption in metric tons |
| `timestamp` | Datetime | Measurement timestamp |

## Data Cleaning Logic (Power Query Steps)
1. **Missing Value Handling:** Replace missing `beaufort_scale` values with median per `route_status`.
2. **Type Validation:** Ensure numeric fields (`speed_knots`, `fuel_consumption_mt`) are properly formatted as decimal numbers.
3. **Outlier Filtering:** Identify records where `fuel_consumption_mt` > 3 standard deviations from vessel type average.

## AI Training Dataset Mapping
The tab `04_AI_Training_Data` maps raw data into High-Quality Prompt-Response Pairs for RLHF/SFT model training:
- **System Instruction:** Role of a Maritime Operations & Data Analyst.
- **User Prompt:** Natural language queries regarding vessel fuel efficiency and weather impact.
- **Expected Response (Ground Truth):** Precise analytical summaries derived via Excel logic.