"""
MCP Desktop Server — Real Windows desktop automation tools.

Tools that ACTUALLY open applications and browsers on the user's machine.
Uses webbrowser (for browser opens) and subprocess.Popen (for app launches).
All launches are non-blocking so the API returns immediately.
"""
from __future__ import annotations

import asyncio
import subprocess
import sys
import webbrowser
from urllib.parse import quote_plus

import structlog

log = structlog.get_logger(__name__)

# ── Windows Application Map ───────────────────────────────────────
# Maps friendly names to Windows executable / URI scheme
WINDOWS_APPS: dict[str, str] = {
    # Calculators & utilities
    "calculator":           "calc",
    "calc":                 "calc",
    "notepad":              "notepad",
    "notepad++":            "notepad++",
    "paint":                "mspaint",
    "wordpad":              "wordpad",
    "snipping tool":        "snippingtool",
    "snip":                 "snippingtool",
    # File management
    "explorer":             "explorer",
    "file explorer":        "explorer",
    "files":                "explorer",
    # System
    "settings":             "ms-settings:",
    "windows settings":     "ms-settings:",
    "task manager":         "taskmgr",
    "control panel":        "control",
    "cmd":                  "cmd",
    "command prompt":       "cmd",
    "powershell":           "powershell",
    "terminal":             "wt",
    # Text editors / IDEs
    "vscode":               "code",
    "vs code":              "code",
    "visual studio code":   "code",
    "code":                 "code",
    "cursor":               "cursor",
    "visual studio":        "devenv",
    # Productivity (Office)
    "word":                 "winword",
    "excel":                "excel",
    "powerpoint":           "powerpnt",
    "outlook":              "outlook",
    "onenote":              "onenote",
    # Communication
    "teams":                "ms-teams:",
    "skype":                "skype:",
    "discord":              "discord",
    "slack":                "slack",
    "zoom":                 "zoom",
    "whatsapp":             "whatsapp",
    "telegram":             "telegram",
    # Browsers
    "chrome":               "chrome",
    "google chrome":        "chrome",
    "firefox":              "firefox",
    "edge":                 "msedge",
    "microsoft edge":       "msedge",
    "brave":                "brave",
    "opera":                "opera",
    # Dev tools
    "github desktop":       "github",
    "docker":               "docker",
    "postman":              "postman",
    "figma":                "figma",
    # Media
    "vlc":                  "vlc",
    "spotify":              "spotify:",
    "photos":               "ms-photos:",
    "camera":               "microsoft.windows.camera:",
    # System settings shortcuts
    "bluetooth":            "ms-settings:bluetooth",
    "wifi":                 "ms-settings:network-wifi",
    "display settings":     "ms-settings:display",
    "sound settings":       "ms-settings:sound",
    "clipboard":            "ms-settings:clipboard",
}

# ── URL Map for popular websites ──────────────────────────────────
WEBSITE_MAP: dict[str, str] = {
    "youtube":          "https://www.youtube.com",
    "google":           "https://www.google.com",
    "gmail":            "https://mail.google.com",
    "github":           "https://github.com",
    "stackoverflow":    "https://stackoverflow.com",
    "twitter":          "https://twitter.com",
    "x":                "https://x.com",
    "reddit":           "https://www.reddit.com",
    "linkedin":         "https://www.linkedin.com",
    "instagram":        "https://www.instagram.com",
    "facebook":         "https://www.facebook.com",
    "whatsapp web":     "https://web.whatsapp.com",
    "netflix":          "https://www.netflix.com",
    "amazon":           "https://www.amazon.in",
    "flipkart":         "https://www.flipkart.com",
    "chatgpt":          "https://chat.openai.com",
    "claude":           "https://claude.ai",
    "gemini":           "https://gemini.google.com",
    "huggingface":      "https://huggingface.co",
    "wikipedia":        "https://www.wikipedia.org",
    "hackerrank":       "https://www.hackerrank.com",
    "leetcode":         "https://leetcode.com",
    "codechef":         "https://www.codechef.com",
    "codeforces":       "https://codeforces.com",
    "mj assistant":     "http://localhost:5173",
}


async def open_browser(url: str) -> dict:
    """
    Open a URL in the system default browser (visible window).
    Uses Python's webbrowser module — always opens the default browser.
    """
    print(f"\n[TOOL CALLED] open_browser | url={url}")
    log.info("[TOOL CALLED] open_browser", url=url)
    try:
        # Resolve site names to URLs
        if not url.startswith(("http://", "https://", "ms-", "mailto:", "file://")):
            site_key = url.lower().strip()
            if site_key in WEBSITE_MAP:
                url = WEBSITE_MAP[site_key]
            else:
                url = f"https://{url}"

        await asyncio.get_event_loop().run_in_executor(
            None, lambda: webbrowser.open(url, new=2)
        )
        print(f"[TOOL SUCCESS] open_browser | url={url}")
        log.info("[TOOL SUCCESS] open_browser", url=url)
        return {
            "success": True,
            "tool": "open_browser",
            "url": url,
            "message": f"✅ Opening **{url}** in your browser",
            "action_type": "browser_open",
        }
    except Exception as e:
        print(f"[TOOL FAILED] open_browser | error={e}")
        log.error("[TOOL FAILED] open_browser", url=url, error=str(e))
        return {
            "success": False,
            "tool": "open_browser",
            "url": url,
            "message": f"❌ Failed to open browser: {e}",
            "error": str(e),
        }


