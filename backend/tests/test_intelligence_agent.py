"""
Unit and Integration Tests for MJ Intelligence Agent, Router Gate, Local RAG, and Safety Gates.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.agents.intelligence.agent import IntelligenceAgent, intelligence_agent
from app.agents.intelligence.router_gate import RouterGate
from app.agents.intelligence.rag import LocalRAGEngine, rag_engine
from app.agents.intelligence.llm import OllamaCircuitBreaker, IntelligenceLLMService
from app.agents.intelligence.traces import trace_recorder
from app.tools.tool_registry import tool_open_application, dispatch_tool


client = TestClient(app)


# ── 1. Router Gate & "DO NOT ACT" Tests ────────────────────────
def test_router_gate_non_action_queries():
    """Verify conversational, career, coding, and knowledge queries are never executed as OS tools."""
    non_action_samples = [
        ("hi", "CONVERSATION"),
        ("hello how are you", "CONVERSATION"),
        ("how to prepare for new AI jobs", "PLANNING"),
        ("how should I study for machine learning interviews", "PLANNING"),
        ("who is Yash", "KNOWLEDGE_WORLD"),
        ("who is PM of India", "KNOWLEDGE_WORLD"),
        ("what is my project", "KNOWLEDGE_PROJECT"),
        ("what model did I train", "KNOWLEDGE_PROJECT"),
        ("what is the intent model accuracy", "KNOWLEDGE_PROJECT"),
        ("write Python code to add two numbers", "CODING"),
        ("explain transformers", "CONVERSATION"),
    ]

    for text, expected_route in non_action_samples:
        decision = RouterGate.evaluate(
            raw_input=text,
            predicted_intent="chat",
            confidence=0.95,
            entities={},
        )
        assert decision["execute_tool"] is False, f"Failed for '{text}': execute_tool was True"
        assert decision["route"] == expected_route, f"Failed route for '{text}': got {decision['route']}, expected {expected_route}"


def test_router_gate_action_queries():
    """Verify genuine desktop commands are allowed to execute."""
    action_samples = [
        ("open youtube", "open_browser"),
        ("open github", "open_github"),
        ("open vscode", "open_vscode"),
        ("open calculator", "open_calculator"),
        ("search songs on youtube", "youtube_search"),
        ("google VTU results", "google_search"),
    ]

    for text, intent in action_samples:
        decision = RouterGate.evaluate(
            raw_input=text,
            predicted_intent=intent,
            confidence=0.98,
            entities={"query": "test"} if "search" in intent else {},
        )
        assert decision["execute_tool"] is True, f"Failed for action '{text}'"
        assert decision["route"] == "ACTION"


def test_router_gate_confirmation_for_risky_ops():
    """Verify risky operations require explicit confirmation."""
    risky_intents = ["github_push", "send_email", "delete_task"]
    for intent in risky_intents:
        decision = RouterGate.evaluate(
            raw_input=f"execute {intent}",
            predicted_intent=intent,
            confidence=0.99,
            entities={},
        )
        assert decision["execute_tool"] is False
        assert decision.get("requires_confirmation") is True
        assert decision["route"] == "CONFIRMATION_REQUIRED"


# ── 2. Local RAG Engine & Citations ────────────────────────────
def test_local_rag_search_and_citations():
    """Verify local RAG retrieves documentation and generates citations."""
    query = "What is the accuracy of the intent model?"
    result = rag_engine.search(query, top_k=2)

    assert result.query == query
    assert len(result.chunks) > 0
    assert len(result.citations) > 0
    assert result.confidence > 0.0

    # Top citation should reference documentation
    top_citation = result.citations[0]
    assert len(top_citation.source_file) > 0
    assert len(top_citation.excerpt) > 0


def test_local_rag_synthesis():
    """Verify RAG direct answer synthesis."""
    query = "What is the intent accuracy?"
    result = rag_engine.search(query, top_k=1)
    answer = rag_engine.synthesize_answer(query, result)

    assert len(answer) > 20
    assert "**Sources:**" in answer


# ── 3. Ollama Circuit Breaker & Fallback ────────────────────────
def test_circuit_breaker_tripping():
    """Verify circuit breaker trips to offline mode after consecutive failures."""
    cb = OllamaCircuitBreaker(failure_threshold=3, cooldown_seconds=5.0)
    assert cb.can_attempt() is True

    cb.record_failure()
    cb.record_failure()
    assert cb.can_attempt() is True
    assert cb.is_offline is False

    cb.record_failure()  # 3rd failure trips
    assert cb.is_offline is True
    assert cb.can_attempt() is False


@pytest.mark.asyncio
async def test_intelligence_agent_offline_resilience():
    """Verify IntelligenceAgent provides natural answers without crashing when Ollama is offline."""
    agent = IntelligenceAgent()

    # Test greeting
    res_greet = await agent.answer("hi")
    assert "MJ AI Assistant" in res_greet["answer"] or "operational" in res_greet["answer"]
    assert res_greet["source"] in {"offline_fallback", "rag_synthesis", "llm_ollama", "llm_cloud"}

    # Test career question
    res_career = await agent.answer("how to prepare for new AI jobs")
    assert "Roadmap" in res_career["answer"] or "Python" in res_career["answer"]
    assert res_career["route"] == "PLANNING"

    # Test coding question
    res_code = await agent.answer("write python code to add two numbers")
    assert "def add" in res_code["answer"] or "```python" in res_code["answer"]
    assert res_code["route"] == "CODING"


# ── 4. Open Application Safety Block ───────────────────────────
@pytest.mark.asyncio
async def test_tool_open_application_safety_block():
    """Verify conversational phrases sent to tool_open_application are safely rejected."""
    bad_inputs = [
        "how to prepare for AI jobs",
        "who is the Prime Minister of India",
        "explain transformers to me",
    ]

    for bad in bad_inputs:
        res = await tool_open_application(entities={}, raw_text=bad)
        assert res["status"] == "error"
        assert "not recognized as a valid desktop application" in res["message"]


# ── 5. FastAPI Endpoints Verification ──────────────────────────
def test_fastapi_intelligence_chat():
    """Verify /api/v1/intelligence/chat endpoint returns structured response."""
    payload = {"message": "what is my project?"}
    response = client.post("/api/v1/intelligence/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "route" in data
    assert "source" in data


def test_fastapi_intelligence_status():
    """Verify /api/v1/intelligence/status returns complete telemetry."""
    response = client.get("/api/v1/intelligence/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ml_router" in data
    assert "rag_engine" in data
    assert "circuit_breaker" in data


def test_fastapi_intelligence_search():
    """Verify /api/v1/intelligence/search returns vector search chunks."""
    payload = {"query": "intent accuracy", "top_k": 2}
    response = client.post("/api/v1/intelligence/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "chunks" in data
    assert len(data["chunks"]) > 0


def test_fastapi_intelligence_traces():
    """Verify /api/v1/intelligence/traces endpoint."""
    response = client.get("/api/v1/intelligence/traces?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
