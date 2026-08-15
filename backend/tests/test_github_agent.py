"""
Unit tests for GitHub Agent and git tools.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.agents.execution.agent import ExecutionAgent
from app.agents.execution.git_tools import get_repo_status
from app.core.langgraph.state import AgentState


def test_get_repo_status():
    status = get_repo_status()
    assert status["status"] == "success"
    assert "branch" in status


@pytest.mark.asyncio
@patch("app.agents.execution.agent.git_add_commit_push")
async def test_execution_agent_git_push(mock_push):
    mock_push.return_value = {
        "status": "success",
        "message": "Pushed to GitHub main",
        "tool_output": "[TOOL] git_add_commit_push\n[SUCCESS] Committed 5 files",
    }

    agent = ExecutionAgent()
    state = AgentState(raw_input="Push my latest code", intent="github_automation")

    result = await agent.execute(state)

    assert result["status"] == "success"
    assert "[TOOL] git_add_commit_push" in result["final_response"]
    mock_push.assert_called_once()
