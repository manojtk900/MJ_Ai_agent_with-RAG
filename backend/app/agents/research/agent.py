"""
Research Agent — Deep multi-source research with verification and report generation.
Searches multiple sources, cross-verifies, and produces structured reports.
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List

import structlog
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.config import settings
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)

RESEARCH_SYNTHESIS_PROMPT = """You are an expert research analyst.

Your task is to synthesize information from multiple sources into a comprehensive research report.

Topic: {topic}

Sources collected:
{sources}

Produce a well-structured research report with:
1. Executive Summary
2. Key Findings (with evidence)
3. Source Analysis (credibility assessment)
4. Conflicting Information (if any)
5. Conclusion and Recommendations
6. References

Be thorough, factual, and cite sources throughout.
"""


class ResearchAgent(BaseAgent):
    name = "research_agent"
    description = "Deep multi-source research, verification, and report generation"
    supported_intents = ["web_research", "deep_research"]
    requires_tools = True
    max_sources: int = 10

    async def _load_tools(self) -> List[Any]:
        tools = []
        if settings.tavily_api_key:
            from langchain_community.tools.tavily_search import TavilySearchResults
            tools.append(TavilySearchResults(max_results=self.max_sources, api_key=settings.tavily_api_key))
        if settings.brave_search_api_key:
            from langchain_community.tools import BraveSearch
            tools.append(BraveSearch.from_api_key(api_key=settings.brave_search_api_key, search_kwargs={"count": 5}))
        return tools or [self._fallback_search()]

    def _fallback_search(self):
        from langchain_community.tools import DuckDuckGoSearchRun
        return DuckDuckGoSearchRun()

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        topic = state.goal or state.raw_input
        log.info("Starting deep research", topic=topic)

        # ── Phase 1: Multi-source search ──────────────────────
        search_queries = await self._generate_queries(topic)
        all_results = []

        async def search_one(tool, q):
            try:
                return await tool.ainvoke(q)
            except Exception as e:
                log.warning("Search error", query=q, error=str(e))
                return []

        # Run searches concurrently across multiple query angles
        tasks = [
            search_one(self.tools[i % len(self.tools)], q)
            for i, q in enumerate(search_queries[:6])
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if not isinstance(r, Exception):
                all_results.extend(r if isinstance(r, list) else [r])

        # ── Phase 2: Synthesize report ────────────────────────
        prompt = ChatPromptTemplate.from_messages([
            ("system", RESEARCH_SYNTHESIS_PROMPT),
            ("human", "Generate the research report now."),
        ])
        chain = prompt | self.llm | StrOutputParser()
        report = await chain.ainvoke({
            "topic": topic,
            "sources": str(all_results[:self.max_sources]),
        })

        return {
            "final_response": report,
            "response_type": "report",
            "artifacts": [
                {"type": "research_report", "data": report},
                {"type": "raw_sources", "data": all_results},
            ],
            "agent_logs": [f"[research_agent] researched '{topic[:60]}' from {len(all_results)} sources"],
        }

    async def _generate_queries(self, topic: str) -> List[str]:
        """Generate multiple search query angles for the topic."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate 5 diverse search queries to thoroughly research a topic. Return one query per line."),
            ("human", "Topic: {topic}"),
        ])
        chain = prompt | self.llm | StrOutputParser()
        result = await chain.ainvoke({"topic": topic})
        queries = [q.strip() for q in result.strip().split("\n") if q.strip()]
        return [topic] + queries[:4]  # Original + 4 variations
