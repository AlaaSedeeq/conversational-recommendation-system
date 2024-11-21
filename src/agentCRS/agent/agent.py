from typing import Dict, List, Callable

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver

from src.agentCRS.tools import fetch_user_info
from src.common.config import load_config
from .state import State

CONFIG = load_config()

class Agent:
    def __init__(self, system_prompt: str, model: BaseChatModel = None, tools: List[Callable] = [], name=""):
        self.system_prompt = system_prompt
        self.name = name
        
        workflow = StateGraph(State)
        
        workflow.add_node("init_session_state", self.init_session_state)
        workflow.add_node("fetch_user_information", fetch_user_info)
        workflow.add_node("llm", self.call_openai)
        workflow.add_node("search", self.do_search)

        workflow.add_conditional_edges(
            START,
            self.is_first_message,
            {"first_msg": "init_session_state", "not_first_msg": "llm"}
        )
        workflow.add_edge("init_session_state", "fetch_user_information")
        workflow.add_edge("fetch_user_information", "llm")
        workflow.add_conditional_edges(
            "llm",
            self.exists_search,
            {"search": "search", "response": END}
        )
        workflow.add_edge("search", "llm")

        checkpointer = MemorySaver()
        self.graph = workflow.compile(checkpointer=checkpointer)
        
        self.tools = {t.name: t for t in tools}

        model = model or ChatOpenAI(model=CONFIG.llms.openai.chat_model)
        self.model = model.bind_tools(tools)

    def init_session_state(
        self, 
        state,
        config
        )-> Dict:
        print("Initiating Session State")
    
        return {
            "user_context": {
                "user_data": {}, 
                "user_exists": "New",
            },
        }

    def update_system_prompt(self, prompt_config: dict) -> str:
        print(f"Updating system prompt for {self.name}...")
        try:
            if prompt_config and isinstance(prompt_config, dict):
                formatted_prompt = self.system_prompt.format_map(prompt_config)
                print(f"Using prompt config for {self.name}")
                print(formatted_prompt)
            else:
                formatted_prompt = self.system_prompt
                print(f"Using default prompt for {self.name},no prompt configs!")
        except KeyError as e:
            formatted_prompt = self.system_prompt
            print(f"Error formatting prompt for {self.name}: {e}")
        return formatted_prompt

    def exists_search(self, state: State):
        result = state['messages'][-1]
        return "search" if len(result.tool_calls) > 0 else "response"

    def is_first_message(self, state: State):
        return "first_msg" if len(state['messages']) == 1 else "not_first_msg"

    async def call_openai(self, state: State):
        messages = state['messages']
        system_prompt = self.update_system_prompt({**state["user_context"]["user_data"], "user_exists": state["user_context"]["user_exists"]})
        print("Sys: ", system_prompt)
        messages = [SystemMessage(content=system_prompt)] + messages
        message = await self.model.ainvoke(messages)
        return {'messages': [message]}

    async def do_search(self, state: State):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f"Calling: {t}")
            if not t['name'] in self.tools:
                print("\n ....bad tool name....")
                result = "bad tool name, retry"
            else:
                result = await self.tools[t['name']].ainvoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        print("Back to the model!")
        return {'messages': results}

    async def ainvoke(self, state: State, config: dict):
        return await self.graph.ainvoke(state, config)