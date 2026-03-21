"""
search_agent.py  —  MongoDB version
-------------------------------------
Core search logic. Member 3 owns this file.
"""

from backend.services.embedding_service import encode
from backend.db.vector_store import search as faiss_search
from backend.db.database import get_schemes_collection
from backend.models.scheme import format_scheme


class SearchAgent:

    def search(self, intent_obj: dict, candidate_ids: list) -> list:
        """
        intent_obj:    { query_text, language, intent, slots }
        candidate_ids: list of embedding_ids eligible for this user
                       (from Member 2's profile agent).
                       Empty list = search all schemes.
        Returns: list of up to 3 scheme dicts, best match first.
        """
        query_text = intent_obj.get("query_text", "")
        intent     = intent_obj.get("intent", "")

        col = get_schemes_collection()

        # ── Resolve eligible embedding_ids ────────────────────────────────────
        if candidate_ids:
            # Only schemes the user is eligible for
            docs = list(col.find(
                {"embedding_id": {"$in": candidate_ids}},
                {"embedding_id": 1}
            ))
        else:
            # No filter — search all (home page / fallback)
            docs = list(col.find({}, {"embedding_id": 1}))

        eligible_embedding_ids = [
            d["embedding_id"] for d in docs
            if d.get("embedding_id") is not None
        ]

        if not eligible_embedding_ids:
            return []

        # ── Enrich query with intent ──────────────────────────────────────────
        enriched_query = query_text
        if intent and intent.lower() not in query_text.lower():
            enriched_query = f"{intent} {query_text}"

        # ── Encode + FAISS search ─────────────────────────────────────────────
        query_vec    = encode(enriched_query)
        raw_results  = faiss_search(query_vec, eligible_embedding_ids, top_k=3)

        if not raw_results:
            return self._category_fallback(intent, col)

        # ── Fetch full scheme docs from MongoDB ───────────────────────────────
        final_results = []
        for i, r in enumerate(raw_results):
            doc = col.find_one({"embedding_id": r["embedding_id"]})
            if doc:
                scheme = format_scheme(doc)
                scheme["match_score"]   = round(r["score"], 4)
                scheme["is_best_match"] = (i == 0)
                final_results.append(scheme)

        return final_results

    # ── Fallback: return top schemes by category ──────────────────────────────
    def _category_fallback(self, intent: str, col) -> list:
        category_map = {
            "health":      "health",
            "pension":     "pension",
            "agriculture": "agriculture",
            "farmer":      "agriculture",
            "women":       "women",
        }
        target = category_map.get(intent.lower(), "")
        query  = {"category": target} if target else {}
        docs   = list(col.find(query).limit(3))

        results = []
        for i, doc in enumerate(docs):
            scheme = format_scheme(doc)
            scheme["match_score"]   = 0.5
            scheme["is_best_match"] = (i == 0)
            results.append(scheme)
        return results
