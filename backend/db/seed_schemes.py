"""
seed_schemes.py  —  MongoDB version
-------------------------------------
Run ONCE to:
1. Parse all guidelines PDFs in data/schemes/
2. Save each scheme to MongoDB
3. Build the FAISS vector index
4. Save the index to data/embeddings/schemes.index

Usage (from project root):
    python backend/db/seed_schemes.py
"""

import os
import json
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import get_schemes_collection
from backend.models.scheme import scheme_document
from backend.utils.pdf_parser import extract_scheme_info
from backend.services.embedding_service import encode_batch
from backend.db.vector_store import build_index, save_index

# ── Paths ─────────────────────────────────────────────────────────────────────
PDF_FOLDER      = "data/schemes"
LINKS_FILE      = "data/form_links.json"
CLOUDINARY_FILE = "data/cloudinary_index.json"

# ── Load reference data ───────────────────────────────────────────────────────
print("Loading form_links.json ...")
with open(LINKS_FILE) as f:
    raw_links = json.load(f)["schemes"]

# Map guidelines PDF filename → scheme metadata
links_map = {s["guidelines_pdf"]: s for s in raw_links}

print("Loading cloudinary_index.json ...")
if not os.path.exists(CLOUDINARY_FILE):
    print("WARNING: cloudinary_index.json not found — PDF URLs will be empty.")
    cdn_urls = {}
else:
    with open(CLOUDINARY_FILE) as f:
        cdn_urls = json.load(f)

# ── Collect guidelines PDFs listed in form_links.json ────────────────────────
# Only process PDFs that are referenced as guidelines in form_links.json
guidelines_files = []
for s in raw_links:
    gf = s["guidelines_pdf"]
    path = os.path.join(PDF_FOLDER, gf)
    if os.path.exists(path):
        guidelines_files.append(gf)
    else:
        print(f"  WARNING: guidelines PDF not found: {gf}")

if not guidelines_files:
    print(f"No matching guidelines PDFs found in {PDF_FOLDER}/")
    sys.exit(1)

# Remove duplicates while preserving order
seen = set()
unique_guidelines = []
for f in guidelines_files:
    if f not in seen:
        seen.add(f)
        unique_guidelines.append(f)

print(f"\nFound {len(unique_guidelines)} unique guidelines PDFs to process:")
for f in unique_guidelines:
    print(f"  - {f}")

# ── Parse each PDF ────────────────────────────────────────────────────────────
print("\nParsing PDFs ...")
parsed = []

for filename in unique_guidelines:
    pdf_path = os.path.join(PDF_FOLDER, filename)
    print(f"  Parsing: {filename}")

    info = extract_scheme_info(pdf_path)

    link_info     = links_map.get(filename, {})
    form_pdf_name = link_info.get("form_pdf", "")

    info["form_url"]           = link_info.get("form_url", "")
    info["guidelines_pdf_url"] = cdn_urls.get(filename, "")
    info["form_pdf_url"]       = cdn_urls.get(form_pdf_name, "")

    # Use name from form_links.json — more accurate than PDF extraction
    if link_info.get("name"):
        info["name"] = link_info["name"]

    parsed.append(info)
    print(f"    Name:     {info['name'][:60]}")
    print(f"    Category: {info['category']}")

# ── Encode descriptions ───────────────────────────────────────────────────────
print(f"\nEncoding {len(parsed)} descriptions into vectors ...")
texts = [p.get("raw_text") or p["description"] for p in parsed]
embeddings = encode_batch(texts)
print(f"Embeddings shape: {embeddings.shape}")

# ── Save to MongoDB ───────────────────────────────────────────────────────────
col = get_schemes_collection()

print("\nClearing existing schemes from MongoDB ...")
col.delete_many({})

print("Saving schemes to MongoDB ...")
docs = []
for i, info in enumerate(parsed):
    doc = scheme_document(
        name                 = info["name"][:299],
        category             = info["category"],
        description          = info["description"],
        eligibility_criteria = info["eligibility_criteria"],
        benefits             = info["benefits"],
        docs_needed          = info["docs_needed"],
        form_url             = info["form_url"],
        guidelines_pdf_url   = info["guidelines_pdf_url"],
        form_pdf_url         = info["form_pdf_url"],
        embedding_id         = i,
    )
    docs.append(doc)

result = col.insert_many(docs)
print(f"Saved {len(result.inserted_ids)} schemes to MongoDB.")

# ── Build FAISS index ─────────────────────────────────────────────────────────
print("\nBuilding FAISS index ...")
index = build_index(np.array(embeddings, dtype="float32"))
save_index(index)

# ── Summary ───────────────────────────────────────────────────────────────────
count = col.count_documents({})
print("\n" + "="*55)
print("SEEDING COMPLETE")
print("="*55)
print(f"  Schemes in MongoDB:   {count}")
print(f"  Vectors in index:     {index.ntotal}")
print(f"  Index saved to:       data/embeddings/schemes.index")
print("\nNext step:")
print("  uvicorn backend.main:app --reload")
