import streamlit as st

from .utils.chat import chat_interface
from .utils.user import handle_user_authentication
from .utils.init_session import initialize_session_state
from .utils.sidebar import render_sidebar

def main():
    """Main application flow."""
    st.set_page_config(
        page_title="Seez CRS",
        page_icon="💬",
        layout="wide"
    )
    
    initialize_session_state()
    
    if not st.session_state.user_id_entered:
        handle_user_authentication()
    else:
        render_sidebar()
        chat_interface()
