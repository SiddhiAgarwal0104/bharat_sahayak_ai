from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.llm_service import generate

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    prompt = (
        "You are Sahayak, a helpful AI assistant for a Indian government schemes portal. "
        "Help users understand and navigate government schemes clearly and accurately.\n"
        f"User: {req.message}"
    )

    try:
        reply = generate(prompt, 'en')
        if not reply:
            raise HTTPException(status_code=502, detail="LLM returned empty response.")
        return {"reply": reply}

    except HTTPException:
        raise  # re-raise clean HTTP errors as-is

    except Exception as e:
        print(f"[Chatbot] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))