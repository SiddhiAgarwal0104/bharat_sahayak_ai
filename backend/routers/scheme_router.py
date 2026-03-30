"""
scheme_router.py
----------------
All scheme-related API endpoints.
Member 3 owns this file.

Endpoints:
  GET  /schemes/recommended          → top schemes for logged-in user (home page)
  GET  /schemes/by-category/{cat}    → all scheme IDs+eligibility for a category
                                        (used by Member 2's profile agent)
  GET  /schemes/{scheme_id}          → full details for one scheme
  POST /schemes/search               → main search — takes intent_obj + candidate_ids
  GET  /schemes/all                  → list all schemes (admin/debug)
  GET  /schemes/{scheme_id}/voice    → TTS audio for scheme explanation (NEW)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from bson import ObjectId
from bson.errors import InvalidId
from backend.agents.search_agent import SearchAgent
from backend.agents.explainer_agent import ExplainerAgent
from backend.agents.profile_agent import ProfileAgent
from backend.models.scheme import format_scheme
from backend.db.database import get_schemes_collection
from backend.config import JWT_SECRET, JWT_ALGORITHM
from backend.services.llm_service import generate, text_to_speech, LANG_MAP

router = APIRouter(prefix="/schemes", tags=["Schemes"])
security = HTTPBearer(auto_error=False)
_search_agent = SearchAgent()
_explainer_agent = ExplainerAgent()


# ── Auth helper ───────────────────────────────────────────────────────────────

def _get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Decode JWT and return user_id (MongoDB ObjectId string).
    Returns "" (anonymous) if no token provided.
    """
    if credentials is None:
        return ""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return str(payload.get("user_id", ""))
    except JWTError:
        return ""


