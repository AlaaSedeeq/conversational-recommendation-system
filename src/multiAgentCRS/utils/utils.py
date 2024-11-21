from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage

def save_graph_image(graph, output_path: str = "data/multi_agent_graph.png"):
    try:
        # Get the PNG bytes from the graph
        png_data = graph.get_graph(xray=True).draw_mermaid_png()
        
        # Save the bytes directly to a file
        with open(output_path, 'wb') as f:
            f.write(png_data)
            
        print(f"Graph visualization saved to: {output_path}")
        
    except Exception as e:
        print(f"Error saving graph visualization: {e}")


def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], 
        exception_key="error"
    )

