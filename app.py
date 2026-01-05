import streamlit as st
import tempfile
import os
import json
from dotenv import load_dotenv

# ------------------------------
# EXISTING IMPORTS (UNCHANGED)
# ------------------------------
from core.db import (
    init_db,
    fetch_all_receipts,
    fetch_receipt_details,
    fetch_policies,
    insert_policy,
    delete_policy,
    fetch_validation_logs
)
from core.policy_loader import load_policies
from core.agent_graph import finance_graph

# ------------------------------
# DISPUTE MODULE
# ------------------------------
from dispute.ui import render_dispute_ui

# -------------------------------------------------
# Environment
# -------------------------------------------------
load_dotenv()

assert os.getenv("GROQ_API_KEY"), "GROQ_API_KEY missing"
assert os.getenv("LANGSMITH_API_KEY"), "LANGSMITH_API_KEY missing"

# -------------------------------------------------
# Init (UNCHANGED)
# -------------------------------------------------
init_db()

with open("load_policy_state.txt", "r") as f:
    load_policy_state = f.read().strip()

if load_policy_state == "False":
    load_policies()
    st.session_state.policies_loaded = True

st.set_page_config(layout="wide")
st.title("📄 AI Dispute Analysis System")

# =================================================
# ✅ TOP-LEVEL TABS (ONLY TWO)
# =================================================
# tab_receipt_analysis, tab_dispute_analysis = st.tabs(
#     ["🚀 Receipt Analysis", "⚖️ Dispute Analysis"]
# )
tab_dispute_analysis = st.tabs(
    ["⚖️ Dispute Analysis"]
)[0]

# # =================================================
# # TAB 1: RECEIPT ANALYSIS (UNCHANGED LOGIC)
# # =================================================
# with tab_receipt_analysis:

#     # ---- Existing internal tabs (UNCHANGED) ----
#     tab_run, tab_receipts, tab_policies, tab_logs = st.tabs(
#         ["🚀 Run Validation", "📂 Receipts", "📜 Policies", "🧾 Validation Logs"]
#     )

#     # -------------------------------
#     # Run Validation
#     # -------------------------------
#     with tab_run:
#         llm_provider = st.selectbox(
#             "Choose LLM Provider",
#             ["groq"]
#         )

#         uploaded = st.file_uploader(
#             "Upload Receipt (PDF or DOCX)",
#             type=["pdf", "docx"]
#         )

#         if uploaded:
#             suffix = uploaded.name.split(".")[-1]
#             with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
#                 tmp.write(uploaded.read())
#                 file_path = tmp.name

#             if st.button("Run End-to-End Validation"):
#                 result = finance_graph.invoke({
#                     "file_path": file_path,
#                     "llm_provider": llm_provider
#                 })

#                 st.subheader("📄 Extracted Receipt Data")
#                 st.json(result["receipt_data"])

#                 st.subheader("⚠️ Validation Decision")
#                 st.json(result["validation"])

#                 st.success(f"Receipt stored with ID: {result['receipt_id']}")

#     # -------------------------------
#     # Receipts Viewer
#     # -------------------------------
#     with tab_receipts:
#         st.subheader("📂 Stored Receipts")

#         receipts = fetch_all_receipts()

#         if not receipts:
#             st.info("No receipts found.")
#         else:
#             for r in receipts:
#                 title = (
#                     f"Receipt ID {r['id']} | "
#                     f"₹{r['total_amount']} | "
#                     f"{r['bill_type']} | "
#                     f"{r['created_at']}"
#                 )

#                 with st.expander(title):
#                     details = fetch_receipt_details(r["id"])
#                     st.json(details)

#     # -------------------------------
#     # Policies Manager
#     # -------------------------------
#     with tab_policies:
#         st.subheader("📜 Company Policies")

#         policies = fetch_policies()

#         for p in policies:
#             cols = st.columns([4, 2, 2, 2, 1])
#             cols[0].write(f"**{p[1]} / {p[2]}** — {p[3]}")
#             cols[1].write(f"₹{p[4]}")
#             cols[2].write(p[5])
#             cols[3].write(p[6])
#             if cols[4].button("❌", key=f"del_{p[0]}"):
#                 delete_policy(p[0])
#                 st.success("Policy deleted successfully")

#         st.divider()
#         st.subheader("➕ Add New Policy")

#         with st.form("add_policy_form"):
#             category = st.text_input("Category")
#             sub_category = st.text_input("Sub-category")
#             rule = st.text_input("Rule")
#             max_amount = st.number_input("Max Amount", min_value=0.0)
#             conditions = st.text_input("Conditions")
#             limit_frequency = st.text_input("Limit Frequency")

#             submitted = st.form_submit_button("Add Policy")

#             if submitted:
#                 insert_policy(
#                     category,
#                     sub_category,
#                     rule,
#                     max_amount,
#                     conditions,
#                     limit_frequency
#                 )
#                 st.session_state.policy_added = True

#         if st.session_state.get("policy_added"):
#             st.success("Policy added successfully")
#             del st.session_state["policy_added"]

#     # -------------------------------
#     # Validation Logs
#     # -------------------------------
#     with tab_logs:
#         st.subheader("🧾 Validation Logs")

#         logs = fetch_validation_logs()

#         if not logs:
#             st.info("No validation logs available.")
#         else:
#             for log in logs:
#                 with st.expander(f"Receipt ID {log[0]} | {log[1]}"):
#                     st.json(json.loads(log[2]))
#                     st.caption(log[3])

# =================================================
# TAB 2: DISPUTE ANALYSIS (ISOLATED)
# =================================================
with tab_dispute_analysis:
    render_dispute_ui()
