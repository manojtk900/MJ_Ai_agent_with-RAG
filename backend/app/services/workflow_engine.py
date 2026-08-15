"""
Autonomous Workflow Engine — Executes multi-step autonomous agent workflows (Morning Briefing, Daily Digest, Project Audit).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import structlog

from app.agents.email.gmail_service import gmail_service
from app.agents.execution.git_tools import get_repo_status
from app.agents.notification.agent import notification_agent

log = structlog.get_logger(__name__)


class WorkflowEngine:
    _instance: Optional[WorkflowEngine] = None

    @classmethod
    def get_instance(cls) -> WorkflowEngine:
        if cls._instance is None:
            cls._instance = WorkflowEngine()
        return cls._instance

    async def execute_morning_briefing(self) -> Dict[str, Any]:
        """
        Morning Briefing Workflow:
        1. Check Gmail (inbox + internship emails)
        2. Check GitHub status
        3. Assemble AI summary
        4. Deliver notification
        """
        log.info("Starting Morning Briefing Workflow...")

        # Step 1: Email Check
        emails = await gmail_service.fetch_unread_emails()
        email_summary = await gmail_service.summarize_emails(emails)

        # Step 2: GitHub Repository Check
        git_status = get_repo_status()
        branch = git_status.get("branch", "main")
        changed_count = git_status.get("changed_files_count", 0)

        # Step 3: Assemble Briefing Report
        now_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
        briefing_md = (
            f"🌅 **Good Morning! Here is your Daily Briefing ({now_str}):**\n\n"
            f"### 📧 Gmail Inbox\n{email_summary}\n\n"
            f"### 🐙 GitHub Repository\n"
            f"- **Active Branch:** `{branch}`\n"
            f"- **Uncommitted Changed Files:** `{changed_count}`\n\n"
            f"Have a productive day!"
        )

        # Step 4: Deliver Notification
        notif_result = await notification_agent.deliver_notification(
            title="🌅 Morning Briefing Ready",
            message=f"You have {len(emails)} unread email(s) and {changed_count} changed file(s) on branch '{branch}'.",
            priority="high",
        )

        log.info("Morning Briefing Workflow complete")

        return {
            "status": "completed",
            "workflow": "morning_briefing",
            "briefing": briefing_md,
            "notification": notif_result,
        }


workflow_engine = WorkflowEngine.get_instance()
