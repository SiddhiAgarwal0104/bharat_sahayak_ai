# backend/db/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pymongo import MongoClient
from backend.config import settings

MONGO_URL = settings.MONGO_URL
MONGO_DB  = settings.MONGO_DB

# ── Async client ──────────────────────────────────────────────────
_async_client = None
_async_db     = None

# ── Sync client — used by your profile_agent ─────────────────────
sync_client  = MongoClient(MONGO_URL)
sync_db      = sync_client[MONGO_DB]
users_col    = sync_db["users"]
sessions_col = sync_db["user_sessions"]


# ── connect_db — matches Member 1's main.py signature ────────────
async def connect_db(document_models: list = None):
    global _async_client, _async_db

    _async_client = AsyncIOMotorClient(MONGO_URL)
    _async_db     = _async_client[MONGO_DB]

    if document_models is None:
        from backend.models.user import User, UserSession
        document_models = [User, UserSession]

    await init_beanie(
        database        = _async_db,
        document_models = document_models
    )
    print("MongoDB Atlas connected via Beanie.")
    create_indexes()


# ── close_db — matches Member 1's main.py signature ──────────────
async def close_db():
    global _async_client
    if _async_client:
        _async_client.close()
    print("MongoDB connection closed.")


# ── Sync indexes ──────────────────────────────────────────────────
def create_indexes():
    try:
        users_col.create_index("email", unique=True)
        users_col.create_index("created_at")
        sessions_col.create_index("user_id")
        sessions_col.create_index([("user_id", 1), ("scheme_id", 1)])
        print("Sync indexes created.")
    except Exception as e:
        print(f"Index warning: {e}")


def get_db():
    return sync_db