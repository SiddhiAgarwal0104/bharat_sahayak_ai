# backend/main.py — temp version (Member 4 owns the final)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.db.database import connect_db, close_db
from backend.models.user import User, UserSession
from backend.routers.auth_router import router as auth_router
from backend.routers.stt_router import router as stt_router

app = FastAPI(title="SahayakAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(stt_router)
app.include_router(stt_router)
from backend.services.nlp_service import router as nlp_router
app.include_router(nlp_router)

@app.on_event("startup")
async def startup():
    # As other members add their models, Member 4 adds them here
    await connect_db(document_models=[User, UserSession])

@app.on_event("shutdown")
async def shutdown():
    await close_db()

@app.get("/health")
def health():
    return {"status": "ok", "db": "MongoDB Atlas"}