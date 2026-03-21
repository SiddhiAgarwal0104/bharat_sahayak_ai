"""
Run once to fix eligibility_criteria for all schemes.
Place this file in: bharat_sahayak_ai/scripts/fix_eligibility.py
Run with: python scripts/fix_eligibility.py
(from project root with PYTHONPATH set)
"""

from backend.db.database import get_schemes_collection

col = get_schemes_collection()

updates = [
    # EPF Pension Withdrawal — retirement age employees
    ("EPF Pension",      {"min_age": 50, "max_age": None, "gender": None, "max_income": None, "caste": None, "pwd_only": False}),

    # NPS (National Pension System) — working age
    ("NPS",              {"min_age": 18, "max_age": 65,   "gender": None, "max_income": None, "caste": None, "pwd_only": False}),

    # Mahila Shakti Kendra / Mission Shakti — women only
    ("Mahila Shakti",    {"min_age": 18, "max_age": None, "gender": "F",  "max_income": None, "caste": None, "pwd_only": False}),
    ("Mission Shakti",   {"min_age": 18, "max_age": None, "gender": "F",  "max_income": None, "caste": None, "pwd_only": False}),

    # RBSK — children up to 18
    ("RBSK",             {"min_age": 0,  "max_age": 18,   "gender": None, "max_income": None, "caste": None, "pwd_only": False}),
    ("Bal Swasthya",     {"min_age": 0,  "max_age": 18,   "gender": None, "max_income": None, "caste": None, "pwd_only": False}),

    # PMMVY — pregnant/lactating women
    ("Matru Vandana",    {"min_age": 19, "max_age": 45,   "gender": "F",  "max_income": None, "caste": None, "pwd_only": False}),
    ("PMMVY",            {"min_age": 19, "max_age": 45,   "gender": "F",  "max_income": None, "caste": None, "pwd_only": False}),

    # PM Kisan — farmers, any age adult
    ("Kisan",            {"min_age": 18, "max_age": None, "gender": None, "max_income": None, "caste": None, "pwd_only": False}),

    # Ayushman Bharat — low income families
    ("Ayushman",         {"min_age": 0,  "max_age": None, "gender": None, "max_income": 500000, "caste": None, "pwd_only": False}),

    # Scholarship schemes — students
    ("Scholarship",      {"min_age": 14, "max_age": 30,   "gender": None, "max_income": 250000, "caste": None, "pwd_only": False}),
    ("Chatravriti",      {"min_age": 14, "max_age": 30,   "gender": None, "max_income": 250000, "caste": None, "pwd_only": False}),

    # Ujjwala — women BPL
    ("Ujjwala",          {"min_age": 18, "max_age": None, "gender": "F",  "max_income": 200000, "caste": None, "pwd_only": False}),

    # Sukanya Samriddhi — girl child
    ("Sukanya",          {"min_age": 0,  "max_age": 10,   "gender": "F",  "max_income": None,   "caste": None, "pwd_only": False}),

    # MGNREGA — rural adults
    ("MGNREGA",          {"min_age": 18, "max_age": None, "gender": None, "max_income": None,   "caste": None, "pwd_only": False}),
    ("Rozgar",           {"min_age": 18, "max_age": None, "gender": None, "max_income": None,   "caste": None, "pwd_only": False}),
]

print("Starting eligibility update...\n")
total_updated = 0

for keyword, criteria in updates:
    result = col.update_many(
        {"name": {"$regex": keyword, "$options": "i"}},
        {"$set": {"eligibility_criteria": criteria}}
    )
    if result.modified_count > 0:
        print(f"  ✓ '{keyword}': updated {result.modified_count} scheme(s)")
        total_updated += result.modified_count
    else:
        print(f"  - '{keyword}': no match found")

print(f"\nDone! Total schemes updated: {total_updated}")
print("\nSchemes still with null criteria (need manual check):")
remaining = col.find({
    "$or": [
        {"eligibility_criteria.min_age": None},
        {"eligibility_criteria": {"$exists": False}}
    ]
}, {"name": 1})
for doc in remaining:
    print(f"  → {doc['name']}")