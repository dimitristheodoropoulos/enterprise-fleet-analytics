# Finance Reconciliation Extension 💰🤖

Part of the [AI-Driven Operational Analytics Platform](../README.md), this module extends the platform's PostgreSQL + FastAPI + LLM architecture to a **finance-operations reconciliation workflow**.

The module demonstrates how transaction reconciliation can combine deterministic matching rules, exception management, human review, audit-oriented state tracking, and LLM-assisted explanations.

The implementation uses **synthetic ERP and bank/PMS transaction data** with deliberately injected discrepancies. It is therefore a reproducible engineering demonstration rather than a production accounting or banking system.

---

# 🎯 Problem Framing

Financial operations frequently require reconciliation between independently generated transaction records.

A simplified workflow is:

```text
ERP / Internal Ledger
        │
        │
        ├──────────────┐
        │              │
        ▼              ▼
   Transaction     Transaction
     Feed A          Feed B
        │              │
        └──────┬───────┘
               ▼
        Matching Engine
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
 Clean Match        Discrepancy
       │                │
       │                ▼
       │          Pending Review
       │                │
       │          Human Decision
       │                │
       │        ┌───────┴───────┐
       │        ▼               ▼
       │     Approved        Rejected
       │        │
       │        ▼
       │   Draft Journal
       │      Entry
       │
       ▼
   Reconciled
```

The main objective is to ensure that unresolved discrepancies are **explicitly represented and reviewed**, rather than silently discarded or automatically treated as valid matches.

---

# 🔍 What the Module Does

## 1. Cross-System Transaction Matching

The reconciliation engine compares transactions originating from two independent feeds:

* ERP/internal ledger.
* Bank/PMS statement.

Transactions are initially paired using a transaction reference and then evaluated against configurable matching criteria.

The reconciliation logic considers:

* Transaction reference.
* Amount.
* Transaction date.
* Presence/absence on either side.

Depending on the result, a transaction can be classified as a clean match or routed to exception handling.

---

## 2. Exception Detection

Transactions that cannot be resolved deterministically are recorded as reconciliation exceptions.

Examples include:

* Unmatched ERP transactions.
* Unmatched bank transactions.
* Amount mismatches.
* Date mismatches.

Instead of silently accepting a discrepancy, the system records it with an explicit status:

```text
PENDING_REVIEW
```

This provides a clear workflow boundary between automated matching and human decision-making.

---

# 👤 Human-in-the-Loop Review

A core design principle is that unresolved discrepancies are **not automatically approved**.

A reviewer can inspect an exception and explicitly record a decision:

```text
APPROVED
REJECTED
```

The review record contains the reviewer identity and the decision.

Conceptually:

```text
Automated Detection
        │
        ▼
 PENDING_REVIEW
        │
        ▼
 Human Review
        │
   ┌────┴────┐
   ▼         ▼
APPROVED   REJECTED
   │
   ▼
Journal Entry Draft
```

This provides a simple human-in-the-loop control point for exceptions that cannot be resolved safely through deterministic matching rules.

The reviewer decision is stored in the database, providing an auditable record of the workflow state.

---

# 🤖 AI-Assisted Exception Explanation

Each reconciliation exception can be sent to the same Gemini-based LLM infrastructure used by the main platform.

The LLM produces a natural-language explanation intended to help the reviewer understand the discrepancy more quickly.

For example, an explanation may summarize:

* Which transaction fields disagree.
* Whether the amount differs.
* Whether the transaction dates differ.
* Which system contains the transaction.
* What type of exception was detected.

The LLM therefore acts as an **explanation and review-assistance layer**, not as the authoritative reconciliation engine.

The deterministic matching logic remains responsible for identifying the actual discrepancy.

This separation is important:

```text
Deterministic Rules
        │
        ▼
Exception Detection
        │
        ├───────────────┐
        │               │
        ▼               ▼
Database Record     LLM Explanation
        │               │
        └───────┬───────┘
                ▼
           Human Review
```

The LLM output should not be treated as an accounting determination or as evidence that a transaction is valid.

---

# 🧾 Journal Entry Generation

When a reviewer approves an exception, the system generates a **draft journal entry** representing the proposed accounting adjustment.

The generated entry contains information such as:

* Debit account.
* Credit account.
* Amount.
* Memo / explanation.
* Source exception.

The entry is stored with a draft status:

```text
DRAFT
```

The implementation demonstrates the workflow from:

```text
Exception
   ↓
Human Approval
   ↓
Journal Entry Draft
```

It does **not** automatically post entries to a live accounting ledger.

That distinction is intentional. In a real accounting environment, journal-entry posting would require additional controls such as:

* Chart-of-accounts validation.
* Segregation of duties.
* Approval policies.
* Accounting-period validation.
* Duplicate prevention.
* Transaction-level audit trails.
* Posting authorization.
* Reversal procedures.

