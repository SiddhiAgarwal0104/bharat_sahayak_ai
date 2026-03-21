"""
main.py  —  MongoDB version
-----------------------------
FastAPI entry point. Member 3's standalone dev server.

Run:
    uvicorn backend.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.scheme_router import router as scheme_router
from backend.db.vector_store import load_index

app = FastAPI(
    title="BharatSahayakAI — Scheme Search API",
    description="Member 3 — Search Agent + MongoDB",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scheme_router)


@app.on_event("startup")
def startup():
    print("[startup] Loading FAISS index ...")
    try:
        load_index()
        print("[startup] FAISS index ready.")
    except FileNotFoundError:
        print("[startup] WARNING: FAISS index not found.")
        print("[startup] Run  python backend/db/seed_schemes.py  first.")


@app.get("/health")
def health():
    return {"status": "ok", "service": "BharatSahayakAI Member 3"}


@app.get("/")
def root():
    return {
        "message": "BharatSahayakAI Scheme Search API",
        "docs":    "http://localhost:8000/docs",
    }
