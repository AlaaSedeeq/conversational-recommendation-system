from langgraph.graph import END
from langgraph.prebuilt import tools_condition
from src.multiAgentCRS.graph.state import State
from src.multiAgentCRS.graph.nodes import follow_up_node

# Routing Functions
def start_decision(state: State):
    tool_msgs = [tool.name for tool in [msg for msg in state["messages"] if msg.type == "tool"]]
    if len(state["messages"]) == 1:
        return "init_session_state"
    
    elif not state["user_context"]["user_exists"]:
        if follow_up_node.completion_tool in tool_msgs: #and "follow_up" in state["active_nodes"]
            return "recommender_new"
        else:
            return "follow_up"
    return "recommender_old"

def fetch_user_info_decision(state):
    if state["user_context"]["user_exists"]:
        return "recommender_old"
    return "follow_up"

def recommender_old_decision(state: State):
    route = tools_condition(state)
    if route == END:
        return END
    return "recommender_tools"

def follow_up_decision(state: State):
    route = tools_condition(state)    
    tool_msgs = [tool.name for tool in [msg for msg in state["messages"] if msg.type == "tool"]]
    if route == END:
        if state["user_context"]["user_exists"] or follow_up_node.completion_tool in tool_msgs:
            return "recommender_new"            
        else: 
            return END
    return "follow_up_tools"
