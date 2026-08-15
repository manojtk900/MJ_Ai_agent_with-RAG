"""
Unit tests for Reminder Agent & Task Scheduler.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.agents.reminder.agent import ReminderAgent
from app.core.langgraph.state import AgentState
from app.services.scheduler import TaskScheduler


def test_task_scheduler_singleton():
    s1 = TaskScheduler.get_instance()
    s2 = TaskScheduler.get_instance()
    assert s1 is s2


@pytest.mark.asyncio
@patch("app.services.scheduler.scheduler_service.schedule_one_time_reminder")
async def test_reminder_agent_one_time(mock_schedule):
    mock_schedule.return_value = "reminder_12345"

    agent = ReminderAgent()
    state = AgentState(raw_input="Remind me tomorrow at 9 AM to submit assignment", intent="reminder")

    result = await agent.execute(state)

    assert "Reminder Scheduled" in result["final_response"]
    assert result["action"] == "reminder.schedule"
    assert result["task_data"]["status"] == "scheduled"
    mock_schedule.assert_called_once()
