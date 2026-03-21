# backend/services/nlp_service.py

import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ── Build absolute path to model ─────────────────────────────────
_BASE_DIR  = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)
             )))
_MODEL_REL = os.getenv("MODEL_PATH", "data/model")
MODEL_PATH = os.path.join(_BASE_DIR, _MODEL_REL)

print(f"Loading model from: {MODEL_PATH}")

# ── Load model ONCE at startup ────────────────────────────────────
_tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
_model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
_model.eval()

with open(os.path.join(MODEL_PATH, "label_map.json"), encoding="utf-8") as f:
    _label_map = json.load(f)

print(f"Model loaded. Intents: {list(_label_map.values())}")


# ── Keyword slot extraction ───────────────────────────────────────
_SLOT_RULES = {
    "kisan"      : "farmer",
    "fasal"      : "crop",
    "tractor"    : "equipment",
    "sinchai"    : "irrigation",
    "scholarship": "scholarship",
    "chhatri"    : "scholarship",
    "school"     : "school",
    "college"    : "college",
    "ayushman"   : "ayushman",
    "hospital"   : "hospital",
    "dialysis"   : "dialysis",
    "pension"    : "pension",
    "vridha"     : "old_age",
    "atal"       : "atal_pension",
    "epf"        : "epf",
    "beti"       : "girl_child",
    "sukanya"    : "savings",
    "ujjwala"    : "lpg",
    "silai"      : "sewing",
}

def _extract_slots(text: str) -> dict:
    text_lower = text.lower()
    for keyword, value in _SLOT_RULES.items():
        if keyword in text_lower:
            return {"sub_category": value}
    return {}


# ── Main classify function ────────────────────────────────────────
def classify(text: str, language: str = "auto") -> dict:
    """
    Called by Member 1's input_agent.
    Returns: { intent, confidence, slots }
    """
    enc = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )
    with torch.no_grad():
        logits = _model(**enc).logits

    probs = torch.softmax(logits, dim=-1)[0]
    idx   = torch.argmax(probs).item()

    return {
        "intent"    : _label_map[str(idx)],
        "confidence": round(probs[idx].item(), 4),
        "slots"     : _extract_slots(text)
    }


# ── FastAPI router ────────────────────────────────────────────────
router = APIRouter(prefix="/nlp", tags=["nlp"])

class ClassifyRequest(BaseModel):
    text:     str
    language: str = "auto"

@router.post("/classify")
def classify_endpoint(req: ClassifyRequest):
    return classify(req.text, req.language)