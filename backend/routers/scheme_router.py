"""
scheme_router.py  —  MongoDB version
--------------------------------------
All scheme API endpoints. Member 3 owns this file.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from backend.agents.search_agent import SearchAgent
from backend.db.database import get_schemes_collection
from backend.models.scheme import format_scheme
from backend.config import JWT_SECRET, JWT_ALGORITHM

router        = APIRouter(prefix="/schemes", tags=["Schemes"])
security      = HTTPBearer(auto_error=False)
_search_agent = SearchAgent()


# ── Auth helper (standalone — no dependency on Member 1) ─────────────────────
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


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/recommended")
def get_recommended(user=Depends(_get_user_obj)):
    """Top auto-matched schemes for the logged-in user. Used on home page."""
    intent_obj = {
        "query_text": user["location"] + " government schemes",
        "language":   user["language_pref"],
        "intent":     "all",
        "slots":      {},
    }
    return _search_agent.search(intent_obj, candidate_ids=[])


@router.get("/by-category/{category}")
def get_by_category(category: str):
    """
    Return all scheme embedding_ids + eligibility for a category.
    Called by Member 2's profile_agent.
    """
    valid = {"health", "pension", "agriculture", "women"}
    if category not in valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {valid}",
        )
    col     = get_schemes_collection()
    schemes = list(col.find({"category": category}, {
        "embedding_id": 1,
        "name": 1,
        "eligibility_criteria": 1,
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
    """Return all schemes — for debugging."""
    col = get_schemes_collection()
    return [format_scheme(s) for s in col.find()]


@router.get("/{scheme_id}")
def get_scheme(scheme_id: str):
    """Return full details for one scheme by embedding_id."""
    col = get_schemes_collection()
    try:
        eid = int(scheme_id)
        doc = col.find_one({"embedding_id": eid})
    except ValueError:
        doc = None

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme {scheme_id} not found.",
        )
    return format_scheme(doc)


@router.post("/search")
def search_schemes(body: dict, user=Depends(_get_user_obj)):
    """
    Main search endpoint called by orchestrator.
    Body: { intent_obj: {...}, candidate_ids: [...] }
    """
    intent_obj    = body.get("intent_obj")
    candidate_ids = body.get("candidate_ids", [])

    if not intent_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must include 'intent_obj'.",
        )
    return _search_agent.search(intent_obj, candidate_ids)
