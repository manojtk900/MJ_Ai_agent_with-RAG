"""
Notifications API Route — Live SSE notifications and task acknowledgement endpoint.
"""
from typing import Any, Dict, List
import asyncio
import json

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.agents.notification.agent import (
    active_notifications,
    notification_agent,
    notification_queue,
)

router = APIRouter(prefix="/notifications")


@router.get("/stream")
async def stream_notifications():
    """Server-Sent Events (SSE) stream for active notifications."""

    async def event_generator():
        while True:
            try:
                # Wait for next notification payload
                payload = await asyncio.wait_for(notification_queue.get(), timeout=15.0)
                yield {
                    "event": "notification",
                    "data": json.dumps(payload),
                }
            except asyncio.TimeoutError:
                # Keep-alive heartbeat comment
                yield {"event": "ping", "data": "keep-alive"}

    return EventSourceResponse(event_generator())


@router.get("/", response_model=List[Dict[str, Any]])
async def list_notifications():
    """Return all active delivered notifications."""
    return list(active_notifications.values())


@router.post("/{task_id}/acknowledge")
async def acknowledge_task_notification(task_id: str):
    """Mark task notification acknowledged and complete the task lifecycle."""
    result = await notification_agent.acknowledge_notification(task_id)
    return result
