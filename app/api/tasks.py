from fastapi import APIRouter, HTTPException, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from app.models.task import TaskCreate, TaskRead

from app.core.security import get_current_user, get_current_user_web
from app.core.database import get_db
from app.services.task_service import TaskService

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskRead)
def create_task(
    task: TaskCreate, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task."""
    task_service = TaskService(db)
    return task_service.create_task(task, current_user)


@router.get("/", response_model=List[TaskRead])
def list_tasks(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for the current user."""
    task_service = TaskService(db)
    return task_service.get_user_tasks(current_user.id)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID."""
    task_service = TaskService(db)
    task = task_service.get_task_by_id(task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int, 
    task: TaskCreate, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task."""
    task_service = TaskService(db)
    updated_task = task_service.update_task(task_id, current_user.id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@router.delete("/{task_id}")
def delete_task(
    task_id: int, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task."""
    task_service = TaskService(db)
    success = task_service.delete_task(task_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return ""  # Return empty string for HTMX to remove the element


@router.post("/{task_id}/status", response_class=HTMLResponse)
def change_status(
    request: Request,
    task_id: int, 
    status: str = Form(...), 
    current_user=Depends(get_current_user_web),
    db: Session = Depends(get_db)
):
    """Change task status and return HTML for HTMX."""
    task_service = TaskService(db)
    task = task_service.update_task_status(task_id, current_user.id, status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return templates.TemplateResponse("task_card.html", {
        "request": request,
        "task": task
    }) 