"""
Intelligence Agent for MJ AI Assistant.
Orchestrates RAG retrieval, structured multi-tier LLM reasoning, code generation, and dialogue.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
import structlog

from app.agents.base import BaseAgent
from app.agents.intelligence.llm import intelligence_llm
from app.agents.intelligence.memory import IntelligenceMemoryBridge
from app.agents.intelligence.prompts import (
    CODING_ASSIST_PROMPT,
    JARVIS_CORE_SYSTEM_PROMPT,
    PLANNING_CAREER_PROMPT,
    RAG_SYNTHESIS_PROMPT,
)
from app.agents.intelligence.rag import rag_engine
from app.agents.intelligence.router_gate import RouterGate
from app.agents.intelligence.schemas import IntelligenceChatResponse, SourceCitation
from app.agents.intelligence.traces import record_trace
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)


class IntelligenceAgent(BaseAgent):
    name = "intelligence_agent"
    description = "Reasoning, RAG QA, Coding Assistance, Career Planning, and Conversational Intelligence"
    supported_intents = [
        "chat", "conversation", "coding", "reasoning", "knowledge_project",
        "knowledge_world", "planning", "clarification"
    ]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """LangGraph node execution handler."""
        raw_text = state.raw_input.strip()
        metadata = dict(state.metadata or {})
        intent = state.intent or "chat"
        confidence = float(metadata.get("confidence", 0.85))
        entities = metadata.get("entities", {})

        # 1. Evaluate through RouterGate
        gate_decision = RouterGate.evaluate(
            raw_input=raw_text,
            predicted_intent=intent,
            confidence=confidence,
            entities=entities,
        )

        route = gate_decision["route"]
        log.info("IntelligenceAgent processing request", route=route, raw_input=raw_text)

        # 2. Process query and generate answer
        response_data = await self.answer(
            prompt=raw_text,
            route=route,
            user_id=state.user_id,
            conversation_id=state.conversation_id,
        )

        return {
            "final_response": response_data["answer"],
            "response_type": "text",
            "source": response_data["source"],
            "citations": response_data.get("citations", []),
            "route": route,
            "agent_logs": [
                f"[intelligence_agent] route={route} source={response_data['source']} latency={response_data['latency_ms']:.1f}ms"
            ],
        }

    async def answer(
        self,
        prompt: str,
        route: Optional[str] = None,
        user_id: Optional[str] = "default_user",
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        High-level answer generation method.
        """
        start_t = time.monotonic()

        # If route not provided, evaluate automatically
        if not route:
            gate_decision = RouterGate.evaluate(
                raw_input=prompt,
                predicted_intent="chat",
                confidence=0.9,
                entities={},
            )
            route = gate_decision["route"]

        # Fetch isolated memory context
        user_ctx = await IntelligenceMemoryBridge.get_user_context(user_id=user_id, conversation_id=conversation_id)

        # Handle Project Knowledge Queries via RAG
        context_str = None
        citations: List[Dict[str, Any]] = []

        if route in {"KNOWLEDGE_PROJECT", "RAG"}:
            search_result = rag_engine.search(prompt, top_k=3)
            if search_result.chunks:
                context_str = "\n\n---\n\n".join([f"[{c.source_file}]\n{c.text}" for c in search_result.chunks])
                citations = [c.model_dump() for c in search_result.citations]

        # Select appropriate prompt
        system_prompt = JARVIS_CORE_SYSTEM_PROMPT
        if route == "KNOWLEDGE_PROJECT" and context_str:
            system_prompt = RAG_SYNTHESIS_PROMPT.format(context=context_str, question=prompt)
        elif route == "CODING":
            system_prompt = CODING_ASSIST_PROMPT.format(question=prompt)
        elif route == "PLANNING":
            system_prompt = PLANNING_CAREER_PROMPT.format(question=prompt)

        # Call multi-tier LLM service
        res = await intelligence_llm.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            context=context_str,
            route=route,
        )

        total_latency = (time.monotonic() - start_t) * 1000

        # Record anonymized trace
        trace_id = record_trace(
            raw_input=prompt,
            predicted_intent="chat",
            confidence=0.95,
            route=route,
            selected_tool=None,
            tool_arguments=None,
            tool_result=res.get("answer")[:200] if res.get("answer") else None,
            success=True,
            latency_ms=total_latency,
            model_provider=res.get("provider"),
            llm_model=res.get("model"),
        )

        return {
            "answer": res["answer"],
            "source": res["source"],
            "provider": res.get("provider"),
            "model": res.get("model"),
            "citations": citations or res.get("citations", []),
            "route": route,
            "latency_ms": total_latency,
            "trace_id": trace_id,
        }

    async def chat(self, message: str, conversation_id: Optional[str] = None) -> IntelligenceChatResponse:
        """API helper for conversational chat."""
        res = await self.answer(prompt=message, conversation_id=conversation_id)
        return IntelligenceChatResponse(
            answer=res["answer"],
            conversation_id=conversation_id or "default",
            route=res["route"],
            intent="chat",
            source=res["source"],
            citations=[SourceCitation(**c) for c in res.get("citations", [])],
            latency_ms=res["latency_ms"],
            trace_id=res.get("trace_id"),
        )

    def retrieve(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Direct vector retrieval helper."""
        res = rag_engine.search(query, top_k=top_k)
        return res.model_dump()

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Raw text generation helper."""
        res = await intelligence_llm.generate_response(
            prompt=prompt,
            system_prompt=system_prompt or JARVIS_CORE_SYSTEM_PROMPT,
        )
        return res["answer"]

    async def explain(self, concept: str) -> str:
        """Explanation helper."""
        prompt = f"Explain the concept of: {concept}"
        res = await self.answer(prompt=prompt, route="CONVERSATION")
        return res["answer"]

    async def code_assist(self, task: str) -> str:
        """Coding assistant helper."""
        res = await self.answer(prompt=task, route="CODING")
        return res["answer"]


# Global instance
intelligence_agent = IntelligenceAgent()
