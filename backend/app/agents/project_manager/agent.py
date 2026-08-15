"""
Project Manager Agent — Project planning, milestone tracking, sprint generation.
"""
from __future__ import annotations
from typing import Any, Dict
import structlog
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)

PM_SYSTEM_PROMPT = """You are an expert AI Project Manager.

Given a project description, create a comprehensive plan:
{
  "project_name": "",
  "description": "",
  "tech_stack": [],
  "total_duration_weeks": 0,
  "phases": [{"name": "", "duration_weeks": 0, "deliverables": [], "tasks": []}],
  "milestones": [{"name": "", "due_week": 0, "deliverable": "", "success_criteria": ""}],
  "sprint_1": {"goal": "", "tasks": ["task1", "task2"], "duration_days": 14, "team_size": 1},
  "tech_debt_risks": [],
  "success_criteria": [],
  "risks": [{"risk": "", "probability": "low|medium|high", "mitigation": ""}]
}
"""


class ProjectManagerAgent(BaseAgent):
    name = "project_manager_agent"
    description = "Project creation, milestone tracking, sprint planning, progress reports"
    supported_intents = ["project_management"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        action = state.metadata.get("pm_action", "create_plan")

        if action == "create_plan":
            return await self._create_plan(state)
        elif action == "progress_report":
            return await self._progress_report(state)
        elif action == "sprint_plan":
            return await self._sprint_plan(state)
        return {"final_response": "Project management action completed"}

    async def _create_plan(self, state: AgentState) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", PM_SYSTEM_PROMPT),
            ("human", "Project: {project}\nContext: {context}\n\nCreate the full project plan."),
        ])
        chain = prompt | self.llm | JsonOutputParser()
        try:
            plan = await chain.ainvoke({"project": state.raw_input, "context": str(state.context)})
        except Exception as e:
            log.error("PM planning error", error=str(e))
            return {"error": str(e), "final_response": f"Planning error: {e}"}

        phases = plan.get("phases", [])
        milestones = plan.get("milestones", [])
        sprint1 = plan.get("sprint_1", {})

        summary = (
            f"## 🗂️ {plan.get('project_name', 'Project Plan')}\n\n"
            f"{plan.get('description', '')}\n\n"
            f"**Tech Stack:** {', '.join(plan.get('tech_stack', ['TBD']))}\n"
            f"**Duration:** {plan.get('total_duration_weeks', '?')} weeks | {len(phases)} phases\n\n"
            f"### 🏁 Milestones\n"
            + "\n".join(f"- Week {m.get('due_week')}: **{m.get('name')}** — {m.get('deliverable')}" for m in milestones)
            + f"\n\n### 🚀 Sprint 1 Goal\n_{sprint1.get('goal', 'TBD')}_\n\n"
            f"**Sprint 1 Tasks:**\n"
            + "\n".join(f"- {t}" for t in sprint1.get("tasks", []))
        )

        return {
            "final_response": summary,
            "response_type": "report",
            "artifacts": [{"type": "project_plan", "data": plan}],
            "agent_logs": [f"[pm_agent] plan created: {plan.get('project_name', 'unknown')}"],
        }

    async def _progress_report(self, state: AgentState) -> Dict[str, Any]:
        project_data = state.metadata.get("project_data", {})
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a concise project progress report with status, completed items, next steps, blockers."),
            ("human", "Project data: {data}"),
        ])
        chain = prompt | self.llm | StrOutputParser()
        report = await chain.ainvoke({"data": str(project_data)})
        return {"final_response": report, "response_type": "report"}

    async def _sprint_plan(self, state: AgentState) -> Dict[str, Any]:
        return {"final_response": "Sprint planning requires active project data.", "response_type": "text"}
