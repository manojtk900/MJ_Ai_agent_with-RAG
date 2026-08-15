"""
Base Agent — Abstract base class for all MJ AI Assistant agents.
Implements the ReAct pattern with retry logic and observability.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.core.langgraph.state import AgentState, ReActStep, ToolCall
from app.services.llm import get_llm

log = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in MJ AI Assistant.
    
    Each agent:
    - Has a name, description, and system prompt
    - Can use tools via the MCP tool registry
    - Implements the ReAct loop (Think → Act → Observe)
    - Logs all activity for observability
    """

    name: str = "base_agent"
    description: str = "Base agent"
    system_prompt: str = "You are a helpful AI assistant."
    supported_intents: List[str] = []
    requires_tools: bool = False

    def __init__(self):
        self.llm = None
        self.tools: List[Any] = []
        self.logger = structlog.get_logger(self.name)

    async def initialize(self, provider: Optional[str] = None) -> None:
        """Lazy-initialize the LLM and tools."""
        if self.llm is None:
            self.llm = get_llm(provider or settings.default_llm_provider)
        if self.requires_tools and not self.tools:
            self.tools = await self._load_tools()

    async def _load_tools(self) -> List[Any]:
        """Override in subclasses to register MCP/LangChain tools."""
        return []

    @abstractmethod
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Core execution logic — implement in each agent."""
        ...

    async def run(self, state: AgentState) -> Dict[str, Any]:
        """
        Entry point — initializes, runs ReAct loop, handles errors.
        """
        await self.initialize()
        start_time = time.monotonic()

        self.logger.info("Agent started", session=state.session_id, intent=state.intent)

        try:
            result = await self._react_loop(state)
        except Exception as e:
            self.logger.error("Agent error", error=str(e), agent=self.name)
            result = {
                "error": str(e),
                "final_response": f"I encountered an error: {str(e)}",
                "agent_logs": [f"[{self.name}] ERROR: {str(e)}"],
            }

        latency = (time.monotonic() - start_time) * 1000
        self.logger.info("Agent completed", latency_ms=f"{latency:.0f}")

        result.setdefault("agent_logs", [])
        result["agent_logs"].append(f"[{self.name}] completed in {latency:.0f}ms")
        result["performance_metrics"] = {
            **state.performance_metrics,
            self.name: {"latency_ms": latency},
        }

        return result

    async def _react_loop(self, state: AgentState) -> Dict[str, Any]:
        """
        Implements the ReAct pattern:
        Think → Act → Observe → (repeat) → Finalize
        """
        max_iterations = settings.max_agent_retries + 1
        react_steps = list(state.react_steps)

        for i in range(max_iterations):
            # ── Think ─────────────────────────────────────────
            thought = await self._think(state, react_steps)
            step = ReActStep(thought=thought, step_index=i)

            # ── Decide Action ─────────────────────────────────
            if self._should_use_tool(thought):
                tool_name, tool_input = self._parse_tool_call(thought)
                step.action = tool_name
                step.action_input = tool_input

                # ── Act ───────────────────────────────────────
                observation, tool_call = await self._act(tool_name, tool_input)
                step.observation = observation
                react_steps.append(step)

                # ── Observe → loop again ──────────────────────
                continue

            # ── No tool needed — finalize ─────────────────────
            react_steps.append(step)
            result = await self.execute(state)
            result["react_steps"] = react_steps
            return result

        # Exhausted iterations
        return {
            "react_steps": react_steps,
            "error": "Max iterations reached",
            "final_response": "I was unable to complete this task within the allowed steps.",
        }

    async def _think(self, state: AgentState, steps: List[ReActStep]) -> str:
        """Generate a thought about the current state."""
        return f"Processing {state.intent} for user {state.user_id}"

    def _should_use_tool(self, thought: str) -> bool:
        return "USE_TOOL:" in thought

    def _parse_tool_call(self, thought: str):
        # Simplified parser — real impl uses structured output
        return "default_tool", {}

    async def _act(self, tool_name: str, tool_input: Dict[str, Any]):
        """Execute a tool call and return observation."""
        from app.core.mcp.registry import tool_registry
        start = time.monotonic()
        try:
            result = await tool_registry.call(tool_name, tool_input)
            tc = ToolCall(
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=result,
                latency_ms=(time.monotonic() - start) * 1000,
            )
            return str(result), tc
        except Exception as e:
            tc = ToolCall(tool_name=tool_name, tool_input=tool_input, error=str(e))
            return f"Error: {e}", tc

    def build_messages(self, state: AgentState) -> List:
        """Build message list from state for LLM call."""
        messages = [SystemMessage(content=self.system_prompt)]
        # Inject context from Context Engineering layer
        if state.context:
            ctx_str = "\n".join(f"{k}: {v}" for k, v in state.context.items())
            messages.append(SystemMessage(content=f"Context:\n{ctx_str}"))
        # Add conversation history
        messages.extend(state.messages[-20:])  # Last 20 messages
        return messages
