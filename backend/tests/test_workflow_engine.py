"""
Unit tests for Autonomous Workflow Engine.
"""
import pytest
from app.services.workflow_engine import workflow_engine


@pytest.mark.asyncio
async def test_morning_briefing_workflow():
    result = await workflow_engine.execute_morning_briefing()

    assert result["status"] == "completed"
    assert result["workflow"] == "morning_briefing"
    assert "Good Morning" in result["briefing"]
    assert result["notification"]["status"] == "delivered"
