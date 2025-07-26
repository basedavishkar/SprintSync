from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.task import (
    TaskCreate, TaskRead,
    TimeLogCreate, TimeLogRead,
    EstimateCreate, EstimateRead
)
from app.models.database_models import Task, TimeLog, Estimate
from app.dependencies.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskRead)
def create_task(
    task: TaskCreate, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        user_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/", response_model=List[TaskRead])
def list_tasks(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(
        Task.id == task_id, 
        Task.user_id == current_user.id
    ).first()
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
    db_task = db.query(Task).filter(
        Task.id == task_id, 
        Task.user_id == current_user.id
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.title = task.title
    db_task.description = task.description
    db_task.status = task.status
    
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/{task_id}")
def delete_task(
    task_id: int, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(
        Task.id == task_id, 
        Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"ok": True}


@router.post("/{task_id}/status", response_model=TaskRead)
def change_status(
    task_id: int, 
    status: str, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(
        Task.id == task_id, 
        Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = status
    db.commit()
    db.refresh(task)
    return task


# TimeLog endpoints
@router.post("/{task_id}/timelogs", response_model=TimeLogRead)
def create_timelog(
    task_id: int, 
    timelog: TimeLogCreate, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if task exists and belongs to user
    task = db.query(Task).filter(
        Task.id == task_id, 
        Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    duration = None
    if timelog.end_time:
        duration = (timelog.end_time - timelog.start_time).total_seconds() / 60.0
    
    db_timelog = TimeLog(
        task_id=task_id,
        start_time=timelog.start_time,
        end_time=timelog.end_time,
        duration=duration
    )
    db.add(db_timelog)
    db.commit()
    db.refresh(db_timelog)
    return db_timelog


@router.get("/{task_id}/timelogs", response_model=List[TimeLogRead])
def list_timelogs(
    task_id: int, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if task belongs to user
    task = db.query(Task).filter(
        Task.id == task_id, 
        Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    timelogs = db.query(TimeLog).filter(TimeLog.task_id == task_id).all()
    return timelogs


# Estimate endpoints
@router.post("/{task_id}/estimates", response_model=EstimateRead)
def create_estimate(
    task_id: int, 
    estimate: EstimateCreate, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if task exists and belongs to user
    task = db.query(Task).filter(
        Task.id == task_id, 
        Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_estimate = Estimate(
        task_id=task_id,
        estimated_min=estimate.estimated_min,
        estimated_max=estimate.estimated_max
    )
    db.add(db_estimate)
    db.commit()
    db.refresh(db_estimate)
    return db_estimate


@router.get("/{task_id}/estimates", response_model=List[EstimateRead])
def list_estimates(
    task_id: int, 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if task belongs to user
    task = db.query(Task).filter(
        Task.id == task_id, 
        Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    estimates = db.query(Estimate).filter(Estimate.task_id == task_id).all()
    return estimates 