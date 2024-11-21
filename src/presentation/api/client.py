import aiohttp
from typing import Optional, Dict, Any

from src.common.config import load_config
from src.common.logger import logger
from .types import GraphType

CONFIG = load_config()

class ChatAPIClient:
    def __init__(self, timeout: int = 60):
        self.base_url = CONFIG.api.base_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_thread_id: Optional[str] = None

    async def ensure_session(self):
        """Ensure an active client session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self):
        """Close the client session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def chat(self, message: str, user_id: str, graph_type: GraphType = GraphType.SINGLE) -> Dict[str, Any]:
        """Send a chat message and get response."""
        await self.ensure_session()
        try:
            async with self.session.post(
                f"{self.base_url}/chat",
                json={
                    "message": message,
                    "user_id": user_id,
                    "graph_type": graph_type.value
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.current_thread_id = result.get("thread_id")
                    return result
                else:
                    error_detail = await response.text()
                    raise Exception(f"Error {response.status}: {error_detail}")
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}", exc_info=True)
            return None

    async def get_session_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get session information for a user."""
        await self.ensure_session()
        try:
            async with self.session.get(
                f"{self.base_url}/session/{user_id}"
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting session info: {str(e)}", exc_info=True)
            return None
