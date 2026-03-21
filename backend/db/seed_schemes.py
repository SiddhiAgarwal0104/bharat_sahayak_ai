# backend/db/seed_schemes.py
# Member 3 owns this file — run ONCE to load PDFs into MongoDB + build FAISS index
# Usage: python backend/db/seed_schemes.py

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

PDF_FOLDER      = "data/schemes"
LINKS_FILE      = "data/form_links.json"
CLOUDINARY_FILE = "data/cloudinary_index.json"

print("Loading form_links.json ...")
with open(LINKS_FILE) as f:
    raw_links = json.load(f)["schemes"]

links_map = {s["guidelines_pdf"]: s for s in raw_links}

print("Loading cloudinary_index.json ...")
cdn_urls = {}
if os.path.exists(CLOUDINARY_FILE):
    with open(CLOUDINARY_FILE) as f:
        cdn_urls = json.load(f)
else:
    print("WARNING: cloudinary_index.json not found — PDF URLs will be empty.")

# ── Collect unique guidelines PDFs ───────────────────────────────────────────
seen, unique_guidelines = set(), []
for s in raw_links:
    gf   = s["guidelines_pdf"]
    path = os.path.join(PDF_FOLDER, gf)
    if gf not in seen and os.path.exists(path):
        seen.add(gf)
        unique_guidelines.append(gf)
    elif not os.path.exists(path):
        print(f"  WARNING: PDF not found — {gf}")

if not unique_guidelines:
    print(f"No guidelines PDFs found in {PDF_FOLDER}/")
    sys.exit(1)

print(f"\nFound {len(unique_guidelines)} guidelines PDFs:")
for f in unique_guidelines:
    print(f"  - {f}")

# ── Parse PDFs ────────────────────────────────────────────────────────────────
print("\nParsing PDFs ...")
parsed = []
for filename in unique_guidelines:
    pdf_path  = os.path.join(PDF_FOLDER, filename)
    print(f"  Parsing: {filename}")
    info      = extract_scheme_info(pdf_path)
    link_info = links_map.get(filename, {})

    info["form_url"]           = link_info.get("form_url", "")
    info["guidelines_pdf_url"] = cdn_urls.get(filename, "")
    info["form_pdf_url"]       = cdn_urls.get(link_info.get("form_pdf", ""), "")
    if link_info.get("name"):
        info["name"] = link_info["name"]

    parsed.append(info)
    print(f"    Name:     {info['name'][:60]}")
    print(f"    Category: {info['category']}")

# ── Encode ────────────────────────────────────────────────────────────────────
print(f"\nEncoding {len(parsed)} descriptions ...")
texts      = [p.get("raw_text") or p["description"] for p in parsed]
embeddings = encode_batch(texts)
print(f"Shape: {embeddings.shape}")

# ── Save to MongoDB ───────────────────────────────────────────────────────────
col = get_schemes_collection()
print("\nClearing existing schemes ...")
col.delete_many({})

docs = []
for i, info in enumerate(parsed):
    docs.append(scheme_document(
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
    ))

result = col.insert_many(docs)
print(f"Saved {len(result.inserted_ids)} schemes to MongoDB.")

# ── Build FAISS index ─────────────────────────────────────────────────────────
print("\nBuilding FAISS index ...")
index = build_index(np.array(embeddings, dtype="float32"))
save_index(index)

count = col.count_documents({})
print("\n" + "="*50)
print("SEEDING COMPLETE")
print("="*50)
print(f"  Schemes in MongoDB : {count}")
print(f"  Vectors in index   : {index.ntotal}")
print(f"  Index path         : data/embeddings/schemes.index")
print("\nNext: uvicorn backend.main:app --reload")
