# backend/agents/input_agent.py
# Member 4's orchestrator calls InputAgent().process()
from backend.services.stt_service import transcribe
from backend.utils.language_utils import detect_language

class InputAgent:
    def process(self, input_data: dict) -> dict:
        """
        input_data: {'type': 'audio'|'text', 'content': bytes|str}
        Returns IntentObject: {query_text, language, intent, slots, confidence}
        """
        if input_data.get("type") == "audio":
            stt      = transcribe(input_data["content"])
            text     = stt["text"]
            language = stt["language"]
        else:
            text     = input_data.get("content", "").strip()
            language = detect_language(text)

        try:
            from backend.services.nlp_service import classify
            nlp        = classify(text, language)
            intent     = nlp.get("intent", "other")
            slots      = nlp.get("slots", {})
            confidence = nlp.get("confidence", 0.0)
        except ImportError:
            intent, slots, confidence = self._fallback(text)

        return {"query_text": text, "language": language,
                "intent": intent, "slots": slots, "confidence": confidence}

    def _fallback(self, text: str) -> tuple:
        t = text.lower()
        if any(w in t for w in ["school","college","scholarship","vidya","shiksha","padhai","chhatri"]):
            return "education", {}, 0.75
        if any(w in t for w in ["kisan","farmer","krishi","fasal","crop","beej","pm kisan"]):
            return "agriculture", {}, 0.75
        if any(w in t for w in ["hospital","swasthya","doctor","ayushman","health","dawai"]):
            return "health", {}, 0.75
        if any(w in t for w in ["pension","vridha","retirement","senior","widow","divyang"]):
            return "pension", {}, 0.75
        return "other", {}, 0.5