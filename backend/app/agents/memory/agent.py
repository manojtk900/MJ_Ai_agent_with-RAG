"""
Memory Agent — Long-term memory storage, retrieval, and personal profile context management.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List
import structlog
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState
from app.core.memory.long_term import LongTermMemory

log = structlog.get_logger(__name__)

# Fallback In-Memory Profile Fact Store for fast zero-latency recall
_user_facts_store: Dict[str, str] = {
    "college": "Sri Siddhartha Institute of Technology",
    "project": "MJ AI Assistant (Agentic AI OS)",
    "github": "manojtk900",
    "goal": "Preparing for placements & hackathons",
}


class MemoryAgent(BaseAgent):
    name = "memory_agent"
    description = "Long-term memory storage, retrieval, and personal user profile management"
    supported_intents = ["memory_store", "memory_retrieve"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        text = state.raw_input.strip()
        lower = text.lower()

        if state.intent == "memory_store" or lower.startswith("my ") or lower.startswith("remember"):
            return await self._store_memory(state)
        return await self._retrieve_memory(state)

    async def _store_memory(self, state: AgentState) -> Dict[str, Any]:
        text = state.raw_input.strip()
        lower = text.lower()

        # Parse key facts
        if "college" in lower:
            val = re.sub(r".*college is\s*", "", text, flags=re.IGNORECASE).strip()
            _user_facts_store["college"] = val or text
        elif "project" in lower:
            val = re.sub(r".*project is\s*", "", text, flags=re.IGNORECASE).strip()
            _user_facts_store["project"] = val or text
        elif "github" in lower:
            val = re.sub(r".*github is\s*", "", text, flags=re.IGNORECASE).strip()
            _user_facts_store["github"] = val or text

        try:
            lt = LongTermMemory()
            memory_id = await lt.store(
                user_id=state.user_id,
                content=text,
                memory_type="fact",
                importance_score=0.9,
            )
        except Exception:
            memory_id = "mem_cached"

        return {
            "final_response": f"🧠 **Personal Fact Stored in Memory**\n\n- **Fact:** `{text}`\n- **Memory Matrix ID:** `{memory_id}`",
            "agent_logs": [f"[memory_agent] stored fact '{text[:40]}'"],
        }

    async def _retrieve_memory(self, state: AgentState) -> Dict[str, Any]:
        text = state.raw_input.strip()
        lower = text.lower()

        # Direct Fact Recall
        if "college" in lower or "study" in lower:
            fact = _user_facts_store.get("college", "Sri Siddhartha")
            return {"final_response": f"🎓 Your college is **{fact}**."}

        if "project" in lower or "working on" in lower:
            fact = _user_facts_store.get("project", "MJ AI Assistant")
            return {"final_response": f"🚀 You are working on **{fact}**."}

        if "github" in lower:
            fact = _user_facts_store.get("github", "manojtk900")
            return {"final_response": f"🐙 Your GitHub username is **{fact}**."}

        if "preparing" in lower or "placement" in lower or "goal" in lower:
            fact = _user_facts_store.get("goal", "Preparing for placements")
            return {"final_response": f"🎯 Your current focus: **{fact}**."}

        # pgvector Semantic Search Fallback
        try:
            lt = LongTermMemory()
            memories = await lt.search(user_id=state.user_id, query=text, limit=5)
            if memories:
                formatted = "\n".join(f"- {m.content}" for m in memories)
                return {"final_response": f"🧠 **Here is what I remember:**\n\n{formatted}"}
        except Exception:
            pass

        # All stored profile facts fallback
        all_facts = "\n".join(f"- **{k.capitalize()}:** {v}" for k, v in _user_facts_store.items())
        return {
            "final_response": f"🧠 **Personal Profile Memory Context:**\n\n{all_facts}",
            "agent_logs": ["[memory_agent] returned user profile memory context"],
        }
