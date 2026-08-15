"""
LangGraph Workflow — Main orchestration graph implementing
ReAct + Reflection pattern with Human-in-the-Loop support.

Flow:
  Input → Controller → Planner → Executor → Reflection → Output
                                    ↑              |
                                    └──── retry ───┘
                                    
Human-in-the-Loop gate at Execution when risk_level >= MEDIUM.
"""
from __future__ import annotations

import structlog
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import settings
from app.core.langgraph.state import AgentState
from app.core.langgraph import nodes

log = structlog.get_logger(__name__)


def should_require_approval(state: AgentState) -> str:
    """Route to human approval gate if action is risky."""
    if state.pending_approval and state.pending_approval.requires_approval:
        if state.pending_approval.approved is None:
            return "human_approval"
    return "executor"


def should_reflect(state: AgentState) -> str:
    """After execution, decide if we need to reflect or can output."""
    if state.error and state.retry_count < state.max_retries:
        return "reflect"
    if state.needs_reflection:
        return "reflect"
    return "output"


def should_retry(state: AgentState) -> str:
    """After reflection, retry or output."""
    if state.error and state.retry_count < state.max_retries:
        return "executor"
    return "output"


def should_plan(state: AgentState) -> str:
    """After controller, decide if planning is needed."""
    complex_intents = {
        "code_generation", "web_research", "file_processing",
        "email_management", "browser_automation", "system_operation",
        "github_automation", "deployment", "project_management",
        "background_task", "scheduled_task",
    }
    if state.intent in complex_intents:
        return "planner"
    return "router"


def route_to_agent(state: AgentState) -> str:
    """Route to the correct specialized agent."""
    intent_to_agent = {
        # ── ML Model Native Intents ───────────────────────────
        "youtube_search": "desktop_agent",
        "google_search": "desktop_agent",
        "open_browser": "desktop_agent",
        "open_github": "desktop_agent",
        "open_vscode": "desktop_agent",
        "open_notepad": "desktop_agent",
        "open_calculator": "desktop_agent",
        "open_application": "desktop_agent",
        "send_email": "email_agent",
        "read_email": "email_agent",
        "summarize_email": "email_agent",
        "create_task": "reminder_agent",
        "delete_task": "reminder_agent",
        "update_task": "reminder_agent",
        "github_push": "execution_agent",
        "github_pull": "execution_agent",
        "github_create_repo": "execution_agent",
        "remember_fact": "memory_agent",
        "recall_memory": "memory_agent",
        "chat": "chat_agent",
        "workflow_create": "execution_agent",
        "workflow_run": "execution_agent",
        # ── Extended / Core Pipeline Intents ───────────────────
        "conversation": "chat_agent",
        "coding": "chat_agent",
        "reasoning": "chat_agent",
        "web_search": "search_agent",
        "quick_search": "search_agent",
        "memory_store": "memory_agent",
        "memory_retrieve": "memory_agent",
        "desktop_operation": "desktop_agent",
        "app_open": "desktop_agent",
        "web_research": "research_agent",
        "deep_research": "research_agent",
        "file_read": "file_agent",
        "file_write": "file_agent",
        "pdf_analysis": "file_agent",
        "system_operation": "desktop_agent",
        "browser_automation": "desktop_agent",
        "reminder": "reminder_agent",
        "schedule_task": "scheduler_agent",
        "code_generation": "execution_agent",
        "github_automation": "execution_agent",
        "deployment": "execution_agent",
        "project_management": "project_manager_agent",
        "voice_processing": "voice_agent",
    }
    agent = intent_to_agent.get(state.intent, "chat_agent")
    log.info("Routing to agent", agent=agent, intent=state.intent)
    return agent


def build_workflow(checkpointer=None) -> StateGraph:
    """
    Construct the full LangGraph StateGraph for MJ AI Assistant.
    """
    graph = StateGraph(AgentState)

    # ── Add Nodes ─────────────────────────────────────────────
    graph.add_node("controller", nodes.controller_node)
    graph.add_node("planner", nodes.planner_node)
    graph.add_node("router", nodes.router_node)
    graph.add_node("human_approval", nodes.human_approval_node)

    # Specialized Agent Nodes
    graph.add_node("chat_agent", nodes.chat_agent_node)
    graph.add_node("search_agent", nodes.search_agent_node)
    graph.add_node("research_agent", nodes.research_agent_node)
    graph.add_node("memory_agent", nodes.memory_agent_node)
    graph.add_node("desktop_agent", nodes.desktop_agent_node)
    graph.add_node("system_agent", nodes.system_agent_node)
    graph.add_node("browser_agent", nodes.browser_agent_node)
    graph.add_node("email_agent", nodes.email_agent_node)
    graph.add_node("reminder_agent", nodes.reminder_agent_node)
    graph.add_node("file_agent", nodes.file_agent_node)
    graph.add_node("voice_agent", nodes.voice_agent_node)
    graph.add_node("execution_agent", nodes.execution_agent_node)
    graph.add_node("scheduler_agent", nodes.scheduler_agent_node)
    graph.add_node("project_manager_agent", nodes.project_manager_agent_node)

    # Core pipeline nodes
    graph.add_node("executor", nodes.executor_node)   # Unified execution wrapper
    graph.add_node("reflection", nodes.reflection_node)
    graph.add_node("output", nodes.output_node)

    # ── Entry Point ───────────────────────────────────────────
    graph.add_edge(START, "controller")

    # ── Controller → Planner or Router ───────────────────────
    graph.add_conditional_edges(
        "controller",
        should_plan,
        {"planner": "planner", "router": "router"},
    )

    # ── Planner → Router ─────────────────────────────────────
    graph.add_edge("planner", "router")

    # ── Router → Agent ───────────────────────────────────────
    graph.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "chat_agent": "chat_agent",
            "search_agent": "search_agent",
            "research_agent": "research_agent",
            "memory_agent": "memory_agent",
            "desktop_agent": "desktop_agent",
            "system_agent": "system_agent",
            "browser_agent": "browser_agent",
            "email_agent": "email_agent",
            "reminder_agent": "reminder_agent",
            "file_agent": "file_agent",
            "voice_agent": "voice_agent",
            "execution_agent": "execution_agent",
            "scheduler_agent": "scheduler_agent",
            "project_manager_agent": "project_manager_agent",
        },
    )

    # ── All agents → executor (approval gate) ─────────────────
    for agent_node in [
        "chat_agent", "search_agent", "research_agent", "memory_agent",
        "desktop_agent", "system_agent", "browser_agent", "email_agent",
        "reminder_agent", "file_agent", "voice_agent", "execution_agent",
        "scheduler_agent", "project_manager_agent",
    ]:

        graph.add_conditional_edges(
            agent_node,
            should_require_approval,
            {"human_approval": "human_approval", "executor": "executor"},
        )

    # ── Human approval → executor or output ──────────────────
    graph.add_conditional_edges(
        "human_approval",
        lambda s: "executor" if s.pending_approval and s.pending_approval.approved else "output",
        {"executor": "executor", "output": "output"},
    )

    # ── Executor → Reflection or Output ──────────────────────
    graph.add_conditional_edges(
        "executor",
        should_reflect,
        {"reflect": "reflection", "output": "output"},
    )

    # ── Reflection → Retry or Output ─────────────────────────
    graph.add_conditional_edges(
        "reflection",
        should_retry,
        {"executor": "executor", "output": "output"},
    )

    # ── Output → END ─────────────────────────────────────────
    graph.add_edge("output", END)

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_approval"],  # Pause for human review
    )


async def get_workflow_with_checkpointer():
    """Returns the compiled workflow with PostgreSQL checkpointing."""
    async with await AsyncPostgresSaver.from_conn_string(
        settings.database_url.replace("+asyncpg", "")
    ) as checkpointer:
        await checkpointer.setup()
        return build_workflow(checkpointer=checkpointer)


# Module-level workflow (no persistence — for simple use cases)
simple_workflow = build_workflow()
