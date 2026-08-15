"""
Projects API Route — Project planning, milestones, and sprint tracking.
"""
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/projects")

_projects: Dict[str, Dict] = {}


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    user_id: Optional[str] = None
    tech_stack: List[str] = []
    target_date: Optional[str] = None
    priority: str = "medium"
    tags: List[str] = []


class MilestoneRequest(BaseModel):
    name: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    deliverable: Optional[str] = None


@router.post("/", status_code=201)
async def create_project(request: ProjectCreateRequest):
    """Create a new project."""
    project_id = str(uuid.uuid4())
    project = {
        "id": project_id,
        "name": request.name,
        "description": request.description,
        "user_id": request.user_id,
        "status": "active",
        "tech_stack": request.tech_stack,
        "target_date": request.target_date,
        "priority": request.priority,
        "tags": request.tags,
        "milestones": [],
        "completion_percentage": 0.0,
        "created_at": str(uuid.uuid1()),
    }
    _projects[project_id] = project
    return project


@router.get("/")
async def list_projects(
    user_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
):
    """List all projects."""
    projects = list(_projects.values())
    if user_id:
        projects = [p for p in projects if p.get("user_id") == user_id]
    if status:
        projects = [p for p in projects if p.get("status") == status]
    return {"projects": projects, "total": len(projects)}


@router.get("/{project_id}")
async def get_project(project_id: str):
    """Get a specific project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return _projects[project_id]


@router.post("/{project_id}/milestones", status_code=201)
async def add_milestone(project_id: str, milestone: MilestoneRequest):
    """Add a milestone to a project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    ms = {
        "id": str(uuid.uuid4()),
        "name": milestone.name,
        "description": milestone.description,
        "due_date": milestone.due_date,
        "deliverable": milestone.deliverable,
        "status": "pending",
    }
    _projects[project_id]["milestones"].append(ms)
    return ms


@router.post("/{project_id}/plan")
async def generate_project_plan(project_id: str):
    """
    Use Project Manager Agent to generate a detailed plan.
    Requires LLM configuration.
    """
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    project = _projects[project_id]
    return {
        "project_id": project_id,
        "project_name": project["name"],
        "message": "Connect OpenAI/Gemini key to generate AI-powered project plan",
        "action": "Use POST /api/v1/chat/ with message: 'Create project plan for " + project["name"] + "'",
    }


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    _projects.pop(project_id)
    return {"status": "deleted", "project_id": project_id}
