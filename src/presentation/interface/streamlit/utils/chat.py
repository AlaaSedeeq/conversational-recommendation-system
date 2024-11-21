import streamlit as st
from typing import Optional
import asyncio

from src.common.logger import logger
from .utils import Message, DEFAULT_ERROR_MESSAGE

async def process_chat_message(message: str) -> Optional[str]:
    """Process a single chat message and return response."""
    try:
        client = st.session_state.api_client
        
        result = await client.chat(
            message=message,
            user_id=st.session_state.user_state.user_id,
            graph_type=st.session_state.user_state.current_graph
        )
        
        if result and "response" in result:
            response_content = result["response"]["messages"][-1]["content"]
            
            if "thread_id" in result:
                st.session_state.user_state.thread_id = result["thread_id"]
                
            return response_content
        
        return DEFAULT_ERROR_MESSAGE
            
    except Exception as e:
        logger.error(f"Failed to get chatbot response: {str(e)}", exc_info=True)
        return DEFAULT_ERROR_MESSAGE

def chat_interface():
    """Main chat interface without agent type selection."""
    st.title("Seez-CRS")
    
    # Subtle indicator of current agent type
    st.markdown(
        f"""<div style='padding: 0.5rem; background-color: #f0f7ff; border-radius: 5px; 
        display: inline-block; font-size: 0.9rem;'>
        🤖 Active Agent: <strong>{st.session_state.user_state.current_graph.value.replace('_', ' ').title()}</strong>
        </div>""",
        unsafe_allow_html=True
    )
    
    for msg in st.session_state.user_state.messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)
            st.caption(f"{msg.timestamp.strftime('%H:%M:%S')} - {msg.graph_type.value}")

    if prompt := st.chat_input("Write your question about cars...", key="chat_input"):
        user_msg = Message(
            role="user",
            content=prompt,
            graph_type=st.session_state.user_state.current_graph
        )
        st.session_state.user_state.messages.append(user_msg)
        
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"{user_msg.timestamp.strftime('%H:%M:%S')} - {user_msg.graph_type.value}")

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Processing your request..."):
                response = asyncio.run(process_chat_message(prompt))
                
            if response:
                assistant_msg = Message(
                    role="assistant",
                    content=response,
                    graph_type=st.session_state.user_state.current_graph
                )
                st.session_state.user_state.messages.append(assistant_msg)
                message_placeholder.markdown(response)
                st.caption(f"{assistant_msg.timestamp.strftime('%H:%M:%S')} - {assistant_msg.graph_type.value}")
