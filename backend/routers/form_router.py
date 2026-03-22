from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.agents.orchestrator import Orchestrator
from backend.agents.form_agent import FormAgent
from backend.routers.auth_router import get_current_user
from backend.models.user import User

router       = APIRouter()
orchestrator = Orchestrator()
form_agent   = FormAgent()

@router.post("/{scheme_id}/start")
async def start_form(scheme_id: str, current_user: User = Depends(get_current_user)):
    result = await orchestrator.handle({
        "user_id"   : str(current_user.id),
        "action"    : "apply",
        "scheme_id" : scheme_id,
        "language"  : current_user.language_pref or "hi",
        "input_type": "text",
        "content"   : "",
    })
    return result

@router.get("/{scheme_id}/step/{n}")
async def get_step(scheme_id: str, n: int, session_id: str,
                   current_user: User = Depends(get_current_user)):
    step = await form_agent.get_step(session_id, n, current_user.language_pref or "hi")
    if step is None:
        raise HTTPException(status_code=404, detail="No more fields")
    return step

@router.post("/{scheme_id}/next")
async def next_step(scheme_id: str, session_id: str,
                    current_user: User = Depends(get_current_user)):
    new_index = await form_agent.advance(session_id)
    step = await form_agent.get_step(session_id, new_index, current_user.language_pref or "hi")
    return step if step else {"completed": True}

@router.post("/{scheme_id}/back")
async def prev_step(scheme_id: str, session_id: str,
                    current_user: User = Depends(get_current_user)):
    new_index = await form_agent.go_back(session_id)
    step = await form_agent.get_step(session_id, new_index, current_user.language_pref or "hi")
    return step

@router.post("/{scheme_id}/complete")
async def complete_form(scheme_id: str, session_id: str,
                        current_user: User = Depends(get_current_user)):
    await form_agent.complete_session(session_id)
    return {"message": "Form guidance completed!", "session_id": session_id}

class QueryRequest(BaseModel):
    input_type : str            = "text"
    content    : str            = ""
    action     : str            = "query"
    scheme     : Optional[dict] = None
    scheme_id  : Optional[str]  = None

@router.post("/query")
async def query(body: QueryRequest, current_user: User = Depends(get_current_user)):
    result = await orchestrator.handle({
        "user_id"   : str(current_user.id),
        "input_type": body.input_type,
        "content"   : body.content,
        "action"    : body.action,
        "language"  : current_user.language_pref or "hi",
        "scheme"    : body.scheme,
        "scheme_id" : body.scheme_id,
    })
    return result
