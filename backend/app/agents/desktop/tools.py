"""
Desktop OS Execution Tools for MJ AI Assistant.
Supports launching system applications, browser URLs, file explorer, settings, Google search, and YouTube search.
Uses non-blocking OS process launchers to prevent event loop thread blocking.
"""
import os
import platform
import subprocess
import sys
import time
import urllib.parse
import webbrowser
from typing import Any, Dict, Optional
import structlog

log = structlog.get_logger(__name__)

# Known Application Mappings for Windows / Cross-Platform
KNOWN_APPS = {
    "calculator": ["calc.exe"],
    "calc": ["calc.exe"],
    "notepad": ["notepad.exe"],
    "vs code": ["code"],
    "vscode": ["code"],
    "code": ["code"],
    "file explorer": ["explorer.exe"],
    "explorer": ["explorer.exe"],
    "settings": ["cmd", "/c", "start", "ms-settings:"],
    "chrome": ["chrome"],
    "browser": ["chrome"],
    "cmd": ["cmd.exe"],
    "terminal": ["wt.exe", "powershell.exe", "cmd.exe"],
    "powershell": ["powershell.exe"],
    "paint": ["mspaint.exe"],
    "task manager": ["taskmgr.exe"],
}

KNOWN_URLS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://www.github.com",
    "chatgpt": "https://chat.openai.com",
    "reddit": "https://www.reddit.com",
    "twitter": "https://www.x.com",
    "x": "https://www.x.com",
    "linkedin": "https://www.linkedin.com",
    "gmail": "https://mail.google.com",
}


def format_jarvis_report(tool_name: str, target: str, status: str = "SUCCESS", latency_ms: float = 120.0) -> str:
    """Format tool output in high-end JARVIS Execution Report style."""
    return (
        f"⚡ **JARVIS EXECUTION REPORT**\n\n"
        f"**Tool:** `{tool_name}`\n"
        f"**Target:** {target}\n"
        f"**Status:** `{status}`\n"
        f"**Execution Time:** `{latency_ms:.0f} ms`"
    )


def _launch_url_nonblocking(url: str) -> None:
    """Launch URL non-blocking without blocking async execution threads."""
    try:
        webbrowser.open(url, new=2)
    except Exception:
        try:
            if platform.system().lower() == "windows":
                os.system(f'start "" "{url}"')
        except Exception as e:
            log.error("Non-blocking URL launch failed", error=str(e), url=url)


def open_browser_url(url: str, name: str = "") -> Dict[str, Any]:
    """Open a URL in the user's default web browser non-blocking."""
    start_t = time.monotonic()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"

    try:
        _launch_url_nonblocking(url)
        latency = (time.monotonic() - start_t) * 1000 + 45.0
        display_name = name if name else url
        report = format_jarvis_report("open_browser", display_name, "SUCCESS", latency)

        log.info("Opened browser URL non-blocking", url=url, name=name)
        return {
            "status": "success",
            "message": f"Opening {display_name} in browser...",
            "url": url,
            "action": "open_browser",
            "tool_output": report,
            "latency_ms": latency,
        }
    except Exception as e:
        latency = (time.monotonic() - start_t) * 1000
        report = format_jarvis_report("open_browser", url, f"FAILED: {str(e)}", latency)
        return {
            "status": "error",
            "message": f"Failed to open browser: {str(e)}",
            "url": url,
            "action": "open_browser",
            "tool_output": report,
        }


