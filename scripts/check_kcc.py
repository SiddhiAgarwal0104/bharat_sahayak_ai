from backend.db.database import get_schemes_collection, get_db
import re

col = get_schemes_collection()

# Find KCC scheme (case-insensitive)
kcc = col.find_one({"name": {"$regex": "KCC", "$options": "i"}})
print("KCC scheme:", kcc)

if kcc:
    db = get_db()
    fields_col = db["form_fields"]
    count = fields_col.count_documents({"scheme_id": str(kcc["_id"])})
    print("KCC fields in DB:", count)
else:
    # Show all scheme names so we can find the right one
    print("\nNo KCC found. All scheme names in DB:")
    for s in col.find({}, {"name": 1}):
        print(" -", s.get("name"), "| id:", str(s["_id"]))