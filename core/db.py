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

def init_db():
    with get_cursor() as cur:

        cur.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gst_number TEXT,
            receipt_number TEXT,
            document_type TEXT,
            receipt_date TEXT,
            vendor_name TEXT,
            buyer_name TEXT,
            vendor_address TEXT,
            bill_type TEXT,
            total_amount REAL,
            tax_amount REAL,
            raw_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            sub_category TEXT,
            rule TEXT,
            max_amount REAL,
            conditions TEXT,
            limit_frequency TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS validation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER,
            decision TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

import json
from core.db import get_cursor


def fetch_all_receipts():
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                id,
                vendor_name,
                bill_type,
                total_amount,
                tax_amount,
                created_at
            FROM receipts
            ORDER BY created_at DESC
        """)
        rows = cur.fetchall()

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "vendor_name": r[1],
            "bill_type": r[2],
            "total_amount": r[3],
            "tax_amount": r[4],
            "created_at": r[5],
        })

    return results

def fetch_receipt_details(receipt_id: int):
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                gst_number,
                receipt_number,
                document_type,
                receipt_date,
                vendor_name,
                buyer_name,
                vendor_address,
                bill_type,
                total_amount,
                tax_amount,
                raw_text,
                created_at
            FROM receipts
            WHERE id = ?
        """, (receipt_id,))
        row = cur.fetchone()

    if not row:
        return None

    return {
        "gst_number": row[0],
        "receipt_number": row[1],
        "document_type": row[2],
        "receipt_date": row[3],
        "vendor_name": row[4],
        "buyer_name": row[5],
        "vendor_address": row[6],
        "bill_type": row[7],
        "total_amount": row[8],
        "tax_amount": row[9],
        "raw_text": row[10],
        "created_at": row[11],
    }


def fetch_policies():
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, category, sub_category, rule, max_amount, conditions, limit_frequency
            FROM policies
            ORDER BY category
        """)
        return cur.fetchall()


def insert_policy(category, sub_category, rule, max_amount, conditions, limit_frequency):
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO policies (category, sub_category, rule, max_amount, conditions, limit_frequency)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (category, sub_category, rule, max_amount, conditions, limit_frequency))


def delete_policy(policy_id: int):
    with get_cursor() as cur:
        cur.execute("""
            DELETE FROM policies
            WHERE id = ?
        """, (policy_id,))


def fetch_validation_logs():
    with get_cursor() as cur:
        cur.execute("""
            SELECT receipt_id, decision, details, created_at
            FROM validation_logs
            ORDER BY created_at DESC
        """)
        return cur.fetchall()
