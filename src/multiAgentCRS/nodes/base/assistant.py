from typing import List, Callable, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import ToolMessage

class AssistantNode:
    def __init__(
            self, 
            name: str, 
            system_prompt: str, 
            tools: List[Callable] = None, 
            completion_tool: str = "", 
            llm_chain: Optional[Runnable] = None,
            model_name: str = "gpt-4"
    ) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.completion_tool = completion_tool
        self.llm = llm_chain or ChatOpenAI(model=model_name)

    def update_system_prompt(self, prompt_config: dict) -> str:
        print(f"Updating system prompt for {self.name}...")
        try:
            if prompt_config and isinstance(prompt_config, dict):
                formatted_prompt = self.system_prompt.format_map(prompt_config)
                print(f"Using prompt config for {self.name}")
            else:
                formatted_prompt = self.system_prompt
                print(f"Using default prompt for {self.name}, no prompt configs!")
            return formatted_prompt
            
        except KeyError as e:
            print(f"Error formatting prompt for {self.name}: {e}")
            return self.system_prompt

    def is_completed(self, state: Dict[str, Any]) -> bool:
        messages = state.get("messages", [])
        return any(
            isinstance(msg, ToolMessage) and msg.name == self.completion_tool
            for msg in reversed(messages)
        )

    async def __call__(self, state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        print(f"Current Node: {self.name.title()}\n")
        
        system_prompt = self.update_system_prompt(
            {**state["user_context"]["user_data"]}
        )
        
        assistant_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}")
        ])
        
        llm_chain = (
            assistant_prompt | self.llm.bind_tools(self.tools)
            if self.tools
            else assistant_prompt | self.llm
        )
        
        while True:
            response = await llm_chain.ainvoke(state)
            
            if response.tool_calls or (
                response.content and (
                    not isinstance(response.content, list) or 
                    response.content[0].get("text")
                )
            ):
                break
                
            state = {
                **state, 
                "messages": state["messages"] + [
                    ("user", "Your last response was empty. Please provide a correct response.")
                ]
            }

        # Update state based on completion status
        if self.is_completed({**state, "messages": state["messages"] + [response]}):
            active_nodes = list(set(state["active_nodes"]) - {self.name})
            return {
                "messages": response, 
                "completed_nodes": [self.name], 
                "active_nodes": active_nodes
            }
            
        active_nodes = list(set(state["active_nodes"]) | {self.name})
        return {
            "messages": response, 
            "active_nodes": active_nodes
        }
