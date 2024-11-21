from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from .db import SessionManager
from .types import ChatRequest, ChatResponse
from src.multiAgentCRS.graph.builder import build_multi_agent_graph
from src.agentCRS.builder import build_single_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.single_graph = build_single_agent()
    app.state.multi_agent_graph = build_multi_agent_graph()
    app.state.session_manager = SessionManager()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        thread_id, is_new_session = app.state.session_manager.get_or_create_session(
            request.user_id
        )
        
        graph_type = request.graph_type.lower()
        if graph_type not in ["multi", "single"]:
            raise HTTPException(status_code=400, detail="Invalid graph type")
            
        graph = (
            app.state.multi_agent_graph 
            if graph_type == "multi" 
            else app.state.single_graph
        )
        
        response = await graph.ainvoke(
            {"messages": ("user", request.message)},
            {"configurable": {"thread_id": thread_id, "user_id": request.user_id}}
        )
        
        app.state.session_manager.update_last_interaction(request.user_id)
        
        return ChatResponse(
            response=response,
            thread_id=thread_id,
            is_new_session=is_new_session
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/session/{user_id}")
async def get_session_info(user_id: str):
    """Get session information for a user."""
    session_info = app.state.session_manager.get_session_info(user_id)
    if session_info:
        return session_info
    raise HTTPException(status_code=404, detail="Session not found")
