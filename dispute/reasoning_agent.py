# from core.llm_factory import get_llm

# def explain_dispute(dispute_context: dict) -> str:
#     llm = get_llm("groq")

#     PROMPT = """
# You are a senior financial reconciliation engineer.

# Use ONLY the provided input.
# Do NOT invent numbers.
# Do NOT perform new calculations.

# INPUT:
# {context}

# Explain clearly why the invoice amount and received amount differ (if they do).
# Be neutral, professional, and audit-friendly.
# """

#     return llm.invoke(
#         PROMPT.format(context=dispute_context)
#     ).content

from typing import List, Dict
from core.llm_factory import get_llm


def generate_dispute_explanation(
    customer_name: str,
    analysis_rows: List[Dict]
) -> str:
    """
    analysis_rows structure (example):

    [
        {
            "invoice_number": str,
            "invoice_date": str,
            "currency": str,
            "basic_amount": float,
            "tax_amount": float,
            "invoice_total_amount": float,
            "paid_amount": float,
            "outstanding_amount": float,
            "status": str,
            "transactions": [
                {
                    "transaction_date": str,
                    "amount": float,
                    "tax_deducted": float,
                    "bank_charges": float,
                    "gateway_fee": float,
                    "forex_charges": float,
                    "currency": str,
                    "narration": str
                }
            ]
        }
    ]
    """

    llm = get_llm(provider="groq")

    # -------------------------------
    # SYSTEM PROMPT (NON-NEGOTIABLE)
    # -------------------------------
    system_prompt = """
You are a Senior Finance Reconciliation Analyst preparing an audit-grade
reconciliation narrative for finance, compliance, and audit stakeholders.

YOUR RESPONSIBILITY:
- Read and understand ALL invoice and transaction data provided.
- Internally analyze transaction patterns per invoice.
- Produce a SUMMARY-ONLY explanation.

ABSOLUTE RULES (MANDATORY):
- Use ONLY the data explicitly provided.
- Do NOT perform calculations of any kind.
- Do NOT recompute totals, balances, or deductions.
- Do NOT alter, normalize, or convert currencies.
- Do NOT infer missing data or assume business intent.
- Do NOT provide recommendations or corrective actions.
- Do NOT repeat tables or list transaction rows.
- Do NOT enumerate individual transactions, even if many exist.

Transactions are provided ONLY for internal analysis,
NOT for reproduction in the explanation.

Your output must remain readable even if:
- One invoice has hundreds of transactions
- Multiple invoices are analyzed together
"""

    # -------------------------------
    # USER PROMPT (TASK-SPECIFIC)
    # -------------------------------
    user_prompt = f"""
Customer Name:
{customer_name}

Reconciliation Dataset (Invoices with Transactions):
{analysis_rows}

INSTRUCTIONS FOR OUTPUT:

Generate a structured, narrative reconciliation explanation.

GENERAL FORMAT:
- Write one clearly separated section per invoice.
- Do NOT include tables, bullet lists of transactions, or raw rows.
- Do NOT quote or restate the input data verbatim.

FOR EACH INVOICE, EXPLAIN:

1. Invoice Overview
   - Invoice number
   - Invoice date
   - Currency
   - Basic amount
   - Tax amount
   - Total invoice amount

2. Transaction Assessment (SUMMARY ONLY)
   - Whether the invoice has:
     • No transactions
     • A single transaction
     • Multiple transactions
   - Describe transaction behavior at a pattern level:
     • Multiple partial payments
     • Presence of deductions or charges
   - Explicitly mention if any of the following appear across transactions:
     • Tax deducted
     • Bank charges
     • Gateway fees
     • Forex charges

3. Currency Observations
   - State whether transaction currency matches invoice currency.
   - If different currencies exist, mention this ONLY as an observation.
   - Do NOT interpret, convert, or explain exchange impact.

4. Reconciliation Outcome
   - Paid amount (as provided)
   - Outstanding amount (as provided)
   - Final invoice status (PENDING / PARTIALLY_PAID / COMPLETED)

LANGUAGE & TONE REQUIREMENTS:
- Professional
- Neutral
- Audit-friendly
- Factual
- Explanation-focused
- No assumptions
- No conclusions beyond the provided data

REMEMBER:
Tables are already visible to the user.
Your task is to explain the data, not restate it.
"""

    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.content.strip()
