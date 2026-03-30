import json
import re
from backend.services.llm_service import generate, LANG_MAP


def _strip_markdown(text: str) -> str:
    """Remove markdown formatting so gTTS doesn't read out asterisks, hashes etc."""
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)  # **bold**, *italic*
    text = re.sub(r'#{1,6}\s?', '', text)                 # ## headings
    text = re.sub(r'^[-•]\s?', '', text, flags=re.MULTILINE)  # bullet points
    text = re.sub(r'\n{2,}', '. ', text)                  # blank lines → pause
    text = re.sub(r'\n', ' ', text)                       # single newlines → space
    text = re.sub(r'\s{2,}', ' ', text)                   # collapse extra spaces
    return text.strip()


class ExplainerAgent:
    def explain(self, scheme: dict, user_language: str = 'hi') -> str:
        lang_name = LANG_MAP.get(user_language, 'Hindi')
        prompt = (
            f'You are a helpful government scheme advisor reading out information to a citizen over audio.\n'
            f'Explain this scheme in simple spoken {lang_name} in under 150 words.\n'
            f'IMPORTANT: Plain sentences only — NO markdown, NO asterisks, NO bullet points, NO headings, NO numbering.\n'
            f'Cover: what the scheme is, who can apply, main benefit, and key documents needed.\n\n'
            f'Scheme:\n{json.dumps(scheme, indent=2)}'
        )
        result = generate(prompt, user_language)
        if result:
            return _strip_markdown(result)
        return _strip_markdown(self._fallback(scheme, user_language))

    def _fallback(self, scheme: dict, lang: str) -> str:
        name     = scheme.get('name', 'Yeh Yojana')
        category = scheme.get('category', 'sarkari')
        messages = {
            'hi': (
                f"{name}. "
                f"Yeh bharat sarkar ki ek {category} yojana hai jo zarooratmand nagrikon ko seedha madad deti hai. "
                f"Jo nagrik paatrata sharten poori karte hain unhe is yojana ka labh milta hai. "
                f"Paatra laabhaarthi ko seedhe unke bank khate mein rashi ya seva ka labh diya jaata hai. "
                f"Zaruri dastaavez: Aadhaar Card, Bank Passbook, Aay Praman Patra, aur Niwas Praman Patra. "
                f"Adhik jaankari ke liye yojana ki official website par jayen."
            ),
            'en': (
                f"{name}. "
                f"This is a government {category} scheme that provides direct support to eligible citizens. "
                f"Citizens who meet the eligibility criteria such as income, age, and documentation requirements can apply. "
                f"Eligible beneficiaries receive financial support directly into their bank account. "
                f"Documents needed: Aadhaar Card, Bank Passbook, Income Certificate, and Residence Certificate. "
                f"Visit the official website for more details."
            ),
            'ta': (
                f"{name}. "
                f"Ithu oru {category} thittam. Thakuthiyaana makkalukku nera udavi vazhangugindrathu. "
                f"Thakuthy nibandhanaigalai poorththi seigiravar ellaarukkum payan kidaikkum. "
                f"Thakuthiyaana palaanaargalukku neraaga bank kanam moolam udavi kidaikkum. "
                f"Thevaiyana aanavaigal: Aadhaar Card, Bank Passbook, Varumaana Saanru, Vaazhvidam Saanru. "
                f"Mela vivarangalukku official website paarkkavum."
            ),
            'te': (
                f"{name}. "
                f"This is a government {category} scheme providing direct support to eligible citizens. "
                f"Eligible citizens receive direct bank support. "
                f"Documents needed: Aadhaar Card, Bank Passbook, Income Certificate, Residence Certificate. "
                f"Visit the official website for more details."
            ),
            'bn': (
                f"{name}. "
                f"Eita ekta {category} sarkar prakalpa jo yogya nagrikder seedha sahayata dey. "
                f"Je nagrik yogyatar sharta puraon karen tini ei prakalpar labh paben. "
                f"Yogya suvidhabhogiра seedha bank account-e arthik sahayata paben. "
                f"Darkari kagajpatra: Aadhaar Card, Bank Passbook, Aay Promanpatra, Basobas Promanpatra. "
                f"Bishad tathyer jonno official website dekun."
            ),
            'mr': (
                f"{name}. "
                f"Hi ek {category} sarkari yojana aahe jo paatra nagrikanna seedha madad karate. "
                f"Jo nagrik paatrata shartee poornya karato tyaala ya yojanecha labh milto. "
                f"Paatra laabhaarthinaa thety bank khatyaat rakkam dili jaate. "
                f"Aavashyak kagadpatre: Aadhaar Card, Bank Passbook, Utpanna Dakhala, Rahivasi Dakhala. "
                f"Adhik mahitisaathi official website bheta dya."
            ),
        }
        return messages.get(lang, messages['en'])