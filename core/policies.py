POLICIES = [

    # -----------------------
    # FOOD & MEALS
    # -----------------------
    ("Food", "Meals", "Daily meal expense", 2000, "Food only, no liquor", "daily"),
    # ("Food", "Liquor", "Liquor expenses", 0, "Strictly prohibited"),

    # -----------------------
    # TRAVEL
    # -----------------------
    ("Travel", "Cab", "Local cab travel", 1500, "Within city limits","daily"),
    # ("Travel", "Taxi", "Outstation taxi", 5000, "Manager approval required"),
    ("Travel", "Train", "Train travel", 5000, "AC 2-tier maximum","total"),
    ("Travel", "Flight", "Flight travel", 20000, "Economy class only","total"),

    # -----------------------
    # ACCOMMODATION
    # -----------------------
    ("Accommodation", "Hotel", "Hotel stay", 5000, "3-star hotels only","daily"),
    # ("Accommodation", "Guest House", "Guest house stay", 3000, "Company-approved only"),

    # -----------------------
    # EDUCATION & LEARNING
    # -----------------------
    ("Education", "Online Course", "Online learning programs", 15000, "Job-related courses only","total"),
    ("Education", "Workshop", "Workshops & seminars", 20000, "Pre-approval mandatory","total"),
    ("Education", "Books", "Books & study material", 3000, "Technical / professional books only","monthly"),

    # -----------------------
    # UTILITIES
    # -----------------------
    ("Utilities", "Internet", "Internet bill reimbursement", 2000, "Single active connection","monthly"),

    # -----------------------
    # HOUSEHOLD / SUPPORT
    # -----------------------
    ("Household", "Laundry", "Laundry services", 2000, "Reimbursable for business travel","daily"),
    ("Household", "Driver", "Driver services", 5000, "Pre-approval mandatory","monthly"),

    # -----------------------
    # IT / CLOUD / SOFTWARE
    # -----------------------
    ("IT", "Cloud", "Cloud infrastructure usage", 20000, "Project and cost-center approved","monthly"),
    ("IT", "SaaS", "SaaS / software subscriptions", 20000, "Business tools only","monthly"),

    # -----------------------
    # CORPORATE
    # -----------------------
    ("Corporate", "Events", "Corporate events & offsites", 50000, "HR approval required","total"),

    ("Statutory", "Tax", "Statutory taxes", float("inf"), "Always allowed","total")
]
