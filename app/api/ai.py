from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.ai_service import ai_service

load_dotenv()

router = APIRouter(prefix="/ai", tags=["ai"])


class SuggestRequest(BaseModel):
    title: str = Field(None, example="Build a chatbot")
    mode: str = Field(
        ..., example="draft", description="Either 'draft' or 'plan'"
    )


class SuggestResponse(BaseModel):
    suggestion: str = Field(
        ..., example="Implement a chatbot using OpenAI's GPT-3 API..."
    )


class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Failed to generate AI suggestion: ...")


@router.post(
    "/suggest",
    response_model=SuggestResponse,
    responses={
        401: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def suggest_task(
    req: SuggestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI-powered task suggestion endpoint."""
    try:
        if req.mode not in ["draft", "plan"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid mode. Must be 'draft' or 'plan'.",
            )
        if req.mode == "draft":
            if not req.title:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Title is required for draft mode.",
                )
            suggestion = ai_service.generate_task_description(req.title)
        else:
            from app.services.task_service import TaskService

            task_service = TaskService(db)
            user_tasks = task_service.get_user_tasks(current_user.id)
            tasks_data = [
                {"title": task.title, "status": task.status}
                for task in user_tasks
            ]
            suggestion = ai_service.generate_daily_plan(
                current_user.username, tasks_data
            )
        return SuggestResponse(suggestion=suggestion)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI suggestion: {str(e)}",
        )
