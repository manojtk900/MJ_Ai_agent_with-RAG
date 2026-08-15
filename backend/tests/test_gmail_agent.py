"""
Unit tests for Gmail Agent and email filtering.
"""
import pytest
from app.agents.email.agent import EmailAgent
from app.core.langgraph.state import AgentState


@pytest.mark.asyncio
async def test_email_agent_internship_filter():
    agent = EmailAgent()
    state = AgentState(raw_input="Any internship emails?", intent="email_read")

    result = await agent.execute(state)

    assert "Found" in result["final_response"]
    assert len(result["emails"]) > 0


@pytest.mark.asyncio
async def test_email_agent_draft_reply():
    agent = EmailAgent()
    state = AgentState(
        raw_input="Reply politely to Deloitte recruiter",
        intent="email_send",
        metadata={"to": "careers@deloitte.com", "subject": "Internship Response"},
    )

    result = await agent.execute(state)

    assert "Email Draft Ready" in result["final_response"]
    assert result["requires_approval"] is True
