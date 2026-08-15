"""
Email / Gmail Agent — Read, filter, summarize, and draft emails.
"""
from __future__ import annotations

from typing import Any, Dict
import structlog
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.config import settings
from app.core.langgraph.state import AgentState
from app.agents.email.gmail_service import gmail_service

log = structlog.get_logger(__name__)


class EmailAgent(BaseAgent):
    name = "email_agent"
    description = "Read, filter (internship/placement), summarize, and send emails via Gmail"
    supported_intents = ["email_read", "email_send"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        text = state.raw_input.lower()
        if state.intent == "email_send" or "reply" in text or "send email" in text:
            return await self._draft_email(state)
        return await self._read_and_filter_emails(state)

    async def _read_and_filter_emails(self, state: AgentState) -> Dict[str, Any]:
        text = state.raw_input.lower()

        if "internship" in text:
            emails = await gmail_service.filter_emails("internship")
            title = "Internship Emails"
        elif "placement" in text:
            emails = await gmail_service.filter_emails("placement")
            title = "Placement Emails"
        else:
            emails = await gmail_service.fetch_unread_emails()
            title = "Inbox Summary"

        summary = await gmail_service.summarize_emails(emails)

        return {
            "final_response": summary,
            "response_type": "text",
            "emails": emails,
            "agent_logs": [f"[email_agent] processed {len(emails)} {title} emails"],
        }

    async def _draft_email(self, state: AgentState) -> Dict[str, Any]:
        """Draft an email and flag for approval."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional email assistant. Draft a polite and clear email based on the user's request."),
            ("human", "Request: {request}\nTo: {to}\nSubject: {subject}"),
        ])

        to_addr = state.metadata.get("to", "recipient@example.com")
        subject = state.metadata.get("subject", "Follow up from MJ Assistant")

        if self.llm is not None:
            chain = prompt | self.llm | StrOutputParser()
            try:
                draft = await chain.ainvoke({
                    "request": state.raw_input,
                    "to": to_addr,
                    "subject": subject,
                })
            except Exception:
                draft = f"Dear Recipient,\n\nIn response to your message: {state.raw_input}.\n\nBest regards,\nManoj"
        else:
            draft = f"Dear Recipient,\n\nIn response to your message: {state.raw_input}.\n\nBest regards,\nManoj"

        return {
            "action": "email.send",
            "subject": subject,
            "final_response": f"📧 **Email Draft Ready**\n\n**To:** `{to_addr}`\n**Subject:** `{subject}`\n\n```text\n{draft}\n```\n\n*Awaiting your approval to send.*",
            "response_type": "text",
            "artifacts": [{"type": "email_draft", "to": to_addr, "subject": subject, "body": draft}],
            "requires_approval": True,
        }
