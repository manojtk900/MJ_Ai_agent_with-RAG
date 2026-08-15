"""
Memory Model — stores short/long-term memory with pgvector embeddings.
"""
import uuid
from enum import Enum as PyEnum

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base, TimestampMixin


class MemoryType(PyEnum):
    USER_PREFERENCE = "user_preference"
    CONVERSATION_SUMMARY = "conversation_summary"
    TASK_RESULT = "task_result"
    LEARNED_BEHAVIOR = "learned_behavior"
    ENTITY = "entity"             # Named entities (people, places, etc.)
    SKILL = "skill"               # Learned user skill/workflow
    FACT = "fact"                 # General factual memory


class Memory(Base, TimestampMixin):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    memory_type = Column(Enum(MemoryType), nullable=False, index=True)

    # Content
    content = Column(Text, nullable=False)            # Human-readable memory
    summary = Column(String(500))                      # Short summary
    keywords = Column(JSON, default=list)              # For keyword search

    # Vector embedding (pgvector) — replaces ChromaDB
    embedding = Column(Vector(settings.embedding_dimensions))

    # Scoring
    importance_score = Column(Float, default=0.5)      # 0.0–1.0
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(String(50))              # ISO timestamp

    # Source linkage
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)

    # Metadata
    metadata_ = Column("metadata", JSON, default=dict)
    is_active = Column(Boolean, default=True)
    expires_at = Column(String(50), nullable=True)     # Optional TTL

    # Relationships
    user = relationship("User", back_populates="memories")

    def __repr__(self):
        return f"<Memory {self.id} [{self.memory_type}]>"
