"""
A2A (Agent-to-Agent) Protocol — Multi-agent communication standard.

Enables agents to delegate sub-tasks to each other with:
- Typed messages
- Result passing
- Error propagation
- Execution chain tracking
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

log = structlog.get_logger(__name__)


class A2AMessage:
    """Message passed between agents."""

    def __init__(
        self,
        sender: str,
        recipient: str,
        task: str,
        payload: Dict[str, Any],
        parent_message_id: Optional[str] = None,
    ):
        self.message_id = str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.task = task
        self.payload = payload
        self.parent_message_id = parent_message_id
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "task": self.task,
            "payload": self.payload,
            "status": self.status,
            "created_at": self.created_at,
        }


class A2AProtocol:
    """
    Agent-to-Agent communication protocol.
    
    Example flow:
        Research Agent → Search Agent: "search for X"
        Search Agent → Research Agent: "here are results"
        Research Agent → Report Agent: "generate report from results"
    """

    _message_log: List[A2AMessage] = []

    async def send(
        self,
        sender_name: str,
        recipient_name: str,
        task: str,
        payload: Dict[str, Any],
    ) -> A2AMessage:
        """Send a task to another agent and await result."""
        message = A2AMessage(
            sender=sender_name,
            recipient=recipient_name,
            task=task,
            payload=payload,
        )
        self._message_log.append(message)
        log.info("A2A message sent", from_=sender_name, to=recipient_name, task=task)

        # Dynamic agent dispatch
        result = await self._dispatch(recipient_name, task, payload)
        message.result = result
        message.status = "completed"
        return message

    async def _dispatch(self, agent_name: str, task: str, payload: Dict[str, Any]) -> Any:
        """Dynamically load and run the target agent."""
        agent_map = {
            "search_agent": "app.agents.search.agent.SearchAgent",
            "research_agent": "app.agents.research.agent.ResearchAgent",
            "memory_agent": "app.agents.memory.agent.MemoryAgent",
            "chat_agent": "app.agents.chat.agent.ChatAgent",
            "file_agent": "app.agents.file.agent.FileAgent",
            "execution_agent": "app.agents.execution.agent.ExecutionAgent",
            "project_manager_agent": "app.agents.project_manager.agent.ProjectManagerAgent",
        }

        class_path = agent_map.get(agent_name)
        if not class_path:
            raise ValueError(f"Unknown agent: {agent_name}")

        module_path, class_name = class_path.rsplit(".", 1)
        import importlib
        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)
        agent = agent_class()

        from app.core.langgraph.state import AgentState
        state = AgentState(
            raw_input=task,
            intent=payload.get("intent", task),
            metadata=payload,
        )
        result = await agent.run(state)
        return result.get("final_response", "")

    def get_message_log(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self._message_log]


# Module singleton
a2a_protocol = A2AProtocol()
