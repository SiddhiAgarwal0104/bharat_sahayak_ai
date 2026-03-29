from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.llm_service import generate

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        if not req.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty.")
            
        # The user requested a generic chatbot unconnected from the rest of the website's auth
        prompt = (
            f"You are a helpful and polite AI assistant. "
            f"Please answer the following user question clearly and accurately:\n"
            f"User: {req.message}"
        )

        reply = generate(prompt, 'en') # Defaulting to generic/english logic
        if not reply:
            reply = "Sorry, I could not generate a response at this time."

        return {"reply": reply}

    except Exception as e:
        print(f"[Chatbot] Error processing chat: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while communicating with the assistant.")
