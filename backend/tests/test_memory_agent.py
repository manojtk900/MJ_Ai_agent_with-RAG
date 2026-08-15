"""
Unit tests for Memory Agent & Long-Term Personal Profile Memory.
"""
import pytest
from app.agents.memory.agent import MemoryAgent
from app.core.langgraph.state import AgentState


@pytest.mark.asyncio
async def test_memory_agent_store():
    agent = MemoryAgent()
    state = AgentState(
        raw_input="My college is Sri Siddhartha and my project is MJ AI Assistant",
        intent="memory_store",
        user_id="user_123",
    )

    result = await agent.execute(state)
    assert "Personal Fact Stored" in result["final_response"]


@pytest.mark.asyncio
async def test_memory_agent_recall():
    agent = MemoryAgent()

    # Store
    store_state = AgentState(raw_input="My college is Sri Siddhartha", intent="memory_store")
    await agent.execute(store_state)

    # Retrieve
    retrieve_state = AgentState(raw_input="What is my college?", intent="memory_retrieve")
    result = await agent.execute(retrieve_state)

    assert "Sri Siddhartha" in result["final_response"]
