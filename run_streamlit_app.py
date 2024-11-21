import os
import streamlit as st

def setup_openai_key():
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            pass
    
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found. Please set it either as an environment variable "
            "or in the Streamlit secrets management."
        )
    
    os.environ["OPENAI_API_KEY"] = api_key
    return api_key

if __name__ == "__main__":
    try:
        setup_openai_key()

        from src.presentation.interface.streamlit.app import main
        from src.common.logger import logger

        import asyncio
        
        try:
            main()
        except Exception as e:
            st.error(f"Application error: {str(e)}")
            logger.error("Application failed", exc_info=True)
        finally:
            # Cleanup API client session
            if "api_client" in st.session_state:
                asyncio.run(st.session_state.api_client.close())

        # from src.presentation.interface.streamlit.app import start_chat
        # from src.presentation.interface.streamlit.utils.session import init_session

        # init_session()
        # start_chat()
        
    except Exception as e:
        st.error(f"Error during startup: {str(e)}")
        raise
