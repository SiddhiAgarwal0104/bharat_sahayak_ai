# scripts/fix_json_scheme_ids.py
# This fixes JSON files whose filename IS the correct scheme_id
# but whose internal scheme_id field is wrong or missing.

import json, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

fixed = 0
skipped = 0

for path in glob.glob("data/forms/*.json"):
    filename = os.path.basename(path)
    name_without_ext = filename.replace(".json", "")

    # Only process files whose filename looks like a MongoDB ObjectId (24 hex chars)
    if len(name_without_ext) != 24 or not all(c in "0123456789abcdef" for c in name_without_ext):
        print(f"  Skipping (not an ObjectId filename): {filename}")
        skipped += 1
        continue

    correct_id = name_without_ext

    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            with open(path, "r", encoding=enc) as f:
                data = json.load(f)
            break
        except:
            data = None

    if data is None:
        print(f"  ERROR reading: {filename}")
        continue

    current_id = data.get("scheme_id", "")
    fields_count = len(data.get("fields", []))

    print(f"  {filename}: internal scheme_id='{current_id}', fields={fields_count}")

    if current_id != correct_id:
        data["scheme_id"] = correct_id
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"    FIXED: {current_id} -> {correct_id}")
        fixed += 1
    else:
        print(f"    OK (already correct)")

print(f"\nDone. Fixed {fixed} files, skipped {skipped}.")
print("Now run: python scripts/seed_forms.py")