"""
Notification Agent — Real-time notification manager and task delivery loop.
Delivers popups, dashboard alerts, and completes task lifecycle upon acknowledgement.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List
import structlog

from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)

# Global Notification Queue for SSE / WebSocket streaming
notification_queue: asyncio.Queue = asyncio.Queue()
active_notifications: Dict[str, Dict[str, Any]] = {}


class NotificationAgent(BaseAgent):
    name = "notification_agent"
    description = "Delivers real-time notifications and manages task acknowledgement/completion"
    supported_intents = ["notify_deliver", "notify_acknowledge"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        intent = state.intent
        if intent == "notify_acknowledge":
            return await self.acknowledge_notification(state.metadata.get("task_id", ""))

        return await self.deliver_notification(
            title=state.metadata.get("title", "Task Notification"),
            message=state.raw_input,
            task_id=state.metadata.get("task_id", ""),
            priority=state.metadata.get("priority", "medium"),
        )

    async def deliver_notification(
        self, title: str, message: str, task_id: str = "", priority: str = "medium"
    ) -> Dict[str, Any]:
        """Publish notification event to global SSE queue."""
        import uuid
        notif_id = f"notif_{uuid.uuid4().hex[:8]}"
        payload = {
            "id": notif_id,
            "task_id": task_id,
            "title": title,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "delivered",
            "acknowledged": False,
        }

        active_notifications[notif_id] = payload
        await notification_queue.put(payload)

        log.info("Notification delivered", notif_id=notif_id, title=title)

        return {
            "final_response": f"🔔 [NOTIFICATION DELIVERED]\n**{title}**\n{message}",
            "notification_id": notif_id,
            "status": "delivered",
            "agent_logs": [f"[notification_agent] delivered notification {notif_id}"],
        }

    async def acknowledge_notification(self, task_id: str) -> Dict[str, Any]:
        """Acknowledge notification and mark task completed."""
        from app.api.routes.tasks import _tasks
        if task_id in _tasks:
            _tasks[task_id]["status"] = "completed"
            _tasks[task_id]["completion_percentage"] = 100.0

        for nid, notif in active_notifications.items():
            if notif.get("task_id") == task_id or nid == task_id:
                notif["acknowledged"] = True
                notif["status"] = "completed"

        log.info("Task notification acknowledged and completed", task_id=task_id)

        return {
            "final_response": f"✅ Task `{task_id}` marked as COMPLETED and acknowledged.",
            "task_id": task_id,
            "status": "completed",
            "agent_logs": [f"[notification_agent] acknowledged task {task_id}"],
        }


notification_agent = NotificationAgent()
