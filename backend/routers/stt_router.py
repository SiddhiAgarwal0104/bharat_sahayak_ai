# backend/routers/stt_router.py
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
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
    # Validate audio file
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    # Read audio bytes
    audio_bytes = await audio.read()
    
    if not audio_bytes or len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio file too small or empty")
    
    print(f"[STT] Received audio: {len(audio_bytes)} bytes, filename={audio.filename}, hint={language_hint}")
    
    # Use frontend hint first, then fall back to user's registered language preference
    hint = language_hint or current_user.language_pref
    try:
        result = transcribe(audio_bytes, language_hint=hint)
        print(f"[STT] Success: transcribed '{result.get('text', '')[:50]}...' in {result.get('language', 'unknown')}")
        return result
    except Exception as e:
        print(f"[STT] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")