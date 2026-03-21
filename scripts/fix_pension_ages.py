"""
Place at: scripts/fix_pension_ages.py
Run: python scripts/fix_pension_ages.py
"""
from backend.db.database import get_schemes_collection

col = get_schemes_collection()

# Pension schemes should have realistic minimum ages
# A 20-year-old should NOT see pension schemes
pension_fixes = [
    ("NPS",             50),  # National Pension System - near retirement
    ("Unified Pension", 50),  # UPS - government employees near retirement
    ("Atal Pension",    40),  # APY - for unorganised sector workers, min meaningful age
    ("EPF",             55),  # EPF withdrawal - near retirement
]

print("Fixing pension minimum ages...\n")
for keyword, min_age in pension_fixes:
    r = col.update_many(
        {"name": {"$regex": keyword, "$options": "i"}},
        {"$set": {"eligibility_criteria.min_age": min_age}}
    )
    if r.modified_count:
        print(f"  {keyword}: min_age set to {min_age} ({r.modified_count} updated)")
    else:
        print(f"  {keyword}: no match")

# Fix Women category - SMAM, PMKSY, PMFBY should be agriculture not women
agriculture_fixes = ["SMAM", "PMKSY", "PMFBY", "Mechanization", "Sinchayee", "Fasal Bima", "Kisan"]
print("\nRe-fixing agriculture categories...")
for kw in agriculture_fixes:
    r = col.update_many(
        {"name": {"$regex": kw, "$options": "i"}},
        {"$set": {"category": "agriculture"}}
    )
    if r.modified_count:
        print(f"  {kw} -> agriculture ({r.modified_count})")

# Verify final state
print("\nFinal eligibility_criteria for pension schemes:")
for doc in col.find({"category": "pension"}, {"name": 1, "eligibility_criteria": 1}):
    crit = doc.get("eligibility_criteria", {})
    print(f"  {doc['name']}: min_age={crit.get('min_age')}, max_age={crit.get('max_age')}")

print("\nCategory counts:")
for cat in ["health", "pension", "agriculture", "women"]:
    print(f"  {cat}: {col.count_documents({'category': cat})}")