def _get_user_obj(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Returns a minimal user dict from JWT payload.
    user_id is kept as a string (MongoDB ObjectId hex) — NOT cast to int.
    """
    if credentials is None:
        return {"user_id": "", "language_pref": "en", "location": ""}
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "user_id":       str(payload.get("user_id", "")),
            "language_pref": payload.get("language_pref", "en"),
            "location":      payload.get("location", ""),
        }
    except JWTError:
        return {"user_id": "", "language_pref": "en", "location": ""}


# ── Endpoints ─────────────────────────────────────────────────────────────────

# NOTE: /recommended and /all MUST be defined BEFORE /{scheme_id}
# so FastAPI does not swallow them as path parameters.

@router.get("/recommended")
async def get_recommended(user=Depends(_get_user_obj)):
    """
    Return top recommended schemes for the logged-in user.
    Anonymous users receive an empty list.
    """
    # FIX 1: extract user_id from the user dict (was referencing undefined `user_id`)
    user_id = user["user_id"]
    if not user_id:
        return []   # anonymous — nothing to recommend

    # FIX 2: build intent_obj (was referencing undefined `intent_obj`)
    intent_obj = {
        "query_text": "recommended schemes",
        "language":   user.get("language_pref", "en"),
        "intent":     "all",
        "slots":      {},
    }

    eligible_ids = await ProfileAgent().get_eligible_scheme_ids(user_id, intent="all")
    results = _search_agent.search(intent_obj, candidate_ids=eligible_ids)
    return results


@router.get("/by-category/{category}")
def get_by_category(category: str):
    """
    Return all scheme IDs and their eligibility_criteria for a given category.
    Called by Member 2's profile_agent to get candidates before filtering.

    Args:
        category: "health" | "pension" | "agriculture" | "women"
    """
    valid_categories = {"health", "pension", "agriculture", "women"}
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category '{category}'. Must be one of: {valid_categories}",
        )

    col = get_schemes_collection()
    docs = col.find({"category": category})

    return [
        {
            "id":                   str(doc["_id"]),
            "name":                 doc.get("name"),
            "eligibility_criteria": doc.get("eligibility_criteria"),
        }
        for doc in docs
    ]


@router.get("/all")
def get_all_schemes():
    """Return all schemes — useful for debugging and admin view."""
    col = get_schemes_collection()
    return [format_scheme(doc) for doc in col.find()]


@router.post("/search")
def search_schemes(body: dict, user=Depends(_get_user_obj)):
    """
    Main search endpoint — called by the orchestrator.

    Request body:
        {
            "intent_obj":    { "query_text": str, "language": str,
                               "intent": str, "slots": {} },
            "candidate_ids": [1, 3, 7, ...]   ← from Member 2's profile agent
        }

    Returns:
        List of up to 3 scheme dicts with match_score and is_best_match.
    """
    intent_obj    = body.get("intent_obj")
    candidate_ids = body.get("candidate_ids", [])

    if not intent_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must include 'intent_obj'.",
        )

    results = _search_agent.search(intent_obj, candidate_ids)
    return results


# ── Routes with path parameters MUST come after all static routes ─────────────

@router.get("/{scheme_id}/translate")
def translate_scheme(scheme_id: str, lang: str = "hi"):
    """
    Translate scheme fields into the requested language using Gemini.
    Falls back to original English on any error.
    """
    # Normalize lang — reject full words like "Hindi" 
    VALID_LANGS = {"hi", "ta", "te", "bn", "mr"}
    if lang not in VALID_LANGS:
        return {"translated": False}   # "en" or anything invalid → no translation needed

    col = get_schemes_collection()

    doc = None
    try:
        doc = col.find_one({"_id": ObjectId(scheme_id)})
    except (InvalidId, Exception):
        pass

    if doc is None and scheme_id.isdigit():
        doc = col.find_one({"embedding_id": int(scheme_id)})

    if not doc:
        raise HTTPException(status_code=404, detail="Scheme not found")

    scheme   = format_scheme(doc)
    lang_name = LANG_MAP.get(lang, "Hindi")

    def translate_field(text: str, field_label: str) -> str:
        if not text or not text.strip():
            return text
        try:
            prompt = (
                f"Translate the following government scheme {field_label} into simple {lang_name}. "
                f"Keep all numbers, rupee amounts, and proper nouns unchanged. "
                f"Return ONLY the translated text, no explanations, no markdown.\n\n"
                f"{text[:800]}"   # cap at 800 chars to keep Gemini fast
            )
            result = generate(prompt, lang)
            return result.strip() if result else text
        except Exception as e:
            print(f"[translate_scheme] field '{field_label}' failed: {e}")
            return text   # fallback to English on any error

    description = translate_field(scheme.get("description", ""), "description")
    benefits    = translate_field(scheme.get("benefits", ""),    "benefits")
    docs_needed = translate_field(scheme.get("docs_needed", ""), "documents needed")

    print(f"[translate_scheme] {scheme_id} → {lang} done")

    return {
        "translated":  True,
        "language":    lang,
        "description": description,
        "benefits":    benefits,
        "docs_needed": docs_needed,
    }

@router.get("/{scheme_id}/voice")
def get_scheme_voice(scheme_id: str, lang: str = "hi"):
    """
    Generate and return a TTS audio (MP3) explanation of the scheme
    in the requested language.

    Uses ExplainerAgent to build a natural language summary, then
    passes it to text_to_speech() from llm_service.

    Query param:
        lang: ISO 639-1 code — 'hi' | 'en' | 'ta' | 'te' | 'bn' | 'mr'

    Returns:
        audio/mpeg binary stream (MP3)
    """
    col = get_schemes_collection()

    # Resolve scheme — ObjectId first, then numeric embedding_id
    doc = None
    try:
        doc = col.find_one({"_id": ObjectId(scheme_id)})
    except (InvalidId, Exception):
        pass

    if doc is None and scheme_id.isdigit():
        doc = col.find_one({"embedding_id": int(scheme_id)})

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with id={scheme_id} not found.",
        )

    scheme = format_scheme(doc)

    # Generate a spoken explanation via ExplainerAgent (uses Gemini internally)
    explanation_text = _explainer_agent.explain(scheme, user_language=lang)

    # Convert explanation text → MP3 bytes via gTTS
    audio_bytes = text_to_speech(explanation_text, language=lang)

    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text-to-speech conversion failed. Please try again.",
        )

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            # Suggest a filename for browser downloads
            "Content-Disposition": f'inline; filename="scheme_{scheme_id}_{lang}.mp3"',
        },
    )


@router.get("/{scheme_id}")
def get_scheme(scheme_id: str):
    """
    Return full details for a single scheme.
    Accepts either a MongoDB ObjectId hex string (24 chars) or a numeric embedding_id.
    """
    col = get_schemes_collection()

    # Try ObjectId lookup first (frontend passes Mongo _id as string)
    doc = None
    try:
        doc = col.find_one({"_id": ObjectId(scheme_id)})
    except (InvalidId, Exception):
        pass

    # Fallback: numeric embedding_id
    if doc is None and scheme_id.isdigit():
        doc = col.find_one({"embedding_id": int(scheme_id)})

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with id={scheme_id} not found.",
        )

    return format_scheme(doc)