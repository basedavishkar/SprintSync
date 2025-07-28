from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user_web
from app.models.user import UserCreate, UserLogin, UserRead
from app.services.user_service import UserService
from typing import List

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    user_service = UserService(db)
    try:
        user = user_service.create_user(user_data)
        return {"username": user.username, "user_id": user.id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token."""
    user_service = UserService(db)
    user = user_service.authenticate_user(
        user_data.username, user_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users", response_model=List[UserRead])
def list_users(
    current_user: UserRead = Depends(get_current_user_web),
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user_service = UserService(db)
    return user_service.get_all_users()


@router.get("/admin/stats")
def get_admin_stats(
    current_user: UserRead = Depends(get_current_user_web),
    db: Session = Depends(get_db)
):
    """Get system statistics (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    from app.models.user import User
    from app.models.task import Task
    
    # Get basic stats
    total_users = db.query(User).count()
    total_tasks = db.query(Task).count()
    active_tasks = db.query(Task).filter(
        Task.status.in_(["todo", "in_progress"])
    ).count()
    completed_tasks = db.query(Task).filter(Task.status == "done").count()
    
    # Get user activity stats
    user_stats = []
    users = db.query(User).all()
    for user in users:
        user_task_count = db.query(Task).filter(
            Task.user_id == user.id
        ).count()
        user_completed_count = db.query(Task).filter(
            Task.user_id == user.id, 
            Task.status == "done"
        ).count()
        
        completion_rate = 0
        if user_task_count > 0:
            completion_rate = round(
                (user_completed_count / user_task_count * 100), 1
            )
        
        user_stats.append({
            "username": user.username,
            "is_admin": user.is_admin,
            "total_tasks": user_task_count,
            "completed_tasks": user_completed_count,
            "completion_rate": completion_rate
        })
    
    return {
        "system_overview": {
            "total_users": total_users,
            "total_tasks": total_tasks,
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(
                (completed_tasks / total_tasks * 100) 
                if total_tasks > 0 else 0, 1
            )
        },
        "user_activity": user_stats
    }
