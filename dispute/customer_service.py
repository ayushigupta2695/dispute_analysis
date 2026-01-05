from dispute.db import get_cursor
from dispute.validators import validate_customer

def add_customer(data: dict):
    validate_customer(data)
    with get_cursor() as cur:
        cur.execute("""
        INSERT INTO customers (
            customer_name, customer_type, email, phone_number,
            company_name, address, city, state, country, zip_code,
            industry, risk_rating
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(data.values()))

def fetch_customers():
    with get_cursor() as cur:
        cur.execute("SELECT customer_id, customer_name FROM customers ORDER BY customer_name")
        return cur.fetchall()

def fetch_all_customers_full():
    from dispute.db import get_cursor
    with get_cursor() as cur:
        cur.execute("""
            SELECT customer_id, customer_name, customer_type,
                   email, phone_number, city, state, country
            FROM customers
            ORDER BY customer_name
        """)
        return cur.fetchall()
