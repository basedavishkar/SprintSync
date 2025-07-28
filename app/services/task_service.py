from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.task import Task, TaskCreate, TaskUpdate
from app.models.user import User


class TaskService:
    """Service for handling task operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task_data: TaskCreate, user: User) -> Task:
        """Create a new task for the user."""
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            total_minutes=task_data.total_minutes,
            user_id=user.id,
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def get_user_tasks(self, user_id: int) -> List[Task]:
        """Get all tasks for a specific user."""
        return self.db.query(Task).filter(Task.user_id == user_id).all()

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks in the system (admin only)."""
        return self.db.query(Task).all()

    def get_task_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        """Get a specific task by ID, ensuring it belongs to the user."""
        return (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user_id)
            .first()
        )

    def update_task(
        self, task_id: int, user_id: int, task_data: TaskUpdate
    ) -> Optional[Task]:
        """Update a task, ensuring it belongs to the user."""
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return None

        # Update only provided fields
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.status is not None:
            task.status = task_data.status
        if task_data.total_minutes is not None:
            task.total_minutes = task_data.total_minutes

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Delete a task, ensuring it belongs to the user."""
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

    def delete_task_admin(self, task_id: int) -> bool:
        """Delete any task (admin only)."""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

    def update_task_status(
        self, task_id: int, user_id: int, status: str
    ) -> Optional[Task]:
        """Update only the status of a task."""
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return None

        task.status = status
        self.db.commit()
        self.db.refresh(task)
        return task

    def assign_task_to_user(
        self, task_id: int, target_user_id: int
    ) -> Optional[Task]:
        """Assign a task to a different user (admin only)."""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        # Verify target user exists
        target_user = (
            self.db.query(User).filter(User.id == target_user_id).first()
        )
        if not target_user:
            return None

        task.user_id = target_user_id
        self.db.commit()
        self.db.refresh(task)
        return task
