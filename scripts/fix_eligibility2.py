

from backend.db.database import get_schemes_collection

col = get_schemes_collection()

updates = [
    # Janani Suraksha Yojana — pregnant women, low income
    ("Janani Suraksha Yojana",
     {"min_age": 19, "max_age": 45, "gender": "F", "max_income": 200000, "caste": None, "pwd_only": False}),

    # Atal Pension Yojana — working adults, not income tax payers
    ("Atal Pension Yojana",
     {"min_age": 18, "max_age": 40, "gender": None, "max_income": None, "caste": None, "pwd_only": False}),

    # Unified Pension Scheme — government employees
    ("Unified Pension Scheme",
     {"min_age": 18, "max_age": 60, "gender": None, "max_income": None, "caste": None, "pwd_only": False}),

    # Pradhan Mantri Fasal Bima Yojana — farmers
    ("Pradhan Mantri Fasal Bima",
     {"min_age": 18, "max_age": None, "gender": None, "max_income": None, "caste": None, "pwd_only": False}),

    # Pradhan Mantri Krishi Sinchayee Yojana — farmers
    ("Krishi Sinchayee",
     {"min_age": 18, "max_age": None, "gender": None, "max_income": None, "caste": None, "pwd_only": False}),

    # Sub-Mission on Agricultural Mechanization — farmers
    ("Agricultural Mechanization",
     {"min_age": 18, "max_age": None, "gender": None, "max_income": None, "caste": None, "pwd_only": False}),

    # Working Women Hostel (Sakhi Niwas) — working women
    ("Working Women Hostel",
     {"min_age": 18, "max_age": None, "gender": "F", "max_income": 50000, "caste": None, "pwd_only": False}),

    ("Sakhi Niwas",
     {"min_age": 18, "max_age": None, "gender": "F", "max_income": 50000, "caste": None, "pwd_only": False}),
]

print("Fixing remaining schemes...\n")
total = 0

for keyword, criteria in updates:
    result = col.update_many(
        {"name": {"$regex": keyword, "$options": "i"}},
        {"$set": {"eligibility_criteria": criteria}}
    )
    if result.modified_count > 0:
        print(f"  ✓ '{keyword}': updated {result.modified_count} scheme(s)")
        total += result.modified_count
    else:
        print(f"  - '{keyword}': no match found (check name in Atlas)")

print(f"\nDone! Total updated: {total}")

# Final check — any still null?
print("\nStill null (should be empty now):")
remaining = list(col.find(
    {"eligibility_criteria.min_age": None},
    {"name": 1}
))
if remaining:
    for doc in remaining:
        print(f"  → {doc['name']}")
else:
    print("  All schemes have eligibility criteria! ✓")