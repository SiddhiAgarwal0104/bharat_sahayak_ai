"""
database.py  —  MongoDB version
--------------------------------
Replaces SQLAlchemy/PostgreSQL with MongoDB using PyMongo.
Member 3 owns this file.
"""

from pymongo import MongoClient
from pymongo.database import Database
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB",  "sahayak")

_client: MongoClient = None
_db: Database = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URL)
        print(f"[database] Connected to MongoDB at {MONGO_URL}")
    return _client


def get_db() -> Database:
    global _db
    if _db is None:
        _db = get_client()[MONGO_DB]
    return _db


def get_schemes_collection():
    """Returns the schemes collection."""
    return get_db()["schemes"]


def close():
    global _client
    if _client:
        _client.close()
        _client = None
