from dispute.transaction_service import fetch_transactions_by_invoice

def analyze_invoices(invoice_rows):
    """
    invoice_rows:
    (
      invoice_number,
      invoice_date,
      basic_amount,
      tax_amount,
      invoice_total_amount,
      payment_status,
      currency
    )
    """

    results = []

    for (
        inv_no,
        inv_date,
        basic_amt,
        tax_amt,
        total_amt,
        status,
        inv_currency
    ) in invoice_rows:

        txns = fetch_transactions_by_invoice(inv_no)

        txn_summary = []
        total_paid = 0

        for t in txns:
            txn_summary.append({
                "transaction_date": t[0],
                "amount": t[1],
                "tax_deducted": t[2],
                "bank_charges": t[3],
                "gateway_fee": t[4],
                "forex_charges": t[5],
                "currency": t[6],
                "narration": t[7]
            })
            total_paid += t[1]

        outstanding = total_amt - total_paid

        derived_status = (
            "COMPLETED" if outstanding == 0 and total_paid > 0
            else "PARTIALLY_PAID" if total_paid > 0
            else "PENDING"
        )

        results.append({
            "invoice_number": inv_no,
            "invoice_date": inv_date,
            "currency": inv_currency,
            "basic_amount": basic_amt,
            "tax_amount": tax_amt,
            "invoice_total_amount": total_amt,
            "paid_amount": total_paid,
            "outstanding_amount": outstanding,
            "status": derived_status,
            "transactions": txn_summary
        })

    return results
