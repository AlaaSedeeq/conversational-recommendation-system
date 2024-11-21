from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.multiAgentCRS.nodes import fetch_user_information, init_session_state
from src.multiAgentCRS.graph.state import State
from src.multiAgentCRS.graph.nodes import follow_up_node, recommender_old_node, recommender_new_node, follow_up_tools, recommender_old_tools
from src.multiAgentCRS.graph.edges import start_decision, fetch_user_info_decision, follow_up_decision, recommender_old_decision
from src.multiAgentCRS.utils import create_tool_node_with_fallback

def build_multi_agent_graph():
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("init_session_state", init_session_state)
    workflow.add_node("fetch_user_information", fetch_user_information)

    workflow.add_node("follow_up", follow_up_node)
    workflow.add_node("follow_up_tools", create_tool_node_with_fallback(follow_up_tools))

    workflow.add_node("recommender_old", recommender_old_node)
    workflow.add_node("recommender_new", recommender_new_node)
    workflow.add_node("recommender_tools", create_tool_node_with_fallback(recommender_old_tools))

    # Add edges 
    workflow.add_conditional_edges(
        START, 
        start_decision, 
        ["init_session_state", "follow_up", "recommender_old", "recommender_new"], #"router", ]
    )

    workflow.add_edge("init_session_state", "fetch_user_information")
    workflow.add_conditional_edges(
        "fetch_user_information",
        fetch_user_info_decision,
        ["recommender_old", "follow_up"]
    )

    workflow.add_edge("recommender_tools", "recommender_old")
    workflow.add_conditional_edges(
        "recommender_old", 
        recommender_old_decision, 
        ["recommender_tools", END]
    )
    workflow.add_edge("recommender_new", END)

    workflow.add_edge("follow_up_tools", "follow_up")
    workflow.add_conditional_edges(
        "follow_up",
        follow_up_decision, 
        ["recommender_new", "follow_up_tools", END]
    )

    # Compile the graph
    checkpointer = MemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph