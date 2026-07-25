"""
Human-in-the-loop review layer: lists pending exceptions, records a
reviewer's approve/reject decision, and generates a draft journal entry
once an exception is resolved.
"""
from datetime import datetime

from finance.reconciliation import get_connection


def list_exceptions(status: str = "PENDING_REVIEW") -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM reconciliation_exceptions WHERE status = %s ORDER BY created_at DESC;",
        (status,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


def review_exception(exception_id: int, decision: str, reviewed_by: str) -> dict:
    """
    decision: 'APPROVED' or 'REJECTED'.
    On approval, a draft journal entry is generated automatically.
    """
    if decision not in ("APPROVED", "REJECTED"):
        raise ValueError("decision must be 'APPROVED' or 'REJECTED'")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM reconciliation_exceptions WHERE exception_id = %s;", (exception_id,))
    exc = cur.fetchone()
    if not exc:
        cur.close()
        conn.close()
        raise LookupError(f"Exception {exception_id} not found")

    cur.execute(
        """
        UPDATE reconciliation_exceptions
        SET status = %s, reviewed_by = %s, reviewed_at = %s
        WHERE exception_id = %s;
        """,
        (decision, reviewed_by, datetime.utcnow(), exception_id),
    )

    journal_entry = None
    if decision == "APPROVED":
        journal_entry = _generate_journal_entry(cur, exc)

    conn.commit()
    cur.close()
    conn.close()

    return {"exception_id": exception_id, "status": decision, "journal_entry": journal_entry}


def _generate_journal_entry(cur, exc: dict) -> dict:
    """
    Produces a simple draft journal entry for an approved, reconciled item.
    Real chart-of-accounts mapping would replace these placeholder account
    codes in a production system.
    """
    amount = exc["bank_amount"] if exc["bank_amount"] is not None else exc["erp_amount"]
    memo = (
        f"Reconciliation {exc['exception_type']} for {exc['reference']} "
        f"({exc['entity_id']}) — approved after human review."
    )

    cur.execute(
        """
        INSERT INTO journal_entries
            (exception_id, entity_id, account_debit, account_credit, amount, memo, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'DRAFT')
        RETURNING journal_entry_id;
        """,
        (exc["exception_id"], exc["entity_id"], "1010-CASH", "4000-REVENUE-ADJ", amount, memo),
    )
    journal_entry_id = cur.fetchone()["journal_entry_id"]

    return {
        "journal_entry_id": journal_entry_id,
        "account_debit": "1010-CASH",
        "account_credit": "4000-REVENUE-ADJ",
        "amount": float(amount) if amount is not None else None,
        "memo": memo,
    }
