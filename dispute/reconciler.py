from dispute.db import get_cursor

def reconcile_invoice(invoice_number):
    with get_cursor() as cur:
        cur.execute("""
        SELECT invoice_total_amount FROM invoices
        WHERE invoice_number = ?
        """, (invoice_number,))
        invoice_total = cur.fetchone()[0]

        cur.execute("""
        SELECT amount, bank_charges, tax_deducted, gateway_fee, forex_charges
        FROM transactions WHERE linked_invoice_id = ?
        """, (invoice_number,))
        rows = cur.fetchall()

    paid = sum(r[0] for r in rows)
    deductions = sum((r[1] or 0)+(r[2] or 0)+(r[3] or 0)+(r[4] or 0) for r in rows)

    return {
        "invoice_total": invoice_total,
        "total_paid": paid,
        "total_deductions": deductions,
        "difference": invoice_total - paid
    }
