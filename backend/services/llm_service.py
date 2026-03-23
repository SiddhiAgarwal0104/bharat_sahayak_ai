import google.generativeai as genai
from backend.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

# ADD at the top of llm_service.py
from gtts import gTTS
import io

# ADD this new function
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
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f'[LLMService] Gemini error: {e}')
        return ''