"""
Controller Agent — Local ML Command Router & Workflow Entry Point.
Responsibilities: ML Intent detection, NER extraction, tool dispatching, context building.
"""
from __future__ import annotations

from typing import Any, Dict, List

import structlog

from app.agents.base import BaseAgent
from app.agents.intelligence.agent import intelligence_agent
from app.agents.intelligence.router_gate import RouterGate
from app.agents.ml_router import route_command
from app.config import settings
from app.core.context.engine import ContextEngine
from app.core.langgraph.state import AgentState
from app.tools.tool_registry import dispatch_tool

log = structlog.get_logger(__name__)


class ControllerAgent(BaseAgent):
    name = "controller_agent"
    description = "Local ML Intent detection, RouterGate evaluation, and Intelligence dispatching"
    supported_intents = ["*"]  # Handles all intents via local ML routing

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        # ── 1. Build Context ──────────────────────────────────
        context_engine = ContextEngine()
        context = await context_engine.build(
            user_id=state.user_id,
            conversation_id=state.conversation_id,
            current_input=state.raw_input,
        )

        # ── 2. Local ML Command Routing ────────────────────────
        routing = route_command(state.raw_input, confidence_threshold=0.80)
        intent = routing["intent"]
        confidence = routing["confidence"]
        entities = routing["entities"]

        log.info(
            "ML Router predicted command intent",
            intent=intent,
            confidence=confidence,
            entities=entities,
            raw_input=state.raw_input,
        )

        # ── 3. Router Gate & DO NOT ACT Evaluation ─────────────
        gate_decision = RouterGate.evaluate(
            raw_input=state.raw_input,
            predicted_intent=intent,
            confidence=confidence,
            entities=entities,
        )
        route = gate_decision["route"]
        log.info("RouterGate decision", route=route, reason=gate_decision.get("reason"))

        # Update state metadata with extracted entities and route
        metadata = dict(state.metadata or {})
        metadata["entities"] = entities
        metadata["confidence"] = confidence
        metadata["route"] = route

        # ── 4. Confirmation Required Gate ──────────────────────
        if gate_decision.get("requires_confirmation"):
            return {
                "intent": intent,
                "context": context,
                "metadata": metadata,
                "final_response": f"⚠️ **JARVIS CONFIRMATION REQUIRED**\n\nThe requested operation `{intent}` carries risk. Please confirm if you wish to proceed.",
                "action": f"{intent}.confirm",
                "plan": [],
                "risk_level": "high",
                "requires_approval": True,
                "agent_logs": [f"[controller] Operation {intent} held for confirmation: {gate_decision.get('reason')}"],
            }

        # ── 5. Direct Tool Execution (High Confidence Action) ──
        direct_dispatch_intents = {
            "youtube_search",
            "google_search",
            "open_browser",
            "open_github",
            "open_vscode",
            "open_notepad",
            "open_calculator",
            "open_application",
            "remember_fact",
            "recall_memory",
            "create_task",
        }

        if route == "ACTION" and gate_decision.get("execute_tool") and intent in direct_dispatch_intents:
            log.info("Directly dispatching tool from ML Controller", intent=intent)
            tool_res = await dispatch_tool(intent, entities, raw_text=state.raw_input, context=context)
            return {
                "intent": intent,
                "context": context,
                "metadata": metadata,
                "final_response": tool_res.get("tool_output", tool_res.get("message", "Executed")),
                "action": tool_res.get("action", intent),
                "plan": [],
                "risk_level": "safe",
                "requires_approval": False,
                "agent_logs": [
                    f"[controller] ML routed to {intent} (conf={confidence:.3f}) | Direct Tool Dispatch: {tool_res.get('status')}"
                ],
            }

        # ── 6. Conversational / Knowledge / Coding / Planning ──
        if route in {"CONVERSATION", "KNOWLEDGE_PROJECT", "KNOWLEDGE_WORLD", "CODING", "PLANNING"}:
            log.info("Routing query to IntelligenceAgent", route=route, raw_input=state.raw_input)
            intel_res = await intelligence_agent.answer(
                prompt=state.raw_input,
                route=route,
                user_id=state.user_id,
                conversation_id=state.conversation_id,
            )
            return {
                "intent": intent,
                "context": context,
                "metadata": metadata,
                "final_response": intel_res["answer"],
                "action": "intelligence_answer",
                "plan": [],
                "risk_level": "safe",
                "requires_approval": False,
                "agent_logs": [
                    f"[controller] Routed to IntelligenceAgent (route={route}, source={intel_res['source']})"
                ],
            }

        # ── 7. Workflow Routing for Complex Actions ────────────
        requires_planning = intent in {
            "workflow_create",
            "workflow_run",
            "code_generation",
            "deployment",
            "project_management",
        }

        return {
            "intent": intent,
            "context": context,
            "metadata": metadata,
            "plan": [] if requires_planning else state.plan,
            "agent_logs": [
                f"[controller] ML routed to intent={intent} (conf={confidence:.3f}, route={route})"
            ],
        }
