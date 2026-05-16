"""
Agent Session Store

Maps conversation_id → FinServChatAgent instance.
Agents are created on first use and evicted after TTL_SECONDS of inactivity.
This keeps sub-agent history in memory for multi-turn conversations without
needing to re-serialize the full Anthropic message history on every request.
"""

import logging
import time
from threading import Lock

logger = logging.getLogger(__name__)

TTL_SECONDS = 3600  # evict sessions idle for more than 1 hour


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, dict] = {}  # conv_id -> {agent, last_used}
        self._lock = Lock()

    def get(self, conv_id: str):
        """Return existing agent for this conversation, or None."""
        with self._lock:
            entry = self._sessions.get(conv_id)
            if entry:
                entry["last_used"] = time.monotonic()
                return entry["agent"]
        return None

    def put(self, conv_id: str, agent) -> None:
        """Store an agent for this conversation."""
        with self._lock:
            self._sessions[conv_id] = {
                "agent": agent,
                "last_used": time.monotonic(),
            }

    def get_or_create(self, conv_id: str, db_messages: list[dict] | None = None):
        """
        Return the agent for conv_id, creating and hydrating one if needed.

        Args:
            conv_id: Conversation ID.
            db_messages: Message rows from the database (used to hydrate history
                         when creating a new in-memory session).
        """
        from agent.chat_agent import FinServChatAgent

        agent = self.get(conv_id)
        if agent is not None:
            return agent

        logger.info("Creating new FinServChatAgent session for conv %s", conv_id)
        agent = FinServChatAgent()
        if db_messages:
            agent.load_history(db_messages)
        self.put(conv_id, agent)
        return agent

    def evict(self, conv_id: str) -> None:
        """Remove a session (e.g., when a conversation is deleted or cleared)."""
        with self._lock:
            self._sessions.pop(conv_id, None)

    def evict_stale(self) -> int:
        """Remove all sessions that have been idle longer than TTL_SECONDS."""
        cutoff = time.monotonic() - TTL_SECONDS
        with self._lock:
            stale = [k for k, v in self._sessions.items() if v["last_used"] < cutoff]
            for k in stale:
                del self._sessions[k]
        if stale:
            logger.info("Evicted %d stale sessions", len(stale))
        return len(stale)

    def __len__(self):
        with self._lock:
            return len(self._sessions)


# Module-level singleton used by all routers
store = SessionStore()
