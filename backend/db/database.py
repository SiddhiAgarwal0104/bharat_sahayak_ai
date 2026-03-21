# backend/db/database.py
# Combined: Member 3 (sync PyMongo for schemes) + Member 1+2 (async Motor/Beanie for users)

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pymongo import MongoClient
from backend.config import settings

MONGO_URL = settings.MONGO_URL
MONGO_DB  = settings.MONGO_DB

# ── Async client — used by Member 1+2 (auth, users, sessions) ────────────────
_async_client = None
_async_db     = None

# ── Sync client — used by Member 3 (schemes, search, seeding) ────────────────
_sync_client = None
_sync_db     = None


def _get_sync_db():
    global _sync_client, _sync_db
    if _sync_client is None:
        _sync_client = MongoClient(MONGO_URL)
        _sync_db     = _sync_client[MONGO_DB]
    return _sync_db


def get_schemes_collection():
    """Member 3 — sync access to schemes collection."""
    return _get_sync_db()["schemes"]


def get_db():
    """Sync DB — used by Member 2's profile_agent and eligibility rules."""
    return _get_sync_db()


# ── Async connect — called at FastAPI startup by Member 4's main.py ───────────
async def connect_db(document_models: list = None):
    global _async_client, _async_db

    _async_client = AsyncIOMotorClient(MONGO_URL)
    _async_db     = _async_client[MONGO_DB]

    if document_models is None:
        from backend.models.user import User, UserSession
        document_models = [User, UserSession]

    await init_beanie(
        database        = _async_db,
        document_models = document_models,
    )
    print("[database] MongoDB Atlas connected via Beanie (async).")
    _create_sync_indexes()


async def close_db():
    global _async_client
    if _async_client:
        _async_client.close()
    print("[database] MongoDB connection closed.")


def _create_sync_indexes():
    """Create indexes on users and sessions collections."""
    try:
        db = _get_sync_db()
        db["users"].create_index("email", unique=True)
        db["user_sessions"].create_index("user_id")
        print("[database] Sync indexes created.")
    except Exception as e:
        print(f"[database] Index note: {e}")
