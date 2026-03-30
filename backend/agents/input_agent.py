# backend/agents/input_agent.py
from backend.services.stt_service import transcribe
from backend.utils.language_utils import detect_language

# Import ONCE at module level — NOT inside process()
try:
    from backend.services.nlp_service import classify as _nlp_classify
    _NLP_AVAILABLE = True
    print("[InputAgent] NLP service loaded.", flush=True)
except Exception as e:
    _nlp_classify  = None
    _NLP_AVAILABLE = False
    print(f"[InputAgent] NLP unavailable: {e}", flush=True)


class InputAgent:

    def process(self, input_data: dict) -> dict:
        print("[InputAgent] process() called", flush=True)

        if input_data.get("type") == "audio":
            stt      = transcribe(input_data["content"])
            text     = stt["text"]
            language = stt["language"]
        else:
            text     = input_data.get("content", "").strip()
            language = detect_language(text)

        print(f"[InputAgent] text='{text[:50]}' language={language}", flush=True)

        if _NLP_AVAILABLE:
            try:
                print("[InputAgent] running NLP classify...", flush=True)
                nlp        = _nlp_classify(text, language)
                intent     = nlp.get("intent", "other")
                slots      = nlp.get("slots", {})
                confidence = nlp.get("confidence", 0.0)
                print(f"[InputAgent] intent={intent} confidence={confidence}", flush=True)
            except Exception as e:
                print(f"[InputAgent] NLP failed: {e}, using fallback", flush=True)
                intent, slots, confidence = self._fallback(text)
        else:
            intent, slots, confidence = self._fallback(text)

        return {
            "query_text": text,
            "language"  : language,
            "intent"    : intent,
            "slots"     : slots,
            "confidence": confidence,
        }

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
        if any(w in t for w in ["women","mahila","nari","ladki","girl","beti"]):
            return "women", {}, 0.75
        return "other", {}, 0.5