Therefore, the current implementation should be understood as **draft journal-entry generation**, not autonomous accounting.

---

# 🏗️ Architecture

The module reuses the broader platform architecture:

```text
                   Finance Data Sources
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ERP Transactions         Bank/PMS Transactions
              │                         │
              └────────────┬────────────┘
                           ▼
                  Reconciliation Engine
                           │
                           ▼
                 PostgreSQL Exceptions
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
          LLM Explanation       Human Review
                 │                   │
                 └─────────┬─────────┘
                           ▼
                  Draft Journal Entry
                           │
                           ▼
                       FastAPI
```

The architecture deliberately separates:

* Deterministic transaction matching.
* Database persistence.
* LLM explanation.
* Human approval.
* Journal-entry drafting.
* API access.

This separation makes the workflow easier to reason about and reduces the risk of allowing an LLM to directly determine accounting outcomes.

---

# 📂 Contents & Structure

| File                       | Purpose                                                                                     |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| `schema_finance.sql`       | Creates the finance-specific database tables                                                |
| `generate_finance_data.py` | Generates synthetic ERP and bank transaction feeds with deliberately injected discrepancies |
| `reconciliation.py`        | Implements deterministic transaction matching and exception detection                       |
| `review.py`                | Handles human review decisions and journal-entry draft generation                           |
| `explain.py`               | Generates LLM-assisted natural-language explanations for exceptions                         |
| `api.py`                   | FastAPI router exposing the finance workflow endpoints                                      |

---

# 🗄️ Database Schema

The module introduces four finance-specific tables.

## `erp_transactions`

Represents transactions originating from the internal ERP/ledger feed.

## `bank_transactions`

Represents transactions originating from the external bank/PMS feed.

## `reconciliation_exceptions`

Stores discrepancies identified by the reconciliation engine.

Typical information includes:

* Exception type.
* Related transaction identifiers.
* Exception status.
* Description.
* AI-generated explanation.
* Review decision.
* Reviewer information.

## `journal_entries`

Stores draft journal entries generated after approved exceptions.

The separation of transaction feeds from reconciliation exceptions makes it possible to preserve the original source records while tracking the resolution workflow independently.

---

# 🧪 Synthetic Data Generation

The module uses a deterministic-style synthetic data generator to create reproducible test scenarios.

The generator intentionally injects discrepancies such as:

* Amount mismatches.
* Date mismatches.
* ERP-only transactions.
* Bank-only transactions.

This allows the reconciliation engine to be evaluated against known exception types without requiring access to confidential financial data.

The generated dataset should therefore **not** be interpreted as representing real transaction distributions or real-world reconciliation rates.

---

# 🚀 Running the Module

## 1. Apply the finance schema

With PostgreSQL running:

```bash
psql -U postgres -d maritime_db -f finance/schema_finance.sql
```

This creates the finance-specific tables in addition to the main application schema.

---

## 2. Generate synthetic transactions

```bash
python finance/generate_finance_data.py
```

This populates the ERP and bank/PMS transaction tables with synthetic records and intentionally injected discrepancies.

---

## 3. Start the API

The finance router is mounted into the main FastAPI application:

```bash
python -m uvicorn main:app --reload
```

The finance endpoints are then available under:

```text
/finance/...
```

---

# 🔌 API Endpoints

| Method | Endpoint                                    | Purpose                                              |
| ------ | ------------------------------------------- | ---------------------------------------------------- |
| `POST` | `/finance/reconcile`                        | Executes a reconciliation pass and returns a summary |
| `GET`  | `/finance/exceptions?status=PENDING_REVIEW` | Lists exceptions filtered by status                  |
| `GET`  | `/finance/exceptions/{id}/explain`          | Generates an LLM-assisted explanation                |
| `POST` | `/finance/exceptions/{id}/review`           | Records an approve/reject decision                   |
| `GET`  | `/finance/journal-entries?status=DRAFT`     | Lists generated journal-entry drafts                 |

---

# 🧪 Example API Workflow

## Run reconciliation

```bash
curl -X POST http://localhost:8000/finance/reconcile
```

The response summarizes the reconciliation run.

---

## List pending exceptions

```bash
curl "http://localhost:8000/finance/exceptions?status=PENDING_REVIEW"
```

---

## Request an explanation

```bash
curl "http://localhost:8000/finance/exceptions/1/explain"
```

The response contains an LLM-generated natural-language explanation of the selected exception.

---

## Approve an exception

```bash
curl -X POST http://localhost:8000/finance/exceptions/1/review \
  -H "Content-Type: application/json" \
  -d '{"decision": "APPROVED", "reviewed_by": "dimitris"}'
```

Approval triggers the creation of a draft journal entry according to the implemented workflow.

