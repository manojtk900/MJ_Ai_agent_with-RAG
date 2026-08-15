"""
Agents API Route — List, status, and direct invocation of agents.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/agents")


class AgentInfo(BaseModel):
    name: str
    description: str
    status: str
    supported_intents: List[str]


AGENT_REGISTRY = [
    AgentInfo(name="controller_agent", description="Intent detection and routing", status="active", supported_intents=["*"]),
    AgentInfo(name="desktop_agent", description="OS app launcher & browser control", status="active", supported_intents=["desktop_operation", "app_open", "system_operation"]),
    AgentInfo(name="planner_agent", description="Goal decomposition and planning", status="idle", supported_intents=["complex_tasks"]),
    AgentInfo(name="chat_agent", description="General conversation and coding", status="idle", supported_intents=["conversation", "coding", "reasoning"]),
    AgentInfo(name="search_agent", description="Web search with source verification", status="idle", supported_intents=["web_search", "quick_search"]),
    AgentInfo(name="research_agent", description="Deep multi-source research", status="idle", supported_intents=["web_research", "deep_research"]),
    AgentInfo(name="memory_agent", description="Long-term memory (pgvector)", status="active", supported_intents=["memory_store", "memory_retrieve"]),
    AgentInfo(name="system_agent", description="Local machine operations", status="idle", supported_intents=["system_operation"]),
    AgentInfo(name="browser_agent", description="Playwright web automation", status="idle", supported_intents=["browser_automation"]),
    AgentInfo(name="email_agent", description="Read and send emails", status="idle", supported_intents=["email_read", "email_send"]),
    AgentInfo(name="reminder_agent", description="Reminders and calendar events", status="idle", supported_intents=["reminder"]),
    AgentInfo(name="file_agent", description="PDF reading, DOCX/PPTX generation", status="idle", supported_intents=["file_read", "file_write", "pdf_analysis"]),
    AgentInfo(name="voice_agent", description="Speech-to-text and text-to-speech", status="idle", supported_intents=["voice_processing"]),
    AgentInfo(name="execution_agent", description="GitHub automation and code generation", status="idle", supported_intents=["code_generation", "github_automation", "deployment"]),
    AgentInfo(name="scheduler_agent", description="Cron jobs and background workflows", status="idle", supported_intents=["schedule_task"]),
    AgentInfo(name="project_manager_agent", description="Project planning and tracking", status="idle", supported_intents=["project_management"]),
    AgentInfo(name="reflection_agent", description="Output quality evaluation", status="idle", supported_intents=["reflection"]),
]



@router.get("/", response_model=List[AgentInfo])
async def list_agents():
    """Return all registered agents and their current status."""
    return AGENT_REGISTRY


@router.get("/{agent_name}", response_model=AgentInfo)
async def get_agent(agent_name: str):
    """Get details for a specific agent."""
    from fastapi import HTTPException
    for agent in AGENT_REGISTRY:
        if agent.name == agent_name:
            return agent
    raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")


@router.post("/{agent_name}/run")
async def run_agent_directly(agent_name: str, payload: Dict[str, Any]):
    """
    Run a specific agent directly (bypasses Controller routing).
    For debugging and testing purposes.
    """
    return {
        "agent": agent_name,
        "status": "queued",
        "message": f"Direct agent invocation for {agent_name} - connect database and LLM keys to activate",
        "payload_received": payload,
    }
