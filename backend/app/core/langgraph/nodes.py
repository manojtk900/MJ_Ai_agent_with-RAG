"""
LangGraph Nodes — Each node wraps an agent or core pipeline step.
These are the actual functions called by the StateGraph.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

import structlog

from app.core.langgraph.state import AgentState, ApprovalRequest, ReActStep

log = structlog.get_logger(__name__)

HIGH_RISK_ACTIONS = {
    "file.delete", "email.send", "system.execute",
    "github.push", "github.delete", "deploy.production",
    "payment.process", "database.drop",
}


# ── Controller Node ───────────────────────────────────────────
async def controller_node(state: AgentState) -> Dict[str, Any]:
    """
    Controller Agent: Intent detection, routing decision, permission check.
    """
    from app.agents.controller.agent import ControllerAgent
    agent = ControllerAgent()
    result = await agent.run(state)
    log.info("Controller", intent=result.get("intent"), user_id=state.user_id)
    return {
        **result,
        "agent_logs": [f"[controller] intent={result.get('intent')} autonomy={state.autonomy_level}"],
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


# ── Planner Node ──────────────────────────────────────────────
async def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    Planner Agent: Goal decomposition, step-by-step plan creation.
    """
    from app.agents.planner.agent import PlannerAgent
    agent = PlannerAgent()
    result = await agent.run(state)
    log.info("Planner", steps=len(result.get("plan", [])))
    return {
        **result,
        "agent_logs": [f"[planner] created plan with {len(result.get('plan', []))} steps"],
    }


# ── Router Node ───────────────────────────────────────────────
async def router_node(state: AgentState) -> Dict[str, Any]:
    """Determines final agent routing based on intent + plan."""
    return {"agent_logs": [f"[router] routing to agent for intent={state.intent}"]}


# ── Human Approval Node ───────────────────────────────────────
async def human_approval_node(state: AgentState) -> Dict[str, Any]:
    """
    Pauses workflow for human review. LangGraph's interrupt_before
    will stop execution here until approval is granted via API.
    """
    log.warning(
        "Human approval required",
        action=state.pending_approval.action if state.pending_approval else "unknown",
        risk=state.pending_approval.risk_level if state.pending_approval else "unknown",
    )
    return {
        "requires_human_input": True,
        "agent_logs": [f"[approval_gate] waiting for human approval: {state.pending_approval}"],
    }


# ── Executor Node ─────────────────────────────────────────────
async def executor_node(state: AgentState) -> Dict[str, Any]:
    """
    Unified execution wrapper — runs the next plan step and
    increments the ReAct loop counter.
    """
    current_step = state.current_step_index
    plan = state.plan
    if current_step < len(plan):
        step = plan[current_step]
        log.info("Executing step", step=step, index=current_step)
        return {
            "current_step_index": current_step + 1,
            "agent_logs": [f"[executor] step {current_step}: {step}"],
        }
    return {
        "is_complete": True,
        "agent_logs": ["[executor] all steps complete"],
    }


# ── Reflection Node ───────────────────────────────────────────
async def reflection_node(state: AgentState) -> Dict[str, Any]:
    """
    Reflection Agent: Evaluates output quality, identifies errors,
    decides whether to retry or accept.
    """
    from app.agents.reflection.agent import ReflectionAgent
    agent = ReflectionAgent()
    result = await agent.run(state)
    return {
        **result,
        "retry_count": state.retry_count + (1 if state.error else 0),
        "agent_logs": [f"[reflection] retry={state.retry_count} error={state.error}"],
    }


# ── Output Node ───────────────────────────────────────────────
async def output_node(state: AgentState) -> Dict[str, Any]:
    """Finalizes the response and assembles the output payload."""
    return {
        "is_complete": True,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "agent_logs": [f"[output] response_type={state.response_type}"],
    }


# ── Specialized Agent Nodes ───────────────────────────────────
async def chat_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.intelligence.agent import IntelligenceAgent
    return await IntelligenceAgent().run(state)


async def search_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.search.agent import SearchAgent
    return await SearchAgent().run(state)


async def research_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.research.agent import ResearchAgent
    return await ResearchAgent().run(state)


async def memory_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.memory.agent import MemoryAgent
    return await MemoryAgent().run(state)


async def desktop_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.desktop.agent import DesktopAgent
    return await DesktopAgent().run(state)


async def system_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.system.agent import SystemAgent
    result = await SystemAgent().run(state)
    if result.get("action") in HIGH_RISK_ACTIONS:
        result["pending_approval"] = ApprovalRequest(
            action=result["action"],
            description=result.get("description", "System action"),
            risk_level="high",
            requires_approval=True,
        )
    return result




async def browser_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.browser.agent import BrowserAgent
    return await BrowserAgent().run(state)


async def email_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.email.agent import EmailAgent
    result = await EmailAgent().run(state)
    if result.get("action") == "email.send":
        result["pending_approval"] = ApprovalRequest(
            action="email.send",
            description=f"Send email: {result.get('subject', 'No subject')}",
            risk_level="medium",
            requires_approval=state.autonomy_level < 3,
        )
    return result


async def reminder_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.reminder.agent import ReminderAgent
    return await ReminderAgent().run(state)


async def file_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.file.agent import FileAgent
    return await FileAgent().run(state)


async def voice_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.voice.agent import VoiceAgent
    return await VoiceAgent().run(state)


async def execution_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.execution.agent import ExecutionAgent
    return await ExecutionAgent().run(state)


async def scheduler_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.scheduler.agent import SchedulerAgent
    return await SchedulerAgent().run(state)


async def project_manager_agent_node(state: AgentState) -> Dict[str, Any]:
    from app.agents.project_manager.agent import ProjectManagerAgent
    return await ProjectManagerAgent().run(state)
