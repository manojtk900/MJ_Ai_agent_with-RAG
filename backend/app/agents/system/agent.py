"""
System Agent — Local machine operations with permission control.
"""
from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Any, Dict
import structlog
from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)


class SystemAgent(BaseAgent):
    name = "system_agent"
    description = "OS operations: create files, run commands, manage local machine"
    supported_intents = ["system_operation"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        action = state.metadata.get("system_action", "")

        if action == "create_file":
            path = Path(state.metadata.get("path", "output.txt"))
            content = state.metadata.get("content", "")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {"final_response": f"✅ File created: `{path}`", "action": "file.create", "response_type": "action"}

        elif action == "run_command":
            cmd = state.metadata.get("command", "")
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                output = result.stdout or result.stderr
            except subprocess.TimeoutExpired:
                output = "Command timed out after 30 seconds."
            return {
                "final_response": f"```\n$ {cmd}\n\n{output}\n```",
                "action": "system.execute",
                "response_type": "code",
            }

        elif action == "list_dir":
            path = Path(state.metadata.get("path", "."))
            items = sorted(str(p) for p in path.iterdir())
            return {"final_response": "```\n" + "\n".join(items) + "\n```"}

        elif action == "delete_file":
            path = Path(state.metadata.get("path", ""))
            return {
                "action": "file.delete",
                "requires_approval": True,
                "final_response": f"⚠️ Requesting approval to delete: `{path}`",
            }

        return {"final_response": f"Unknown system action: {action}"}
