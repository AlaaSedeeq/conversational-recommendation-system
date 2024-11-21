import sqlite3
from datetime import datetime, timedelta
import uuid
from typing import Optional, Tuple

from src.common.config import load_config

CONFIG = load_config()

class SessionManager:
    def __init__(self, session_timeout_minutes: int = 10):
        self.db_path = CONFIG.data.session_db
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    last_interaction TIMESTAMP NOT NULL
                )
            """)
            conn.commit()

    def get_or_create_session(self, user_id: str) -> Tuple[str, bool]:
        """
        Get existing valid session or create new one.
        Returns: (thread_id, is_new_session)
        """
        with sqlite3.connect(self.db_path) as conn:
            current_time = datetime.utcnow()
            
            # Check existing session
            result = conn.execute("""
                SELECT thread_id, last_interaction 
                FROM user_sessions 
                WHERE user_id = ?
            """, (user_id,)).fetchone()

            if result:
                thread_id, last_interaction = result
                last_interaction = datetime.fromisoformat(last_interaction)
                
                # Check if session is still valid
                if current_time - last_interaction <= self.session_timeout:
                    # Update last interaction time
                    conn.execute("""
                        UPDATE user_sessions 
                        SET last_interaction = ? 
                        WHERE user_id = ?
                    """, (current_time.isoformat(), user_id))
                    return thread_id, False

            # Create new session
            new_thread_id = str(uuid.uuid4())
            conn.execute("""
                INSERT OR REPLACE INTO user_sessions (user_id, thread_id, last_interaction)
                VALUES (?, ?, ?)
            """, (user_id, new_thread_id, current_time.isoformat()))
            conn.commit()
            return new_thread_id, True

    def update_last_interaction(self, user_id: str) -> None:
        """Update the last interaction timestamp for a user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE user_sessions 
                SET last_interaction = ? 
                WHERE user_id = ?
            """, (datetime.utcnow().isoformat(), user_id))
            conn.commit()

    def get_session_info(self, user_id: str) -> Optional[dict]:
        """Get session information for a user."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT thread_id, last_interaction 
                FROM user_sessions 
                WHERE user_id = ?
            """, (user_id,)).fetchone()
            
            if result:
                thread_id, last_interaction = result
                return {
                    "user_id": user_id,
                    "thread_id": thread_id,
                    "last_interaction": last_interaction
                }
            return None
