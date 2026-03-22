from fastapi import APIRouter
from backend.agents.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()

@router.post("/query")
def query(body: dict):
    return orchestrator.handle(body)