from typing import Literal

from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
    agent_type: str | None = None

class ChatRequest(BaseModel):
    message: str
    user_id: int
    history: list[ChatMessage] | None = None

class ChatResponse(BaseModel):
    response: str
    agent_type: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
