# backend/utils/language_utils.py
# Member 2 imports detect_language() from here — build this first.
from langdetect import detect, LangDetectException

_CODE_TO_NAME = {
    "hi": "Hindi",   "en": "English", "ta": "Tamil",
    "te": "Telugu",  "bn": "Bengali", "mr": "Marathi",
    "gu": "Gujarati","pa": "Punjabi",
}
SUPPORTED_CODES = set(_CODE_TO_NAME.keys())

def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "en"
    try:
        code = detect(text)
        return code if code in SUPPORTED_CODES else "en"
    except LangDetectException:
        return "en"

def locale_to_name(code: str) -> str:
    return _CODE_TO_NAME.get(code.lower(), "English")

def name_to_locale(name: str) -> str:
    reverse = {v: k for k, v in _CODE_TO_NAME.items()}
    return reverse.get(name, "en")

def get_supported_languages() -> list:
    return [{"code": k, "name": v} for k, v in _CODE_TO_NAME.items()]