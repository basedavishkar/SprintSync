from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from app.models.task import TaskCreate, TaskRead
from app.core.security import get_current_user_web
from app.core.database import get_db
from app.services.task_service import TaskService
from pydantic import BaseModel, Field

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/tasks", tags=["tasks"])


class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Not authenticated")


@router.post(
    "/",
    response_model=TaskRead,
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def create_task(
    task: TaskCreate,
    current_user=Depends(get_current_user_web),
    db: Session = Depends(get_db),
):
    """Create a new task."""
    if not task.title or not task.status:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title and status are required.",
        )
    task_service = TaskService(db)
    return task_service.create_task(task, current_user)


@router.get(
    "/",
    response_model=List[TaskRead],
    responses={401: {"model": ErrorResponse}},
)
def list_tasks(
    current_user=Depends(get_current_user_web), db: Session = Depends(get_db)
):
    """Get all tasks for the current user."""
    task_service = TaskService(db)
    return task_service.get_user_tasks(current_user.id)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
)
def get_task(
    task_id: int,
    current_user=Depends(get_current_user_web),
    db: Session = Depends(get_db),
):
    """Get a specific task by ID."""
    task_service = TaskService(db)
    task = task_service.get_task_by_id(task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    responses={
        404: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def update_task(
    task_id: int,
    task: TaskCreate,
    current_user=Depends(get_current_user_web),
    db: Session = Depends(get_db),
):
    """Update a task."""
    if not task.title or not task.status:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title and status are required.",
        )
    task_service = TaskService(db)
    updated_task = task_service.update_task(task_id, current_user.id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@router.delete(
    "/{task_id}",
    responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
)
def delete_task(
    task_id: int,
    current_user=Depends(get_current_user_web),
    db: Session = Depends(get_db),
):
    """Delete a task."""
    task_service = TaskService(db)
    success = task_service.delete_task(task_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}


class StatusUpdate(BaseModel):
    status: str = Field(..., example="in_progress")


class TaskAssignment(BaseModel):
    user_id: int = Field(
        ..., example=1, description="ID of the user to assign the task to"
    )


@router.post(
    "/{task_id}/status",
    responses={
        404: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def change_status(
    task_id: int,
    status_update: StatusUpdate,
    current_user=Depends(get_current_user_web),
    db: Session = Depends(get_db),
):
    """Change task status."""
    if status_update.status not in ["todo", "in_progress", "done"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid status value.",
        )
    task_service = TaskService(db)
    task = task_service.update_task_status(
        task_id, current_user.id, status_update.status
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"success": True}


@router.post(
    "/{task_id}/assign",
    responses={
        404: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def assign_task(
    task_id: int,
    assignment: TaskAssignment,
    current_user=Depends(get_current_user_web),
    db: Session = Depends(get_db),
):
    """Assign a task to a different user (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign tasks to users.",
        )

    task_service = TaskService(db)
    task = task_service.assign_task_to_user(task_id, assignment.user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task or user not found")

    return {
        "success": True,
        "message": f"Task assigned to user ID {assignment.user_id}",
    }
