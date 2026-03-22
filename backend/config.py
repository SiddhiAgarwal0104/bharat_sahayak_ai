# backend/config.py
# Combined: Member 3 (MongoDB/Cloudinary) + Member 1+2 (Settings object, JWT, STT)

import os
from dotenv import load_dotenv

load_dotenv()

# ── Raw variables ─────────────────────────────────────────────────────────────
MONGO_URL     = os.getenv("MONGO_URL",    "mongodb://localhost:27017")
MONGO_DB      = os.getenv("MONGO_DB",     "sahayak")
JWT_SECRET    = os.getenv("JWT_SECRET",   "changeme_secret_key")
JWT_ALGORITHM = "HS256"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_PATH    = os.getenv("MODEL_PATH",   "data/model")
BACKEND_URL   = os.getenv("BACKEND_URL",  "http://localhost:8000")
HF_TOKEN      = os.getenv("HF_TOKEN",     "")
HF_MODEL_REPO = os.getenv("HF_MODEL_REPO", "")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501")

# Cloudinary — Member 3
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY    = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")


# ── Settings object — required by Member 1's auth_router + database.py ───────
class Settings:
    def __init__(self):
        self.MONGO_URL            = MONGO_URL
        self.MONGO_DB             = MONGO_DB
        self.JWT_SECRET           = JWT_SECRET
        self.JWT_ALGORITHM        = JWT_ALGORITHM
        self.MODEL_PATH           = MODEL_PATH
        self.HF_TOKEN             = HF_TOKEN
        self.HF_MODEL_REPO        = HF_MODEL_REPO
        self.BACKEND_URL          = BACKEND_URL
        self.ALLOWED_ORIGINS      = ALLOWED_ORIGINS
        self.CLOUDINARY_CLOUD_NAME = CLOUDINARY_CLOUD_NAME
        self.CLOUDINARY_API_KEY   = CLOUDINARY_API_KEY
        self.CLOUDINARY_API_SECRET = CLOUDINARY_API_SECRET
        self.GEMINI_API_KEY = GEMINI_API_KEY

settings = Settings()
