"""
Unit tests for Notification Agent & Task Completion Loop.
"""
import pytest
from app.agents.notification.agent import notification_agent, active_notifications
from app.api.routes.tasks import _tasks


@pytest.mark.asyncio
async def test_notification_delivery():
    res = await notification_agent.deliver_notification(
        title="Test Task",
        message="Submit assignment",
        task_id="task_999",
        priority="high",
    )
    assert res["status"] == "delivered"
    assert "notif_" in res["notification_id"]


@pytest.mark.asyncio
async def test_notification_acknowledgement_loop():
    # 1. Setup task
    _tasks["task_999"] = {"id": "task_999", "title": "Submit assignment", "status": "pending"}

    # 2. Deliver notification
    await notification_agent.deliver_notification(
        title="Submit assignment",
        message="Due now",
        task_id="task_999",
    )

    # 3. User acknowledges
    ack_res = await notification_agent.acknowledge_notification("task_999")

    # 4. Verify task status marked COMPLETED
    assert ack_res["status"] == "completed"
    assert _tasks["task_999"]["status"] == "completed"
