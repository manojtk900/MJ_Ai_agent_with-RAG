"""
Conversation and Message Models
"""
import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean, Column, Enum, Float, ForeignKey,
    Integer, String, Text, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class MessageRole(PyEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    AGENT = "agent"


class ConversationStatus(PyEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), default="New Conversation")
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    summary = Column(Text)                        # LLM-generated summary
    tags = Column(JSON, default=list)
    metadata_ = Column("metadata", JSON, default=dict)
    token_count = Column(Integer, default=0)
    autonomy_level = Column(Integer, default=1)   # Per-conversation override

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation",
                            cascade="all, delete-orphan", order_by="Message.created_at")

    def __repr__(self):
        return f"<Conversation {self.id} — {self.title}>"


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"),
                             nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    agent_name = Column(String(100))           # Which agent produced this message
    tool_calls = Column(JSON, default=list)    # Tool calls made in this message
    tool_results = Column(JSON, default=list)  # Results from tool calls
    model_used = Column(String(100))           # e.g. gpt-4o, claude-sonnet-4-5
    token_count = Column(Integer, default=0)
    latency_ms = Column(Float)                 # Response time
    metadata_ = Column("metadata", JSON, default=dict)
    is_error = Column(Boolean, default=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=True)

    # Workflow tracing
    workflow_run_id = Column(String(100))       # LangGraph run ID
    agent_trace = Column(JSON, default=dict)    # Full ReAct trace

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id} [{self.role}]>"
