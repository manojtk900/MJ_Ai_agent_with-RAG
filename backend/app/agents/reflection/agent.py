"""
Reflection Agent — Evaluates output quality, detects errors, and decides retry strategy.
Implements the Reflection step in the ReAct + Reflection pattern.
"""
from __future__ import annotations

from typing import Any, Dict

import structlog
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)

REFLECTION_PROMPT = """You are the Reflection Agent for MJ AI Assistant.

Your job is to critically evaluate the agent's output and determine next steps.

Evaluate:
1. Did the agent complete the task correctly?
2. Is the output high quality and complete?
3. Were there any errors or issues?
4. Should we retry? If so, what should change?

Return JSON:
{
  "quality_score": 0.0-1.0,
  "is_acceptable": true|false,
  "should_retry": true|false,
  "retry_strategy": "change_model|change_approach|add_context|give_up",
  "issues_found": ["issue1", "issue2"],
  "improvement_suggestions": ["suggestion1"],
  "reflection_summary": "<1-2 sentence summary>"
}

Be strict but fair. Score below 0.6 = retry if attempts remain.
"""


class ReflectionAgent(BaseAgent):
    name = "reflection_agent"
    description = "Output quality evaluation and retry decision making"

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", REFLECTION_PROMPT),
            ("human", (
                "Original goal: {goal}\n"
                "Agent that ran: {agent}\n"
                "Output produced: {output}\n"
                "Error (if any): {error}\n"
                "Retry count: {retry_count}/{max_retries}\n\n"
                "Evaluate this output."
            )),
        ])
        chain = prompt | self.llm | JsonOutputParser()

        try:
            evaluation = await chain.ainvoke({
                "goal": state.goal or state.raw_input,
                "agent": state.target_agent or "unknown",
                "output": state.final_response or "No output",
                "error": state.error or "None",
                "retry_count": state.retry_count,
                "max_retries": state.max_retries,
            })
        except Exception as e:
            log.warning("Reflection fallback", error=str(e))
            evaluation = {
                "quality_score": 0.5,
                "is_acceptable": True,
                "should_retry": False,
                "reflection_summary": "Reflection evaluation unavailable",
            }

        quality = evaluation.get("quality_score", 0.5)
        should_retry = evaluation.get("should_retry", False)
        is_acceptable = evaluation.get("is_acceptable", True)

        log.info(
            "Reflection complete",
            quality=quality,
            retry=should_retry,
            acceptable=is_acceptable,
        )

        updates = {
            "needs_reflection": False,  # Clear flag
            "agent_logs": [
                f"[reflection] quality={quality:.2f} retry={should_retry} "
                f"issues={evaluation.get('issues_found', [])}"
            ],
            "metadata": {
                **state.metadata,
                "reflection": evaluation,
            },
        }

        # If not acceptable and retries remain — clear error for retry
        if should_retry and not is_acceptable and state.retry_count < state.max_retries:
            updates["error"] = f"Retry: {evaluation.get('retry_strategy', 'change_approach')}"

        return updates
