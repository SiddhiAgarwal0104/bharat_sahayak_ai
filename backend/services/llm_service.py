import google.generativeai as genai
from backend.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-2.0-flash')

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