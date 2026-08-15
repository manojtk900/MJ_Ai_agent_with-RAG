"""
Task, Project, and Audit Log Models
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


class TaskStatus(PyEnum):
    PENDING = "pending"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(PyEnum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)

    title = Column(String(500), nullable=False)
    description = Column(Text)
    goal = Column(Text)                                # Original user goal
    plan = Column(JSON, default=list)                  # Step-by-step plan from Planner
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, index=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.SAFE)

    # Execution
    assigned_agent = Column(String(100))               # Which agent is executing
    agent_trace = Column(JSON, default=list)           # Full ReAct trace
    tool_calls_made = Column(JSON, default=list)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Human-in-the-loop
    requires_approval = Column(Boolean, default=False)
    approval_reason = Column(Text)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(String(50), nullable=True)

    # Scheduling
    scheduled_at = Column(String(50), nullable=True)   # ISO timestamp
    cron_expression = Column(String(100), nullable=True)
    is_recurring = Column(Boolean, default=False)
    celery_task_id = Column(String(200), nullable=True)

    # Results
    result = Column(JSON)
    error_message = Column(Text)
    completion_percentage = Column(Float, default=0.0)

    # Metadata
    metadata_ = Column("metadata", JSON, default=dict)
    tags = Column(JSON, default=list)
    due_at = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")
    completion_percentage = Column(Float, default=0.0)

    # GitHub integration
    github_repo = Column(String(500))
    github_owner = Column(String(200))

    # Planning
    milestones = Column(JSON, default=list)
    sprint_plan = Column(JSON, default=list)
    tech_stack = Column(JSON, default=list)

    metadata_ = Column("metadata", JSON, default=dict)
    tags = Column(JSON, default=list)
    due_date = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates=None, foreign_keys=[Task.project_id])


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"),
                     nullable=True, index=True)

    # Action details
    action = Column(String(200), nullable=False, index=True)  # e.g. "file.delete", "email.send"
    agent_name = Column(String(100))
    resource_type = Column(String(100))
    resource_id = Column(String(200))
    description = Column(Text)

    # Risk assessment
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.SAFE)
    required_approval = Column(Boolean, default=False)
    was_approved = Column(Boolean, nullable=True)

    # Request context
    request_ip = Column(String(50))
    request_method = Column(String(10))
    request_path = Column(String(500))
    request_body = Column(JSON)

    # Response
    response_status = Column(Integer)
    response_body = Column(JSON)
    latency_ms = Column(Float)

    # Outcome
    success = Column(Boolean, default=True)
    error_message = Column(Text)

    metadata_ = Column("metadata", JSON, default=dict)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"
