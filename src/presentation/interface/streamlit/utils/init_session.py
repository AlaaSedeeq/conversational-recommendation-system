import streamlit as st

from src.presentation.api.client import ChatAPIClient
from .utils import UserState

def initialize_session_state():
    """Initialize session state variables."""
    if "user_state" not in st.session_state:
        st.session_state.user_state = UserState()
    if "user_id_entered" not in st.session_state:
        st.session_state.user_id_entered = False
    if "api_client" not in st.session_state:
        st.session_state.api_client = ChatAPIClient()
