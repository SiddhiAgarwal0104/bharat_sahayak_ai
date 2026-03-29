import requests
from backend.config import settings

from gtts import gTTS
import io

def text_to_speech(text: str, language: str = 'hi') -> bytes:
    """
    Converts text to speech audio bytes using gTTS.
    Returns MP3 bytes. Returns None on failure.
    Supported: 'hi', 'en', 'ta', 'te', 'bn', 'mr'
    """
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        print(f'[LLMService] TTS error: {e}')
        return None

LANG_MAP = {
    'hi': 'Hindi',
    'en': 'English'
}

def generate(prompt: str, language: str = 'hi') -> str:
    try:
        # We explicitly use simple REST over HTTPS to bypass the SDK gRPC hanging
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"[LLMService] Gemini error ({res.status_code}): {res.text}")
            return ""
    except Exception as e:
        print(f'[LLMService] Gemini Request Exception: {e}')
        return ''