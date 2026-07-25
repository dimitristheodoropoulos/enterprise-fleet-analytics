"""
Reconciliation engine: matches ERP ledger transactions against bank/PMS
transactions by reference, flags amount/date discrepancies, and records
anything it cannot auto-resolve as an exception pending human review.
"""
import uuid
from datetime import timedelta
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor

AMOUNT_TOLERANCE = Decimal("0.01")   # exact-match tolerance for amounts
DATE_TOLERANCE_DAYS = 0              # same-day match required; beyond this -> DATE_MISMATCH


def get_connection():
    return psycopg2.connect(
        dbname="maritime_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432",
        cursor_factory=RealDictCursor,
    )


def run_reconciliation() -> dict:
    """
    Runs a full reconciliation pass over all ERP vs. bank transactions,
    writes exceptions for anything that doesn't cleanly match, and
    returns a summary. Matched-clean pairs are not stored as exceptions —
    only what needs attention or an audit trail.
    """
    run_id = str(uuid.uuid4())[:8]
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM erp_transactions ORDER BY reference;")
    erp_txns = {row["reference"]: row for row in cur.fetchall()}

    cur.execute("SELECT * FROM bank_transactions ORDER BY reference;")
    bank_txns = {row["reference"]: row for row in cur.fetchall()}

    matched_clean = 0
    exceptions = []

    all_references = set(erp_txns.keys()) | set(bank_txns.keys())

    for reference in all_references:
        erp = erp_txns.get(reference)
        bank = bank_txns.get(reference)

        if erp and not bank:
            exceptions.append(_build_exception(
                run_id, reference, erp, None, "UNMATCHED_ERP"
            ))
            continue

        if bank and not erp:
            exceptions.append(_build_exception(
                run_id, reference, None, bank, "UNMATCHED_BANK"
            ))
            continue

        # both sides present — check amount and date
        amount_diff = abs(Decimal(str(erp["amount"])) - Decimal(str(bank["amount"])))
        date_diff = abs((erp["txn_date"] - bank["txn_date"]).days)

        if amount_diff > AMOUNT_TOLERANCE:
            exceptions.append(_build_exception(
                run_id, reference, erp, bank, "AMOUNT_MISMATCH", amount_diff
            ))
        elif date_diff > DATE_TOLERANCE_DAYS:
            exceptions.append(_build_exception(
                run_id, reference, erp, bank, "DATE_MISMATCH"
            ))
        else:
            matched_clean += 1

    if exceptions:
        cur.executemany(
            """
            INSERT INTO reconciliation_exceptions
                (run_id, reference, entity_id, erp_txn_id, bank_txn_id, exception_type,
                 erp_amount, bank_amount, discrepancy_amount, status)
            VALUES (%(run_id)s, %(reference)s, %(entity_id)s, %(erp_txn_id)s, %(bank_txn_id)s,
                    %(exception_type)s, %(erp_amount)s, %(bank_amount)s, %(discrepancy_amount)s,
                    'PENDING_REVIEW');
            """,
            exceptions,
        )
        conn.commit()

    cur.close()
    conn.close()

    return {
        "run_id": run_id,
        "matched_clean": matched_clean,
        "exceptions_found": len(exceptions),
        "exception_breakdown": _breakdown(exceptions),
    }


def _build_exception(run_id, reference, erp, bank, exception_type, discrepancy_amount=None):
    return {
        "run_id": run_id,
        "reference": reference,
        "entity_id": (erp or bank)["entity_id"],
        "erp_txn_id": erp["erp_txn_id"] if erp else None,
        "bank_txn_id": bank["bank_txn_id"] if bank else None,
        "exception_type": exception_type,
        "erp_amount": erp["amount"] if erp else None,
        "bank_amount": bank["amount"] if bank else None,
        "discrepancy_amount": discrepancy_amount,
    }


def _breakdown(exceptions: list) -> dict:
    counts: dict = {}
    for e in exceptions:
        counts[e["exception_type"]] = counts.get(e["exception_type"], 0) + 1
    return counts
