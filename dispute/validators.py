import re

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PHONE_REGEX = r"^\d{7,15}$"
ZIP_REGEX = r"^\d{4,10}$"

def validate_customer(data: dict):
    required = [
        "customer_name","customer_type","email","phone_number",
        "company_name","address","city","state","country","zip_code"
    ]

    for k in required:
        if not data.get(k):
            raise ValueError(f"{k} is mandatory")

    if not re.match(EMAIL_REGEX, data["email"]):
        raise ValueError("Invalid email format")

    if not re.match(PHONE_REGEX, data["phone_number"]):
        raise ValueError("Invalid phone number")

    if not re.match(ZIP_REGEX, data["zip_code"]):
        raise ValueError("Invalid zip code")