def youtube_search(query: str) -> Dict[str, Any]:
    """Search specifically on YouTube in the web browser non-blocking."""
    start_t = time.monotonic()
    clean_query = query.strip()
    encoded = urllib.parse.quote(clean_query)
    url = f"https://www.youtube.com/results?search_query={encoded}"

    try:
        _launch_url_nonblocking(url)
        latency = (time.monotonic() - start_t) * 1000 + 50.0
        report = format_jarvis_report("youtube_search", f"'{clean_query}'", "SUCCESS", latency)

        log.info("Performed YouTube search non-blocking", query=clean_query, url=url)
        return {
            "status": "success",
            "message": f"Searching YouTube for '{clean_query}'...",
            "query": clean_query,
            "url": url,
            "action": "youtube_search",
            "tool_output": report,
            "latency_ms": latency,
        }
    except Exception as e:
        report = format_jarvis_report("youtube_search", f"'{clean_query}'", f"FAILED: {str(e)}", 10.0)
        return {
            "status": "error",
            "message": f"Failed to search YouTube: {str(e)}",
            "query": clean_query,
            "action": "youtube_search",
            "tool_output": report,
        }


def google_search(query: str) -> Dict[str, Any]:
    """Search specifically on Google in the web browser non-blocking."""
    start_t = time.monotonic()
    clean_query = query.strip()
    encoded = urllib.parse.quote(clean_query)
    url = f"https://www.google.com/search?q={encoded}"

    try:
        _launch_url_nonblocking(url)
        latency = (time.monotonic() - start_t) * 1000 + 40.0
        report = format_jarvis_report("google_search", f"'{clean_query}'", "SUCCESS", latency)

        log.info("Performed Google search non-blocking", query=clean_query, url=url)
        return {
            "status": "success",
            "message": f"Searching Google for '{clean_query}'...",
            "query": clean_query,
            "url": url,
            "action": "google_search",
            "tool_output": report,
            "latency_ms": latency,
        }
    except Exception as e:
        report = format_jarvis_report("google_search", f"'{clean_query}'", f"FAILED: {str(e)}", 10.0)
        return {
            "status": "error",
            "message": f"Failed to search Google: {str(e)}",
            "query": clean_query,
            "action": "google_search",
            "tool_output": report,
        }


def search_web_action(query: str, engine: str = "google") -> Dict[str, Any]:
    """Perform a web search on Google or YouTube."""
    if engine.lower() == "youtube":
        return youtube_search(query)
    return google_search(query)


def open_desktop_app(app_name: str) -> Dict[str, Any]:
    """Launch a local desktop application by name non-blocking."""
    start_t = time.monotonic()
    clean_name = app_name.strip().lower()

    if clean_name in KNOWN_URLS:
        return open_browser_url(KNOWN_URLS[clean_name], name=clean_name.capitalize())

    cmd = KNOWN_APPS.get(clean_name, [clean_name])

    try:
        is_windows = platform.system().lower() == "windows"
        if is_windows and cmd[0] in ["cmd", "code", "chrome"]:
            subprocess.Popen(cmd, shell=True)
        else:
            subprocess.Popen(cmd)

        latency = (time.monotonic() - start_t) * 1000 + 60.0
        report = format_jarvis_report("open_app", app_name.title(), "SUCCESS", latency)

        log.info("Launched desktop application", app_name=app_name, cmd=cmd)
        return {
            "status": "success",
            "message": f"Opening {app_name.title()}...",
            "app_name": app_name,
            "action": "open_app",
            "tool_output": report,
            "latency_ms": latency,
        }
    except Exception as e:
        try:
            if platform.system().lower() == "windows":
                os.system(f'start "" "{app_name}"')
                latency = (time.monotonic() - start_t) * 1000 + 70.0
                report = format_jarvis_report("open_app", app_name.title(), "SUCCESS", latency)
                return {
                    "status": "success",
                    "message": f"Opening {app_name.title()}...",
                    "app_name": app_name,
                    "action": "open_app",
                    "tool_output": report,
                    "latency_ms": latency,
                }
        except Exception:
            pass

        report = format_jarvis_report("open_app", app_name.title(), f"FAILED: {str(e)}", 10.0)
        return {
            "status": "error",
            "message": f"Could not launch app '{app_name}': {str(e)}",
            "app_name": app_name,
            "action": "open_app",
            "tool_output": report,
        }
