# scripts/fix_form_ids.py
# Run: python scripts/fix_form_ids.py
import sys, os, glob, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import get_schemes_collection, get_db

schemes_col = get_schemes_collection()
db = get_db()
fields_col = db["form_fields"]

# Get all scheme_ids still needing fix
real_ids = set(str(s["_id"]) for s in schemes_col.find({}, {"_id": 1}))
all_ids = fields_col.distinct("scheme_id")
broken_ids = set(sid for sid in all_ids if sid not in real_ids)

print(f"scheme_ids needing fix: {len(broken_ids)}")
for sid in sorted(broken_ids):
    print(f"  {sid}")

# Pre-load all schemes into memory for safe matching
all_schemes = list(schemes_col.find({}, {"_id": 1, "name": 1}))

def find_scheme_by_name(name):
    """Exact match first, then escaped regex match."""
    # Try exact match
    for s in all_schemes:
        if s["name"].strip().lower() == name.strip().lower():
            return s
    # Try escaped regex on first 30 chars
    prefix = re.escape(name[:30])
    for s in all_schemes:
        if re.search(prefix, s["name"], re.IGNORECASE):
            return s
    return None

fixed_total = 0
remaining = set(broken_ids)

for path in sorted(glob.glob("data/forms/*.json")):
    # Try multiple encodings
    data = None
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            with open(path, "r", encoding=enc) as f:
                data = json.load(f)
            break
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

    if data is None:
        print(f"  SKIP (could not read): {os.path.basename(path)}")
        continue

    sid = data.get("scheme_id")
    if sid not in remaining:
        continue

    form_name = data.get("scheme_name", "")
    print(f"\n  File: {os.path.basename(path)}")
    print(f"  scheme_id={sid}, scheme_name='{form_name}'")

    if not form_name:
        print(f"  SKIP - no scheme_name in file")
        continue

    real_scheme = find_scheme_by_name(form_name)

    if real_scheme:
        real_id = str(real_scheme["_id"])
        print(f"  Matched: '{real_scheme['name']}' -> {real_id}")
        result = fields_col.update_many(
            {"scheme_id": sid},
            {"$set": {"scheme_id": real_id}}
        )
        print(f"  Updated {result.modified_count} fields!")
        fixed_total += result.modified_count
        remaining.discard(sid)
    else:
        print(f"  WARNING: No MongoDB match for '{form_name}'")

# Report remaining unmatched
if remaining:
    print(f"\n=== Unmatched IDs (no JSON file found or no name match) ===")
    for sid in remaining:
        count = fields_col.count_documents({"scheme_id": sid})
        print(f"  '{sid}': {count} fields")

print(f"\n=== Done. Total fields fixed this run: {fixed_total} ===")

# Final verification
print("\n=== Final field counts per scheme ===")
for s in all_schemes:
    count = fields_col.count_documents({"scheme_id": str(s["_id"])})
    status = "OK" if count > 0 else "MISSING"
    print(f"  [{status}] {s['name']}: {count} fields")

print("\n=== KCC specifically ===")
kcc = schemes_col.find_one({"name": {"$regex": "Kisan Credit", "$options": "i"}})
if kcc:
    count = fields_col.count_documents({"scheme_id": str(kcc["_id"])})
    print(f"KCC fields in DB: {count}")