async def youtube_search(query: str) -> dict:
    """
    Search YouTube and open results in the default browser.
    """
    print(f"\n[TOOL CALLED] youtube_search | query={query}")
    log.info("[TOOL CALLED] youtube_search", query=query)
    try:
        encoded = quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: webbrowser.open(url, new=2)
        )
        print(f"[TOOL SUCCESS] youtube_search | query={query} url={url}")
        log.info("[TOOL SUCCESS] youtube_search", query=query, url=url)
        return {
            "success": True,
            "tool": "youtube_search",
            "query": query,
            "url": url,
            "message": f"✅ Searching YouTube for: **{query}**",
            "action_type": "youtube_search",
        }
    except Exception as e:
        print(f"[TOOL FAILED] youtube_search | error={e}")
        log.error("[TOOL FAILED] youtube_search", query=query, error=str(e))
        return {
            "success": False,
            "tool": "youtube_search",
            "query": query,
            "message": f"❌ YouTube search failed: {e}",
            "error": str(e),
        }


async def google_search(query: str) -> dict:
    """
    Search Google and open results in the default browser.
    """
    print(f"\n[TOOL CALLED] google_search | query={query}")
    log.info("[TOOL CALLED] google_search", query=query)
    try:
        encoded = quote_plus(query)
        url = f"https://www.google.com/search?q={encoded}"
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: webbrowser.open(url, new=2)
        )
        print(f"[TOOL SUCCESS] google_search | query={query} url={url}")
        log.info("[TOOL SUCCESS] google_search", query=query, url=url)
        return {
            "success": True,
            "tool": "google_search",
            "query": query,
            "url": url,
            "message": f"✅ Googling: **{query}**",
            "action_type": "google_search",
        }
    except Exception as e:
        print(f"[TOOL FAILED] google_search | error={e}")
        log.error("[TOOL FAILED] google_search", query=query, error=str(e))
        return {
            "success": False,
            "tool": "google_search",
            "query": query,
            "message": f"❌ Google search failed: {e}",
            "error": str(e),
        }


async def open_application(app_name: str) -> dict:
    """
    Launch a Windows application by friendly name.
    Uses subprocess.Popen for non-blocking launch.
    """
    print(f"\n[TOOL CALLED] open_application | app={app_name}")
    log.info("[TOOL CALLED] open_application", app_name=app_name)

    key = app_name.lower().strip()
    executable = WINDOWS_APPS.get(key)

    if not executable:
        # Try partial match
        for k, v in WINDOWS_APPS.items():
            if key in k or k in key:
                executable = v
                break

    if not executable:
        executable = key  # Try as raw command

    try:
        if executable.endswith(":"):
            # Windows URI scheme (ms-settings:, spotify:, etc.)
            subprocess.Popen(
                ["cmd", "/c", "start", "", executable],
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.Popen(
                executable,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        print(f"[TOOL SUCCESS] open_application | app={app_name} exe={executable}")
        log.info("[TOOL SUCCESS] open_application", app_name=app_name, executable=executable)
        return {
            "success": True,
            "tool": "open_application",
            "app_name": app_name,
            "executable": executable,
            "message": f"✅ Launching **{app_name.title()}**",
            "action_type": "app_launch",
        }
    except Exception as e:
        print(f"[TOOL FAILED] open_application | app={app_name} error={e}")
        log.error("[TOOL FAILED] open_application", app_name=app_name, error=str(e))
        return {
            "success": False,
            "tool": "open_application",
            "app_name": app_name,
            "message": f"❌ Could not launch {app_name}: {e}",
            "error": str(e),
        }


async def close_application(app_name: str) -> dict:
    """Kill a running Windows application by process name."""
    print(f"\n[TOOL CALLED] close_application | app={app_name}")
    log.info("[TOOL CALLED] close_application", app_name=app_name)
    key = app_name.lower().strip()
    executable = WINDOWS_APPS.get(key, key)
    proc_name = executable.split("\\")[-1]
    if not proc_name.endswith(".exe"):
        proc_name += ".exe"
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", proc_name],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            print(f"[TOOL SUCCESS] close_application | app={app_name}")
            log.info("[TOOL SUCCESS] close_application", app_name=app_name)
            return {"success": True, "tool": "close_application", "message": f"✅ Closed **{app_name.title()}**"}
        else:
            return {"success": False, "tool": "close_application", "message": f"⚠️ Could not close {app_name}"}
    except Exception as e:
        log.error("[TOOL FAILED] close_application", error=str(e))
        return {"success": False, "tool": "close_application", "message": f"❌ Failed: {e}"}
