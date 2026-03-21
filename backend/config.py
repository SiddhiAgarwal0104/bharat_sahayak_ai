# backend/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# ── Plain variables (your existing code) ─────────────────────────
MONGODB_URL     = os.getenv("MONGO_URL",    "mongodb://localhost:27017")
MONGODB_DB      = os.getenv("MONGO_DB",     "sahayak")
JWT_SECRET      = os.getenv("JWT_SECRET",   "changeme")
MODEL_PATH      = os.getenv("MODEL_PATH",   "data/model")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501")
HF_TOKEN        = os.getenv("HF_TOKEN",     "")
HF_MODEL_REPO   = os.getenv("HF_MODEL_REPO", "")
BACKEND_URL     = os.getenv("BACKEND_URL",  "http://localhost:8000")


# ── Settings object — required by Member 1's auth_router ─────────
class Settings:
    def __init__(self):
        self.MONGO_URL       = MONGODB_URL
        self.MONGO_DB        = MONGODB_DB
        self.JWT_SECRET      = JWT_SECRET
        self.MODEL_PATH      = MODEL_PATH
        self.HF_TOKEN        = HF_TOKEN
        self.HF_MODEL_REPO   = HF_MODEL_REPO
        self.BACKEND_URL     = BACKEND_URL
        self.ALLOWED_ORIGINS = ALLOWED_ORIGINS

settings = Settings()
