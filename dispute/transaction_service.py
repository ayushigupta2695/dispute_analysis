from dispute.db import get_cursor

def insert_transaction(data: dict):
    invoice_number = data["linked_invoice_id"]
    invoice_amount = data["invoice_amount"]
    current_txn_amount = data["amount"]

    with get_cursor() as cur:

        # ----------------------------------
        # 1. Calculate total paid so far
        # ----------------------------------
        cur.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE linked_invoice_id = ?
        """, (invoice_number,))
        total_paid_so_far = cur.fetchone()[0]

        remaining_amount = invoice_amount - total_paid_so_far

        # ----------------------------------
        # 2. Validation
        # ----------------------------------
        if current_txn_amount > remaining_amount:
            raise ValueError(
                f"Transaction amount exceeds remaining invoice balance. "
                f"Remaining amount: {remaining_amount}"
            )

        # ----------------------------------
        # 3. Insert transaction
        # ----------------------------------
        cur.execute("""
        INSERT INTO transactions (
            transaction_date,
            narration,
            amount,
            bank_name,
            reference_number,
            account_number,
            account_type,
            payment_mode,
            currency,
            bank_charges,
            tax_deducted,
            gateway_fee,
            forex_charges,
            customer_id,
            customer_name,
            linked_invoice_id,
            invoice_amount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["transaction_date"],
            data.get("narration"),
            current_txn_amount,
            data["bank_name"],
            data.get("reference_number"),
            data["account_number"],
            data.get("account_type"),
            data["payment_mode"],
            data["currency"],
            data.get("bank_charges", 0),
            data.get("tax_deducted", 0),
            data.get("gateway_fee", 0),
            data.get("forex_charges", 0),
            data["customer_id"],
            data["customer_name"],
            invoice_number,
            invoice_amount
        ))

        # ----------------------------------
        # 4. Update invoice status
        # ----------------------------------
        if current_txn_amount == remaining_amount:
            new_status = "COMPLETED"
        else:
            new_status = "PARTIALLY_PAID"

        cur.execute("""
            UPDATE invoices
            SET payment_status = ?
            WHERE invoice_number = ?
        """, (new_status, invoice_number))

def fetch_transactions(customer_id=None, invoice_number=None):
    from dispute.db import get_cursor

    query = """
        SELECT transaction_date, amount, currency, payment_mode,
               bank_name, linked_invoice_id
        FROM transactions
    """
    params = []

    if customer_id:
        query += " WHERE customer_id = ?"
        params.append(customer_id)

    if invoice_number:
        query += " AND linked_invoice_id = ?"
        params.append(invoice_number)

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def fetch_transactions_by_invoice(invoice_number):
    from dispute.db import get_cursor
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                transaction_date,
                amount,
                tax_deducted,
                bank_charges,
                gateway_fee,
                forex_charges,
                currency,
                narration
            FROM transactions
            WHERE linked_invoice_id = ?
        """, (invoice_number,))
        return cur.fetchall()
