from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    user_text: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    risk_level: str
    score: int