"""
test_search_agent.py
--------------------
Unit tests for Member 3's search components.

Run with:
    python -m pytest tests/test_search_agent.py -v
"""

import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Embedding service tests ───────────────────────────────────────────────────

class TestEmbeddingService:

    def test_encode_english(self):
        from backend.services.embedding_service import encode, EMBEDDING_DIM
        vec = encode("health insurance scheme")
        assert vec.shape == (EMBEDDING_DIM,), f"Expected ({EMBEDDING_DIM},), got {vec.shape}"
        assert abs(sum(vec ** 2) - 1.0) < 1e-4, "Vector should be normalized (unit length)"

    def test_encode_hindi(self):
        from backend.services.embedding_service import encode, EMBEDDING_DIM
        vec = encode("स्वास्थ्य बीमा योजना")   # "health insurance scheme" in Hindi
        assert vec.shape == (EMBEDDING_DIM,)

    def test_encode_empty(self):
        from backend.services.embedding_service import encode, EMBEDDING_DIM
        import numpy as np
        vec = encode("")
        assert vec.shape == (EMBEDDING_DIM,)
        assert np.all(vec == 0), "Empty input should return zero vector"

    def test_encode_batch(self):
        from backend.services.embedding_service import encode_batch, EMBEDDING_DIM
        texts = ["health scheme", "pension plan", "kisan yojana"]
        vecs = encode_batch(texts)
        assert vecs.shape == (3, EMBEDDING_DIM)


# ── PDF parser tests ──────────────────────────────────────────────────────────

class TestPdfParser:

    def test_get_category_health(self):
        from backend.utils.pdf_parser import _get_category
        assert _get_category("health_ayushman.pdf") == "health"

    def test_get_category_pension(self):
        from backend.utils.pdf_parser import _get_category
        assert _get_category("pension_nps_guidelines.pdf") == "pension"

    def test_get_category_agriculture(self):
        from backend.utils.pdf_parser import _get_category
        assert _get_category("agriculture_pm_kisan.pdf") == "agriculture"

    def test_get_category_women(self):
        from backend.utils.pdf_parser import _get_category
        assert _get_category("women_beti_bachao.pdf") == "women"

    def test_eligibility_gender_women(self):
        from backend.utils.pdf_parser import _extract_eligibility
        text = "This scheme is for women only. Eligible applicants must be female."
        criteria = _extract_eligibility(text)
        assert criteria["gender"] == "F"

    def test_eligibility_age(self):
        from backend.utils.pdf_parser import _extract_eligibility
        text = "Applicant age should be between 18 to 60 years of age."
        criteria = _extract_eligibility(text)
        assert criteria["min_age"] == 18
        assert criteria["max_age"] == 60

    def test_eligibility_pwd(self):
        from backend.utils.pdf_parser import _extract_eligibility
        text = "This scheme is exclusively for divyang persons with disability."
        criteria = _extract_eligibility(text)
        assert criteria["pwd_only"] is True

    def test_eligibility_caste(self):
        from backend.utils.pdf_parser import _extract_eligibility
        text = "Applicants belonging to Scheduled Caste, Scheduled Tribe and OBC are eligible."
        criteria = _extract_eligibility(text)
        assert "SC" in criteria["caste"]
        assert "ST" in criteria["caste"]
        assert "OBC" in criteria["caste"]

    def test_eligibility_defaults_null(self):
        from backend.utils.pdf_parser import _extract_eligibility
        text = "Any citizen of India can apply for this scheme."
        criteria = _extract_eligibility(text)
        assert criteria["min_age"] is None
        assert criteria["max_age"] is None
        assert criteria["gender"] is None
        assert criteria["max_income"] is None


# ── Vector store tests ────────────────────────────────────────────────────────

class TestVectorStore:

    def test_build_index(self):
        import numpy as np
        from backend.db.vector_store import build_index
        embeddings = np.random.rand(5, 384).astype("float32")
        index = build_index(embeddings)
        assert index.ntotal == 5

    def test_search_returns_correct_count(self):
        import numpy as np
        from backend.services.embedding_service import encode
        from backend.db.vector_store import build_index, search as vs_search

        # Build a small in-memory index
        texts = ["health insurance", "pension scheme", "farming subsidy", "women education", "crop insurance"]
        from backend.services.embedding_service import encode_batch
        embeddings = encode_batch(texts)

        # Temporarily override the global index
        import backend.db.vector_store as vstore
        vstore._index = build_index(embeddings)

        query_vec = encode("health")
        results = vs_search(query_vec, candidate_ids=[0, 1, 2, 3, 4], top_k=3)
        assert len(results) <= 3
        assert all("embedding_id" in r and "score" in r for r in results)

        # Restore
        vstore._index = None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
