from fastapi import FastAPI, Depends
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.ai import router as ai_router
from app.dependencies.auth import get_current_user
from app.models.user import UserRead

app = FastAPI()

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(ai_router)


@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user=Depends(get_current_user)):
    return {"username": current_user.username}
