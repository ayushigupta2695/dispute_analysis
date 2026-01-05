import sqlite3
import os
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "finance_agents.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@contextmanager
def get_cursor():
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    finally:
        conn.close()

def init_dispute_tables():
    with get_cursor() as cur:

        # -----------------------------
        # CUSTOMER TABLE (unchanged)
        # -----------------------------
        cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT UNIQUE NOT NULL,
            customer_type TEXT NOT NULL,
            email TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            company_name TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            country TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            industry TEXT,
            risk_rating TEXT
        )
        """)

        # -----------------------------
        # DROP & RECREATE INVOICES TABLE
        # -----------------------------
        # cur.execute("DROP TABLE IF EXISTS invoices")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            iid INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            invoice_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            invoice_type TEXT NOT NULL,
            currency TEXT NOT NULL,
            basic_amount REAL NOT NULL,
            tax_amount REAL NOT NULL,
            invoice_total_amount REAL NOT NULL,
            raw_invoice_text TEXT,
            payment_status TEXT NOT NULL DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            customer_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL
        )
        """)

        # -----------------------------
        # TRANSACTIONS TABLE (unchanged)
        # -----------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            tid INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT NOT NULL,
            narration TEXT,
            amount REAL NOT NULL,
            bank_name TEXT NOT NULL,
            reference_number TEXT,
            account_number TEXT NOT NULL,
            account_type TEXT,
            payment_mode TEXT NOT NULL,
            currency TEXT NOT NULL,
            bank_charges REAL DEFAULT 0,
            tax_deducted REAL DEFAULT 0,
            gateway_fee REAL DEFAULT 0,
            forex_charges REAL DEFAULT 0,
            customer_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            linked_invoice_id TEXT NOT NULL,
            invoice_amount REAL NOT NULL
        )
        """)
