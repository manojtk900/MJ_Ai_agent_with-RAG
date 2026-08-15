"""
Long-Term Memory — PostgreSQL + pgvector semantic storage.
Replaces ChromaDB with a single consolidated database.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

log = structlog.get_logger(__name__)


@dataclass
class MemoryRecord:
    id: str
    content: str
    memory_type: str
    importance_score: float
    keywords: List[str]
    score: float = 0.0  # Similarity score from pgvector


class LongTermMemory:
    """
    Long-term memory using PostgreSQL + pgvector.
    
    Operations:
    - store(): embed content and save to PostgreSQL
    - search(): cosine similarity search via pgvector
    - update_importance(): boost frequently accessed memories
    """

    def __init__(self):
        self._embedding_service = None

    async def _get_embedder(self):
        if self._embedding_service is None:
            from app.services.embedding import EmbeddingService
            self._embedding_service = EmbeddingService()
        return self._embedding_service

    async def store(
        self,
        user_id: str,
        content: str,
        memory_type: str = "fact",
        importance_score: float = 0.5,
        keywords: Optional[List[str]] = None,
        conversation_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> str:
        """Embed and store a memory in PostgreSQL."""
        from app.models.base import AsyncSessionLocal
        from app.models.memory import Memory, MemoryType
        import uuid

        embedder = await self._get_embedder()
        embedding = await embedder.embed(content)

        memory_id = str(uuid.uuid4())
        async with AsyncSessionLocal() as session:
            memory = Memory(
                id=memory_id,
                user_id=user_id,
                memory_type=MemoryType(memory_type),
                content=content,
                summary=content[:200],
                keywords=keywords or [],
                embedding=embedding,
                importance_score=importance_score,
                conversation_id=conversation_id,
                task_id=task_id,
            )
            session.add(memory)
            await session.commit()

        log.info("Memory stored", id=memory_id, type=memory_type)
        return memory_id

    async def search(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
        memory_type: Optional[str] = None,
        min_score: float = 0.3,
    ) -> List[MemoryRecord]:
        """
        Semantic search using pgvector cosine similarity.
        """
        from app.models.base import AsyncSessionLocal
        from app.models.memory import Memory
        from sqlalchemy import text

        embedder = await self._get_embedder()
        query_embedding = await embedder.embed(query)
        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"

        async with AsyncSessionLocal() as session:
            # pgvector cosine similarity search
            sql = text("""
                SELECT id, content, memory_type, importance_score, keywords,
                       1 - (embedding <=> :query_embedding::vector) AS similarity_score
                FROM memories
                WHERE user_id = :user_id
                  AND is_active = true
                  {type_filter}
                  AND 1 - (embedding <=> :query_embedding::vector) > :min_score
                ORDER BY embedding <=> :query_embedding::vector
                LIMIT :limit
            """.format(type_filter=f"AND memory_type = '{memory_type}'" if memory_type else ""))

            result = await session.execute(sql, {
                "query_embedding": embedding_str,
                "user_id": user_id,
                "min_score": min_score,
                "limit": limit,
            })
            rows = result.fetchall()

        # Update access count
        if rows:
            ids = [str(r[0]) for r in rows]
            await self._update_access_count(ids)

        return [
            MemoryRecord(
                id=str(r[0]),
                content=r[1],
                memory_type=str(r[2]),
                importance_score=float(r[3]),
                keywords=r[4] or [],
                score=float(r[5]),
            )
            for r in rows
        ]

    async def _update_access_count(self, memory_ids: List[str]) -> None:
        from app.models.base import AsyncSessionLocal
        from app.models.memory import Memory
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(
                text("UPDATE memories SET access_count = access_count + 1 WHERE id = ANY(:ids)"),
                {"ids": memory_ids},
            )
            await session.commit()

    async def delete(self, memory_id: str) -> bool:
        from app.models.base import AsyncSessionLocal
        from app.models.memory import Memory
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(
                text("UPDATE memories SET is_active = false WHERE id = :id"),
                {"id": memory_id},
            )
            await session.commit()
        return True
