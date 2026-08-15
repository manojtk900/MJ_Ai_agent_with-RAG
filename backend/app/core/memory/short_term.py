"""
Short-Term Memory — Redis-backed session memory for fast in-context retrieval.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import structlog
import redis.asyncio as aioredis

from app.config import settings

log = structlog.get_logger(__name__)


class RedisMemory:
    """
    Short-term memory backed by Redis.
    
    Stores:
    - Session state (conversation context, partial results)
    - User preferences cache
    - Agent handoff state
    - Recent tool results
    """

    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self._redis = redis_client

    @classmethod
    async def create_pool(cls, redis_url: str) -> aioredis.Redis:
        """Create and return a Redis connection pool."""
        return await aioredis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )

    async def _get_client(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = await aioredis.from_url(settings.redis_url, decode_responses=True)
        return self._redis

    # ── Session State ─────────────────────────────────────────
    async def set_session(self, session_id: str, data: Dict[str, Any], ttl: int = None) -> None:
        client = await self._get_client()
        ttl = ttl or settings.redis_ttl_session
        await client.setex(f"session:{session_id}", ttl, json.dumps(data))

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        client = await self._get_client()
        raw = await client.get(f"session:{session_id}")
        return json.loads(raw) if raw else None

    async def delete_session(self, session_id: str) -> None:
        client = await self._get_client()
        await client.delete(f"session:{session_id}")

    # ── Conversation History (circular buffer) ────────────────
    async def push_message(self, conversation_id: str, message: Dict[str, Any], max_messages: int = 50) -> None:
        client = await self._get_client()
        key = f"conv:{conversation_id}:messages"
        await client.rpush(key, json.dumps(message))
        # Keep only last N messages
        await client.ltrim(key, -max_messages, -1)
        await client.expire(key, settings.redis_ttl_session)

    async def get_messages(self, conversation_id: str, last_n: int = 20) -> List[Dict[str, Any]]:
        client = await self._get_client()
        key = f"conv:{conversation_id}:messages"
        raw_messages = await client.lrange(key, -last_n, -1)
        return [json.loads(m) for m in raw_messages]

    # ── User Preferences Cache ────────────────────────────────
    async def cache_preferences(self, user_id: str, prefs: Dict[str, Any]) -> None:
        client = await self._get_client()
        await client.setex(f"prefs:{user_id}", settings.redis_ttl_short, json.dumps(prefs))

    async def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        client = await self._get_client()
        raw = await client.get(f"prefs:{user_id}")
        return json.loads(raw) if raw else None

    # ── Tool Result Cache ─────────────────────────────────────
    async def cache_tool_result(self, key: str, result: Any, ttl: int = 300) -> None:
        client = await self._get_client()
        await client.setex(f"tool:{key}", ttl, json.dumps(result))

    async def get_tool_result(self, key: str) -> Optional[Any]:
        client = await self._get_client()
        raw = await client.get(f"tool:{key}")
        return json.loads(raw) if raw else None

    # ── Approval State (for HITL) ─────────────────────────────
    async def set_approval_state(self, task_id: str, state: Dict[str, Any]) -> None:
        client = await self._get_client()
        await client.setex(f"approval:{task_id}", 3600, json.dumps(state))

    async def get_approval_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        client = await self._get_client()
        raw = await client.get(f"approval:{task_id}")
        return json.loads(raw) if raw else None

    # ── Generic K/V ──────────────────────────────────────────
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        client = await self._get_client()
        await client.setex(key, ttl, json.dumps(value))

    async def get(self, key: str) -> Optional[Any]:
        client = await self._get_client()
        raw = await client.get(key)
        return json.loads(raw) if raw else None

    async def delete(self, key: str) -> None:
        client = await self._get_client()
        await client.delete(key)


# Module-level instance for convenience
redis_memory = RedisMemory()
