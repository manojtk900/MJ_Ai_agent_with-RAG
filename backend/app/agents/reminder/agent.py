"""
Reminder Agent — Natural language task memory, one-time reminders, and recurring schedules.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
import structlog
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState
from app.services.scheduler import scheduler_service

log = structlog.get_logger(__name__)


class ReminderAgent(BaseAgent):
    name = "reminder_agent"
    description = "Set natural language reminders, tasks, and recurring cron schedules"
    supported_intents = ["reminder", "schedule_task"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        raw_text = state.raw_input.strip()
        now_dt = datetime.now(timezone.utc)

        # ── Parse Reminder details via LLM ──────────────────────
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert NLP parser for task scheduling.\n"
                "Extract task details from user input.\n"
                "Return a JSON object:\n"
                "{\n"
                '  "task": "<short title>",\n'
                '  "time": "<ISO timestamp YYYY-MM-DD HH:MM:SS or relative>",\n'
                '  "is_recurring": true|false,\n'
                '  "cron_expression": "<5-field cron or empty>",\n'
                '  "priority": "low|medium|high"\n'
                "}\n"
                "Assume relative words like 'tomorrow at 9 AM' are relative to the current reference time.",
            ),
            ("human", "Input: {input}\nCurrent Time (UTC): {now}"),
        ])

        try:
            chain = prompt | self.llm | JsonOutputParser()
            details = await chain.ainvoke({"input": raw_text, "now": now_dt.isoformat()})
        except Exception as e:
            log.warning("Reminder LLM parsing failed, using fallback", error=str(e))
            details = {
                "task": raw_text,
                "time": (now_dt + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "is_recurring": False,
                "cron_expression": "",
                "priority": "medium",
            }

        task_title = details.get("task", raw_text)
        time_str = details.get("time", "")
        is_recurring = details.get("is_recurring", False)
        cron_expr = details.get("cron_expression", "")
        priority = details.get("priority", "medium")

        # ── Calculate target datetime ───────────────────────────
        target_dt = now_dt + timedelta(hours=1)
        if time_str:
            try:
                # Try parsing ISO timestamp
                cleaned_iso = time_str.replace("Z", "+00:00")
                target_dt = datetime.fromisoformat(cleaned_iso)
                if target_dt.tzinfo is None:
                    target_dt = target_dt.replace(tzinfo=timezone.utc)
            except Exception:
                # Relative fallbacks
                if "tomorrow" in raw_text.lower():
                    target_dt = now_dt + timedelta(days=1)
                elif "2 hours" in raw_text.lower() or "in 2h" in raw_text.lower():
                    target_dt = now_dt + timedelta(hours=2)

        # ── Register Schedule with TaskScheduler ────────────────
        import uuid
        task_id = str(uuid.uuid4())[:8]

        job_id = ""
        if is_recurring and cron_expr:
            try:
                job_id = scheduler_service.schedule_recurring_reminder(
                    task_id=task_id,
                    title=task_title,
                    cron_expression=cron_expr,
                    callback_data={"raw": raw_text},
                )
            except Exception:
                job_id = scheduler_service.schedule_one_time_reminder(
                    task_id=task_id,
                    title=task_title,
                    run_at=target_dt,
                    callback_data={"raw": raw_text},
                )
        else:
            job_id = scheduler_service.schedule_one_time_reminder(
                task_id=task_id,
                title=task_title,
                run_at=target_dt,
                callback_data={"raw": raw_text},
            )

        formatted_time = target_dt.strftime("%Y-%m-%d %H:%M:%S UTC")

        response_md = (
            f"⏰ **Reminder Scheduled**\n\n"
            f"- **Task:** {task_title}\n"
            f"- **Scheduled Time:** {formatted_time}\n"
            f"- **Recurring:** {'Yes (' + cron_expr + ')' if is_recurring and cron_expr else 'No'}\n"
            f"- **Priority:** {priority.upper()}\n"
            f"- **Status:** Scheduled (`job_id: {job_id}`)"
        )

        return {
            "final_response": response_md,
            "action": "reminder.schedule",
            "task_data": {
                "id": task_id,
                "task": task_title,
                "time": formatted_time,
                "is_recurring": is_recurring,
                "cron": cron_expr,
                "status": "scheduled",
            },
            "agent_logs": [f"[reminder_agent] task '{task_title}' scheduled for {formatted_time}"],
        }
