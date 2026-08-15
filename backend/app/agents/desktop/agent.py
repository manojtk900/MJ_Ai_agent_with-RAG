"""
Desktop Agent — Action Chaining, Query Extraction & Search Tool Execution.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List
import structlog

from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState
from app.agents.desktop.tools import (
    google_search,
    open_browser_url,
    open_desktop_app,
    youtube_search,
)

log = structlog.get_logger(__name__)


class DesktopAgent(BaseAgent):
    name = "desktop_agent"
    description = "Executes desktop actions: opens apps, browser URLs, Google search, YouTube search, and action plans"
    system_prompt = "You are the Desktop Agent for MJ AI Assistant."
    supported_intents = ["system_operation", "desktop_operation", "app_open", "browser_automation"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        text = state.raw_input.strip()
        lower_text = text.lower()

        log.info("DesktopAgent executing directive", raw_input=text)

        # Check if entire prompt has YouTube context for chained commands
        has_youtube_context = "youtube" in lower_text

        # ── Check for Action Chaining ("and", "then", ";") ──────────
        sub_commands = self._split_compound_commands(text)

        if len(sub_commands) > 1:
            log.info("Action Chaining detected", count=len(sub_commands), commands=sub_commands)
            results = []
            reports = []

            for cmd in sub_commands:
                res = await self._execute_single_action(cmd, has_youtube_context=has_youtube_context)
                results.append(res)
                reports.append(res.get("tool_output", res.get("message", "")))

            combined_report = "\n\n---\n\n".join(reports)
            return {
                "final_response": combined_report,
                "action": "action_chain",
                "status": "success",
                "sub_actions": results,
                "agent_logs": [f"[desktop_agent] executed {len(sub_commands)} chained actions"],
            }

        # Single Action Execution
        res = await self._execute_single_action(text, has_youtube_context=has_youtube_context)
        return {
            "final_response": res.get("tool_output", res.get("message", "")),
            "action": res.get("action", "desktop_execution"),
            "status": res.get("status", "success"),
            "agent_logs": [f"[desktop_agent] executed {res.get('action')}"],
        }

    def _split_compound_commands(self, text: str) -> List[str]:
        """Split user input by ' and ', ' then ', ';', ',' if multiple actions present."""
        lower = text.lower()
        if " and " in lower or " then " in lower or ";" in text:
            parts = re.split(r"\s+(?:and|then)\s+|;", text, flags=re.IGNORECASE)
            cleaned = [p.strip() for p in parts if p.strip()]
            if len(cleaned) > 1:
                return cleaned
        return [text]

    async def _execute_single_action(self, command: str, has_youtube_context: bool = False) -> Dict[str, Any]:
        """Execute a single atomic action (App launch, URL open, YouTube search, Google search)."""
        clean_cmd = command.strip()
        lower = clean_cmd.lower()

        # ── 0. Direct "open youtube search <query>" or "open youtube <query>" ────────
        open_yt_search = re.search(r"^open\s+youtube\s+(?:and\s+|then\s+|for\s+)?(?:search\s+for\s+|search\s+)?(.+)", lower)
        if open_yt_search:
            query = open_yt_search.group(1).strip()
            if query and query not in ["app", "website", "site", "com", "open"]:
                return youtube_search(query)

        # Direct "open google search <query>"
        open_google_search = re.search(r"^open\s+google\s+(?:and\s+|then\s+|for\s+)?(?:search\s+for\s+|search\s+)?(.+)", lower)
        if open_google_search:
            query = open_google_search.group(1).strip()
            if query and query not in ["app", "website", "site", "com", "open"]:
                return google_search(query)

        # ── 1. YouTube Search Patterns ───────────────────────────────
        # Pattern: "search <query> on youtube" / "find <query> on youtube" / "play <query> on youtube"
        yt_on_match = re.search(r"(?:search|find|play|look up)\s+(.+?)\s+on\s+youtube", lower)
        if yt_on_match:
            query = yt_on_match.group(1).strip()
            return youtube_search(query)


        # Pattern: "search youtube for <query>" / "search youtube <query>"
        yt_for_match = re.search(r"(?:search|find)\s+youtube\s+(?:for\s+)?(.+)", lower)
        if yt_for_match:
            query = yt_for_match.group(1).strip()
            return youtube_search(query)

        # Pattern: "youtube search <query>"
        yt_prefix_match = re.search(r"^youtube\s+search\s+(.+)", lower)
        if yt_prefix_match:
            query = yt_prefix_match.group(1).strip()
            return youtube_search(query)

        # ── 2. Google Search Patterns ────────────────────────────────
        # Pattern: "google <query>"
        google_prefix_match = re.search(r"^google\s+(.+)", lower)
        if google_prefix_match:
            query = google_prefix_match.group(1).strip()
            return google_search(query)

        # Pattern: "search <query> on google"
        google_on_match = re.search(r"(?:search|find|look up)\s+(.+?)\s+on\s+google", lower)
        if google_on_match:
            query = google_on_match.group(1).strip()
            return google_search(query)

        # ── 3. Generic Search Patterns ("search <query>" / "find <query>") ─────
        generic_search_match = re.search(r"^(?:search|find|look up)\s+(?:for\s+)?(.+)", lower)
        if generic_search_match:
            query = generic_search_match.group(1).strip()
            # If context mentions YouTube (or command is in a YouTube action chain), route to YouTube search
            if has_youtube_context or "youtube" in lower:
                return youtube_search(query)
            return google_search(query)

        # ── 4. Web URLs and App Launcher ─────────────────────────────
        if lower == "youtube" or lower == "open youtube":
            return open_browser_url("https://www.youtube.com", name="YouTube")

        if lower == "github" or lower == "open github":
            return open_browser_url("https://www.github.com", name="GitHub")

        if lower == "google" or lower == "open google":
            return open_browser_url("https://www.google.com", name="Google")

        # Explicit URL (e.g., "open example.com")
        url_match = re.search(r"open\s+(https?://[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)", lower)
        if url_match:
            raw_url = url_match.group(1)
            return open_browser_url(raw_url)

        # Local Applications
        if "calculator" in lower or lower == "calc" or "open calc" in lower:
            return open_desktop_app("calculator")

        if "notepad" in lower:
            return open_desktop_app("notepad")

        if "vs code" in lower or "vscode" in lower or lower == "open code":
            return open_desktop_app("vs code")

        if "file explorer" in lower or "explorer" in lower or "open folder" in lower:
            return open_desktop_app("file explorer")

        if "setting" in lower:
            return open_desktop_app("settings")

        if "chrome" in lower or "browser" in lower:
            return open_desktop_app("chrome")

        # Generic "open <app>"
        open_match = re.search(r"(?:open|launch|run|start)\s+(.+)", clean_cmd, re.IGNORECASE)
        if open_match:
            target = open_match.group(1).strip()
            return open_desktop_app(target)

        # Default fallback to open desktop app
        return open_desktop_app(clean_cmd)
