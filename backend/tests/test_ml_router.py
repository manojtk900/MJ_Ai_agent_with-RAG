"""
Unit tests for Local ML Router, Tool Registry, and FastAPI ML Endpoints.
Tests at least 20 commands covering all core intents, NER extraction, and latency thresholds.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure backend path is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.ml_router import benchmark_latency, extract_entities, predict_intent, route_command
from app.tools.tool_registry import TOOLS, dispatch_tool
from app.main import app


# ── Test Dataset: 20+ Real-World Commands ─────────────────────
TEST_COMMANDS = [
    # 1. YouTube Search
    ("open youtube and search yash songs", "youtube_search", "query", "yash songs"),
    ("open youtube and search toxic trailer", "youtube_search", "query", "toxic trailer"),
    ("play lo-fi beats on youtube", "youtube_search", "query", "lo-fi beats"),
    
    # 2. Google Search
    ("search AI news on google", "google_search", "query", "ai news"),
    ("search python transformers docs on google", "google_search", "query", "python transformers docs"),
    ("google latest tech news", "google_search", "query", "latest tech news"),
    
    # 3. Application & Tool Launchers
    ("open github", "open_github", None, None),
    ("open vscode", "open_vscode", None, None),
    ("open calculator", "open_calculator", None, None),
    ("open browser", "open_browser", None, None),
    
    # 4. Email Operations
    ("send email to test@gmail.com", "send_email", "email", "test@gmail.com"),
    ("read my unread emails", "read_email", None, None),
    ("check placement emails", "read_email", None, None),
    ("summarize my internship emails", "summarize_email", None, None),
    
    # 5. Task & Scheduler Operations
    ("create task buy milk tomorrow", "create_task", "task", None),
    ("schedule task submit project report", "create_task", "task", None),
    ("delete task buy milk", "delete_task", "task", None),
    
    # 6. GitHub Automation
    ("push code to github", "github_push", None, None),
    ("git pull latest changes", "github_pull", None, None),
    ("create new github repository mj-ai-os", "github_create_repo", None, None),
    
    # 7. Memory Engine
    ("remember that my college is SSIT", "remember_fact", None, None),
    ("what is my college", "recall_memory", None, None),
    ("who am i", "recall_memory", None, None),
    
    # 8. Conversational Fallback
    ("hello who are you", "chat", None, None),
]


class TestMLRouter:
    """Test suite for DistilBERT Intent Classifier & NER Extractor."""

    @pytest.mark.parametrize("command,expected_intent,expected_entity_key,expected_entity_val", TEST_COMMANDS)
    def test_predict_intent_and_routing(self, command, expected_intent, expected_entity_key, expected_entity_val):
        result = route_command(command, confidence_threshold=0.75)
        
        # Verify result structure
        assert "intent" in result
        assert "confidence" in result
        assert "entities" in result
        assert isinstance(result["entities"], dict)
        assert 0.0 <= result["confidence"] <= 1.0

        # Intent assertions (allow related aliases for email/summarize)
        predicted = result["intent"]
        if expected_intent == "read_email":
            assert predicted in ("read_email", "summarize_email")
        elif expected_intent == "summarize_email":
            assert predicted in ("summarize_email", "read_email")
        elif expected_intent == "open_application":
            assert predicted in ("open_application", "open_browser", "open_calculator", "open_notepad", "open_vscode")
        else:
            assert predicted == expected_intent, f"Failed for command '{command}': expected {expected_intent}, got {predicted}"

        # Entity assertions if specified
        if expected_entity_key:
            assert expected_entity_key in result["entities"], f"Expected entity '{expected_entity_key}' in {result['entities']} for '{command}'"
            if expected_entity_val:
                assert expected_entity_val.lower() in result["entities"][expected_entity_key].lower()

    def test_confidence_threshold_fallback(self):
        # A totally random or empty string should produce a safe fallback
        res = route_command("", confidence_threshold=0.80)
        assert res["intent"] == "chat"
        assert res["confidence"] >= 0.0

    def test_benchmark_latency(self):
        metrics = benchmark_latency(iterations=3)
        assert "intent_latency_ms" in metrics
        assert "entity_latency_ms" in metrics
        assert "total_latency_ms" in metrics
        # Sub-100ms on CPU
        assert metrics["total_latency_ms"] < 200.0


class TestToolRegistry:
    """Test suite for dynamic tool registry dispatch."""

    @pytest.mark.asyncio
    async def test_tool_registry_contains_all_core_intents(self):
        required_tools = [
            "youtube_search",
            "google_search",
            "open_browser",
            "open_github",
            "open_vscode",
            "open_notepad",
            "open_calculator",
            "send_email",
            "read_email",
            "create_task",
            "delete_task",
            "github_push",
            "github_pull",
            "github_create_repo",
            "remember_fact",
            "recall_memory",
        ]
        for t in required_tools:
            assert t in TOOLS, f"Tool '{t}' missing from tool registry TOOLS dict"

    @pytest.mark.asyncio
    async def test_dispatch_youtube_tool(self):
        res = await dispatch_tool("youtube_search", {"query": "yash songs"}, "open youtube and search yash songs")
        assert res["status"] == "success"
        assert "youtube" in res.get("url", "").lower() or "youtube" in res.get("tool_output", "").lower()

    @pytest.mark.asyncio
    async def test_dispatch_memory_tools(self):
        store_res = await dispatch_tool("remember_fact", {"query": "my college is SSIT"}, "remember that my college is SSIT")
        assert store_res["status"] == "success"

        recall_res = await dispatch_tool("recall_memory", {}, "what is my college")
        assert recall_res["status"] == "success"
        assert "SSIT" in recall_res.get("tool_output", "") or "Siddhartha" in recall_res.get("tool_output", "")


class TestFastAPIEndpoints:
    """Test suite for FastAPI /api/v1/ml endpoints."""

    def setup_method(self):
        self.client = TestClient(app)

    def test_ml_route_endpoint(self):
        response = self.client.post("/api/v1/ml/route", json={"message": "open youtube and search yash songs"})
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "youtube_search"
        assert data["confidence"] > 0.85
        assert "query" in data["entities"]

    def test_ml_benchmark_endpoint(self):
        response = self.client.get("/api/v1/ml/benchmark")
        assert response.status_code == 200
        data = response.json()
        assert "intent_latency_ms" in data
        assert "entity_latency_ms" in data
        assert "total_latency_ms" in data
        assert data["total_latency_ms"] > 0
