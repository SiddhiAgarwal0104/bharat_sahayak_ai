# backend/services/stt_service.py
import os
import tempfile
import threading
import whisper
from backend.utils.language_utils import detect_language

# Speed-first defaults for local development.
# You can override at runtime:
#   PowerShell: $env:WHISPER_MODEL='base'   (for English only - very fast but poor for Indian languages)
#   PowerShell: $env:WHISPER_MODEL='small'  (recommended for Indian languages - good speed + accuracy)
#   PowerShell: $env:WHISPER_MODEL='medium' (best accuracy, slower)
#   PowerShell: $env:WHISPER_FAST_MODE='1'
_WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small").strip().lower() or "small"
_WHISPER_FAST_MODE = os.getenv("WHISPER_FAST_MODE", "1").strip() in {"1", "true", "yes"}
_model = None
_model_lock = threading.Lock()


def _get_model():
    global _model
    if _model is not None:
        return _model

    with _model_lock:
        if _model is None:
            print(f"[stt_service] Loading Whisper '{_WHISPER_MODEL}' model...")
            _model = whisper.load_model(_WHISPER_MODEL)
            print("[stt_service] Model loaded!")
    return _model


def transcribe(audio_bytes: bytes, language_hint: str | None = None) -> dict:
    """
    Transcribe audio bytes and return text in the SAME language spoken.
    
    Key fix: task="transcribe" keeps the output in the original language.
    task="translate" would convert everything to English — we never want that.
    
    Args:
        audio_bytes:   raw audio bytes (wav/mp3/ogg)
        language_hint: ISO code like 'hi', 'en' — from user's language_pref
    
    Returns:
        {"text": str, "language": str}
    """
    if not audio_bytes:
        raise ValueError("Audio bytes are empty")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        path = tmp.name

    try:
        print(f"[stt_service] Transcribing {len(audio_bytes)} bytes, language_hint={language_hint}")
        whisper_lang = _to_whisper_lang(language_hint)

        # Optimize for Indian languages: use higher beam_size for better accuracy
        is_indian_lang = whisper_lang in {"hi", "ta", "te", "bn", "mr", "gu", "pa"}
        
        # Fast defaults for better latency in interactive UI.
        kwargs = {
            "fp16":                       False,
            "task":                       "transcribe",  # NEVER "translate" — keeps original language
            "temperature":                0.1 if is_indian_lang else 0.0,  # Slightly higher for Indian langs = better accuracy
            "beam_size":                  5 if is_indian_lang else 1,      # Higher for Indian langs = much better accuracy
            "best_of":                    5 if is_indian_lang else 1,      # Higher for Indian langs
            "condition_on_previous_text": False,         # FIX 2: False = more accurate for short clips
            "without_timestamps":         True,          # FIX 3: faster, cleaner output for short audio
            "word_timestamps":            False,
            "verbose":                    False,         # Suppress verbose logs
        }

        # FIX 4: Always pass language if we know it — stops Whisper guessing wrong
        if whisper_lang:
            kwargs["language"] = whisper_lang

        # FIX 5: Language-specific prompts guide Whisper to stay in that language
        # Enhanced prompts help prevent repetition and mixed language output
        prompts = {
            "hi": "यह सरकारी योजना के बारे में हिंदी में प्रश्न है। कृपया हिंदी में पूरा उत्तर दें।",
            "ta": "இது அரசு திட்டம் பற்றிய தமிழ் கேள்வி. தமிழ் மொழியில் முழுமையான பதிலை கொடுக்கவும்.",
            "te": "ఇది ప్రభుత్వ పథకం గురించి తెలుగు ప్రశ్న. దయచేసి తెలుగు భాషలో సంపూర్ణ సమాధానం ఇవ్వండి.",
            "bn": "এটি সরকারি প্রকল্প সম্পর্কে বাংলা প্রশ্ন। দয়করে বাংলায় সম্পূর্ণ উত্তর দিন।",
            "mr": "हे सरकारी योजनेबद्दल मराठीत प्रश्न आहे. कृपया पूर्ण उत्तर मराठीत द्या.",
            "gu": "આ સરકારી યોજના વિશે ગુજરાતીમાં પ્રશ્ન છે. કૃપયા સંપૂર્ણ જવાબ ગુજરાતીમાં આપો.",
            "pa": "ਇਹ ਸਰਕਾਰੀ ਯੋਜਨਾ ਬਾਰੇ ਪੰਜਾਬੀ ਵਿੱਚ ਸਵਾਲ ਹੈ। ਕਿਰਪਾ ਪੂਰੀ ਜਵਾਬ ਪੰਜਾਬੀ ਵਿੱਚ ਦਿਓ।",
            "en": "This is a question about a government scheme in English. Please provide a complete answer in English.",
        }
        if whisper_lang and whisper_lang in prompts:
            kwargs["initial_prompt"] = prompts[whisper_lang]

        print(f"[stt_service] Starting Whisper transcription with language={whisper_lang}")
        model = _get_model()
        result   = model.transcribe(path, **kwargs)
        text     = result.get("text", "").strip()
        detected = _norm(result.get("language", ""))

        # FIX 6: Trust language_hint over Whisper's detection
        # Whisper sometimes detects wrong language for short audio clips
        if whisper_lang:
            lang = whisper_lang
        elif detected in {"hi","en","ta","te","bn","mr","gu","pa"}:
            lang = detected
        else:
            lang = detect_language(text)

        # FIX 7: Clean up common Whisper artifacts
        text = _clean_text(text, lang)

        print(f"[stt_service] Transcription complete: lang={lang}, text_length={len(text)}")
        return {"text": text, "language": lang}
    
    except Exception as e:
        print(f"[stt_service] ERROR during transcription: {type(e).__name__}: {str(e)}")
        raise

    finally:
        try:
            os.unlink(path)
        except:
            pass


