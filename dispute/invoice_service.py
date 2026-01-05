from dispute.db import get_cursor

def add_invoice(data: dict):
    with get_cursor() as cur:
        cur.execute("""
        INSERT INTO invoices (
            invoice_number,
            invoice_date,
            due_date,
            invoice_type,
            currency,
            basic_amount,
            tax_amount,
            invoice_total_amount,
            raw_invoice_text,
            payment_status,
            customer_id,
            customer_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["invoice_number"],
            data["invoice_date"],
            data["due_date"],
            data["invoice_type"],
            data["currency"],
            data["basic_amount"],
            data["tax_amount"],
            data["invoice_total_amount"],
            data.get("raw_invoice_text"),
            data["payment_status"],
            data["customer_id"],
            data["customer_name"]
        ))

def fetch_open_invoices(customer_id):
    with get_cursor() as cur:
        cur.execute("""
        SELECT invoice_number, invoice_total_amount
        FROM invoices
        WHERE customer_id = ?
        AND UPPER(payment_status) IN ('PENDING', 'PARTIALLY_PAID')
        """, (customer_id,))
        return cur.fetchall()

def fetch_invoices(customer_id=None):
    from dispute.db import get_cursor

    query = """
        SELECT invoice_number, invoice_date, due_date,
               invoice_type, invoice_total_amount, payment_status
        FROM invoices
    """
    params = []

    if customer_id:
        query += " WHERE customer_id = ?"
        params.append(customer_id)

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()

def fetch_invoices_by_customer(customer_id):
    from dispute.db import get_cursor
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                invoice_number,
                invoice_date,
                basic_amount,
                tax_amount,
                invoice_total_amount,
                payment_status,
                currency
            FROM invoices
            WHERE customer_id = ?
        """, (customer_id,))
        return cur.fetchall()


def fetch_invoices_by_customer_and_date(customer_id, from_date, to_date):
    from dispute.db import get_cursor
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                invoice_number,
                invoice_date,
                basic_amount,
                tax_amount,
                invoice_total_amount,
                payment_status,
                currency
            FROM invoices
            WHERE customer_id = ?
              AND invoice_date BETWEEN ? AND ?
        """, (customer_id, from_date, to_date))
        return cur.fetchall()

