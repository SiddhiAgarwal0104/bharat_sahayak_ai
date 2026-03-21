
"""
embedding_service.py
--------------------
Loads the multilingual sentence-transformer model and exposes
encode() and encode_batch() functions.

Member 3 owns this file.

Model: paraphrase-multilingual-MiniLM-L12-v2
- Supports Hindi, English, Tamil, Telugu, Bengali, Marathi and 50+ languages
- ~400 MB download on first run (cached after that)
- Produces 384-dimensional vectors
"""

import numpy as np
from sentence_transformers import SentenceTransformer

# ── Load model ONCE at module level ──────────────────────────────────────────
# NEVER move this inside encode() or encode_batch() — it would reload the
# entire 400 MB model on every API call, making the app unusably slow.
print("[embedding_service] Loading multilingual model...")
try:
    _MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
except Exception:
    _MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", local_files_only=True)
print("[embedding_service] Model loaded.")

EMBEDDING_DIM = 384   # output dimension of this model


def encode(text: str) -> np.ndarray:
    """
    Encode a single string (user query) into a 384-dim float32 vector.

    Args:
        text: any string, any language

    Returns:
        numpy array of shape (384,), normalized (unit length)
    """
    if not text or not text.strip():
        # Return zero vector for empty input — won't match anything
        return np.zeros(EMBEDDING_DIM, dtype="float32")

    vec = _MODEL.encode(
        [text],
        normalize_embeddings=True,   # unit length → cosine sim = dot product
        show_progress_bar=False,
    )
    return vec[0].astype("float32")


def encode_batch(texts: list) -> np.ndarray:
    """
    Encode a list of strings (scheme descriptions) in one efficient batch.
    Used only during seeding — not during live queries.

    Args:
        texts: list of strings

    Returns:
        numpy array of shape (len(texts), 384), each row normalized
    """
    if not texts:
        return np.zeros((0, EMBEDDING_DIM), dtype="float32")

    vecs = _MODEL.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,   # shows progress bar when seeding 24 schemes
        batch_size=16,
    )
    return vecs.astype("float32")


