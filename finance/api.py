"""
FastAPI router for the Finance Reconciliation extension.
Mounted into the main app (see main.py: app.include_router(finance_router)).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from finance.explain import explain_exception
from finance.reconciliation import get_connection, run_reconciliation
from finance.review import list_exceptions, review_exception

router = APIRouter(prefix="/finance", tags=["finance-reconciliation"])


class ReviewDecision(BaseModel):
    decision: str          # "APPROVED" or "REJECTED"
    reviewed_by: str


@router.post("/reconcile")
def trigger_reconciliation():
    """Runs a full ERP vs. bank/PMS reconciliation pass and reports the summary."""
    try:
        return run_reconciliation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reconciliation run failed: {e}")


@router.get("/exceptions")
def get_exceptions(status: str = "PENDING_REVIEW"):
    """Lists reconciliation exceptions awaiting (or resolved by) human review."""
    return list_exceptions(status=status)


@router.get("/exceptions/{exception_id}/explain")
def get_exception_explanation(exception_id: int):
    """Returns an AI-generated natural-language explanation for one exception."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reconciliation_exceptions WHERE exception_id = %s;", (exception_id,))
    exc = cur.fetchone()
    cur.close()
    conn.close()

    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")

    explanation = explain_exception(dict(exc))
    return {"exception_id": exception_id, "explanation": explanation}


@router.post("/exceptions/{exception_id}/review")
def submit_review(exception_id: int, body: ReviewDecision):
    """
    Records a human decision (approve/reject) on a pending exception.
    Approval automatically generates a draft journal entry.
    """
    try:
        return review_exception(exception_id, body.decision, body.reviewed_by)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/journal-entries")
def get_journal_entries(status: str = "DRAFT"):
    """Lists journal entries generated from approved reconciliation exceptions."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM journal_entries WHERE status = %s ORDER BY created_at DESC;", (status,))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows
