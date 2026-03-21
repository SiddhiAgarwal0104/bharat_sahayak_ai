# backend/db/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.config import settings

_client: AsyncIOMotorClient = None

async def connect_db(document_models: list):
    global _client
    _client = AsyncIOMotorClient(settings.MONGO_URL)       # MONGO_URL not MONGODB_URL
    db = _client[settings.MONGO_DB]                        # MONGO_DB not MONGODB_DB
    await init_beanie(database=db, document_models=document_models)
    print(f"[DB] Connected to MongoDB Atlas — database: {settings.MONGO_DB}")

async def close_db():
    global _client
    if _client:
        _client.close()