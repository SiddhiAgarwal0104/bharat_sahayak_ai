from fastapi import APIRouter, Depends
from backend.agents.orchestrator import Orchestrator
from backend.routers.auth_router import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/query", tags=["query"])
orchestrator = Orchestrator()

@router.post("")
async def query(request: dict, current_user: User = Depends(get_current_user)):
    return await orchestrator.handle({
        **request,
        "user_id": str(current_user.id),
        "action": "query",
    })