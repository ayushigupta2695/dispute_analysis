import pandas as pd
import pdfplumber
import tempfile

def parse_statement(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    if file.name.endswith(".pdf"):
        rows = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                rows.extend(page.extract_table()[1:])
        return pd.DataFrame(rows)
    raise ValueError("Unsupported format")
