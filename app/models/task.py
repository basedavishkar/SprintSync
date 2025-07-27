from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from typing import Optional


# SQLAlchemy Model
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="todo")  # todo, in_progress, done
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="tasks")


# Pydantic Models
class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: str = "todo"


class TaskRead(BaseModel):
    id: int
    title: str
    description: str
    status: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    status: str = None 