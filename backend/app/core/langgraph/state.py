"""
LangGraph Agent State — shared state schema across all agents.
"""
from __future__ import annotations

import operator
from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional
from uuid import UUID

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Represents a single tool invocation."""
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Optional[Any] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ReActStep(BaseModel):
    """A single step in the ReAct loop."""
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    reflection: Optional[str] = None
    step_index: int = 0


class ApprovalRequest(BaseModel):
    """Human-in-the-loop approval request."""
    action: str
    description: str
    risk_level: Literal["safe", "low", "medium", "high", "critical"] = "low"
    requires_approval: bool = False
    approved: Optional[bool] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None


class AgentState(BaseModel):
    """
    Central state shared across all nodes in the LangGraph workflow.
    Every agent reads from and writes to this state.
    """

    # ── Identity ──────────────────────────────────────────────
    session_id: str = ""
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    task_id: Optional[str] = None
    workflow_run_id: Optional[str] = None

    # ── Message History ───────────────────────────────────────
    messages: Annotated[List[BaseMessage], add_messages] = Field(default_factory=list)
    raw_input: str = ""                       # Original user input
    input_type: Literal["text", "voice", "file", "image"] = "text"

    # ── Routing ───────────────────────────────────────────────
    intent: Optional[str] = None              # Detected intent
    target_agent: Optional[str] = None        # Which agent handles this
    agent_chain: List[str] = Field(default_factory=list)  # A2A chain

    # ── Planning ──────────────────────────────────────────────
    goal: Optional[str] = None
    plan: List[Dict[str, Any]] = Field(default_factory=list)
    current_step_index: int = 0
    plan_complete: bool = False

    # ── Execution (ReAct) ─────────────────────────────────────
    react_steps: List[ReActStep] = Field(default_factory=list)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    is_complete: bool = False
    needs_reflection: bool = False

    # ── Memory & Context ──────────────────────────────────────
    short_term_memory: List[Dict[str, Any]] = Field(default_factory=list)
    long_term_memories: List[Dict[str, Any]] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)  # Context Engineering layer

    # ── Human-in-the-Loop ─────────────────────────────────────
    pending_approval: Optional[ApprovalRequest] = None
    autonomy_level: int = 1                   # 0–3
    requires_human_input: bool = False

    # ── Final Output ──────────────────────────────────────────
    final_response: Optional[str] = None
    response_type: Literal["text", "action", "report", "code", "error"] = "text"
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)  # Generated files/data
    error: Optional[str] = None

    # ── Observability ─────────────────────────────────────────
    agent_logs: Annotated[List[str], operator.add] = Field(default_factory=list)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # ── Metadata ──────────────────────────────────────────────
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
