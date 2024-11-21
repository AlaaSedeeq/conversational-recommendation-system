import streamlit as st

from src.presentation.api.types import GraphType

def handle_user_authentication():
    """Handle user authentication flow with agent type selection."""
    st.markdown("### User Authentication")
    st.markdown(
        "To mimic the Amazon login experience, as I can not map usernames to user ids",
    )
    
    # Add agent type selection at login
    graph_type = st.radio(
        "Select Agent Type",
        ["Multi Agent", "Single Agent"],
        key="initial_graph_type",
        horizontal=True,
    )
    
    user_id = st.text_input(
        "Please enter user id:",
        placeholder="Enter your user ID",
        key="user_id_input"
    )
    
    st.markdown(
        "Examples of old user ids: A1EMDSTJDUE6B0, A31I3HXMD5H1EL, A33V29EHMG9XVJ",
        help="These are sample user IDs for testing"
    )
    
    if st.button("Enter", key="auth_button"):
        if user_id.strip():
            st.session_state.user_state.user_id = user_id
            # Set the graph type at login
            st.session_state.user_state.current_graph = (
                GraphType.MULTI if graph_type == "Multi Agent" else GraphType.SINGLE
            )
            st.session_state.user_id_entered = True
            st.rerun()
        else:
            st.error("Please enter a valid user ID")
