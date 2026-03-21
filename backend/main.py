# backend/main.py
# Combined: Member 1 (auth, STT) + Member 2 (NLP) + Member 3 (schemes, search)
# Member 4 will add form_router and orchestrator on top of this

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.db.database import connect_db, close_db
from backend.db.vector_store import load_index

app = FastAPI(
    title="BharatSahayakAI",
    description="Combined API — Members 1 + 2 + 3",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Member 1 routers ──────────────────────────────────────────────────────────
try:
    from backend.routers.auth_router import router as auth_router
    app.include_router(auth_router)
except Exception as e:
    print(f"[main] auth_router not loaded: {e}")

try:
    from backend.routers.stt_router import router as stt_router
    app.include_router(stt_router)
except Exception as e:
    print(f"[main] stt_router not loaded: {e}")

# ── Member 2 routers ──────────────────────────────────────────────────────────
try:
    from backend.services.nlp_service import router as nlp_router
    app.include_router(nlp_router)
except Exception as e:
    print(f"[main] nlp_router not loaded: {e}")

try:
    from backend.routers.query_router import router as query_router
    app.include_router(query_router)
except Exception as e:
    print(f"[main] query_router not loaded: {e}")

# ── Member 3 routers ──────────────────────────────────────────────────────────
try:
    from backend.routers.scheme_router import router as scheme_router
    app.include_router(scheme_router)
except Exception as e:
    print(f"[main] scheme_router not loaded: {e}")

# ── Member 4 routers (added later) ───────────────────────────────────────────
# from backend.routers.form_router import router as form_router
# app.include_router(form_router)


# ── Startup / Shutdown ────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    # Connect MongoDB with Beanie for async models (users, sessions)
    try:
        from backend.models.user import User, UserSession
        await connect_db(document_models=[User, UserSession])
    except Exception as e:
        print(f"[startup] Beanie init skipped: {e}")

    # Load FAISS index for scheme search (Member 3)
    try:
        load_index()
        print("[startup] FAISS index ready.")
    except FileNotFoundError:
        print("[startup] WARNING: FAISS index not found.")
        print("[startup] Run: python backend/db/seed_schemes.py")


@app.on_event("shutdown")
async def shutdown():
    await close_db()


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "db": "MongoDB Atlas", "service": "BharatSahayakAI"}


@app.get("/")
def root():
    return {
        "message": "BharatSahayakAI API",
        "docs":    "http://localhost:8000/docs",
        "members": {
            "1": "auth, STT",
            "2": "NLP, profile, eligibility",
            "3": "schemes, search, embeddings",
            "4": "forms, orchestrator (coming soon)",
        }
    }
