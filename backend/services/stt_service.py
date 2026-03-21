# backend/services/stt_service.py
import os
import tempfile
import whisper
from backend.utils.language_utils import detect_language

# FIX 1: Use "small" model instead of "base"
# base  = faster but less accurate, often translates Hindi to English
# small = much better accuracy for Indian languages, still fast enough
# medium = best accuracy but slow (use only if small is not good enough)
_model = whisper.load_model("small")


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
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        path = tmp.name

    try:
        whisper_lang = _to_whisper_lang(language_hint)

        kwargs = {
            "fp16":                       False,
            "task":                       "transcribe",  # NEVER "translate" — keeps original language
            "temperature":                0.0,           # deterministic output, no randomness
            "beam_size":                  5,
            "best_of":                    5,
            "condition_on_previous_text": False,         # FIX 2: False = more accurate for short clips
            "without_timestamps":         True,          # FIX 3: faster, cleaner output for short audio
            "word_timestamps":            False,
        }

        # FIX 4: Always pass language if we know it — stops Whisper guessing wrong
        if whisper_lang:
            kwargs["language"] = whisper_lang

        # FIX 5: Language-specific prompts guide Whisper to stay in that language
        # Without a prompt, Whisper sometimes outputs transliterated or mixed text
        prompts = {
            "hi": "यह एक सरकारी योजना के बारे में हिंदी में प्रश्न है।",
            "ta": "இது ஒரு அரசு திட்டம் பற்றிய தமிழ் கேள்வி.",
            "te": "ఇది ప్రభుత్వ పథకం గురించి తెలుగు ప్రశ్న.",
            "bn": "এটি একটি সরকারি প্রকল্প সম্পর্কে বাংলা প্রশ্ন।",
            "mr": "हे एक सरकारी योजनेबद्दल मराठीत प्रश्न आहे.",
            "gu": "આ એક સરકારી યોજના વિશે ગુજરાતીમાં પ્રશ્ન છે.",
            "pa": "ਇਹ ਇੱਕ ਸਰਕਾਰੀ ਯੋਜਨਾ ਬਾਰੇ ਪੰਜਾਬੀ ਵਿੱਚ ਸਵਾਲ ਹੈ।",
            "en": "This is a question about a government scheme in English.",
        }
        if whisper_lang and whisper_lang in prompts:
            kwargs["initial_prompt"] = prompts[whisper_lang]

        result   = _model.transcribe(path, **kwargs)
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

        return {"text": text, "language": lang}

    finally:
        os.unlink(path)


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
    return cleaned


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