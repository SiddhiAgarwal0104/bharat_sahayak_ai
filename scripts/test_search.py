"""
test_search.py
--------------
Test the full search pipeline end-to-end WITHOUT needing the FastAPI server.

Usage:
    python scripts/test_search.py
    python scripts/test_search.py "kisan subsidy for farmers"
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.embedding_service import encode
from backend.db.vector_store import load_index, search
from backend.agents.search_agent import SearchAgent
from backend.db.database import SessionLocal
from backend.models.scheme import Scheme

# ── Check index exists ────────────────────────────────────────────────────────
INDEX_PATH = "data/embeddings/schemes.index"
if not os.path.exists(INDEX_PATH):
    print(f"ERROR: Index not found at {INDEX_PATH}")
    print("Run  python backend/db/seed_schemes.py  first.")
    sys.exit(1)

# ── Load index ────────────────────────────────────────────────────────────────
print("Loading FAISS index...")
load_index()

# ── Check DB has schemes ──────────────────────────────────────────────────────
db = SessionLocal()
count = db.query(Scheme).count()
db.close()
print(f"Schemes in DB: {count}")

if count == 0:
    print("ERROR: No schemes in DB. Run seed_schemes.py first.")
    sys.exit(1)

# ── Test queries ──────────────────────────────────────────────────────────────
test_queries = [
    sys.argv[1] if len(sys.argv) > 1 else None,
    "health insurance for poor family",
    "pension for senior citizens",
    "subsidy for farmers agriculture",
    "scheme for women and girls",
    "kisan yojana kheti",            # Hindi agriculture query
    "swasthya bima yojana",          # Hindi health query
]

# Remove None and duplicates
test_queries = list(dict.fromkeys([q for q in test_queries if q]))

agent = SearchAgent()

for query in test_queries:
    print("\n" + "─" * 50)
    print(f"Query: '{query}'")
    print("─" * 50)

    intent_obj = {
        "query_text": query,
        "language":   "auto",
        "intent":     "",
        "slots":      {},
    }

    # Search all schemes (no candidate filtering in test)
    results = agent.search(intent_obj, candidate_ids=[])

    if not results:
        print("  No results returned.")
    else:
        for i, r in enumerate(results):
            badge = "★ BEST" if r.get("is_best_match") else f"  #{i+1}"
            print(f"\n  {badge}  {r['name']}")
            print(f"         Category: {r['category']}")
            print(f"         Score:    {r.get('match_score', 0):.4f}")
            print(f"         Benefits: {str(r.get('benefits',''))[:100]}")

print("\n\nAll tests done.")
print("If results look wrong, re-check pdf_parser.py extraction quality.")
