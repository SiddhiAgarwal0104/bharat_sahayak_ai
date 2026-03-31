"""Translation service — uses Gemini to translate scheme fields into Indic languages."""

import json
from backend.services.llm_service import generate

FIELDS_TO_TRANSLATE = ["description", "benefits", "docs_needed"]

LANG_MAP = {
    "hi": "Hindi", "ta": "Tamil", "te": "Telugu",
    "bn": "Bengali", "mr": "Marathi",
}


def translate_scheme(scheme: dict, target_language: str) -> dict:
    """
    Translate the key display fields of a scheme dict.
    Returns a flat dict: { translated: True, description: "...", benefits: "...", docs_needed: "..." }
    Returns {} on failure so the frontend gracefully falls back to English.
    """
    if target_language == "en":
        return {}

    lang_name = LANG_MAP.get(target_language)
    if not lang_name:
        return {}

    # Build a payload with only the fields that exist
    payload = {f: scheme[f] for f in FIELDS_TO_TRANSLATE if scheme.get(f)}

    if not payload:
        return {}

    prompt = (
        f"You are a government scheme translator. Translate ONLY the values in this JSON into simple, "
        f"spoken {lang_name} that a common citizen can understand. "
        f"Keep proper nouns, scheme names, and amounts (like Rs. 6000) unchanged. "
        f"Return ONLY valid JSON with the exact same keys — no markdown, no explanation.\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )

    raw = generate(prompt, target_language)
    if not raw:
        return {}

    # Strip any accidental markdown fences
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        translated = json.loads(raw)
        translated["translated"] = True
        return translated
    except Exception as e:
        print(f"[TranslationService] JSON parse failed: {e}\nRaw: {raw[:200]}")
        return {}