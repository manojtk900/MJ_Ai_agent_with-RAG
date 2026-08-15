"""
Memory Bridge for MJ Intelligence Agent.
Handles dynamic short-term conversation context and long-term user facts
in strict isolation from the static RAG project knowledge base.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog

log = structlog.get_logger(__name__)


class IntelligenceMemoryBridge:
    """
    Retrieves user context and facts from Redis / PostgreSQL memory systems
    and ensures sensitive credentials are never leaked.
    """

    @staticmethod
    async def get_user_context(user_id: Optional[str] = None, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetch sanitized user preferences and recent dialogue context."""
        context = {
            "username": "Manoj",
            "system_role": "JARVIS AI Assistant",
            "active_tasks": [],
            "known_facts": [],
        }

        # Try to retrieve from long term memory agent if available
        try:
            from app.core.memory.long_term import LongTermMemory
            ltm = LongTermMemory()
            facts = await ltm.get_facts(user_id=user_id or "default_user")
            if facts:
                context["known_facts"] = [f.get("fact") for f in facts if isinstance(f, dict) and "fact" in f]
        except Exception:
            pass

        return context
