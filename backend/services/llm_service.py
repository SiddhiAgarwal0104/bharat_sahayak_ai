import google.generativeai as genai
from gtts import gTTS
import io
import re
from backend.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')   # ← fix: 2.5-flash doesn't exist yet

LANG_MAP = {
    'hi': 'Hindi',
    'en': 'English',
    'ta': 'Tamil',
    'te': 'Telugu',
    'bn': 'Bengali',
    'mr': 'Marathi',
}

def _strip_markdown(text: str) -> str:
    """Remove markdown so gTTS doesn't read out asterisks, hashes etc."""
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)   # **bold**, *italic*
    text = re.sub(r'#{1,6}\s?', '', text)                  # ## headings
    text = re.sub(r'\n{2,}', '. ', text)                   # blank lines → pause
    text = re.sub(r'\n', ' ', text)                        # single newlines
    text = re.sub(r'\s{2,}', ' ', text)                    # extra spaces
    return text.strip()

def generate(prompt: str, language: str = 'hi') -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f'[LLMService] Gemini error: {e}')
        return ''

def text_to_speech(text: str, language: str = 'hi') -> bytes:
    # gTTS language code map — 'te' not supported, fall back to 'en'
    GTTS_LANG_MAP = {
        'hi': 'hi',
        'en': 'en',
        'ta': 'ta',
        'te': 'en',   # Telugu not supported by gTTS, fallback to English
        'bn': 'bn',
        'mr': 'mr',
    }
    gtts_lang = GTTS_LANG_MAP.get(language, 'hi')
    clean_text = _strip_markdown(text)

    print(f'[LLMService] TTS → lang={gtts_lang}, chars={len(clean_text)}')

    try:
        tts = gTTS(text=clean_text, lang=gtts_lang, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        print(f'[LLMService] TTS error: {e}')
        return None