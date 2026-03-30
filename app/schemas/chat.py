from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    user_id: int
    context: dict = {}

class ChatResponse(BaseModel):
    response: str
    agent_type: str
    confidence: float = 0.0