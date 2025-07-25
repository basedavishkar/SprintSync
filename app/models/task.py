from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: int
    created_at: datetime
    user_id: str

class TaskInDB(TaskRead):
    pass

class TimeLogBase(BaseModel):
    task_id: int
    start_time: datetime
    end_time: Optional[datetime] = None

class TimeLogCreate(TimeLogBase):
    pass

class TimeLogRead(TimeLogBase):
    id: int
    duration: Optional[float] = None

class TimeLogInDB(TimeLogRead):
    pass

class EstimateBase(BaseModel):
    task_id: int
    estimated_min: float
    estimated_max: float

class EstimateCreate(EstimateBase):
    pass

class EstimateRead(EstimateBase):
    id: int
    created_at: datetime

class EstimateInDB(EstimateRead):
    pass 