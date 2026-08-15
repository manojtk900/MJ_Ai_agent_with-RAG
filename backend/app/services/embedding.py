"""
Embedding Service — Generates vector embeddings for pgvector storage.
Supports OpenAI text-embedding-3-small (1536d) and fallback zero vector.
"""
from __future__ import annotations

from typing import List

import structlog

from app.config import settings

log = structlog.get_logger(__name__)


class EmbeddingService:
    """
    Generates embeddings for pgvector semantic search.
    Falls back to zero vector if OpenAI key is not configured.
    """

    async def embed(self, text: str) -> List[float]:
        """Embed a single text string."""
        if not settings.openai_api_key:
            log.warning("OpenAI key not set — returning zero vector")
            return [0.0] * settings.embedding_dimensions

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.embeddings.create(
                input=text[:8192],
                model=settings.embedding_model,
            )
            return response.data[0].embedding
        except Exception as e:
            log.error("Embedding failed", error=str(e))
            return [0.0] * settings.embedding_dimensions

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embed multiple texts."""
        if not settings.openai_api_key:
            return [[0.0] * settings.embedding_dimensions for _ in texts]

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.embeddings.create(
                input=[t[:8192] for t in texts],
                model=settings.embedding_model,
            )
            return [d.embedding for d in response.data]
        except Exception as e:
            log.error("Batch embedding failed", error=str(e))
            return [[0.0] * settings.embedding_dimensions for _ in texts]
