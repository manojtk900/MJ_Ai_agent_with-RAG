"""
Router Gate — Action vs Knowledge vs Chat vs Planning Discriminator with DO-NOT-ACT Filter.
Ensures conversational and analytical queries never mistakenly execute OS desktop tools.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple
import structlog

from app.agents.intelligence.schemas import RiskLevel, RouteCategory

log = structlog.get_logger(__name__)

# Direct Action Intents from ML Classifier
ACTION_INTENTS = {
    "youtube_search",
    "google_search",
    "open_browser",
    "open_github",
    "open_vscode",
    "open_notepad",
    "open_calculator",
    "open_application",
    "send_email",
    "read_email",
    "summarize_email",
    "create_task",
    "delete_task",
    "update_task",
    "github_push",
    "github_pull",
    "github_create_repo",
    "remember_fact",
    "recall_memory",
}

# Question / Non-Action Starters that MUST NEVER become open_app()
QUESTION_STARTERS = (
    "how", "what", "who", "why", "when", "where", "which",
    "tell me", "explain", "describe", "write", "code", "create a function",
    "can you", "could you explain", "is there", "do you know",
    "how to", "how do i", "how should i", "give me", "suggest",
)

# Project Knowledge Indicators
PROJECT_KEYWORDS = {
    "project", "mj", "jarvis", "architecture", "intent", "entity", "ner",
    "distilbert", "model", "accuracy", "f1", "dataset", "router",
    "desktop agent", "intelligence agent", "controller", "langgraph",
    "fastapi", "tools", "backend", "frontend", "training", "knowledge base"
}

# World / Real-Time Knowledge Indicators
WORLD_KEYWORDS = {
    "pm of india", "prime minister", "president", "weather", "news", "jobs",
    "salary", "capital of", "who is", "latest news", "stock price",
    "vtu results", "cricket score", "today", "yesterday"
}

# Coding Indicators
CODING_KEYWORDS = {
    "python", "javascript", "react", "fastapi", "html", "css", "sql",
    "function", "algorithm", "dsa", "bubble sort", "binary search",
    "write code", "fix error", "syntax", "class", "async", "script"
}

# Career & Planning Indicators
PLANNING_KEYWORDS = {
    "prepare for", "roadmap", "learning path", "study plan", "study",
    "interview prep", "interview", "how to learn", "how to become",
    "career", "guidance", "tips for", "how should i", "prepare"
}


class RouterGate:
    """
    Evaluates ML predictions, user input heuristics, and risk matrices to determine
    the exact routing category and prevent false action execution.
    """

    @staticmethod
    def evaluate(
        raw_input: str,
        predicted_intent: str,
        confidence: float,
        entities: Dict[str, Any],
    ) -> Dict[str, Any]:
        text = raw_input.strip()
        lower = text.lower()

        # ── 0. Check for Explicit Action Prefixes ───────────────────────
        is_explicit_action_prefix = lower.startswith((
            "open ", "launch ", "start ", "run ", "search ", "google ", "play ", "youtube ",
            "remind ", "create task", "schedule ", "set reminder", "add task", "remember "
        ))
        has_non_action_suffix = any(lower.startswith(f"{verb} {q}") for verb in ("open", "launch", "start") for q in ("how", "what", "who", "why", "when", "where", "explain"))

        if is_explicit_action_prefix and not has_non_action_suffix:
            # Low-risk action with direct command prefix
            if predicted_intent in ACTION_INTENTS:
                high_risk_intents = {"github_push", "delete_task", "send_email"}
                if predicted_intent in high_risk_intents:
                    return {
                        "route": "CONFIRMATION_REQUIRED",
                        "intent": predicted_intent,
                        "execute_tool": False,
                        "requires_confirmation": True,
                        "reason": f"High risk operation ({predicted_intent}) requires confirmation",
                    }
                return {
                    "route": "ACTION",
                    "intent": predicted_intent,
                    "execute_tool": True,
                    "reason": f"Explicit imperative action verb detected ({predicted_intent})",
                }

        # ── 1. Check for Mandatory "DO NOT ACT" Filters ─────────────────
        is_question = lower.startswith(QUESTION_STARTERS) or lower.endswith("?")
        has_planning_kw = any(kw in lower for kw in PLANNING_KEYWORDS)
        has_coding_kw = any(kw in lower for kw in CODING_KEYWORDS) and not is_explicit_action_prefix
        has_project_kw = any(kw in lower for kw in PROJECT_KEYWORDS)
        has_world_kw = any(kw in lower for kw in WORLD_KEYWORDS)

        # Conversational greetings
        if lower in {"hi", "hello", "hey", "good morning", "good evening", "namaste", "sup", "yo"}:
            return {
                "route": "CONVERSATION",
                "intent": "conversation",
                "execute_tool": False,
                "reason": "Direct greeting phrase",
            }

        # Career / Planning questions (e.g., "how to prepare for new AI jobs", "how should I study")
        if has_planning_kw or ("how to" in lower and not is_explicit_action_prefix) or ("how should i" in lower):
            return {
                "route": "PLANNING",
                "intent": "planning",
                "execute_tool": False,
                "reason": "Career / Planning query — blocked from OS tools",
            }

        # Coding questions (e.g., "write Python code to add two numbers")
        if (has_coding_kw or lower.startswith(("write", "code", "implement", "create a function"))) and not is_explicit_action_prefix:
            return {
                "route": "CODING",
                "intent": "coding",
                "execute_tool": False,
                "reason": "Coding assistance query — routed to Intelligence Agent",
            }

        # Project RAG questions (e.g., "what is my project?", "what is the intent accuracy?")
        if (has_project_kw and is_question) or "what model" in lower or "intent accuracy" in lower or "my project" in lower:
            return {
                "route": "KNOWLEDGE_PROJECT",
                "intent": "knowledge_project",
                "execute_tool": False,
                "reason": "Project architecture / training query — routed to Local RAG",
            }

        # Real-time / World questions (e.g., "who is PM of India", "who is Yash")
        if (has_world_kw or lower.startswith("who is") or lower.startswith("who was")) and not is_explicit_action_prefix:
            return {
                "route": "KNOWLEDGE_WORLD",
                "intent": "knowledge_world",
                "execute_tool": False,
                "reason": "World knowledge / person query — routed to Web / Intelligence",
            }

        # General Question Fallback
        if is_question and not is_explicit_action_prefix:
            return {
                "route": "CONVERSATION",
                "intent": "conversation",
                "execute_tool": False,
                "reason": "General question — blocked from OS tools",
            }

        # ── 2. Action Intent Evaluation & Confidence Gating ────────────
        if predicted_intent in ACTION_INTENTS:
            # Dangerous operations requiring explicit confirmation
            high_risk_intents = {"github_push", "delete_task", "send_email"}
            if predicted_intent in high_risk_intents:
                return {
                    "route": "CONFIRMATION_REQUIRED",
                    "intent": predicted_intent,
                    "execute_tool": False,
                    "requires_confirmation": True,
                    "reason": f"High risk operation ({predicted_intent}) requires explicit user confirmation",
                }

            # Valid Low-Risk Action with High Confidence (>= 0.90)
            if confidence >= 0.90:
                return {
                    "route": "ACTION",
                    "intent": predicted_intent,
                    "execute_tool": True,
                    "reason": f"High confidence action intent ({predicted_intent}, conf={confidence:.3f})",
                }

            # Moderate Confidence Action (0.70 <= confidence < 0.90)
            if 0.70 <= confidence < 0.90:
                # Check if it has clear action phrasing
                if lower.startswith(("open", "launch", "start", "run", "search", "google", "youtube", "play", "find")):
                    return {
                        "route": "ACTION",
                        "intent": predicted_intent,
                        "execute_tool": True,
                        "reason": f"Moderate confidence action with imperative action verb (conf={confidence:.3f})",
                    }
                else:
                    return {
                        "route": "CONFIRMATION_REQUIRED",
                        "intent": predicted_intent,
                        "execute_tool": False,
                        "requires_confirmation": True,
                        "reason": f"Ambiguous action confidence ({confidence:.3f}), requesting clarification",
                    }

        # ── 3. Fallback Route: Intelligence Agent ──────────────────────
        return {
            "route": "CONVERSATION",
            "intent": "chat",
            "execute_tool": False,
            "reason": "Unclassified / Low confidence intent routed to Intelligence Agent",
        }
