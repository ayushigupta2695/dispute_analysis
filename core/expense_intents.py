# core/expense_intents.py
# -------------------------------------------------
# GENERIC, DOMAIN-AGNOSTIC EXPENSE INTENTS
# -------------------------------------------------
from typing import Optional

INTENT_KEYWORDS = {
    "FOOD_CONSUMPTION": [
        "food", "meal", "breakfast", "lunch", "dinner",
        "paneer", "roti", "dal", "rice", "pulav", "pulao",
        "khichdi", "salad", "water", "mineral", "papad",
        "tikka", "curry", "sabzi", "naan", "paratha"
    ],

    "LODGING": [
        "room", "stay", "night", "accommodation", "suite"
    ],

    "PERSONAL_SERVICE": [
        "laundry", "dry clean", "driver", "cleaning"
    ],

    "CLOUD_COMPUTE": [
        "aws", "ec2", "rds", "s3", "cloud",
        "compute", "storage", "bandwidth",
        "data transfer", "cloudwatch", "guardduty"
    ],

    "SOFTWARE_SUBSCRIPTION": [
        "license", "subscription", "saas", "software"
    ],

    "BUSINESS_EVENT": [
        "conference", "seminar", "workshop", "event"
    ],

    "GAMBLING": [
        "casino", "poker", "bet", "gambling"
    ],

    "ALCOHOL_ENTERTAINMENT": [
        "bar", "pub", "liquor", "wine", "beer"
    ],

    "STATUTORY_TAX": [
        "cgst", "sgst", "igst", "gst"
    ],
    "TRAVEL": ["cab", "taxi", "transport", "uber", "ola"],
}


# -------------------------------------------------
# INTENT → POLICY CATEGORY (ALIGNS WITH DB)
# -------------------------------------------------

INTENT_TO_POLICY = {
    "FOOD_CONSUMPTION": "Food",
    "LODGING": "Accommodation",
    "PERSONAL_SERVICE": "Household",
    "CLOUD_COMPUTE": "IT",
    "SOFTWARE_SUBSCRIPTION": "IT",
    "BUSINESS_EVENT": "Corporate",
    "STATUTORY_TAX": "Statutory",
    "TRAVEL" : "Travel",
    # Hard stops
    "GAMBLING": "UNSUPPORTED",
    "ALCOHOL_ENTERTAINMENT": "UNSUPPORTED"
}


# def detect_intent(description: str) -> str | None:
def detect_intent(description: str) -> Optional[str]:
    if not description:
        return None

    desc = description.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in desc for k in keywords):
            return intent
    return None


# def intent_to_policy(intent: str | None) -> str:
def intent_to_policy(intent: Optional[str]) -> str:
    if not intent:
        return "UNSUPPORTED"
    return INTENT_TO_POLICY.get(intent, "UNSUPPORTED")
