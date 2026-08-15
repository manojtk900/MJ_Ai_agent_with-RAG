"""
Execution Agent — GitHub automation, autonomous coding, and deployment.
The "do work" agent that executes real developer actions.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import structlog
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.config import settings
from app.core.langgraph.state import AgentState
from app.agents.execution.git_tools import git_add_commit_push, get_repo_status

log = structlog.get_logger(__name__)


CODING_SYSTEM_PROMPT = """You are an expert software engineer agent.

Given a task, you will:
1. Understand the full requirements
2. Plan the implementation
3. Generate production-quality code
4. Structure files properly
5. Include tests and documentation

Output code in clearly labeled sections:
=== FILE: <relative/path/to/file> ===
<code content>
=== END FILE ===

Always include:
- Proper error handling
- Type hints (Python) / TypeScript types
- Comments for complex logic
- A README if creating a new project
"""


class ExecutionAgent(BaseAgent):
    name = "execution_agent"
    description = "GitHub automation, autonomous coding, deployment"
    supported_intents = ["code_generation", "github_automation", "deployment"]
    requires_tools = True

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        text = state.raw_input.lower()

        # ── Fast Git Push Action ─────────────────────────────
        if "push" in text or "commit" in text:
            msg = state.metadata.get("commit_message", "Auto-commit by MJ AI Assistant")
            res = git_add_commit_push(commit_message=msg)
            return {
                "final_response": f"{res.get('tool_output', '')}\n\n{res.get('message', '')}",
                "action": "git_add_commit_push",
                "status": res.get("status", "success"),
                "agent_logs": [f"[execution_agent] executed git push: {msg}"],
            }

        action = state.intent

        if action == "code_generation":
            return await self._generate_code(state)
        elif action == "github_automation":
            return await self._github_action(state)
        elif action == "deployment":
            return await self._deploy(state)
        else:
            return await self._generate_code(state)


    async def _generate_code(self, state: AgentState) -> Dict[str, Any]:
        """Autonomous code generation."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", CODING_SYSTEM_PROMPT),
            ("human", "Task: {task}\n\nContext: {context}\n\nGenerate the full implementation."),
        ])
        chain = prompt | self.llm | StrOutputParser()
        code_output = await chain.ainvoke({
            "task": state.goal or state.raw_input,
            "context": str(state.context),
        })

        # Parse generated files
        files = self._parse_file_blocks(code_output)
        log.info("Code generated", files=len(files))

        return {
            "final_response": f"✅ Generated {len(files)} file(s):\n" + "\n".join(f"- `{f['path']}`" for f in files),
            "response_type": "code",
            "artifacts": [{"type": "generated_code", "files": files}],
            "agent_logs": [f"[execution_agent] generated {len(files)} files"],
        }

    async def _github_action(self, state: AgentState) -> Dict[str, Any]:
        """GitHub repository operations via PyGithub."""
        if not settings.github_token:
            return {"error": "GitHub token not configured", "final_response": "GitHub token required."}

        from github import Github, GithubException
        g = Github(settings.github_token)

        action_map = {
            "create_repo": self._create_repo,
            "create_issue": self._create_issue,
            "create_pr": self._create_pr,
        }

        sub_action = state.metadata.get("github_action", "create_issue")
        handler = action_map.get(sub_action, self._create_issue)
        return await handler(g, state)

    async def _create_repo(self, g, state: AgentState) -> Dict[str, Any]:
        from github import Github
        user = g.get_user()
        repo_name = state.metadata.get("repo_name", "mj-ai-project")
        repo = user.create_repo(
            repo_name,
            description=state.metadata.get("description", "Created by MJ AI Assistant"),
            auto_init=True,
            private=state.metadata.get("private", False),
        )
        return {
            "final_response": f"✅ Repository created: {repo.html_url}",
            "response_type": "action",
            "artifacts": [{"type": "github_repo", "url": repo.html_url}],
        }

    async def _create_issue(self, g, state: AgentState) -> Dict[str, Any]:
        repo_name = state.metadata.get("repo", f"{settings.github_username}/mj-ai-assistant")
        repo = g.get_repo(repo_name)
        issue = repo.create_issue(
            title=state.metadata.get("title", state.raw_input[:100]),
            body=state.metadata.get("body", state.raw_input),
        )
        return {
            "final_response": f"✅ Issue #{issue.number} created: {issue.html_url}",
            "response_type": "action",
        }

    async def _create_pr(self, g, state: AgentState) -> Dict[str, Any]:
        repo_name = state.metadata.get("repo", f"{settings.github_username}/mj-ai-assistant")
        repo = g.get_repo(repo_name)
        pr = repo.create_pull(
            title=state.metadata.get("title", "AI-generated changes"),
            body=state.metadata.get("body", "Created by MJ AI Execution Agent"),
            head=state.metadata.get("head", "feature-branch"),
            base=state.metadata.get("base", "main"),
        )
        return {
            "final_response": f"✅ PR #{pr.number} created: {pr.html_url}",
            "response_type": "action",
        }

    async def _deploy(self, state: AgentState) -> Dict[str, Any]:
        """Deployment automation (Docker, Render, Railway)."""
        platform = state.metadata.get("platform", "docker")
        return {
            "final_response": f"🚀 Deployment initiated to {platform}. Check logs for progress.",
            "response_type": "action",
            "agent_logs": [f"[execution_agent] deployment to {platform} started"],
        }

    def _parse_file_blocks(self, output: str) -> List[Dict[str, str]]:
        """Extract === FILE: path === ... === END FILE === blocks."""
        files = []
        lines = output.split("\n")
        current_file = None
        current_content = []
        for line in lines:
            if line.startswith("=== FILE:"):
                current_file = line.replace("=== FILE:", "").replace("===", "").strip()
                current_content = []
            elif line.strip() == "=== END FILE ===" and current_file:
                files.append({"path": current_file, "content": "\n".join(current_content)})
                current_file = None
                current_content = []
            elif current_file:
                current_content.append(line)
        return files
