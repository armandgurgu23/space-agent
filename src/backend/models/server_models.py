from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict

# Request/Response models
class StartChatResponse(BaseModel):
    session_id: str
    message: str
    created_at: datetime


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    session_id: str
    user_message: str
    assistant_response: str
    timestamp: datetime


class ChatHistory(BaseModel):
    session_id: str
    messages: List[Dict[str, str]]