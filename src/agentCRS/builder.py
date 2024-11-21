from src.agentCRS.agent import Agent
from src.agentCRS.tools import get_recommendations
from src.agentCRS.prompts import agent_system_prompt

def build_single_agent():
    return  Agent(tools=[get_recommendations], system_prompt=agent_system_prompt, name="Recommender")
