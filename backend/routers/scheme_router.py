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
  GET  /schemes/{scheme_id}/voice    → TTS audio for scheme explanation
  GET  /schemes/{scheme_id}/translate → translated fields in requested language
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from bson import ObjectId
from bson.errors import InvalidId
import json
import re
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


# ── Auth helpers ──────────────────────────────────────────────────────────────

def _get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if credentials is None:
        return ""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return str(payload.get("user_id", ""))
    except JWTError:
        return ""


def _get_user_obj(credentials: HTTPAuthorizationCredentials = Depends(security)):
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


# ── Internal helpers ──────────────────────────────────────────────────────────

def _strip_markdown(text: str) -> str:
    """Remove markdown symbols that may appear in DB text or LLM output."""
    if not text:
        return text
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'#{1,6}\s?', '', text)
    text = re.sub(r'^[-•●▪]\s?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+[\.\)]\s?', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{2,}', ' ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def _resolve_scheme(col, scheme_id: str):
    """Try ObjectId lookup first, then fall back to numeric embedding_id."""
    doc = None
    try:
        doc = col.find_one({"_id": ObjectId(scheme_id)})
    except (InvalidId, Exception):
        pass

    if doc is None and scheme_id.isdigit():
        doc = col.find_one({"embedding_id": int(scheme_id)})

    return doc


def _extract_json_from_response(raw: str) -> dict | None:
    """
    Robustly extract a JSON object from a Gemini response string.
    Handles:
      - Clean JSON
      - JSON wrapped in ```json ... ``` fences
      - JSON buried inside extra prose (finds first { ... } block)
    Returns parsed dict or None on failure.
    """
    if not raw:
        return None

    # Step 1: strip markdown fences
    cleaned = raw.strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()

    # Step 2: try direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Step 3: find first {...} block in the response (handles prose wrapping)
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    return None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/recommended")
async def get_recommended(user=Depends(_get_user_obj)):
    user_id = user["user_id"]
    if not user_id:
        return []

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
    col = get_schemes_collection()
    return [format_scheme(doc) for doc in col.find()]


@router.post("/search")
def search_schemes(body: dict, user=Depends(_get_user_obj)):
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
    Translate scheme display fields into the requested Indic language using Gemini.

    Sends all three fields in ONE JSON prompt for consistency and speed.
    Falls back gracefully — always returns something so the UI is never blank.
    """
    VALID_LANGS = {"hi", "ta", "te", "bn", "mr"}
    if lang not in VALID_LANGS:
        return {"translated": False}

    col = get_schemes_collection()
    doc = _resolve_scheme(col, scheme_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Scheme not found")

    scheme    = format_scheme(doc)
    lang_name = LANG_MAP.get(lang, "Hindi")

    # Strip markdown from source text before sending to Gemini so the model
    # is not confused by bullet symbols in the input.
    # Do NOT cap text length — truncating caused cut-off sentences that
    # broke Gemini's JSON output. Gemini 1.5-flash handles long text fine.
    fields_to_translate = {}
    for field in ("description", "benefits", "docs_needed"):
        val = scheme.get(field, "")
        if val and val.strip():
            fields_to_translate[field] = _strip_markdown(val.strip())

    if not fields_to_translate:
        print(f"[translate_scheme] No fields to translate for scheme={scheme_id}")
        return {"translated": False}

    print(f"[translate_scheme] Sending to Gemini: scheme={scheme_id} lang={lang} "
          f"fields={list(fields_to_translate.keys())} "
          f"desc_len={len(fields_to_translate.get('description', ''))}")

    prompt = (
        f"You are a government scheme translator for Indian citizens.\n"
        f"Translate ONLY the values in the JSON below into simple, spoken {lang_name}.\n"
        f"A common citizen with basic education must be able to understand it.\n\n"
        f"STRICT RULES:\n"
        f"1. Return ONLY a valid JSON object with exactly the same keys as given.\n"
        f"2. Do NOT add any text before or after the JSON.\n"
        f"3. Do NOT use markdown, bullet points, asterisks, or numbering.\n"
        f"4. Keep all numbers, rupee amounts, URLs, and proper nouns unchanged.\n"
        f"5. If a value is already short and simple, keep the translation concise too.\n\n"
        f"Input JSON:\n"
        f"{json.dumps(fields_to_translate, ensure_ascii=False)}"
    )

    raw = generate(prompt, lang)

    print(f"[translate_scheme] Gemini raw (first 300 chars): {repr(raw[:300]) if raw else 'EMPTY'}")

    # Parse robustly — handles fences, prose wrapping, etc.
    parsed = _extract_json_from_response(raw)

    if not parsed:
        # Gemini failed to return valid JSON — return cleaned English originals
        # so the UI shows something readable instead of spinning forever.
        print(f"[translate_scheme] Parse failed scheme={scheme_id} lang={lang} — returning English fallback")
        return {
            "translated":  False,
            "description": fields_to_translate.get("description", scheme.get("description", "")),
            "benefits":    fields_to_translate.get("benefits",    scheme.get("benefits", "")),
            "docs_needed": fields_to_translate.get("docs_needed", scheme.get("docs_needed", "")),
        }

    result = {
        "translated": True,
        "language":   lang,
    }
    for field in ("description", "benefits", "docs_needed"):
        value = parsed.get(field) or fields_to_translate.get(field) or scheme.get(field, "")
        result[field] = _strip_markdown(str(value)) if value else ""

    print(f"[translate_scheme] OK — scheme={scheme_id} lang={lang} "
          f"desc_preview={result.get('description', '')[:80]}")
    return result


@router.get("/{scheme_id}/voice")
def get_scheme_voice(scheme_id: str, lang: str = "hi"):
    """
    Generate and return a TTS audio (MP3) explanation of the scheme
    in the requested language.
    """
    col = get_schemes_collection()
    doc = _resolve_scheme(col, scheme_id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with id={scheme_id} not found.",
        )

    scheme = format_scheme(doc)
    explanation_text = _explainer_agent.explain(scheme, user_language=lang)
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
            "Content-Disposition": f'inline; filename="scheme_{scheme_id}_{lang}.mp3"',
        },
    )


@router.get("/{scheme_id}")
def get_scheme(scheme_id: str):
    """Return full details for a single scheme."""
    col = get_schemes_collection()
    doc = _resolve_scheme(col, scheme_id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with id={scheme_id} not found.",
        )

    return format_scheme(doc)