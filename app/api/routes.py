from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.agents.orchestrator import AgentOrchestrator
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
orchestrator = AgentOrchestrator()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        response = await orchestrator.route_message(request)
        # TODO: Save conversation to DB
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))