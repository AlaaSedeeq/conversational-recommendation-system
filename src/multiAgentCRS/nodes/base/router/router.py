from typing import Dict, List, Any, Optional, Union, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage, AIMessage, ToolMessage
from langchain_core.messages.tool import ToolCall

from src.multiAgentCRS.graph.state import State

from .types import RouterResponse

class Router:
    def __init__(
        self,
        nodes: Union[List[str], Dict[str, str]], 
        system_prompt: str,
        llm: Optional[ChatOpenAI] = None,
        model: str = "",
        default_node: Optional[str] = None,
        max_preview: int = 100,
        max_history: int = 10,
        k_latest_messages: int = 6,
        max_assistant_preview: int = 20,
        default_tool_response: str = "Tool successfully executed",
        default_model: str = "gpt-4o"
    ) -> None:
        """
        Initialize Router node.
        
        Args:
            nodes: List of node names or Dict of node names to descriptions
            llm: Language model instance (optional)
            model: Model name (optional)
            system_prompt: System prompt for the router (optional)
            default_node: Default node to route to (optional)
        """
        self.model = model if "gpt-4o" in model else default_model
        self.llm = llm or ChatOpenAI(model=self.model).with_structured_output(RouterResponse)
        self.nodes = nodes
        self.default_node = default_node or self._get_default_node()
        self.system_prompt = system_prompt
        self.max_preview = max_preview
        self.max_history = max_history
        self.k_latest_messages = k_latest_messages
        self.max_assistant_preview = max_assistant_preview
        self.default_tool_response = default_tool_response or "Tool successfully executed"

    def _get_default_node(self) -> str:
        """Get default node from nodes configuration."""
        return (
            self.nodes[0] if isinstance(self.nodes, list) 
            else list(self.nodes.keys())[0]
        )

    def _format_message(self, message: AnyMessage) -> Optional[str]:
        """Format a single message for history."""
        if isinstance(message, HumanMessage):
            return f"User: {message.content}"
        elif isinstance(message, AIMessage) and message.content:
            preview = message.content[:self.max_preview] + "...(preview)"
            return f"Assistant: {preview}"
        return None

    def _prepare_message_history(self, messages: List[AnyMessage]) -> str:
        """Prepare message history for router context."""
        formatted_messages = [
            msg for msg in (self._format_message(m) for m in messages)
            if msg is not None
        ]
        return "\n".join(formatted_messages)

    def _get_nodes_description(self, state: State) -> Tuple[List[str], str]:
        """Get available nodes and their description."""
        completed_nodes = state.get("completed_nodes", [])

        if isinstance(self.nodes, list):
            available_nodes = [
                node for node in self.nodes 
                if node not in completed_nodes
            ]
            nodes_description = ", ".join(available_nodes)
        else:
            available_nodes = {
                node: desc 
                for node, desc in self.nodes.items() 
                if node not in completed_nodes
            }
            nodes_description = "\n".join(
                f"- {node}: {desc}" 
                for node, desc in available_nodes.items()
            )
            available_nodes = list(available_nodes.keys())

        return available_nodes, nodes_description

    def _create_router_messages(self, 
                              state: State, 
                              nodes_description: str) -> List[Union[SystemMessage, HumanMessage]]:
        """Create messages for router LLM."""
        system_prompt = (
            f"{self.system_prompt}\n\n"
            f"Available agents:\n{nodes_description}\n\n"
            "Output should be with two keys: "
            "'agent_name' (the name of the best-suited agent) and 'request' (a concise summary of the user's request)."
        )
        latest_messages = self._prepare_message_history(state.get("messages", []))
        user_msg = f"Chat History:\n{latest_messages}\n\nAgents Name:"
        
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_msg)
        ]

    def _add_router_tool(self, router_response: RouterResponse) -> Dict[str, Any]:
        """Add route tool to state."""
        routing_message = (
            f"The assistant is now the {router_response.agent_name}. "
            "Reflect on the above conversation between the host assistant and the user. "
            "Do not mention who you are - just act as the proxy for the assistant."
            )
        messages = [
            AIMessage(content="", tool_calls=[ToolCall(name="Router", args={"agent_name": router_response.agent_name, "request": router_response.request}, id="")]),
            ToolMessage(content=routing_message, name="Router", tool_call_id=""),
            ]
        return messages

    def __call__(self, state: State, config: RunnableConfig) -> Dict[str, Any]:
        """Route to appropriate node based on conversation state."""
        print("\nCurrent Node: Router")
        
        available_nodes, nodes_description = self._get_nodes_description(state)
        
        if not available_nodes:
            print(f"Router selected default node: {self.default_node}")
            return {"latest_router_decision": self.default_node}

        messages = self._create_router_messages(state, nodes_description)
        
        while True:
            try:
                response = self.llm.invoke(messages)
                print("Response: ", response)
                node_name = response.agent_name
                
                if node_name and node_name in available_nodes:
                    break
                    
                messages.append(
                    HumanMessage(
                        content="Not a valid node! Please try again. "
                        f"Your output should be an agent name from the available agents {available_nodes}."
                    )
                )
            except Exception as e:
                print(f"Error in router: {e}")
                node_name = self.default_node

        print(f"Router selected: {node_name}")
        
        messages = self._add_router_tool(response)
        return {"messages": messages,  "latest_router_decision": node_name}
