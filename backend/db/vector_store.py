# backend/db/vector_store.py
# Member 3 owns this file — FAISS index management

import os
import numpy as np
import faiss

INDEX_PATH = "data/embeddings/schemes.index"
_index: faiss.Index = None


def build_index(embeddings: np.ndarray) -> faiss.Index:
    embeddings = embeddings.astype("float32")
    dim        = embeddings.shape[1]
    index      = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"[vector_store] Built index — {index.ntotal} vectors (dim={dim})")
    return index


def save_index(index: faiss.Index, path: str = INDEX_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    faiss.write_index(index, path)
    print(f"[vector_store] Saved → {path}")


def load_index(path: str = INDEX_PATH) -> faiss.Index:
    global _index
    if _index is None:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"FAISS index not found at '{path}'. "
                "Run: python backend/db/seed_schemes.py"
            )
        _index = faiss.read_index(path)
        print(f"[vector_store] Loaded from {path} ({_index.ntotal} vectors)")
    return _index


def get_index() -> faiss.Index:
    global _index
    if _index is None:
        return load_index()
    return _index


def search(query_vector: np.ndarray, candidate_ids: list, top_k: int = 3) -> list:
    index         = get_index()
    if index.ntotal == 0:
        return []

    candidate_set = set(candidate_ids)
    k             = min(index.ntotal, max(top_k * 10, 30))
    query         = query_vector.reshape(1, -1).astype("float32")
    scores, ids   = index.search(query, k)

    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx < 0:
            continue
        if idx in candidate_set:
            results.append({"embedding_id": int(idx), "score": float(score)})
        if len(results) == top_k:
            break
    return results


def reset_index():
    global _index
    _index = None
