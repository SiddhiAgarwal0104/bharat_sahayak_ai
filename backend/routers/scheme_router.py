# backend/routers/scheme_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from bson import ObjectId
from bson.errors import InvalidId
from backend.agents.search_agent import SearchAgent
from backend.agents.profile_agent import ProfileAgent
from backend.db.database import get_schemes_collection
from backend.models.scheme import format_scheme
from backend.config import JWT_SECRET, JWT_ALGORITHM

router         = APIRouter(prefix="/schemes", tags=["Schemes"])
profile_router = APIRouter(prefix="/profile", tags=["Profile"])
security       = HTTPBearer(auto_error=False)
_search_agent  = SearchAgent()
_profile_agent = ProfileAgent()


def _get_user_obj(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        return {"user_id": "anon", "language_pref": "en", "location": ""}
    try:
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        return {
            "user_id":       payload.get("user_id", "anon"),
            "language_pref": payload.get("language_pref", "en"),
            "location":      payload.get("location", ""),
        }
    except JWTError:
        return {"user_id": "anon", "language_pref": "en", "location": ""}


# ── /profile/eligible — used by search page ──────────────────────────────────
@profile_router.get("/eligible")
def get_eligible(intent: str = "", user=Depends(_get_user_obj)):
    """Returns embedding_ids the logged-in user is eligible for."""
    user_id = user["user_id"]
    if user_id == "anon":
        return {"scheme_ids": []}
    ids = _profile_agent.get_eligible_scheme_ids(user_id, intent)
    return {"scheme_ids": ids}


# ── /schemes/recommended ─────────────────────────────────────────────────────
@router.get("/recommended")
def get_recommended(user=Depends(_get_user_obj)):
    user_id = user["user_id"]
    candidate_ids = []
    if user_id != "anon":
        for intent in ["health", "pension", "agriculture", "women"]:
            ids = _profile_agent.get_eligible_scheme_ids(user_id, intent)
            candidate_ids.extend(ids)

    intent_obj = {
        "query_text": user["location"] + " government schemes benefit",
        "language":   user["language_pref"],
        "intent":     "all",
        "slots":      {},
    }
    return _search_agent.search(intent_obj, candidate_ids=candidate_ids)


# ── /schemes/by-category/{category} ─────────────────────────────────────────
@router.get("/by-category/{category}")
def get_by_category(category: str):
    col     = get_schemes_collection()
    schemes = list(col.find({"category": category}, {
        "embedding_id": 1, "name": 1, "eligibility_criteria": 1,
    }))
    return [
        {
            "id":                   str(s["_id"]),
            "embedding_id":         s.get("embedding_id"),
            "name":                 s.get("name"),
            "eligibility_criteria": s.get("eligibility_criteria"),
        }
        for s in schemes
    ]


@router.get("/all")
def get_all_schemes():
    col = get_schemes_collection()
    return [format_scheme(s) for s in col.find()]


@router.get("/{scheme_id}")
def get_scheme(scheme_id: str):
    col = get_schemes_collection()
    doc = None

    # 1. Try MongoDB ObjectId first (what the frontend sends)
    try:
        doc = col.find_one({"_id": ObjectId(scheme_id)})
    except (InvalidId, Exception):
        pass

    # 2. Fallback: try embedding_id (integer)
    if doc is None:
        try:
            doc = col.find_one({"embedding_id": int(scheme_id)})
        except (ValueError, Exception):
            pass

    if not doc:
        raise HTTPException(status_code=404, detail=f"Scheme {scheme_id} not found.")

    return format_scheme(doc)


@router.post("/search")
def search_schemes(body: dict, user=Depends(_get_user_obj)):
    intent_obj    = body.get("intent_obj")
    candidate_ids = body.get("candidate_ids", [])
    if not intent_obj:
        raise HTTPException(status_code=400, detail="'intent_obj' required.")
    return _search_agent.search(intent_obj, candidate_ids)