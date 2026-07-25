"""
Generates a natural-language explanation for a reconciliation exception,
reusing the same OpenAI-compatible Gemini client pattern already used by
the Fleet Analytics AI Copilot (chatbot_agent.py / main.py).
"""
import os

from openai import OpenAI

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key_env = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
        _client = OpenAI(
            api_key=api_key_env,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    return _client


def explain_exception(exception: dict) -> str:
    """
    Returns a short, human-readable explanation (Greek) of a reconciliation
    exception, suitable for display next to the item in a review dashboard.
    """
    prompt = (
        "Είσαι ένας βοηθός λογιστικής συμφωνίας (reconciliation assistant). "
        "Σου δίνεται μία εξαίρεση συμφωνίας μεταξύ δύο συστημάτων (ERP vs Bank/PMS). "
        "Εξήγησε σε 1-2 προτάσεις, στα Ελληνικά, τι πιθανόν συμβαίνει και τι θα πρέπει "
        "να ελέγξει ο άνθρωπος πριν εγκρίνει ή απορρίψει την εξαίρεση.\n\n"
        f"Τύπος εξαίρεσης: {exception.get('exception_type')}\n"
        f"Reference: {exception.get('reference')}\n"
        f"Entity: {exception.get('entity_id')}\n"
        f"Ποσό ERP: {exception.get('erp_amount')}\n"
        f"Ποσό Bank/PMS: {exception.get('bank_amount')}\n"
        f"Διαφορά: {exception.get('discrepancy_amount')}\n"
    )

    try:
        response = _get_client().chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": "Απαντάς πάντα σύντομα και στα Ελληνικά."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        # Graceful degradation — same principle as the fraud-detection-mlops
        # failover pattern: never block the review workflow if the LLM call fails.
        return (
            f"[AI εξήγηση μη διαθέσιμη: {e}] Χειροκίνητος έλεγχος απαιτείται για "
            f"{exception.get('exception_type')} στο reference {exception.get('reference')}."
        )
