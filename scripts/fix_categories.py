"""
Place at: scripts/fix_categories.py
Run: python scripts/fix_categories.py
"""
from backend.db.database import get_schemes_collection

col = get_schemes_collection()

fixes = [
    ("SMAM",         "agriculture"),
    ("Mechanization","agriculture"),
    ("PMKSY",        "agriculture"),
    ("Sinchayee",    "agriculture"),
    ("Fasal Bima",   "agriculture"),
    ("PMFBY",        "agriculture"),
    ("Kisan",        "agriculture"),
    ("Ujjwala",      "women"),
    ("Sukanya",      "women"),
    ("Mahila",       "women"),
    ("Matru",        "women"),
    ("Janani",       "women"),
    ("Working Women","women"),
    ("NPS",          "pension"),
    ("Atal Pension", "pension"),
    ("EPF",          "pension"),
    ("Unified Pension","pension"),
    ("Ayushman",     "health"),
    ("RBSK",         "health"),
]

for kw, cat in fixes:
    r = col.update_many(
        {"name": {"$regex": kw, "$options": "i"}},
        {"$set": {"category": cat}}
    )
    if r.modified_count:
        print(f"  {kw} -> {cat}: {r.modified_count} updated")

print("\nCategory distribution now:")
for cat in ["health", "pension", "agriculture", "women", "other"]:
    count = col.count_documents({"category": cat})
    print(f"  {cat}: {count}")