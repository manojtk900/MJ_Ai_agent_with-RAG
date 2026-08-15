"""
Search Agent — Fast web search with source verification.
Uses Tavily as primary, DuckDuckGo as fallback.
"""
from __future__ import annotations

from typing import Any, Dict, List

import structlog
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.config import settings
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)


class SearchAgent(BaseAgent):
    name = "search_agent"
    description = "Fast web search with source verification"
    supported_intents = ["web_search", "quick_search"]
    requires_tools = True

    async def _load_tools(self) -> List[Any]:
        if settings.tavily_api_key:
            return [TavilySearchResults(max_results=5, api_key=settings.tavily_api_key)]
        # Fallback to DuckDuckGo
        from langchain_community.tools import DuckDuckGoSearchRun
        return [DuckDuckGoSearchRun()]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        query = state.raw_input
        log.info("Searching web", query=query)

        # Run search
        search_tool = self.tools[0] if self.tools else None
        if not search_tool:
            return {"error": "No search tool available", "final_response": "Search unavailable."}

        try:
            raw_results = await search_tool.ainvoke(query)
        except Exception as e:
            log.error("Search failed", error=str(e))
            return {"error": str(e), "final_response": f"Search failed: {e}"}

        # Synthesize results with LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a search result synthesizer. Provide a clear, accurate answer based on the search results. Always cite sources."),
            ("human", "Query: {query}\n\nSearch Results:\n{results}\n\nSynthesize a comprehensive answer with source citations."),
        ])
        chain = prompt | self.llm | StrOutputParser()
        response = await chain.ainvoke({"query": query, "results": str(raw_results)})

        return {
            "final_response": response,
            "response_type": "text",
            "artifacts": [{"type": "search_results", "data": raw_results}],
            "agent_logs": [f"[search_agent] searched: {query[:60]}"],
        }
