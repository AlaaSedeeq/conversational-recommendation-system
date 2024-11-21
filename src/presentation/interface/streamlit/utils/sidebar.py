import streamlit as st
from datetime import datetime
from .utils import UserState

def render_session_info():
    """Render session information in a clean, styled way."""
    st.markdown("### 🔍 Session Information")
    
    # Create container with custom styling
    container_style = """
        <style>
            .stMarkdown {
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
            }
            .info-label {
                color: #666;
                font-size: 0.9rem;
                margin-bottom: 0.2rem;
            }
            .info-value {
                background-color: white;
                padding: 0.5rem;
                border-radius: 5px;
                font-family: monospace;
                font-size: 0.9rem;
                word-break: break-all;
                margin-bottom: 1rem;
            }
            .info-stats {
                display: flex;
                justify-content: space-between;
                margin-bottom: 1rem;
            }
            .stat-box {
                flex: 1;
                text-align: center;
                background-color: white;
                padding: 0.5rem;
                border-radius: 5px;
                margin: 0 0.25rem;
            }
        </style>
    """
    st.markdown(container_style, unsafe_allow_html=True)
    
    # User ID
    st.markdown("<p class='info-label'>👤 User ID</p>", unsafe_allow_html=True)
    st.code(st.session_state.user_state.user_id, language=None)
    
    # Thread ID
    st.markdown("<p class='info-label'>🧵 Thread ID</p>", unsafe_allow_html=True)
    thread_id = st.session_state.user_state.thread_id or "Not started"
    st.code(thread_id, language=None)
    
    # Stats in columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p class='info-label'>💬 Messages</p>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='stat-box'>{len(st.session_state.user_state.messages)}</div>",
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown("<p class='info-label'>🤖 Agent</p>", unsafe_allow_html=True)
        agent_type = st.session_state.user_state.current_graph.value.replace('_', ' ').title()
        st.markdown(
            f"<div class='stat-box'>{agent_type}</div>",
            unsafe_allow_html=True
        )
    
    # Last updated
    st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

def render_session_controls():
    """Render session control buttons."""
    st.markdown("### 🎮 Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "🔄 New Chat",
            key="new_session",
            help="Start a new chat while keeping the same agent",
            use_container_width=True,
        ):
            current_graph = st.session_state.user_state.current_graph
            st.session_state.user_state = UserState(
                st.session_state.user_state.user_id
            )
            st.session_state.user_state.current_graph = current_graph
            st.rerun()
    
    with col2:
        if st.button(
            "🔀 Switch Agent",
            key="change_agent",
            help="Go back to login to select a different agent",
            use_container_width=True,
        ):
            st.session_state.user_id_entered = False
            st.rerun()

def render_sidebar():
    """Render the complete sidebar."""
    with st.sidebar:
        render_session_info()
        st.markdown("---")
        render_session_controls()
        st.markdown("---")