---

## List draft journal entries

```bash
curl "http://localhost:8000/finance/journal-entries?status=DRAFT"
```

---

# 📊 Verified End-to-End Demonstration

A successful end-to-end run was performed against a synthetic dataset containing:

```text
ERP transactions:   300
Bank transactions:  297
```

The reconciliation engine produced the following result:

```json
{
  "run_id": "cd01d906",
  "matched_clean": 214,
  "exceptions_found": 101,
  "exception_breakdown": {
    "UNMATCHED_ERP": 18,
    "UNMATCHED_BANK": 15,
    "DATE_MISMATCH": 24,
    "AMOUNT_MISMATCH": 44
  }
}
```

The results are consistent with the purpose of the synthetic dataset: discrepancies were deliberately injected to exercise the exception-handling paths.

The run was followed by:

1. Retrieval of a pending exception.
2. Human approval of the exception.
3. Successful creation of a draft journal entry.

This verifies the complete application workflow:

```text
Synthetic Transactions
        ↓
Reconciliation
        ↓
Exception Detection
        ↓
Pending Review
        ↓
Human Approval
        ↓
Draft Journal Entry
```

The result should be interpreted as an **end-to-end software workflow verification**, not as evidence of accounting accuracy or production reconciliation performance.

---

# 🔐 Control & Safety Considerations

Financial workflows require stronger controls than a typical analytics application.

This demonstration intentionally keeps the LLM outside the authoritative accounting decision path.

The architecture is:

```text
                    LLM
                     │
                     ▼
              Explanation Only
                     │
                     ▼
Transaction → Rules → Exception → Human Review
                                  │
                                  ▼
                           Journal Draft
```

The deterministic reconciliation engine identifies discrepancies, while the human reviewer makes the approval decision.

This is preferable to allowing an LLM to directly:

* Approve transactions.
* Modify source records.
* Determine accounting treatment autonomously.
* Post journal entries.

For production deployment, additional controls would be required around authentication, authorization, audit logging, data privacy, accounting validation, and segregation of duties.

---

# ⚠️ Limitations

This module is intentionally a **proof-of-concept / engineering demonstration** rather than a production accounting platform.

Important limitations include:

### Synthetic transaction data

The ERP and bank feeds are generated locally and do not represent real financial transaction populations.

### Simplified matching logic

The matching engine uses transaction references, amounts, dates, and predefined tolerances. Real reconciliation systems may require substantially more sophisticated matching strategies.

Examples include:

* Fuzzy reference matching.
* One-to-many matching.
* Many-to-one matching.
* Duplicate detection.
* Currency conversion.
* Fees and bank charges.
* Settlement-date differences.
* Partial payments.
* Recurring transactions.

### Simplified accounting logic

The journal-entry generation logic is intentionally simplified and should not be treated as a complete accounting rules engine.

### LLM explanation reliability

LLM-generated explanations can contain errors or misleading interpretations. They are therefore positioned as reviewer assistance rather than authoritative financial decisions.

### No live financial-system posting

Generated journal entries remain drafts and are not automatically posted to an external ERP or accounting system.

### Security and compliance

A production financial system would require significantly stronger controls for:

* Authentication.
* Authorization.
* Secrets management.
* Encryption.
* Auditability.
* Data retention.
* Personally identifiable information.
* Financial-data privacy.
* Regulatory compliance.
* Segregation of duties.

---

# 🔬 What This Demonstrates

The main value of this module is the combination of deterministic automation and controlled human oversight.

It demonstrates:

* Cross-system reconciliation.
* Exception classification.
* Explicit workflow states.
* Human-in-the-loop validation.
* LLM-assisted investigation.
* Draft journal-entry generation.
* REST API integration.
* PostgreSQL persistence.
* End-to-end workflow testing.

The architectural principle is:

> **Automate deterministic work, surface uncertainty explicitly, use AI to assist investigation, and keep consequential financial decisions under controlled human review.**

This is particularly important when applying generative AI to operational workflows where an incorrect automated decision could have financial consequences.

---

# 🎯 Summary

The Finance Reconciliation Extension adapts the platform's reusable architecture to a second operational domain:

```text
                AI-Driven Analytics Platform
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
   Maritime Analytics              Finance Operations
          │                                 │
          ▼                                 ▼
   ML / Text-to-SQL                 Reconciliation
          │                                 │
          │                         Exception Detection
          │                                 │
          │                         Human-in-the-Loop
          │                                 │
          │                         LLM Explanation
          │                                 │
          │                         Journal Drafting
          │                                 │
          └────────────────┬────────────────┘
                           ▼
                    FastAPI + PostgreSQL
```

The module demonstrates that the platform architecture can be reused beyond fleet analytics while maintaining a clear separation between **automated processing, AI-assisted explanation, and human authorization**.
