"""
test_parser.py
--------------
Test the PDF parser on all scheme PDFs in data/schemes/.
Run this FIRST before seeding to verify extraction quality.

Usage:
    python scripts/test_parser.py
    python scripts/test_parser.py health_ayushman_bharat_guidelines.pdf
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.pdf_parser import extract_scheme_info

PDF_FOLDER = "data/schemes"

# ── Which files to test ───────────────────────────────────────────────────────
if len(sys.argv) > 1:
    # Test a specific file
    files = [sys.argv[1]]
else:
    # Test all guidelines PDFs
    all_files = os.listdir(PDF_FOLDER)
    files = sorted([f for f in all_files if "guidelines" in f and f.endswith(".pdf")])

if not files:
    print(f"No guidelines PDFs found in {PDF_FOLDER}/")
    print("Check that your PDFs have 'guidelines' in the filename.")
    sys.exit(1)

print(f"\nTesting {len(files)} PDF(s)...\n")

for filename in files:
    path = os.path.join(PDF_FOLDER, filename)
    if not os.path.exists(path):
        path = filename   # maybe absolute path was given

    print("=" * 60)
    print(f"FILE: {filename}")
    print("=" * 60)

    try:
        info = extract_scheme_info(path)
    except Exception as e:
        print(f"ERROR: {e}")
        continue

    print(f"Name:     {info['name']}")
    print(f"Category: {info['category']}")
    print(f"\nDescription (first 300 chars):")
    print(f"  {info['description'][:300]}")

    print(f"\nEligibility:")
    for k, v in info["eligibility_criteria"].items():
        if v is not None and v is not False:
            print(f"  {k}: {v}")

    print(f"\nBenefits (first 200 chars):")
    print(f"  {info['benefits'][:200] if info['benefits'] else 'Not found'}")

    print(f"\nDocs needed (first 200 chars):")
    print(f"  {info['docs_needed'][:200] if info['docs_needed'] else 'Not found'}")

    print(f"\nRaw text length: {len(info['raw_text'])} chars")
    print()

print("\nDone. If any fields look wrong, edit backend/utils/pdf_parser.py")
print("and re-run this test until results look good.")
print("\nNext step: python backend/db/seed_schemes.py")
