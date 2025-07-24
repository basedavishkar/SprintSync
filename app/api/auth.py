from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from app.models.user import UserCreate, UserLogin, UserRead, UserInDB
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory user 'DB'
fake_users_db = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/signup", response_model=UserRead)
def signup(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(user.password)
    user_in_db = UserInDB(username=user.username, hashed_password=hashed_password)
    fake_users_db[user.username] = user_in_db
    return UserRead(username=user.username)


@router.post("/login")
def login(user: UserLogin):
    user_in_db = fake_users_db.get(user.username)
    if not user_in_db or not pwd_context.verify(user.password, user_in_db.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"} 