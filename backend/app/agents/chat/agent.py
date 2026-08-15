"""
Chat Agent — General conversation, coding help, reasoning.
Supports streaming and multi-model responses.
"""
from __future__ import annotations

from typing import Any, Dict

import structlog
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)

CHAT_SYSTEM_PROMPT = """You are MJ, an advanced AI assistant — part of the MJ AI Operating System.

You are helpful, precise, and thoughtful. You excel at:
- General conversations and Q&A
- Code generation, debugging, and review (all languages)
- Logical reasoning and problem solving
- Explaining complex concepts clearly

Guidelines:
- Be concise but thorough
- Use code blocks for code with proper language tags
- Format responses with markdown when helpful
- Acknowledge uncertainty rather than hallucinating

Current date: {date}
User: {username}
Autonomy Level: {autonomy_level}
"""


class ChatAgent(BaseAgent):
    name = "chat_agent"
    description = "General conversation, coding, reasoning"
    supported_intents = ["conversation", "coding", "reasoning"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        from datetime import date
        system = CHAT_SYSTEM_PROMPT.format(
            date=date.today().isoformat(),
            username=state.user_preferences.get("username", "User"),
            autonomy_level=state.autonomy_level,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            MessagesPlaceholder("history"),
            ("human", "{input}"),
        ])

        chain = prompt | self.llm | StrOutputParser()

        response = await chain.ainvoke({
            "history": state.messages[:-1] if len(state.messages) > 1 else [],
            "input": state.raw_input,
        })

        log.info("Chat response generated", length=len(response))
        return {
            "final_response": response,
            "response_type": "text",
            "agent_logs": [f"[chat_agent] generated {len(response)} chars"],
        }
