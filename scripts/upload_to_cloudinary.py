"""
upload_to_cloudinary.py
-----------------------
Run ONCE to upload all PDFs from data/schemes/ to Cloudinary.
Saves every filename → URL mapping to data/cloudinary_index.json.

Usage:
    python scripts/upload_to_cloudinary.py

Requirements:
    - .env file with CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
    - pip install cloudinary python-dotenv
"""

import os
import json
import sys

# Allow imports from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cloudinary
import cloudinary.uploader
from backend.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

# ── Configure Cloudinary ──────────────────────────────────────────────────────
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

PDF_FOLDER      = "data/schemes"
OUTPUT_JSON     = "data/cloudinary_index.json"

# Load existing index if it exists (so re-running doesn't re-upload everything)
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON) as f:
        results = json.load(f)
    print(f"Loaded existing index with {len(results)} entries.")
else:
    results = {}

# ── Upload each PDF ───────────────────────────────────────────────────────────
pdf_files = sorted([f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")])

if not pdf_files:
    print(f"No PDFs found in {PDF_FOLDER}/")
    print("Make sure you have copied your scheme PDFs into that folder.")
    sys.exit(1)

print(f"\nFound {len(pdf_files)} PDFs. Uploading to Cloudinary...\n")

for filename in pdf_files:
    if filename in results:
        print(f"  Skipping (already uploaded): {filename}")
        continue

    path = os.path.join(PDF_FOLDER, filename)
    print(f"  Uploading: {filename} ...")

    try:
        response = cloudinary.uploader.upload(
            path,
            resource_type="raw",              # PDFs are raw files, not images
            public_id=f"sahayak_pdfs/{filename}",
            overwrite=True,
            use_filename=True,
        )
        url = response["secure_url"]
        results[filename] = url
        print(f"    Done → {url[:80]}...")

    except Exception as e:
        print(f"    ERROR uploading {filename}: {e}")
        print("    Check your Cloudinary credentials in .env")

# ── Save results ──────────────────────────────────────────────────────────────
with open(OUTPUT_JSON, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nAll done. {len(results)} URLs saved to {OUTPUT_JSON}")
print("You can now run: python backend/db/seed_schemes.py")
