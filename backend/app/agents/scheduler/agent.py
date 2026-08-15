"""
Scheduler Agent — Recurring cron jobs and background workflows.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict
import structlog
from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)


class SchedulerAgent(BaseAgent):
    name = "scheduler_agent"
    description = "Recurring cron jobs, background workflows, automated scheduling"
    supported_intents = ["schedule_task"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        from croniter import croniter
        cron_expr = state.metadata.get("cron", "0 9 * * 1")
        task_name = state.metadata.get("name", f"task_{state.user_id}")
        task_description = state.metadata.get("task", state.raw_input)

        if not croniter.is_valid(cron_expr):
            return {"error": f"Invalid cron: {cron_expr}", "final_response": f"❌ Invalid cron expression: `{cron_expr}`"}

        next_run = croniter(cron_expr, datetime.now()).get_next(datetime)

        return {
            "final_response": (
                f"⏰ **Scheduled Task Created**\n\n"
                f"- **Name:** `{task_name}`\n"
                f"- **Schedule:** `{cron_expr}`\n"
                f"- **Task:** {task_description}\n"
                f"- **Next run:** {next_run.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                f"> The task will run automatically in the background."
            ),
            "response_type": "action",
            "artifacts": [{"type": "scheduled_task", "name": task_name, "cron": cron_expr, "task": task_description}],
            "agent_logs": [f"[scheduler_agent] registered {task_name} cron={cron_expr}"],
        }
