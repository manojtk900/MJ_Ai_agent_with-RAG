"""
Pydantic Schemas for MJ Intelligence Agent, Structured Tool Calling, RAG, and Traces.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
RouteCategory = Literal[
    "ACTION",
    "KNOWLEDGE_PROJECT",
    "KNOWLEDGE_WORLD",
    "CODING",
    "CONVERSATION",
    "PLANNING",
    "CONFIRMATION_REQUIRED",
    "CLARIFICATION_REQUIRED",
]


class ToolDefinition(BaseModel):
    name: str
    description: str
    risk_level: RiskLevel = "LOW"
    requires_confirmation: bool = False
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: float = 10.0
    allowed: bool = True


class ToolCallSchema(BaseModel):
    tool: str = Field(..., description="Registered tool name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Validated arguments matching tool parameters")
    thought: Optional[str] = Field(default=None, description="Reasoning for selecting this tool")


class AgentDecision(BaseModel):
    decision_type: Literal["tool_call", "answer", "need_confirmation", "need_clarification"] = "answer"
    tool_call: Optional[ToolCallSchema] = None
    answer: Optional[str] = None
    confirmation_prompt: Optional[str] = None
    clarification_prompt: Optional[str] = None


class SourceCitation(BaseModel):
    source_file: str
    chunk_index: int
    score: float
    excerpt: str


class RAGChunk(BaseModel):
    id: str
    text: str
    source_file: str
    chunk_index: int
    category: str = "general"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RAGSearchResult(BaseModel):
    query: str
    chunks: List[RAGChunk] = Field(default_factory=list)
    citations: List[SourceCitation] = Field(default_factory=list)
    confidence: float = 0.0


class IntelligenceChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32000)
    conversation_id: Optional[str] = None
    user_id: Optional[str] = "default_user"
    stream: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntelligenceChatResponse(BaseModel):
    answer: str
    conversation_id: str
    route: RouteCategory
    intent: str
    source: Literal["rag", "llm_ollama", "llm_cloud", "rag_synthesis", "offline_fallback", "tool"] = "rag_synthesis"
    citations: List[SourceCitation] = Field(default_factory=list)
    tool_called: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    latency_ms: float = 0.0
    requires_confirmation: bool = False
    trace_id: Optional[str] = None


class ExecutionTrace(BaseModel):
    trace_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user_id: str = "default_user"
    raw_input: str
    predicted_intent: str
    confidence: float
    route: RouteCategory
    selected_tool: Optional[str] = None
    tool_arguments: Optional[Dict[str, Any]] = None
    tool_result: Optional[Any] = None
    success: bool = True
    error: Optional[str] = None
    latency_ms: float = 0.0
    model_provider: Optional[str] = None
    llm_model: Optional[str] = None
    user_feedback: Optional[str] = None


class IntelligenceStatusResponse(BaseModel):
    status: str = "healthy"
    ml_router: Dict[str, Any]
    rag_engine: Dict[str, Any]
    ollama_status: Dict[str, Any]
    cloud_llm_status: Dict[str, Any]
    circuit_breaker: Dict[str, Any]
    total_traces: int = 0
