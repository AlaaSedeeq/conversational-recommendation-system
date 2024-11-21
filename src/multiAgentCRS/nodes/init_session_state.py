from datetime import datetime
from typing import List, Callable, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import ToolMessage

async def init_session_state(state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    print("\nCurrent Node: Init Session State")
    return {
        "completed_nodes": [],
        "active_nodes": [],
        "latest_router_decision": "",
        "user_context": {
            "user_data": {}, 
            "user_exists": False,
        },
    }
