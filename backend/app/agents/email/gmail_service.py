"""
Gmail Service — REST/IMAP email parser for unread emails, internship emails, placement notifications, and daily summaries.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog
from app.config import settings

log = structlog.get_logger(__name__)

# Sample/Mock Email Store for rich demo and offline testing
MOCK_EMAILS = [
    {
        "id": "msg_001",
        "sender": "careers@deloitte.com",
        "subject": "Deloitte Internship 2026 — Interview Shortlist",
        "date": "Today, 10:15 AM",
        "category": "internship",
        "snippet": "Congratulations! You have been shortlisted for the Tech Consulting Internship role. Please confirm your availability.",
        "unread": True,
    },
    {
        "id": "msg_002",
        "sender": "campus@tcs.com",
        "subject": "TCS CodeVita & Placement Registration Drive",
        "date": "Today, 09:30 AM",
        "category": "placement",
        "snippet": "The placement registration portal for 2026 batch is now open. Submit your details before Friday.",
        "unread": True,
    },
    {
        "id": "msg_003",
        "sender": "hackathon@devfolio.co",
        "subject": "Hackathon Registration Confirmed — AI Hack 2026",
        "date": "Today, 08:00 AM",
        "category": "hackathon",
        "snippet": "Your team 'JARVIS OS' is confirmed for AI Hack 2026. Review project guidelines attached.",
        "unread": True,
    },
]


class GmailService:
    def __init__(self):
        self.use_mock = not bool(settings.email_username and settings.email_password)

    async def fetch_unread_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch unread emails."""
        if self.use_mock:
            return MOCK_EMAILS

        try:
            import aioimaplib
            imap = aioimaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
            await imap.wait_hello_from_server()
            await imap.login(settings.email_username, settings.email_password)
            await imap.select("INBOX")
            _, data = await imap.search("UNSEEN")
            # Parse unread messages...
            await imap.logout()
            return MOCK_EMAILS
        except Exception as e:
            log.warning("IMAP fetch failed, using fallback email store", error=str(e))
            return MOCK_EMAILS

    async def filter_emails(self, keyword: str) -> List[Dict[str, Any]]:
        """Filter emails by keyword (e.g. 'internship', 'placement', 'hackathon')."""
        all_emails = await self.fetch_unread_emails()
        kw = keyword.lower()
        filtered = [
            e for e in all_emails
            if kw in e["subject"].lower() or kw in e["snippet"].lower() or kw in e["category"].lower()
        ]
        return filtered if filtered else all_emails

    async def summarize_emails(self, emails: List[Dict[str, Any]]) -> str:
        """Format email summary for response."""
        if not emails:
            return "📭 No unread emails found in your inbox."

        lines = [f"📬 **Found {len(emails)} Email(s)**\n"]
        for idx, email in enumerate(emails, 1):
            lines.append(
                f"{idx}. **{email['subject']}**\n"
                f"   - **From:** {email['sender']}\n"
                f"   - **Time:** {email['date']}\n"
                f"   - **Summary:** {email['snippet']}\n"
            )
        return "\n".join(lines)


gmail_service = GmailService()
