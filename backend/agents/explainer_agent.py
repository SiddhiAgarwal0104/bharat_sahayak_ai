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
        name     = scheme.get('name', 'Yeh Yojana')
        category = scheme.get('category', 'sarkari')
        messages = {
            'hi': (
                f"**{name}**\n\n"
                f"**1. Yojana kya hai?**\n"
                f"Yeh bharat sarkar ki ek {category} yojana hai jo zarooratmand nagrikon ko seedha madad deti hai.\n\n"
                f"**2. Kise milega labh?**\n"
                f"Jo nagrik paatrata sharten poori karte hain unhe is yojana ka labh milta hai.\n\n"
                f"**3. Kya milega?**\n"
                f"Paatra laabhaarthi ko seedhe unke bank khate mein rashi ya seva ka labh diya jaata hai.\n\n"
                f"**4. Zaruri Dastaavez:**\n"
                f"- Aadhaar Card\n- Bank Passbook\n- Aay Praman Patra\n- Niwas Praman Patra\n\n"
                f"Adhik jaankari ke liye yojana ki official website par jayen."
            ),
            'en': (
                f"**{name}**\n\n"
                f"**1. What is this scheme?**\n"
                f"This is a government {category} scheme that provides direct support to eligible citizens.\n\n"
                f"**2. Who can benefit?**\n"
                f"Citizens who meet the eligibility criteria such as income, age, and documentation requirements.\n\n"
                f"**3. What is the benefit?**\n"
                f"Eligible beneficiaries receive financial support directly into their bank account.\n\n"
                f"**4. Documents needed:**\n"
                f"- Aadhaar Card\n- Bank Passbook\n- Income Certificate\n- Residence Certificate\n\n"
                f"Visit the official website for more details."
            ),
            'ta': (
                f"**{name}**\n\n"
                f"**1. Ith enna thittam?**\n"
                f"Ithu oru {category} thittam. Thakuthiyaana makkalukku nera udavi vazhangugindrathu.\n\n"
                f"**2. Yarukkு kidaikkum?**\n"
                f"Thakuthy nibandhanaigalai poorththi seigiravar ellaarukkum payan kidaikkum.\n\n"
                f"**3. Enna kidaikkum?**\n"
                f"Thakuthiyaana palaanaargalukku neraaga bank kanam moolam udavi kidaikkum.\n\n"
                f"**4. Thevaiyana Aanavaigal:**\n"
                f"- Aadhaar Card\n- Bank Passbook\n- Varumaana Saanru\n- Vaazhvidam Saanru\n\n"
                f"Mela vivarangalukku official website paarkkavum."
            ),
            'te': (
                f"**{name}**\n\n"
                f"**1. Ee patha enthi?**\n"
                f"Ithu oka {category} patha. Arthyna paurulatho neruuga sahaayam chesedi.\n\n"
                f"**2. Evariki labham?**\n"
                f"Arthatanu nibandhanalanu poorthi chesina vaallaku ee patha labham dosthundi.\n\n"
                f"**3. Emi labham?**\n"
                f"Arthulu neruuga bank account loki pampadataayi.\n\n"
                f"**4. Avasarama Dastavejulu:**\n"
                f"- Aadhaar Card\n- Bank Passbook\n- Aadaaya Dhruveekaran\n- Nivaasa Dhruveekaran\n\n"
                f"Ekkuva vivaraalu kosam official website choosandi."
            ),
            'bn': (
                f"**{name}**\n\n"
                f"**1. Ei prakalpa ki?**\n"
                f"Eita ekta {category} sarkar prakalpa jo yogya nagrikder seedha sahayata dey.\n\n"
                f"**2. Ke paben?**\n"
                f"Je nagrik yogyatar sharta puraon karen tini ei prakalpar labh paben.\n\n"
                f"**3. Ki paben?**\n"
                f"Yogya suvidhabhogiরা seedha bank account-e arthik sahayata paben.\n\n"
                f"**4. Darkari Kagajpatra:**\n"
                f"- Aadhaar Card\n- Bank Passbook\n- Aay Promanpatra\n- Basobas Promanpatra\n\n"
                f"Bishad tathyer jonno official website dekun."
            ),
            'mr': (
                f"**{name}**\n\n"
                f"**1. Hi yojana kaay aahe?**\n"
                f"Hi ek {category} sarkari yojana aahe jo paatra nagrikanna seedha madad karate.\n\n"
                f"**2. Konyala labh milel?**\n"
                f"Jo nagrik paatrata shartee poornya karato tyaala ya yojanecha labh milto.\n\n"
                f"**3. Kaay milel?**\n"
                f"Paatra laabhaarthinaa thety bank khatyaat rakkam dili jaate.\n\n"
                f"**4. Aavashyak Kagadpatre:**\n"
                f"- Aadhaar Card\n- Bank Passbook\n- Utpanna Dakhala\n- Rahivasi Dakhala\n\n"
                f"Adhik mahitisaathi official website bheta dya."
            ),
        }
        return messages.get(lang, messages['en'])