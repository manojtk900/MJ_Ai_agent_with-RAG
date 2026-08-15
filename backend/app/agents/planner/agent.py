"""
Planner Agent — Decomposes goals into executable steps.
"""
from __future__ import annotations

from typing import Any, Dict, List

import structlog
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)

PLANNER_PROMPT = """You are the Planner Agent for MJ AI Assistant.

Given a user's goal, decompose it into a clear, sequential plan.

Return a JSON object:
{
  "goal": "<reformulated clear goal>",
  "plan": [
    {
      "step": 1,
      "action": "<action name>",
      "agent": "<agent_to_execute>",
      "description": "<what this step does>",
      "inputs": {},
      "expected_output": "<what we expect>",
      "can_parallelize": false
    }
  ],
  "estimated_steps": <number>,
  "complexity": "low|medium|high",
  "dependencies": []
}

Available agents: controller, chat, search, research, memory, system, browser, 
email, reminder, file, voice, execution, scheduler, project_manager, reflection

Keep plans concise. Max 10 steps. Parallelize where possible.
"""


class PlannerAgent(BaseAgent):
    name = "planner_agent"
    description = "Goal decomposition and workflow creation"

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", PLANNER_PROMPT),
            ("human", "Goal: {goal}\nContext: {context}\nUser preferences: {prefs}"),
        ])
        chain = prompt | self.llm | JsonOutputParser()

        goal = state.goal or state.raw_input
        try:
            result = await chain.ainvoke({
                "goal": goal,
                "context": str(state.context),
                "prefs": str(state.user_preferences),
            })
        except Exception as e:
            log.warning("Planner fallback", error=str(e))
            result = {
                "goal": goal,
                "plan": [{"step": 1, "action": "execute", "agent": "chat_agent",
                           "description": "Handle request directly", "inputs": {}}],
                "estimated_steps": 1,
            }

        plan = result.get("plan", [])
        log.info("Plan created", steps=len(plan), goal=result.get("goal"))

        return {
            "goal": result.get("goal", goal),
            "plan": plan,
            "agent_logs": [f"[planner] {len(plan)}-step plan created for: {goal[:80]}"],
        }
