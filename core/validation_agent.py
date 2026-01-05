import json
from core.db import get_cursor
from core.expense_intents import detect_intent, intent_to_policy


def resolve_unit_price(item):
    """
    Finance-safe unit price resolution.
    """
    qty = item.get("quantity")
    unit_price = item.get("unit_price")
    total = item.get("total_amount")

    if unit_price is not None:
        return float(unit_price)

    if qty and total:
        try:
            return round(float(total) / float(qty), 2)
        except Exception:
            return None

    if total:
        return float(total)

    return None


def validate_receipt(receipt_id: int, receipt_data: dict) -> dict:
    """
    GENERIC, INTENT-DRIVEN, POLICY-CLOSED VALIDATION
    """

    line_items = receipt_data.get("line_items", [])
    header = receipt_data.get("header", {})
    no_of_days=header.get("Number of days")
    approved_items = []
    violations = []
    uncovered_items = []

    if not line_items:
        return {
            "decision": "REJECTED",
            "approved_items": [],
            "violations": [],
            "uncovered_items": [
                {"reason": "No line items found in receipt"}
            ],
            "explanation": "Receipt could not be validated."
        }

    # -------------------------------------------------
    # LOAD POLICIES
    # -------------------------------------------------
    with get_cursor() as cur:
        cur.execute("""
            SELECT category, rule, max_amount, conditions, limit_frequency
            FROM policies
        """)
        policies = cur.fetchall()

    policy_map = {
        category: {
            "rule": rule,
            "limit": max_amount,
            "conditions": conditions,
            "limit_frequency": limit_freq
        }
        for category, rule, max_amount, conditions, limit_freq in policies
    }

    # -------------------------------------------------
    # AGGREGATE BY POLICY CATEGORY (GENERIC)
    # -------------------------------------------------
    category_totals = {}

    for item in line_items:
        desc = (item.get("description") or "").lower()
        amount = item.get("total_amount") or 0
        intent = detect_intent(desc)
        policy_category = intent_to_policy(intent)

        # ❌ Unsupported expense
        if policy_category == "UNSUPPORTED":
            uncovered_items.append({
                "item": desc,
                "unit_price": resolve_unit_price(item),
                "reason": "No matching company policy"
            })
            continue

        # Taxes always allowed
        if policy_category == "Statutory":
            approved_items.append({
                "item": desc,
                "unit_price": resolve_unit_price(item),
                "status": "Statutory tax"
            })
            continue

        category_totals[policy_category] = (
            category_totals.get(policy_category, (0, 0, 0))[0] + amount ,  resolve_unit_price(item) ,  item.get("quantity", 1)
        )

    # -------------------------------------------------
    # VALIDATE CATEGORY TOTALS AGAINST POLICY
    # -------------------------------------------------
    for category, value_tuple in category_totals.items():
        total, up, qty = value_tuple
        policy = policy_map.get(category)

        if not policy:
            violations.append({
                "policy": category,
                "limit": None,
                "unit_price": up,
                "actual": total,
                "reason": "Policy not defined"
            })
            continue

        limit = policy["limit"]
        limit_frequency=policy["limit_frequency"]

        def limit_freq_check(limit_frequency,total,up,qty,limit):
            flag=False
            if limit_frequency=="daily":
                if no_of_days==1:
                    if total>limit:
                        flag=False
                    else:
                        flag=True
                elif (total/no_of_days)> limit:
                    flag=False
                else:
                    flag=True
            else:
                if total>limit:
                    flag=False
                else:
                    flag=True
            return flag
            
        if limit is not None and not limit_freq_check(limit_frequency,total,up,qty,limit):
            violations.append({
                "policy": category,
                "rule": policy["rule"],
                "limit": limit,
                "unit_price": up,
                "actual": total,
                "reason": f"{category} expense exceeds allowed limit"
            })
        else:
            approved_items.append({
                "category": category,
                "total": total,
                "unit_price": up,
                "status": "Within policy limits"
            })

    # -------------------------------------------------
    # FINAL DECISION
    # -------------------------------------------------
    if violations or uncovered_items:
        decision = "REJECTED"
        explanation = (
            "Receipt contains expenses that are either not covered "
            "by company policy or violate defined limits."
        )
    else:
        decision = "APPROVED"
        explanation = "All receipt expenses comply with company policies."

    result = {
        "decision": decision,
        "approved_items": approved_items,
        "violations": violations,
        "uncovered_items": uncovered_items,
        "explanation": explanation
    }

    # -------------------------------------------------
    # AUDIT LOG
    # -------------------------------------------------
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO validation_logs (receipt_id, decision, details)
            VALUES (?, ?, ?)
        """, (
            receipt_id,
            decision,
            json.dumps(result)
        ))

    return result
