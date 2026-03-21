# backend/routers/stt_router.py
from fastapi import APIRouter, Depends, File, Form, UploadFile
from backend.services.stt_service import transcribe
from backend.routers.auth_router import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/stt", tags=["stt"])


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language_hint: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
):
    """
    Transcribe uploaded audio file.
    
    Priority order for language:
    1. language_hint sent by frontend (if user manually selected a language)
    2. current_user.language_pref (set during registration — most reliable)
    3. Whisper auto-detection (fallback)
    
    This ensures output is always in the user's own language.
    """
    # Use frontend hint first, then fall back to user's registered language preference
    hint = language_hint or current_user.language_pref
    return transcribe(await audio.read(), language_hint=hint)