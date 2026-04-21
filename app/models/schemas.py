from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    user_text: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    risk_level: str
    score: int
    evidence: List[str]
    model_provider: str
    model_name: str