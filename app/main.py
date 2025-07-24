from fastapi import FastAPI, Depends
from app.api.auth import router as auth_router
from app.dependencies.auth import get_current_user
from app.models.user import UserRead

app = FastAPI()

app.include_router(auth_router)


@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user=Depends(get_current_user)):
    return {"username": current_user.username}
