"""
Chat API Route — WebSocket + REST endpoints for agent conversations.
All heavy imports (langgraph workflow, redis) are done lazily inside
each endpoint so the module loads even if those services aren't ready.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.config import settings

router = APIRouter(prefix="/chat")
log = structlog.get_logger(__name__)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32000)
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    autonomy_level: int = Field(default=1, ge=0, le=3)
    llm_provider: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    input_type: str = "text"   # text | voice | file | image


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    message_id: str
    agent_used: Optional[str] = None
    response_type: str = "text"
    artifacts: list = []
    requires_approval: bool = False
    approval_request: Optional[Dict[str, Any]] = None
    workflow_run_id: Optional[str] = None
    latency_ms: Optional[float] = None


def _get_state_class():
    """Lazy import AgentState."""
    from app.core.langgraph.state import AgentState
    return AgentState


def _get_workflow():
    """Lazy import LangGraph workflow."""
    from app.core.langgraph.workflow import simple_workflow
    return simple_workflow


def _get_redis():
    """Lazy import Redis memory."""
    from app.core.memory.short_term import redis_memory
    return redis_memory


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint — runs the full LangGraph agent workflow.
    Falls back to a simple echo response if LangGraph is not configured.
    """
    import time
    start = time.monotonic()

    conversation_id = request.conversation_id or str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    workflow_run_id = str(uuid.uuid4())

    log.info("Sending request", conversation_id=conversation_id, input_length=len(request.message))

    # Try to load short-term memory
    try:
        redis_mem = _get_redis()
        session_data = await redis_mem.get_session(conversation_id)
    except Exception:
        session_data = None

    # Try to run LangGraph workflow
    try:
        AgentState = _get_state_class()
        workflow = _get_workflow()

        state = AgentState(
            session_id=session_id,
            user_id=request.user_id,
            conversation_id=conversation_id,
            workflow_run_id=workflow_run_id,
            raw_input=request.message,
            input_type=request.input_type,
            autonomy_level=request.autonomy_level,
            metadata=request.metadata,
        )

        config = {"configurable": {"thread_id": conversation_id}}
        result = await workflow.ainvoke(state, config=config)
        final_response = result.get("final_response") or "I processed your request."
        agent_used = result.get("target_agent")
        response_type = result.get("response_type", "text")
        artifacts = result.get("artifacts", [])

    except Exception as e:
        # LangGraph not configured or LLM key missing — return informative response
        log.warning("Workflow unavailable, using fallback", error=str(e))
        final_response = (
            f"⚙️ **MJ AI Assistant** is running!\n\n"
            f"Your message: *{request.message}*\n\n"
            f"To activate AI responses, configure your LLM API key in `.env`:\n"
            f"```\nOPENAI_API_KEY=sk-...\n# or\nGOOGLE_API_KEY=AIza...\n```\n\n"
            f"Then restart the server."
        )
        agent_used = "system"
        response_type = "text"
        artifacts = []

    # Save to Redis (best-effort)
    try:
        redis_mem = _get_redis()
        await redis_mem.push_message(conversation_id, {
            "role": "user", "content": request.message,
        })
        await redis_mem.push_message(conversation_id, {
            "role": "assistant", "content": final_response, "agent": agent_used,
        })
    except Exception:
        pass  # Redis not required

    latency = round((time.monotonic() - start) * 1000, 2)
    log.info("Response received", conversation_id=conversation_id, agent=agent_used)
    log.info("Request duration", duration_ms=latency)

    return ChatResponse(
        message=final_response,
        conversation_id=conversation_id,
        message_id=str(uuid.uuid4()),
        agent_used=agent_used,
        response_type=response_type,
        artifacts=artifacts,
        requires_approval=False,
        workflow_run_id=workflow_run_id,
        latency_ms=latency,
    )


@router.post("/{session_id}/approve")
async def approve_action(session_id: str, approved: bool):
    """Human-in-the-Loop: approve or reject a pending agent action."""
    try:
        redis_mem = _get_redis()
        approval_state = await redis_mem.get_approval_state(session_id)
    except Exception:
        approval_state = None

    if not approval_state:
        raise HTTPException(status_code=404, detail="No pending approval found")

    await redis_mem.delete(f"approval:{session_id}")
    log.info("Action approval", session=session_id, approved=approved)

    if approved:
        return {"status": "approved", "message": "Action approved and will be executed"}
    return {"status": "rejected", "message": "Action was rejected by user"}


@router.websocket("/ws/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time streaming chat."""
    await websocket.accept()
    log.info("WebSocket connected", conversation_id=conversation_id)

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            if not message:
                continue

            await websocket.send_json({"type": "start", "conversation_id": conversation_id})

            try:
                AgentState = _get_state_class()
                workflow = _get_workflow()

                state = AgentState(
                    session_id=str(uuid.uuid4()),
                    conversation_id=conversation_id,
                    raw_input=message,
                    autonomy_level=data.get("autonomy_level", 1),
                )
                config = {"configurable": {"thread_id": conversation_id}}
                result = await workflow.ainvoke(state, config=config)
                await websocket.send_json({
                    "type": "message",
                    "content": result.get("final_response", ""),
                    "agent": result.get("target_agent"),
                    "response_type": result.get("response_type", "text"),
                })
            except Exception as e:
                await websocket.send_json({"type": "error", "error": str(e)})

            await websocket.send_json({"type": "end"})

    except WebSocketDisconnect:
        log.info("WebSocket disconnected", conversation_id=conversation_id)
    except Exception as e:
        log.error("WebSocket error", error=str(e))
        try:
            await websocket.close()
        except Exception:
            pass
