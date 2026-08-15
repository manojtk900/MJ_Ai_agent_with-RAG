"""
Tasks API Route — Create, list, update, and manage agent tasks.
"""
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/tasks")

# In-memory store for dev (replace with DB in production)
_tasks: Dict[str, Dict] = {}


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    goal: Optional[str] = None
    user_id: Optional[str] = None
    priority: str = "medium"  # low | medium | high | critical
    autonomy_level: int = Field(default=1, ge=0, le=3)
    scheduled_at: Optional[str] = None
    cron_expression: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class TaskUpdateRequest(BaseModel):
    status: Optional[str] = None
    completion_percentage: Optional[float] = None
    result: Optional[Any] = None


@router.post("/", status_code=201)
async def create_task(request: TaskCreateRequest):
    """Create a new agent task."""
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "title": request.title,
        "description": request.description,
        "goal": request.goal,
        "user_id": request.user_id,
        "status": "pending",
        "priority": request.priority,
        "autonomy_level": request.autonomy_level,
        "scheduled_at": request.scheduled_at,
        "cron_expression": request.cron_expression,
        "is_recurring": bool(request.cron_expression),
        "tags": request.tags,
        "metadata": request.metadata,
        "completion_percentage": 0.0,
        "retry_count": 0,
        "created_at": str(uuid.uuid1()),
    }
    _tasks[task_id] = task
    return task


@router.get("/")
async def list_tasks(
    user_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    """List all tasks, optionally filtered by user or status."""
    tasks = list(_tasks.values())
    if user_id:
        tasks = [t for t in tasks if t.get("user_id") == user_id]
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    return {"tasks": tasks[-limit:], "total": len(tasks)}


@router.get("/{task_id}")
async def get_task(task_id: str):
    """Get a specific task by ID."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return _tasks[task_id]


@router.patch("/{task_id}")
async def update_task(task_id: str, request: TaskUpdateRequest):
    """Update task status or completion percentage."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    task = _tasks[task_id]
    if request.status:
        task["status"] = request.status
    if request.completion_percentage is not None:
        task["completion_percentage"] = request.completion_percentage
    if request.result is not None:
        task["result"] = request.result
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Cancel and remove a task."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    _tasks.pop(task_id)
    return {"status": "deleted", "task_id": task_id}
