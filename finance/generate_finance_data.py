"""
Seeds two independent transaction feeds (ERP ledger vs. bank/PMS statement)
into PostgreSQL, with deliberately injected discrepancies so the
reconciliation engine has real exceptions to find.

Run after schema_finance.sql has been applied:
    python finance/generate_finance_data.py
"""
import random
from datetime import datetime, timedelta

import psycopg2

ENTITIES = ["SANI-GOLF", "SANI-BEACH", "IKOS-DASSIA", "IKOS-OLIVIA", "IKOS-ARIA"]


def get_connection():
    return psycopg2.connect(
        dbname="maritime_db",  # same local DB used by the rest of the project
        user="postgres",
        password="1234",
        host="localhost",
        port="5432",
    )


def seed(num_transactions: int = 300, discrepancy_rate: float = 0.15):
    conn = get_connection()
    cur = conn.cursor()

    start_date = datetime(2026, 6, 1)
    erp_rows = []
    bank_rows = []

    for i in range(num_transactions):
        reference = f"REF-{10000 + i}"
        entity = random.choice(ENTITIES)
        amount = round(random.uniform(150.0, 25000.0), 2)
        txn_date = start_date + timedelta(days=random.randint(0, 29))
        description = f"Guest folio settlement {reference}"

        erp_amount = amount
        bank_amount = amount
        bank_date = txn_date

        roll = random.random()
        if roll < discrepancy_rate:
            # amount mismatch (e.g. bank fee deducted, FX rounding, partial settlement)
            bank_amount = round(amount - random.uniform(0.5, 50.0), 2)
        elif roll < discrepancy_rate * 1.6:
            # date mismatch (e.g. weekend settlement lag)
            bank_date = txn_date + timedelta(days=random.randint(1, 4))
        elif roll < discrepancy_rate * 2.2:
            # missing on the bank side entirely (unmatched ERP entry)
            bank_amount = None

        erp_rows.append((reference, entity, erp_amount, "EUR", txn_date, description))
        if bank_amount is not None:
            bank_rows.append((reference, entity, bank_amount, "EUR", bank_date, description))

    # A few bank-only entries with no ERP counterpart (unmatched bank side)
    for i in range(int(num_transactions * 0.05)):
        reference = f"REF-BANKONLY-{i}"
        entity = random.choice(ENTITIES)
        amount = round(random.uniform(100.0, 5000.0), 2)
        txn_date = start_date + timedelta(days=random.randint(0, 29))
        bank_rows.append((reference, entity, amount, "EUR", txn_date, "Unmatched incoming payment"))

    cur.executemany(
        """
        INSERT INTO erp_transactions (reference, entity_id, amount, currency, txn_date, description)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        erp_rows,
    )
    cur.executemany(
        """
        INSERT INTO bank_transactions (reference, entity_id, amount, currency, txn_date, description)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        bank_rows,
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"-> Seeded {len(erp_rows)} ERP rows and {len(bank_rows)} bank rows "
          f"(~{discrepancy_rate * 100:.0f}% intentional discrepancy rate).")


if __name__ == "__main__":
    seed()
