from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from src.presentation.api.types import GraphType

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = datetime.now()
    graph_type: GraphType = GraphType.SINGLE

class UserState:
    def __init__(self, user_id: str = ""):
        self.user_id = user_id
        self.messages: list[Message] = []
        self.thread_id: Optional[str] = None
        self.last_interaction: datetime = datetime.now()
        self.current_graph: GraphType = GraphType.SINGLE

DEFAULT_ERROR_MESSAGE = "Something went wrong. Please try again later."
