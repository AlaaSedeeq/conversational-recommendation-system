from src.multiAgentCRS.nodes import AssistantNode
from src.multiAgentCRS.graph.prompts import recommender_old_prompt, recommender_new_prompt, follow_up_prompt
from src.multiAgentCRS.tools import get_recommendations

recommender_old_tools = [get_recommendations]
recommender_old_node = AssistantNode(
    name="recommender_old", 
    system_prompt=recommender_old_prompt, 
    tools=recommender_old_tools
)

# Recommender Agent for new users
recommender_new_node = AssistantNode(
    name="recommender_new", 
    system_prompt=recommender_new_prompt, 
)

# Follow-up Agent
follow_up_tools = [get_recommendations]
follow_up_node = AssistantNode(
    name="follow_up", 
    system_prompt=follow_up_prompt, 
    tools=follow_up_tools,
    completion_tool=get_recommendations.func.__name__
)