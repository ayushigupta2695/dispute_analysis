import streamlit as st
import pandas as pd
from datetime import timedelta

from dispute.db import init_dispute_tables
from dispute.customer_service import (
    add_customer,
    fetch_customers,
    fetch_all_customers_full
)
from dispute.invoice_service import (
    add_invoice,
    fetch_open_invoices,
    fetch_invoices
)
from dispute.transaction_service import (
    insert_transaction,
    fetch_transactions
)
from dispute.reasoning_agent import generate_dispute_explanation
# from dispute.dispute_engine import analyze_dispute
# from dispute.reasoning_agent import explain_dispute


def format_inr(value):
    try:
        return f"₹ {value:,.2f}"
    except Exception:
        return value


# ============================================================
# CUSTOMER MANAGEMENT TAB
# ============================================================
def render_customer_tab():
    st.subheader("Customer Management")

    with st.form("cust_form"):
        data = {
            "customer_name": st.text_input("Customer Name"),
            "customer_type": st.selectbox(
                "Customer Type",
                ["Individual", "Business", "Enterprise", "Government"]
            ),
            "email": st.text_input("Email"),
            "phone_number": st.text_input("Phone Number"),
            "company_name": st.text_input("Company Name"),
            "address": st.text_area("Address"),
            "city": st.text_input("City"),
            "state": st.text_input("State"),
            "country": st.text_input("Country"),
            "zip_code": st.text_input("Zip Code"),
            "industry": st.text_input("Industry (optional)"),
            "risk_rating": st.text_input("Risk Rating (optional)")
        }

        if st.form_submit_button("Add Customer"):
            try:
                add_customer(data)
                st.success("Customer added successfully.")
            except Exception as e:
                st.error(str(e))

    st.divider()
    st.subheader("Customer Records")

    customers = fetch_all_customers_full()
    if customers:
        df = pd.DataFrame(
            customers,
            columns=[
                "Customer ID",
                "Customer Name",
                "Customer Type",
                "Email",
                "Phone Number",
                "City",
                "State",
                "Country"
            ]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No customers found.")


# ============================================================
# INVOICE MANAGEMENT TAB
# ============================================================
def render_invoice_tab():
    st.subheader("Invoice Management")

    customers = fetch_customers()
    if not customers:
        st.info("No customers found. Add a customer first.")
        return

    customer_map = {c[1]: c[0] for c in customers}

    customer_name = st.selectbox(
        "Select Customer",
        ["-- Select --"] + list(customer_map.keys()),
        key="inv_customer"
    )

    if customer_name == "-- Select --":
        st.info("Select a customer to add an invoice.")
        return

    customer_id = customer_map[customer_name]

    with st.form("invoice_form"):
        invoice_number = st.text_input("Invoice Number")

        invoice_date = st.date_input("Invoice Date", key="invoice_date")

        if "inv_last_date" not in st.session_state:
            st.session_state.inv_last_date = invoice_date
            st.session_state.inv_due_date = invoice_date + timedelta(days=15)

        if invoice_date != st.session_state.inv_last_date:
            st.session_state.inv_due_date = invoice_date + timedelta(days=15)
            st.session_state.inv_last_date = invoice_date

        due_date = st.date_input(
            "Due Date (Auto +15 days, editable)",
            value=st.session_state.inv_due_date,
            key="invoice_due_date"
        )

        invoice_type = st.selectbox(
            "Invoice Type",
            ["Standard", "Tax", "Recurring", "Usage-Based", "Other"]
        )

        currency = st.text_input("Currency", value="INR",disabled=True)
        basic_amount = st.number_input("Basic Amount", min_value=0.0)
        tax_amount = st.number_input("Tax Amount", min_value=0.0)

        total_amount = basic_amount + tax_amount
        st.info(f"Invoice Total Amount: {total_amount}")

        payment_status = st.text_input("Payment Status", value="PENDING",disabled=True)
        # st.selectbox(
        #     "Payment Status",
        #     ["PENDING", "COMPLETED", "PARTIALLY_PAID"],
        #     index=0
        # )

        if st.form_submit_button("Add Invoice"):
            try:
                add_invoice({
                    "invoice_number": invoice_number,
                    "invoice_date": str(invoice_date),
                    "due_date": str(due_date),
                    "invoice_type": invoice_type,
                    "currency": currency,
                    "basic_amount": basic_amount,
                    "tax_amount": tax_amount,
                    "invoice_total_amount": total_amount,
                    "raw_invoice_text": None,
                    "payment_status": payment_status,
                    "customer_id": customer_id,
                    "customer_name": customer_name
                })
                st.success("Invoice added successfully.")
            except Exception as e:
                st.error(str(e))

    st.divider()
    st.subheader("Invoices")

    invoices = fetch_invoices(customer_id)
    if invoices:
        df = pd.DataFrame(
            invoices,
            columns=[
                "Invoice Number",
                "Invoice Date",
                "Due Date",
                "Invoice Type",
                "Invoice Amount",
                "Payment Status"
            ]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No invoices available.")


# ============================================================
# TRANSACTION MANAGEMENT TAB
# ============================================================
def render_transaction_tab():
    st.subheader("Transaction Management")

    customers = fetch_customers()
    if not customers:
        st.info("Please add customers first.")
        return

    customer_map = {c[1]: c[0] for c in customers}

    customer_name = st.selectbox(
        "Select Customer",
        ["-- Select --"] + list(customer_map.keys()),
        key="txn_customer"
    )

    if customer_name == "-- Select --":
        st.info("Select a customer to proceed.")
        return

    customer_id = customer_map[customer_name]

    invoices = fetch_open_invoices(customer_id)
    if not invoices:
        st.warning("No PENDING or PARTIALLY_PAID invoices for this customer.")
        return

    invoice_map = {inv[0]: inv[1] for inv in invoices}

    invoice_number = st.selectbox(
        "Linked Invoice",
        list(invoice_map.keys()),
        key="txn_invoice"
    )

    invoice_amount = invoice_map[invoice_number]
    st.text_input("Invoice Amount", value=str(invoice_amount), disabled=True)

    with st.form("txn_form"):
        transaction_date = st.date_input("Transaction Date")
        narration = st.text_area("Narration")

        amount = st.number_input("Transaction Amount", min_value=0.0)

        bank_name = st.selectbox(
            "Bank Name",
            [
                "ICICI", "SBI", "UCO", "HDFC", "AXIS", "CANARA", "IDFC", "OTHERS"
            ]
        )
        account_number = st.text_input("Account Number")

        payment_mode = st.selectbox(
            "Payment Mode",
            [
                "Cash", "Cheque", "Bank Transfer", "UPI",
                "Debit Card", "Credit Card", "Net Banking",
                "Wallet", "Payment Gateway", "Demand Draft", "NEFT"
            ]
        )

        currency = st.text_input("Currency", value="INR",disabled=True)

        reference_number = st.text_input("Reference Number")
        account_type = st.selectbox(
            "Account Type",
            [
                "Current", "Savings", "Others"
            ]
        )

        bank_charges = st.number_input("Bank Charges", min_value=0.0)
        tax_deducted = st.number_input("Tax Deducted", min_value=0.0)
        gateway_fee = st.number_input("Gateway Fee", min_value=0.0)
        forex_charges = st.number_input("Forex Charges", min_value=0.0)

        if st.form_submit_button("Add Transaction"):
            try:
                insert_transaction({
                    "transaction_date": str(transaction_date),
                    "narration": narration,
                    "amount": amount,
                    "bank_name": bank_name,
                    "reference_number": reference_number,
                    "account_number": account_number,
                    "account_type": account_type,
                    "payment_mode": payment_mode,
                    "currency": currency,
                    "bank_charges": bank_charges,
                    "tax_deducted": tax_deducted,
                    "gateway_fee": gateway_fee,
                    "forex_charges": forex_charges,
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "linked_invoice_id": invoice_number,
                    "invoice_amount": invoice_amount
                })
                st.success("Transaction added and invoice status updated.")
            except Exception as e:
                st.error(str(e))

    st.divider()
    st.subheader("Transactions")

    transactions = fetch_transactions(customer_id, invoice_number)
    if transactions:
        df = pd.DataFrame(
            transactions,
            columns=[
                "Transaction Date",
                "Amount",
                "currency",
                "Payment Mode",
                "Bank Name",
                "Linked Invoice"
            ]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No transactions found.")


# ============================================================
# DISPUTE & RECONCILIATION TAB
# ============================================================
def render_dispute_tab():
    import pandas as pd
    import streamlit as st

    from dispute.customer_service import fetch_customers
    from dispute.invoice_service import (
        fetch_invoices_by_customer,
        fetch_invoices_by_customer_and_date
    )
    from dispute.dispute_engine import analyze_invoices
    from dispute.reasoning_agent import generate_dispute_explanation

    st.subheader("Dispute & Reconciliation")

    # -----------------------------
    # Customer Selection (Mandatory)
    # -----------------------------
    customers = fetch_customers()
    if not customers:
        st.info("No customers available.")
        return

    customer_map = {c[1]: c[0] for c in customers}

    customer_name = st.selectbox(
        "Select Customer",
        ["-- Select --"] + list(customer_map.keys()),
        key="disp_customer"
    )

    if customer_name == "-- Select --":
        st.info("Please select a customer to proceed.")
        return

    customer_id = customer_map[customer_name]

    st.divider()

    # -----------------------------
    # Invoice Selection Mode
    # -----------------------------
    mode = st.radio(
        "Invoice Selection Mode",
        ["Date Range", "Specific Invoices"],
        horizontal=True
    )

    invoice_rows = []

    if mode == "Date Range":
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input("From Date")
        with col2:
            to_date = st.date_input("To Date")

        if from_date > to_date:
            st.error("From Date cannot be after To Date.")
            return

        invoice_rows = fetch_invoices_by_customer_and_date(
            customer_id,
            str(from_date),
            str(to_date)
        )

    else:
        all_invoices = fetch_invoices_by_customer(customer_id)
        invoice_numbers = [i[0] for i in all_invoices]

        selected = st.multiselect(
            "Select Invoice Numbers",
            invoice_numbers
        )

        invoice_rows = [i for i in all_invoices if i[0] in selected]

    if not invoice_rows:
        st.warning("No invoices found for the selected criteria.")
        return

    # -----------------------------
    # Deterministic Analysis
    # -----------------------------
    analysis = analyze_invoices(invoice_rows)
    # df = pd.DataFrame(analysis)
    analysis_for_table = []

    for row in analysis:
        clean_row = row.copy()
        clean_row.pop("transactions", None)  # remove nested list
        analysis_for_table.append(clean_row)

    df = pd.DataFrame(analysis_for_table)

    # -----------------------------
    # Output: Tables
    # -----------------------------
    st.subheader("Invoice vs Transaction Summary")
    # st.dataframe(df, use_container_width=True)
    df_display = df.copy()

    df_display["invoice_total_amount"] = df_display["invoice_total_amount"].apply(format_inr)
    df_display["paid_amount"] = df_display["paid_amount"].apply(format_inr)
    df_display["outstanding_amount"] = df_display["outstanding_amount"].apply(format_inr)

    st.dataframe(df_display, use_container_width=True)

    # -----------------------------
    # Visuals
    # -----------------------------
    st.subheader("Invoice Amount vs Paid Amount")
    chart_df = df[["invoice_number", "invoice_total_amount", "paid_amount"]]
    st.bar_chart(
        chart_df.set_index("invoice_number")
    )

    st.subheader("Outstanding Balance Overview")
    st.bar_chart(
        df.set_index("invoice_number")["outstanding_amount"]
    )

    # -----------------------------
    # Categorized Insights
    # -----------------------------
    st.subheader("Reconciliation Breakdown")

    st.markdown("**Fully Reconciled Invoices**")
    st.dataframe(df[df["status"] == "COMPLETED"])

    st.markdown("**Partially Reconciled Invoices**")
    st.dataframe(df[df["status"] == "PARTIALLY_PAID"])

    st.markdown("**Pending / Missing Payments**")
    st.dataframe(df[df["status"] == "PENDING"])

    
    # -----------------------------
    # Narrative Explanation
    # -----------------------------
    st.subheader("Reconciliation Summary Explanation")

    explanation_text = generate_dispute_explanation(
        customer_name=customer_name,
        analysis_rows=analysis
    )

    # --- FORCE INR SYMBOL IN EXPLANATION TEXT ---
    explanation_text = explanation_text.replace("$", "₹")

    st.write(explanation_text)

    # -----------------------------
    # Footer
    # -----------------------------
    st.divider()
    st.caption(
        "For further enquiries, please contact:\n\n"
        "**hr@company.com**"
    )



# ============================================================
# MAIN ENTRY POINT
# ============================================================
def render_dispute_ui():
    init_dispute_tables()

    st.title("⚖️ Dispute Analysis")

    cust_tab, inv_tab, txn_tab, disp_tab = st.tabs([
        "Customer Management",
        "Invoice Management",
        "Transaction Management",
        "Dispute & Reconciliation"
    ])

    with cust_tab:
        render_customer_tab()

    with inv_tab:
        render_invoice_tab()

    with txn_tab:
        render_transaction_tab()

    with disp_tab:
        render_dispute_tab()
