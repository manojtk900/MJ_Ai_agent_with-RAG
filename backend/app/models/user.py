"""
User Model
"""
import uuid
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class AutonomyLevel(PyEnum):
    CHAT_ONLY = 0
    ASK_BEFORE_ACTION = 1
    AUTO_SAFE_ACTIONS = 2
    FULLY_AUTONOMOUS = 3


class UserRole(PyEnum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(String(500))
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Agent preferences
    autonomy_level = Column(Integer, default=1, nullable=False)
    default_llm_provider = Column(String(50), default="openai")
    default_model = Column(String(100), default="gpt-4o")
    voice_enabled = Column(Boolean, default=False)
    preferred_tts_voice = Column(String(50), default="alloy")
    system_prompt = Column(Text)
    timezone = Column(String(50), default="UTC")

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
