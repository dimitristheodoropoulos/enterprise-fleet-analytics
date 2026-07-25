-- Finance Reconciliation Extension — schema
-- Simulates two independent systems that need cross-system reconciliation
-- (e.g. an ERP/accounting ledger vs. a bank/PMS statement feed), plus
-- the exception-handling and audit tables needed for human-in-the-loop review.

-- "System A" — e.g. internal ERP / accounting ledger entries
CREATE TABLE IF NOT EXISTS erp_transactions (
    erp_txn_id      SERIAL PRIMARY KEY,
    reference       VARCHAR(64) NOT NULL,      -- shared reconciliation key (invoice/order/ref no.)
    entity_id       VARCHAR(32) NOT NULL,       -- e.g. resort/property/cost-center code
    amount          NUMERIC(14, 2) NOT NULL,
    currency        VARCHAR(3) NOT NULL DEFAULT 'EUR',
    txn_date        DATE NOT NULL,
    description     TEXT
);

-- "System B" — e.g. bank statement / payment processor / PMS feed
CREATE TABLE IF NOT EXISTS bank_transactions (
    bank_txn_id     SERIAL PRIMARY KEY,
    reference       VARCHAR(64) NOT NULL,
    entity_id       VARCHAR(32) NOT NULL,
    amount          NUMERIC(14, 2) NOT NULL,
    currency        VARCHAR(3) NOT NULL DEFAULT 'EUR',
    txn_date        DATE NOT NULL,
    description     TEXT
);

-- Result of each reconciliation run: matched pairs, amount/date discrepancies,
-- and unmatched items that need human review.
CREATE TABLE IF NOT EXISTS reconciliation_exceptions (
    exception_id       SERIAL PRIMARY KEY,
    run_id              VARCHAR(64) NOT NULL,
    reference           VARCHAR(64),
    entity_id           VARCHAR(32),
    erp_txn_id          INTEGER REFERENCES erp_transactions(erp_txn_id),
    bank_txn_id         INTEGER REFERENCES bank_transactions(bank_txn_id),
    exception_type      VARCHAR(32) NOT NULL,   -- AMOUNT_MISMATCH | UNMATCHED_ERP | UNMATCHED_BANK | DATE_MISMATCH
    erp_amount          NUMERIC(14, 2),
    bank_amount         NUMERIC(14, 2),
    discrepancy_amount  NUMERIC(14, 2),
    ai_explanation      TEXT,                   -- LLM-generated natural-language explanation
    status              VARCHAR(16) NOT NULL DEFAULT 'PENDING_REVIEW', -- PENDING_REVIEW | APPROVED | REJECTED
    reviewed_by         VARCHAR(64),
    reviewed_at         TIMESTAMP,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Journal entries proposed automatically from successfully matched/approved items.
CREATE TABLE IF NOT EXISTS journal_entries (
    journal_entry_id    SERIAL PRIMARY KEY,
    exception_id        INTEGER REFERENCES reconciliation_exceptions(exception_id),
    entity_id           VARCHAR(32),
    account_debit       VARCHAR(64),
    account_credit      VARCHAR(64),
    amount              NUMERIC(14, 2),
    memo                TEXT,
    status              VARCHAR(16) NOT NULL DEFAULT 'DRAFT', -- DRAFT | POSTED
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);
