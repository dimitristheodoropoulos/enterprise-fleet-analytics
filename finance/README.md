# Finance Reconciliation Extension 💰🤖

Part of the [AI-Driven Operational Analytics Platform](../README.md) — this module applies the same architecture (PostgreSQL, FastAPI, LLM explanation layer) built for maritime fleet analytics to a finance-operations use case: automated reconciliation, exception handling with human-in-the-loop validation, and journal entry generation.

## What it does
* **Cross-system matching:** Reconciles transactions between two independent feeds (e.g. an internal ERP ledger vs. a bank/PMS statement) by reference, flagging amount mismatches, date mismatches, and unmatched entries on either side.
* **Anomaly / exception detection:** Every discrepancy the matching engine can't cleanly resolve is recorded as a `PENDING_REVIEW` exception rather than silently ignored or auto-approved.
* **Human-in-the-loop validation:** A reviewer approves or rejects each exception via a dedicated endpoint; the decision and reviewer are recorded for audit purposes.
* **AI-generated explanations:** Each exception can be explained in natural language (via the same Gemini client used by the AI Copilot) to speed up human review.
* **Automated journal entry generation:** Approving an exception automatically drafts a journal entry (debit/credit/amount/memo), ready for posting.

## 📂 Contents & Structure
* **`schema_finance.sql`** — Creates the four new tables: `erp_transactions`, `bank_transactions`, `reconciliation_exceptions`, `journal_entries`.
* **`generate_finance_data.py`** — Seeds mock ERP and bank transaction feeds with intentionally injected discrepancies (amount mismatches, date mismatches, unmatched entries on either side).
* **`reconciliation.py`** — The matching engine: pairs ERP and bank transactions by reference, applies amount/date tolerance, and records anything unresolved as an exception.
* **`review.py`** — Human-in-the-loop layer: lists pending exceptions, records approve/reject decisions, and auto-generates a draft journal entry on approval.
* **`explain.py`** — LLM-based natural-language explanation for each exception, reusing the same Gemini client pattern as the AI Copilot (`chatbot_agent.py`).
* **`api.py`** — FastAPI router exposing all finance endpoints; mounted into the main app in `main.py`.

## New tables
* `erp_transactions` / `bank_transactions` — the two systems being reconciled.
* `reconciliation_exceptions` — every mismatch found, its type, status, and AI explanation.
* `journal_entries` — draft entries generated from approved exceptions.

## Running it
```bash
# 1. Apply the finance schema (in addition to the main schema)
psql -U postgres -d maritime_db -f finance/schema_finance.sql

# 2. Seed mock ERP + bank transactions with intentional discrepancies
python finance/generate_finance_data.py

# 3. Start the API (finance router is mounted automatically in main.py)
python -m uvicorn main:app --reload
```

## API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/finance/reconcile` | Runs a full reconciliation pass, returns a summary |
| GET | `/finance/exceptions?status=PENDING_REVIEW` | Lists exceptions by status |
| GET | `/finance/exceptions/{id}/explain` | AI-generated explanation for one exception |
| POST | `/finance/exceptions/{id}/review` | Records an approve/reject decision (`{"decision": "APPROVED", "reviewed_by": "..."}`) |
| GET | `/finance/journal-entries?status=DRAFT` | Lists generated journal entries |

Example:
```bash
curl -X POST http://localhost:8000/finance/reconcile
curl "http://localhost:8000/finance/exceptions?status=PENDING_REVIEW"
curl -X POST http://localhost:8000/finance/exceptions/1/review \
  -H "Content-Type: application/json" \
  -d '{"decision": "APPROVED", "reviewed_by": "dimitris"}'
```

## Verified end-to-end run
A live run against 300 seeded ERP rows / 297 bank rows produced:
```json
{"run_id":"cd01d906","matched_clean":214,"exceptions_found":101,
 "exception_breakdown":{"UNMATCHED_ERP":18,"UNMATCHED_BANK":15,"DATE_MISMATCH":24,"AMOUNT_MISMATCH":44}}
```
followed by a successful human approval and automatic journal entry draft for one of the flagged exceptions.
