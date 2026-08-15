"""
MCP Browser Server — Playwright-powered browser automation tools.
"""
from typing import Any


async def navigate_url(url: str) -> str:
    """Navigate to URL and return page text content."""
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            content = await page.inner_text("body")
            title = await page.title()
            await browser.close()
            return f"Title: {title}\n\nContent:\n{content[:8000]}"
    except ImportError:
        return "Playwright not installed. Run: pip install playwright && playwright install"
    except Exception as e:
        return f"Browser error: {e}"


async def extract_text(url: str, selector: str = "body") -> str:
    """Extract text from a CSS selector on a page."""
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            text = await page.inner_text(selector)
            await browser.close()
            return text[:5000]
    except Exception as e:
        return f"Extraction error: {e}"


async def take_screenshot(url: str) -> bytes:
    """Take a screenshot of a URL."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        screenshot = await page.screenshot(type="png")
        await browser.close()
        return screenshot


async def click_element(url: str, selector: str) -> str:
    """Click an element on a page."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.click(selector)
        await browser.close()
        return f"Clicked: {selector}"
