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
            return "Yeh ek sarkari yojana hai jo logon ko madad karti hai."

        return result