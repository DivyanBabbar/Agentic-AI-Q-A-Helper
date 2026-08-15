"""Short-term conversation memory for session management."""

from collections import defaultdict
from typing import List, Dict


class ConversationMemory:
    """
    Manages short-term conversation memory with a sliding window.

    Memory is separated by session_id, storing user and assistant messages.
    Only the most recent N messages are retained.
    """

    def __init__(self, window_size: int = 10):
        """
        Initialize the conversation memory.

        Args:
            window_size: Maximum number of messages to retain per session.
                        Defaults to 10 (5 turns, since each turn has 2 messages).
        """
        self.window_size = window_size
        self.sessions: Dict[str, List[Dict[str, str]]] = defaultdict(list)

    def add_message(self, session_id: str, role: str, message: str) -> None:
        """
        Add a message to the session memory.

        Args:
            session_id: Unique identifier for the session.
            role: Either "user" or "assistant".
            message: The message content.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        # Add the message
        self.sessions[session_id].append({"role": role, "message": message})

        # Enforce the sliding window: keep only the most recent messages
        if len(self.sessions[session_id]) > self.window_size:
            self.sessions[session_id] = self.sessions[session_id][-self.window_size :]

    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Retrieve the message history for a session.

        Args:
            session_id: Unique identifier for the session.

        Returns:
            A list of message dictionaries with 'role' and 'message' keys.
        """
        return self.sessions.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        """
        Clear the memory for a specific session.

        Args:
            session_id: Unique identifier for the session to clear.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
