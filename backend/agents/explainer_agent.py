import json
from backend.services.llm_service import generate, LANG_MAP

class ExplainerAgent:
    def explain(self, scheme: dict, user_language: str = 'hi') -> str:

        lang_name = LANG_MAP.get(user_language, 'Hindi')

        prompt = (
            f'You are a helpful government scheme advisor.\n'
            f'Explain this scheme in simple {lang_name}.\n'
            f'Keep it under 200 words.\n\n'
            f'Scheme:\n{json.dumps(scheme, indent=2)}'
        )

        result = generate(prompt, user_language)

        if not result:
            result = self._fallback(scheme, user_language)

        return result

    def _fallback(self, scheme: dict, lang: str) -> str:
        name     = scheme.get('name', 'Yeh yojana')
        benefits = scheme.get('benefits', 'vittiya sahayata')
        docs     = scheme.get('docs_needed', 'Aadhaar card')
        category = scheme.get('category', '')

        if lang == 'hi':
            return (
                f"**{name}** bharat sarkar ki ek mahatvapurn yojana hai.\n\n"
                f"**Yojana kya hai?** Yeh yojana {category} kshetra mein "
                f"paatra nagrikon ko sahayata pradan karti hai.\n\n"
                f"**Labh:** {benefits}\n\n"
                f"**Zaruri Dastaavez:** {docs}\n\n"
                f"Adhik jaankari ke liye official website par jayen."
            )
        return (
            f"**{name}** is an important government scheme.\n\n"
            f"**What is it?** This scheme provides support to eligible "
            f"citizens in the {category} sector.\n\n"
            f"**Benefits:** {benefits}\n\n"
            f"**Documents needed:** {docs}\n\n"
            f"Visit the official website for more information."
        )