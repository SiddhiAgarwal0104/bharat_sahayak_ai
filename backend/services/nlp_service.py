# backend/services/nlp_service.py

import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from huggingface_hub import hf_hub_download
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

HF_REPO  = os.getenv("HF_MODEL_REPO", "tanyabora/sahayakai-mbert-intent")
HF_TOKEN = os.getenv("HF_TOKEN")

print(f"Loading model from HuggingFace: {HF_REPO}")

# ── Load model ONCE at startup ────────────────────────────────────
_tokenizer = AutoTokenizer.from_pretrained(HF_REPO, token=HF_TOKEN)
_model     = AutoModelForSequenceClassification.from_pretrained(HF_REPO, token=HF_TOKEN)
_model.eval()

label_map_path = hf_hub_download(repo_id=HF_REPO, filename="label_map.json", token=HF_TOKEN)
with open(label_map_path, encoding="utf-8") as f:
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