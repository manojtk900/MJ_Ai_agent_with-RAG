"""
Context Engineering Engine — Builds rich context for every agent invocation.
This is the "Context Engineering" layer: more than prompt engineering.

Assembles:
- User preferences and profile
- Relevant long-term memories (pgvector search)
- Recent conversation history (Redis)
- Current task state
- System/time context
- Permission context
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

log = structlog.get_logger(__name__)


class ContextEngine:
    """
    Builds a rich context dictionary that every agent uses.
    
    Context includes:
    - who the user is
    - what they've done before
    - what they prefer
    - what's currently happening
    - what permissions they have
    """

    async def build(
        self,
        user_id: Optional[str],
        conversation_id: Optional[str],
        current_input: str,
        task_history_limit: int = 5,
        memory_limit: int = 8,
    ) -> Dict[str, Any]:
        """Build the full context dictionary."""
        context: Dict[str, Any] = {}

        # ── System Context ────────────────────────────────────
        now = datetime.now(timezone.utc)
        context["current_datetime"] = now.isoformat()
        context["current_date"] = now.strftime("%Y-%m-%d")
        context["current_time"] = now.strftime("%H:%M UTC")
        context["day_of_week"] = now.strftime("%A")

        if not user_id:
            return context

        # ── User Profile ──────────────────────────────────────
        try:
            user_prefs = await self._get_user_preferences(user_id)
            context["user_preferences"] = user_prefs
            context["username"] = user_prefs.get("username", "User")
            context["autonomy_level"] = user_prefs.get("autonomy_level", 1)
            context["timezone"] = user_prefs.get("timezone", "UTC")
        except Exception as e:
            log.warning("Failed to load user prefs", error=str(e))

        # ── Relevant Memories ─────────────────────────────────
        try:
            memories = await self._get_relevant_memories(user_id, current_input, limit=memory_limit)
            if memories:
                context["relevant_memories"] = [
                    {"content": m["content"], "type": m["type"], "score": m["score"]}
                    for m in memories
                ]
        except Exception as e:
            log.warning("Failed to load memories", error=str(e))

        # ── Recent Conversation ───────────────────────────────
        if conversation_id:
            try:
                recent_messages = await self._get_recent_messages(conversation_id)
                context["recent_messages_count"] = len(recent_messages)
            except Exception as e:
                log.warning("Failed to load messages", error=str(e))

        # ── Task History ──────────────────────────────────────
        try:
            recent_tasks = await self._get_recent_tasks(user_id, limit=task_history_limit)
            if recent_tasks:
                context["recent_tasks"] = recent_tasks
        except Exception as e:
            log.warning("Failed to load task history", error=str(e))

        # ── Permission Context ────────────────────────────────
        context["permissions"] = {
            "can_execute_code": True,
            "can_browse_web": True,
            "can_send_email": False,    # Requires explicit grant
            "can_delete_files": False,  # Always requires approval
            "can_access_github": True,
        }

        log.debug("Context built", keys=list(context.keys()), user=user_id)
        return context

    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Load user preferences from Redis cache or PostgreSQL."""
        from app.core.memory.short_term import redis_memory
        cached = await redis_memory.get_preferences(user_id)
        if cached:
            return cached

        # Fallback to DB
        from app.models.base import AsyncSessionLocal
        from app.models.user import User
        from sqlalchemy import select
        import uuid
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.id == uuid.UUID(user_id))
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                prefs = {
                    "username": user.username,
                    "autonomy_level": user.autonomy_level,
                    "timezone": user.timezone,
                    "default_model": user.default_model,
                    "voice_enabled": user.voice_enabled,
                }
                await redis_memory.cache_preferences(user_id, prefs)
                return prefs
        return {}

    async def _get_relevant_memories(self, user_id: str, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Semantic search for relevant memories."""
        from app.core.memory.long_term import LongTermMemory
        lt = LongTermMemory()
        memories = await lt.search(user_id=user_id, query=query, limit=limit)
        return [{"content": m.content, "type": m.memory_type, "score": m.score} for m in memories]

    async def _get_recent_messages(self, conversation_id: str, n: int = 10) -> List[Dict[str, Any]]:
        from app.core.memory.short_term import redis_memory
        return await redis_memory.get_messages(conversation_id, last_n=n)

    async def _get_recent_tasks(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent task history from PostgreSQL."""
        from app.models.base import AsyncSessionLocal
        from app.models.task import Task
        from sqlalchemy import select, desc
        import uuid
        async with AsyncSessionLocal() as session:
            stmt = (
                select(Task.title, Task.status, Task.created_at)
                .where(Task.user_id == uuid.UUID(user_id))
                .order_by(desc(Task.created_at))
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = result.fetchall()
            return [{"title": r[0], "status": str(r[1]), "created_at": str(r[2])} for r in rows]
