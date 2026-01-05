from langchain_core.prompts import PromptTemplate
from core.llm_factory import get_llm
from core.db import get_cursor
from core.document_parser import extract_text
from core.json_utils import safe_json_loads

PROMPT = """
You are an expert enterprise finance document parser.

Your task is to extract structured data from ALL types of receipts and invoices,
including:
- Retail receipts
- Service invoices
- Cloud / IT / SaaS billing receipts (AWS, Azure, GCP, Oracle, SAP)

========================
OUTPUT FORMAT (STRICT)
========================
Return ONLY valid JSON.
Do NOT add explanations.
Do NOT add markdown.
Use null if a value is truly missing.

========================
HEADER FIELDS
========================
Extract the following under "header":
- "Number of days"
  number of days for which the product or item or food was consumed as per the invoice. You have to calulate this from the date and other stuff.If number of days is not mentioned explicityly, kindly give 1 as default output.

- "GST Number"
  Synonyms: GSTIN, GST No, GST Number

- "Receipt Number"
  Synonyms: Receipt Number, Invoice Number, Bill Number

- "Document Type"
  One of: Receipt | Invoice | Bill

- "Date"
  Synonyms: Receipt Date, Invoice Date, Date of Issue

- "Vendor Name"
  Synonyms: Issued By, Seller, Service Provider, Company Name

- "Buyer Name"
  Synonyms: Billed To, Customer, Client, Account Holder

- "Vendor Address"
  Address near Issued By / Seller section

- "Bill Type"
  Classify as one of:
  Food | Travel | Accommodation | Education | Utilities | IT | Cloud | SaaS | Corporate | Other

- "Total Amount"
  Synonyms: Total Amount Charged, Total Payable, Grand Total

- "Tax Amount"
  If CGST/SGST/IGST are present, return their SUM.



========================
LINE ITEMS
========================
Extract "line_items" as a list.

Each line item must include:
- description
- quantity (number or null)
- unit_price (number or null)
- total_amount (number or null)


IMPORTANT FOR CLOUD / IT RECEIPTS:
- Usage-based rows (e.g., EC2 hours, data transfer, metrics) ARE valid line items.
- Quantity may be usage units (hours, GB, TB-month).
- If unit price is shown, extract it.
- If only total amount is shown, set unit_price = null.

========================
SPECIAL CLOUD RULES
========================
- AWS, Azure, GCP receipts MUST be classified as Bill Type = "IT" or "Cloud".
- Do NOT ignore service usage tables.
- Do NOT return null if values are clearly present.

========================
INPUT DOCUMENT
========================
Receipt Text:
{receipt_text}

"""

def analyze_receipt(file_path, llm_provider):
    raw_text = extract_text(file_path)
    llm = get_llm(llm_provider)

    prompt = PromptTemplate(
        template=PROMPT,
        input_variables=["receipt_text"]
    )

    response = llm.invoke(prompt.format(receipt_text=raw_text))

    try:
        parsed = safe_json_loads(response.content)
    except Exception as e:
        parsed = {
            "header": {},
            "line_items": [],
            "error": str(e),
            "raw_llm_output": response.content
        }

    header = parsed.get("header", {})
    line_items = parsed.get("line_items", [])

    with get_cursor() as cur:
        cur.execute("""
        INSERT INTO receipts (
            gst_number, receipt_number, document_type, receipt_date,
            vendor_name, buyer_name, vendor_address, bill_type,
            total_amount, tax_amount, raw_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            header.get("GST Number"),
            header.get("Receipt Number"),
            header.get("Document Type"),
            header.get("Date"),
            header.get("Vendor Name"),
            header.get("Buyer Name"),
            header.get("Vendor Address"),
            header.get("Bill Type"),
            header.get("Total Amount"),
            header.get("Tax Amount"),
            raw_text
        ))

        receipt_id = cur.lastrowid

    return {
        "receipt_id": receipt_id,
        "receipt_data": {
            "header": header,
            "line_items": line_items
        }
    }
