# ⚖️ AI-Powered Dispute & Reconciliation System

## Project Overview

The **AI-Powered Dispute & Reconciliation System** is a finance-focused application designed to **analyze invoice payment discrepancies**, **reconcile transactions**, and **generate audit-ready explanations** using a hybrid approach:

* **Deterministic financial computation** for accuracy
* **LLM-based reasoning** for scalable, human-readable explanations

The system ensures **data integrity, audit safety, and scalability**, even when invoices have **hundreds of associated transactions**.

---

## Key Objectives

* Provide a structured workflow for:

  * Customer management
  * Invoice management
  * Transaction tracking
  * Dispute & reconciliation analysis
* Maintain **clear separation** between:

  * Raw data (tables)
  * Analytical computation
  * Narrative explanation
* Generate **explanation-first outputs** without repeating transactional tables
* Ensure the solution remains usable at enterprise scale

---

## Core Capabilities

### 1. Customer Management

* Create and manage customers with validation
* Capture business, contact, and risk metadata
* Acts as the master entity for all downstream data

### 2. Invoice Management

* Create invoices linked to customers
* Store:

  * Basic amount
  * Tax amount
  * Total invoice amount
  * Currency
  * Payment status
* Supports multiple invoice types (standard, tax, recurring, etc.)

### 3. Transaction Management

* Record one or more transactions per invoice
* Supports:

  * Partial payments
  * Multiple payment modes
  * Bank charges
  * Tax deductions
  * Gateway fees
  * Forex charges
* Automatically updates invoice payment status:

  * `PENDING`
  * `PARTIALLY_PAID`
  * `COMPLETED`

### 4. Dispute & Reconciliation Analysis

* Compare invoice totals vs received payments
* Supports invoice selection via:

  * Date range
  * Specific invoice numbers
* Displays:

  * Invoice vs paid vs outstanding tables
  * Visual summaries (bar charts)
* Generates **LLM-based narrative explanations**:

  * One section per invoice
  * Pattern-level transaction analysis
  * No raw transaction repetition
  * Audit-friendly, neutral language

---

## Architecture Overview

```
Streamlit UI
   |
   |-- Customer Management
   |-- Invoice Management
   |-- Transaction Management
   |-- Dispute & Reconciliation
          |
          |-- Deterministic Engine (Python)
          |-- LLM Reasoning Layer (Groq)
```

### Design Philosophy

| Layer                | Responsibility                            |
| -------------------- | ----------------------------------------- |
| Database             | Stores raw financial facts                |
| Deterministic Engine | Computes paid, outstanding, and status    |
| LLM Reasoning Agent  | Explains relationships and outcomes       |
| UI                   | Displays tables + explanations separately |

> **The LLM never recalculates numbers.**
> **The system never hides data.**

---

## Technology Stack

* **Frontend / UI**: Streamlit
* **Backend**: Python
* **Database**: SQLite
* **LLM Provider**: Groq
* **PDF Parsing**: pdfplumber
* **Data Handling**: Pandas
* **Environment Management**: python-dotenv

---

## Project Structure

```
project-root/
│
├── app.py
│
├── core/
│   ├── db.py
│   ├── agent_graph.py
│   ├── policy_loader.py
│   └── llm_factory.py
│
├── dispute/
│   ├── db.py
│   ├── ui.py
│   ├── customer_service.py
│   ├── invoice_service.py
│   ├── transaction_service.py
│   ├── dispute_engine.py
│   ├── reasoning_agent.py
│   ├── validators.py
│   └── statement_parser.py
│
├── finance_agents.db
├── .env
└── README.md
```

---

## How Dispute Reasoning Works

1. **Invoices and transactions are fetched**
2. **Deterministic logic computes**:

   * Paid amount
   * Outstanding amount
   * Invoice status
3. **All data is passed to the LLM**
4. **LLM produces a summary-only explanation**:

   * Reviews all transactions internally
   * Explains patterns (not rows)
   * Mentions charges and currency observations
   * Produces one section per invoice

### Important Guarantee

* Tables are shown **only in the UI**
* Explanations are **table-free and scalable**
* Works even when an invoice has **hundreds of transactions**

---

## Environment Setup

### 1. Create `.env` file

```
GROQ_API_KEY=your_groq_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

---

## Validation & Safety Rules

* No recalculation by the LLM
* No inference of missing values
* No currency conversion
* No assumptions beyond provided data
* Explanation is neutral, factual, and audit-friendly

---

## Current Scope

### In Scope

* Customer, invoice, and transaction management
* Deterministic reconciliation
* LLM-based narrative explanation
* Visual summaries

### Out of Scope

* This is only POC

---

## Intended Use Cases

* Invoice payment disputes
* Partial payment analysis
* Audit preparation
* Finance operations review
* POC for AI-assisted finance reconciliation

---

## Disclaimer

This project is a **proof of concept** intended to demonstrate:

* Finance-safe AI reasoning
* Explainable reconciliation workflows
* Scalable narrative generation

It is **not a replacement** for statutory accounting systems.
