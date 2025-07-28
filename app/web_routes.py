from fastapi import APIRouter, Request, status, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token, get_current_user_web
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.models.user import User
from app.models.task import TaskCreate

# Templates
templates = Jinja2Templates(directory="app/templates")

# Router
router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Redirect root to dashboard."""
    return RedirectResponse(
        url="/dashboard", status_code=status.HTTP_302_FOUND
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page."""
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard page with user tasks."""
    # Get current user from cookie
    current_user = None
    token = request.cookies.get("token")

    if token:
        try:
            payload = decode_token(token)
            if payload:
                user_service = UserService(db)
                current_user = user_service.get_user_by_username(
                    payload.get("sub")
                )
        except Exception:
            pass

    if not current_user:
        return RedirectResponse(
            url="/login", status_code=status.HTTP_302_FOUND
        )

    # Get user's tasks using service
    task_service = TaskService(db)
    tasks = task_service.get_user_tasks(current_user.id)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "current_user": current_user, "tasks": tasks},
    )


@router.get("/web/tasks/", response_class=HTMLResponse)
async def tasks_list(request: Request, db: Session = Depends(get_db)):
    """Get tasks as HTML for HTMX."""
    try:
        current_user = get_current_user_web(request, db)
        task_service = TaskService(db)
        
        # If admin, show all tasks. Otherwise, show only user's tasks
        if current_user.is_admin:
            tasks = task_service.get_all_tasks()
        else:
            tasks = task_service.get_user_tasks(current_user.id)

        return templates.TemplateResponse(
            "task_list.html",
            {"request": request, "tasks": tasks, "current_user": current_user},
        )
    except Exception as e:
        print(f"Error in tasks_list: {e}")
        return templates.TemplateResponse(
            "task_list.html",
            {
                "request": request,
                "tasks": [],
                "current_user": None,
                "error": f"Not authenticated: {str(e)}",
            },
        )


@router.post("/web/tasks/", response_class=HTMLResponse)
async def create_task_web(
    request: Request,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    """Create a task via web form."""
    try:
        current_user = get_current_user_web(request, db)
        task_service = TaskService(db)

        # Set default status if not provided
        if not task_data.status:
            task_data.status = "todo"

        task_service.create_task(task_data, current_user)

        # Return updated task list HTML
        tasks = task_service.get_user_tasks(current_user.id)
        return templates.TemplateResponse(
            "task_list.html",
            {"request": request, "tasks": tasks, "current_user": current_user},
        )
    except Exception as e:
        print(f"Error in create_task_web: {e}")
        return templates.TemplateResponse(
            "task_list.html",
            {
                "request": request,
                "tasks": [],
                "current_user": None,
                "error": f"Error creating task: {str(e)}",
            },
        )


@router.delete("/web/tasks/{task_id}")
async def delete_task_web(
    task_id: int, request: Request, db: Session = Depends(get_db)
):
    """Delete a task via web interface."""
    try:
        current_user = get_current_user_web(request, db)
        task_service = TaskService(db)
        
        # If admin, allow deleting any task. Otherwise, only user's own tasks
        if current_user.is_admin:
            success = task_service.delete_task_admin(task_id)
        else:
            success = task_service.delete_task(task_id, current_user.id)
            
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"success": True}
    except Exception:
        raise HTTPException(status_code=403, detail="Not authenticated")


@router.post("/web/tasks/{task_id}/assign")
async def assign_task_web(
    task_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """Assign a task to a different user via web interface (admin only)."""
    try:
        current_user = get_current_user_web(request, db)
        
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can assign tasks to users.",
            )
        
        # Get the user_id from the request body
        body = await request.json()
        target_user_id = body.get("user_id")
        
        if not target_user_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="user_id is required.",
            )
        
        task_service = TaskService(db)
        task = task_service.assign_task_to_user(task_id, target_user_id)
        
        if not task:
            raise HTTPException(
                status_code=404, 
                detail="Task or user not found"
            )
        
        return {
            "success": True, 
            "message": f"Task assigned to user ID {target_user_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in assign_task_web: {e}")
        raise HTTPException(status_code=403, detail="Not authenticated")


@router.get("/web/users", response_class=HTMLResponse)
async def get_users_for_admin(request: Request, db: Session = Depends(get_db)):
    """Get all users for admin task assignment (admin only)."""
    try:
        current_user = get_current_user_web(request, db)
        
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can access user list.",
            )
        
        user_service = UserService(db)
        users = user_service.get_all_users()
        
        # Return users as JSON for frontend consumption
        from fastapi.responses import JSONResponse
        return JSONResponse({
            "users": [
                {"id": user.id, "username": user.username} 
                for user in users
            ]
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_users_for_admin: {e}")
        raise HTTPException(status_code=403, detail="Not authenticated")


@router.get("/debug/tasks", response_class=HTMLResponse)
async def debug_tasks(request: Request, db: Session = Depends(get_db)):
    """Debug endpoint to check tasks in database."""
    # Get all users and their tasks
    task_service = TaskService(db)

    users = db.query(User).all()
    user_info = []

    for user in users:
        tasks = task_service.get_user_tasks(user.id)
        user_info.append(
            {
                "username": user.username,
                "user_id": user.id,
                "task_count": len(tasks),
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "status": t.status,
                        "created_at": t.created_at,
                    }
                    for t in tasks
                ],
            }
        )

    return templates.TemplateResponse(
        "debug_tasks.html", {"request": request, "users": user_info}
    )


@router.post("/auth/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """Handle logout."""
    response = RedirectResponse(
        url="/login", status_code=status.HTTP_302_FOUND
    )
    response.delete_cookie(key="token")
    return response


@router.get("/auth/logout", response_class=HTMLResponse)
async def logout_get(request: Request):
    """Handle logout via GET request (fallback)."""
    response = RedirectResponse(
        url="/login", status_code=status.HTTP_302_FOUND
    )
    response.delete_cookie(key="token")
    return response
