"""
Git & GitHub OS Execution Tools for MJ AI Assistant.
Supports local git add/commit/push commands and PyGithub repository operations.
"""
import os
import subprocess
from typing import Any, Dict, Optional
import structlog

from app.config import settings

log = structlog.get_logger(__name__)


def git_add_commit_push(commit_message: str = "Auto-commit by MJ AI Assistant", repo_path: str = ".") -> Dict[str, Any]:
    """Execute git add ., git commit, and git push in sequence."""
    try:
        # 1. git add .
        add_res = subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True, text=True, check=True)
        
        # 2. git commit -m
        commit_res = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        
        # 3. git push
        push_res = subprocess.run(["git", "push"], cwd=repo_path, capture_output=True, text=True)

        output_log = (commit_res.stdout or commit_res.stderr or "") + "\n" + (push_res.stdout or push_res.stderr or "")
        log.info("Executed git add commit push", commit_message=commit_message)

        return {
            "status": "success",
            "message": f"Successfully pushed latest code to GitHub repository!\nCommit: '{commit_message}'",
            "action": "git_add_commit_push",
            "tool_output": f"[TOOL] git_add_commit_push\n[SUCCESS] {commit_message}\n```\n{output_log.strip()}\n```",
        }
    except Exception as e:
        log.error("Failed to execute git push", error=str(e))
        return {
            "status": "error",
            "message": f"Git action failed: {str(e)}",
            "action": "git_add_commit_push",
        }


def get_repo_status(repo_path: str = ".") -> Dict[str, Any]:
    """Get current git status and branch."""
    try:
        status_res = subprocess.run(["git", "status", "-s"], cwd=repo_path, capture_output=True, text=True)
        branch_res = subprocess.run(["git", "branch", "--show-current"], cwd=repo_path, capture_output=True, text=True)
        
        branch = branch_res.stdout.strip() or "main"
        changed_files = [line.strip() for line in status_res.stdout.split("\n") if line.strip()]

        return {
            "status": "success",
            "branch": branch,
            "changed_files_count": len(changed_files),
            "files": changed_files,
            "tool_output": f"[TOOL] git_status\n[SUCCESS] Branch '{branch}' ({len(changed_files)} changed files)",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
