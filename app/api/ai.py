from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.ai_service import ai_service

load_dotenv()

router = APIRouter(prefix="/ai", tags=["ai"])


class SuggestRequest(BaseModel):
    title: str = None
    mode: str = "draft"  # "draft" or "plan"


class SuggestResponse(BaseModel):
    suggestion: str


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_task(
    req: SuggestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI-powered task suggestion endpoint."""
    
    try:
        if req.mode == "draft" and req.title:
            suggestion = ai_service.generate_task_description(req.title)
        else:
            # Get user's actual tasks for context
            from app.services.task_service import TaskService
            task_service = TaskService(db)
            user_tasks = task_service.get_user_tasks(current_user.id)
            
            # Convert to list of dicts for AI service
            tasks_data = [
                {"title": task.title, "status": task.status} 
                for task in user_tasks
            ]
            
            suggestion = ai_service.generate_daily_plan(
                current_user.username, 
                tasks_data
            )
        
        return SuggestResponse(suggestion=suggestion)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate AI suggestion: {str(e)}"
        ) 