def _clean_text(text: str, lang: str) -> str:
    """Remove common Whisper artifacts from transcription."""
    # Whisper sometimes adds these filler phrases
    noise_phrases = [
        "Thank you.", "Thanks for watching.", "Subscribe.", "Like and subscribe.",
        ".", "...", " ", "Subtitles by", "Translated by",
    ]
    cleaned = text.strip()
    for phrase in noise_phrases:
        if cleaned == phrase:
            return ""
    
    # FIX 8: Remove repeated words (very common artifact in Indian language transcription)
    # Split into words and remove consecutive duplicates
    words = cleaned.split()
    
    if len(words) > 1:
        # Remove consecutive duplicate words (Whisper sometimes repeats words 10+ times)
        deduplicated = [words[0]]
        for word in words[1:]:
            # Only keep if different from the last kept word
            if word.lower() != deduplicated[-1].lower():
                deduplicated.append(word)
        
        cleaned = " ".join(deduplicated)
    
    return cleaned.strip()


def _norm(w: str) -> str:
    m = {
        "hindi":   "hi", "english": "en", "tamil":   "ta", "telugu":  "te",
        "bengali": "bn", "marathi": "mr", "gujarati":"gu", "punjabi": "pa",
        "hi":"hi", "en":"en", "ta":"ta", "te":"te",
        "bn":"bn", "mr":"mr", "gu":"gu", "pa":"pa",
    }
    return m.get(w.lower(), "en")


def _to_whisper_lang(lang: str | None) -> str | None:
    if not lang:
        return None
    m = {
        "hi":"hi", "en":"en", "ta":"ta", "te":"te",
        "bn":"bn", "mr":"mr", "gu":"gu", "pa":"pa",
        "hindi":"hi", "english":"en", "tamil":"ta", "telugu":"te",
        "bengali":"bn", "marathi":"mr", "gujarati":"gu", "punjabi":"pa",
    }
    return m.get(lang.lower())


# ── Quick standalone test ──────────────────────────────────────────────────────
# python backend/services/stt_service.py audio.wav hi
if __name__ == "__main__":
    import sys
    hint = sys.argv[2] if len(sys.argv) > 2 else None
    with open(sys.argv[1], "rb") as f:
        r = transcribe(f.read(), language_hint=hint)
    print("Text    :", r["text"])
    print("Language:", r["language"])