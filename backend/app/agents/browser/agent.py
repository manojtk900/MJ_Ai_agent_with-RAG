"""
Browser Agent — Web automation using Playwright.
Navigate websites, fill forms, extract data, download files.
"""
from __future__ import annotations

from typing import Any, Dict

import structlog

from app.agents.base import BaseAgent
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)


class BrowserAgent(BaseAgent):
    name = "browser_agent"
    description = "Web automation with Playwright — navigate, click, fill forms, extract data"
    supported_intents = ["browser_automation"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        action = state.metadata.get("browser_action", "navigate")
        url = state.metadata.get("url", "")

        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                if action == "navigate":
                    await page.goto(url, wait_until="networkidle")
                    content = await page.content()
                    title = await page.title()
                    await browser.close()
                    return {
                        "final_response": f"✅ Navigated to: {title}\n\nPage content extracted ({len(content)} chars)",
                        "artifacts": [{"type": "page_content", "url": url, "title": title, "content": content[:5000]}],
                        "agent_logs": [f"[browser_agent] navigated to {url}"],
                    }

                elif action == "screenshot":
                    await page.goto(url)
                    screenshot = await page.screenshot(type="png")
                    await browser.close()
                    return {
                        "final_response": f"✅ Screenshot captured from {url}",
                        "artifacts": [{"type": "screenshot", "data": screenshot}],
                    }

                elif action == "fill_form":
                    await page.goto(url)
                    fields = state.metadata.get("fields", {})
                    for selector, value in fields.items():
                        await page.fill(selector, value)
                    await page.click(state.metadata.get("submit_selector", "button[type=submit]"))
                    await browser.close()
                    return {
                        "final_response": "✅ Form submitted successfully",
                        "agent_logs": [f"[browser_agent] form filled at {url}"],
                    }

                elif action == "extract":
                    await page.goto(url)
                    selector = state.metadata.get("selector", "body")
                    text = await page.inner_text(selector)
                    await browser.close()
                    return {
                        "final_response": f"✅ Data extracted:\n\n{text[:3000]}",
                        "artifacts": [{"type": "extracted_text", "content": text}],
                    }

                await browser.close()
                return {"final_response": "Browser action completed", "response_type": "action"}

        except ImportError:
            return {"error": "Playwright not installed", "final_response": "Browser agent unavailable."}
        except Exception as e:
            log.error("Browser error", error=str(e))
            return {"error": str(e), "final_response": f"Browser error: {e}"}
