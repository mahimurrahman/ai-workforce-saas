from fastapi import APIRouter, HTTPException

from app.agents.orchestrator import AgentOrchestrator
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
orchestrator = AgentOrchestrator()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        return await orchestrator.route_message(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
