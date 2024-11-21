from typing import Annotated, Dict
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    completed_nodes: Annotated[list[str], lambda x, y: list(set(x + y))]
    active_nodes: Annotated[list[str], lambda x, y: y]
    latest_router_decision: str
    user_context: Dict = {}
