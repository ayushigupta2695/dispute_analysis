from core.db import get_cursor
from core.policies import POLICIES

def load_policies():
    with get_cursor() as cur:
        cur.execute("DELETE FROM policies")
        for p in POLICIES:
            cur.execute("""
            INSERT INTO policies (category, sub_category, rule, max_amount, conditions, limit_frequency)
            VALUES (?, ?, ?, ?, ?, ?)
            """, p)
