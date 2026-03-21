"""
vector_store.py
---------------
Manages the FAISS vector index for scheme similarity search.
Member 3 owns this file.

FAISS IndexFlatIP = exact inner product search.
Since embeddings are normalized, inner product == cosine similarity.
Higher score = more similar.
"""

import os
import numpy as np
import faiss

INDEX_PATH = "data/embeddings/schemes.index"

# Global index — loaded once at app startup, reused for all queries
_index: faiss.Index = None


# ── Build + Save ─────────────────────────────────────────────────────────────

def build_index(embeddings: np.ndarray) -> faiss.Index:
    """
    Build a FAISS flat inner-product index from a numpy embedding matrix.

    Args:
        embeddings: shape (n_schemes, 384), float32, normalized

    Returns:
        faiss.IndexFlatIP ready for search
    """
    embeddings = embeddings.astype("float32")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"[vector_store] Built index with {index.ntotal} vectors (dim={dim})")
    return index


def save_index(index: faiss.Index, path: str = INDEX_PATH):
    """Save FAISS index to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    faiss.write_index(index, path)
    print(f"[vector_store] Index saved → {path}")


# ── Load ──────────────────────────────────────────────────────────────────────

def load_index(path: str = INDEX_PATH) -> faiss.Index:
    """
    Load FAISS index from disk into memory.
    Called once at FastAPI startup. Subsequent calls return the cached index.
    """
    global _index
    if _index is None:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"FAISS index not found at '{path}'. "
                "Run  python backend/db/seed_schemes.py  first."
            )
        _index = faiss.read_index(path)
        print(f"[vector_store] Index loaded from {path} ({_index.ntotal} vectors)")
    return _index


def get_index() -> faiss.Index:
    """Return already-loaded index (call load_index first)."""
    global _index
    if _index is None:
        return load_index()
    return _index


# ── Search ────────────────────────────────────────────────────────────────────

def search(
    query_vector: np.ndarray,
    candidate_ids: list,
    top_k: int = 3,
) -> list:
    """
    Search the FAISS index but only return results whose embedding_id
    is in candidate_ids (the eligible schemes from Member 2's profile agent).

    Args:
        query_vector:  shape (384,), float32, normalized
        candidate_ids: list of embedding_ids (ints) that are eligible for this user
        top_k:         how many results to return (default 3)

    Returns:
        list of dicts: [{ "embedding_id": int, "score": float }, ...]
        sorted by score descending (best match first)
    """
    index = get_index()

    if index.ntotal == 0:
        return []

    # Convert candidate_ids to a set for O(1) lookup
    candidate_set = set(candidate_ids)

    # Search broader than top_k so we have candidates to filter from
    k = min(index.ntotal, max(top_k * 10, 30))

    query = query_vector.reshape(1, -1).astype("float32")
    scores, ids = index.search(query, k)

    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx < 0:
            continue   # FAISS returns -1 for empty slots
        if idx in candidate_set:
            results.append({
                "embedding_id": int(idx),
                "score":        float(score),
            })
        if len(results) == top_k:
            break

    return results


def reset_index():
    """Force reload index from disk (useful after re-seeding)."""
    global _index
    _index = None
