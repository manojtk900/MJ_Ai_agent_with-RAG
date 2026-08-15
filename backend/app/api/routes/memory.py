"""
Memory API Route — Store, search, and manage long-term memories.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/memory")


class MemoryCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    memory_type: str = "fact"
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    keywords: List[str] = []
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None


class MemorySearchRequest(BaseModel):
    query: str
    user_id: str
    limit: int = Field(default=10, ge=1, le=50)
    memory_type: Optional[str] = None
    min_score: float = 0.3


@router.get("/")
async def search_memories(
    query: str = Query(..., description="Semantic search query"),
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Semantic search over long-term memories using pgvector."""
    return {
        "query": query,
        "user_id": user_id,
        "results": [],
        "message": "Connect PostgreSQL + pgvector to enable semantic search",
    }


@router.post("/")
async def store_memory(request: MemoryCreateRequest):
    """Store a new memory with embedding."""
    import uuid
    return {
        "memory_id": str(uuid.uuid4()),
        "status": "stored",
        "content": request.content,
        "memory_type": request.memory_type,
        "message": "Connect PostgreSQL + pgvector to persist memories",
    }


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """Soft-delete a memory by ID."""
    return {"memory_id": memory_id, "status": "deleted"}


@router.get("/types")
async def get_memory_types():
    """List all available memory types."""
    return {
        "types": [
            "user_preference",
            "conversation_summary",
            "task_result",
            "learned_behavior",
            "entity",
            "skill",
            "fact",
        ]
    }
