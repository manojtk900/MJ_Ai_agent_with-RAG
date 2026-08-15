"""
Unit tests for Desktop Agent search capabilities, query extraction, and action chaining.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.agents.desktop.tools import (
    google_search,
    open_browser_url,
    open_desktop_app,
    youtube_search,
)
from app.agents.desktop.agent import DesktopAgent
from app.core.langgraph.state import AgentState


@patch("webbrowser.open")
def test_youtube_search_tool(mock_web_open):
    mock_web_open.return_value = True
    result = youtube_search("kannada songs")
    assert result["status"] == "success"
    assert result["action"] == "youtube_search"
    assert "youtube.com/results?search_query=kannada%20songs" in result["url"]
    mock_web_open.assert_called_once()


@patch("webbrowser.open")
def test_google_search_tool(mock_web_open):
    mock_web_open.return_value = True
    result = google_search("VTU results")
    assert result["status"] == "success"
    assert result["action"] == "google_search"
    assert "google.com/search?q=VTU%20results" in result["url"]
    mock_web_open.assert_called_once()


@pytest.mark.asyncio
@patch("webbrowser.open")
async def test_desktop_agent_open_youtube_and_search_songs(mock_web_open):
    mock_web_open.return_value = True
    agent = DesktopAgent()

    state = AgentState(raw_input="open youtube and search songs", intent="desktop_operation")
    result = await agent.execute(state)

    assert result["status"] == "success"
    assert result["action"] == "action_chain"
    assert len(result["sub_actions"]) == 2
    assert result["sub_actions"][1]["action"] == "youtube_search"
    assert result["sub_actions"][1]["query"] == "songs"


@pytest.mark.asyncio
@patch("webbrowser.open")
async def test_desktop_agent_search_kannada_songs_on_youtube(mock_web_open):
    mock_web_open.return_value = True
    agent = DesktopAgent()

    state = AgentState(raw_input="search kannada songs on youtube", intent="desktop_operation")
    result = await agent.execute(state)

    assert result["status"] == "success"
    assert "youtube_search" in result["final_response"]
    assert "kannada songs" in result["final_response"]


@pytest.mark.asyncio
@patch("webbrowser.open")
async def test_desktop_agent_google_vtu_results(mock_web_open):
    mock_web_open.return_value = True
    agent = DesktopAgent()

    state = AgentState(raw_input="google VTU results", intent="desktop_operation")
    result = await agent.execute(state)

    assert result["status"] == "success"
    assert "google_search" in result["final_response"]
    assert "vtu results" in result["final_response"].lower()



@pytest.mark.asyncio
@patch("webbrowser.open")
async def test_desktop_agent_search_python_tutorial(mock_web_open):
    mock_web_open.return_value = True
    agent = DesktopAgent()

    state = AgentState(raw_input="search python tutorial", intent="desktop_operation")
    result = await agent.execute(state)

    assert result["status"] == "success"
    assert "google_search" in result["final_response"]
    assert "python tutorial" in result["final_response"]


@pytest.mark.asyncio
@patch("webbrowser.open")
async def test_desktop_agent_open_youtube_and_search_toxic(mock_web_open):
    mock_web_open.return_value = True
    agent = DesktopAgent()

    state = AgentState(raw_input="open youtube and search yash toxic trailer", intent="desktop_operation")
    result = await agent.execute(state)

    assert result["status"] == "success"
    assert result["action"] == "action_chain"
    assert result["sub_actions"][1]["action"] == "youtube_search"
    assert result["sub_actions"][1]["query"] == "yash toxic trailer"


@pytest.mark.asyncio
@patch("webbrowser.open")
async def test_desktop_agent_open_youtube_search_songs_no_and(mock_web_open):
    mock_web_open.return_value = True
    agent = DesktopAgent()

    state = AgentState(raw_input="open youtube search songs", intent="desktop_operation")
    result = await agent.execute(state)

    assert result["status"] == "success"
    assert "youtube_search" in result["final_response"]
    assert "songs" in result["final_response"]

