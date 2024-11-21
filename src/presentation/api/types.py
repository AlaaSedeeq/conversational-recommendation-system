from pydantic import BaseModel
from enum import Enum

class GraphType(Enum):
    SINGLE = "single"
    MULTI = "multi"

class ChatRequest(BaseModel):
    message: str
    user_id: str
    graph_type: str = "single"

class ChatResponse(BaseModel):
    response: dict
    thread_id: str
    is_new_session: bool
