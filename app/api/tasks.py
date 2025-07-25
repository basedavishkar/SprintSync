from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from app.models.task import (
    TaskCreate, TaskRead, TaskInDB,
    TimeLogCreate, TimeLogRead, TimeLogInDB,
    EstimateCreate, EstimateRead, EstimateInDB
)
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

# In-memory DBs
fake_tasks_db = {}
fake_timelogs_db = {}
fake_estimates_db = {}

task_id_counter = 1
timelog_id_counter = 1
estimate_id_counter = 1

# Dummy data
fake_tasks_db[1] = TaskInDB(
    id=1,
    title="Initial Task",
    description="This is a dummy task.",
    status="todo",
    created_at=datetime.utcnow(),
    user_id="demo_user"
)
task_id_counter = 2

@router.post("/", response_model=TaskRead)
def create_task(task: TaskCreate, current_user=Depends(get_current_user)):
    global task_id_counter
    task_obj = TaskInDB(
        id=task_id_counter,
        title=task.title,
        description=task.description,
        status=task.status,
        created_at=datetime.utcnow(),
        user_id=current_user.username
    )
    fake_tasks_db[task_id_counter] = task_obj
    task_id_counter += 1
    return task_obj

@router.get("/", response_model=List[TaskRead])
def list_tasks(current_user=Depends(get_current_user)):
    return [t for t in fake_tasks_db.values() if t.user_id == current_user.username]

@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, current_user=Depends(get_current_user)):
    task = fake_tasks_db.get(task_id)
    if not task or task.user_id != current_user.username:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task: TaskCreate, current_user=Depends(get_current_user)):
    existing = fake_tasks_db.get(task_id)
    if not existing or existing.user_id != current_user.username:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = TaskInDB(
        id=task_id,
        title=task.title,
        description=task.description,
        status=task.status,
        created_at=existing.created_at,
        user_id=current_user.username
    )
    fake_tasks_db[task_id] = updated
    return updated

@router.delete("/{task_id}")
def delete_task(task_id: int, current_user=Depends(get_current_user)):
    task = fake_tasks_db.get(task_id)
    if not task or task.user_id != current_user.username:
        raise HTTPException(status_code=404, detail="Task not found")
    del fake_tasks_db[task_id]
    return {"ok": True}

@router.post("/{task_id}/status", response_model=TaskRead)
def change_status(task_id: int, status: str, current_user=Depends(get_current_user)):
    task = fake_tasks_db.get(task_id)
    if not task or task.user_id != current_user.username:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = status
    fake_tasks_db[task_id] = task
    return task

# TimeLog endpoints
@router.post("/{task_id}/timelogs", response_model=TimeLogRead)
def create_timelog(task_id: int, timelog: TimeLogCreate, current_user=Depends(get_current_user)):
    global timelog_id_counter
    if task_id not in fake_tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    duration = None
    if timelog.end_time:
        duration = (timelog.end_time - timelog.start_time).total_seconds() / 60.0
    timelog_obj = TimeLogInDB(
        id=timelog_id_counter,
        task_id=task_id,
        start_time=timelog.start_time,
        end_time=timelog.end_time,
        duration=duration
    )
    fake_timelogs_db[timelog_id_counter] = timelog_obj
    timelog_id_counter += 1
    return timelog_obj

@router.get("/{task_id}/timelogs", response_model=List[TimeLogRead])
def list_timelogs(task_id: int, current_user=Depends(get_current_user)):
    return [t for t in fake_timelogs_db.values() if t.task_id == task_id]

# Estimate endpoints
@router.post("/{task_id}/estimates", response_model=EstimateRead)
def create_estimate(task_id: int, estimate: EstimateCreate, current_user=Depends(get_current_user)):
    global estimate_id_counter
    if task_id not in fake_tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    estimate_obj = EstimateInDB(
        id=estimate_id_counter,
        task_id=task_id,
        estimated_min=estimate.estimated_min,
        estimated_max=estimate.estimated_max,
        created_at=datetime.utcnow()
    )
    fake_estimates_db[estimate_id_counter] = estimate_obj
    estimate_id_counter += 1
    return estimate_obj

@router.get("/{task_id}/estimates", response_model=List[EstimateRead])
def list_estimates(task_id: int, current_user=Depends(get_current_user)):
    return [e for e in fake_estimates_db.values() if e.task_id == task_id] 