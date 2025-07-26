from fastapi import FastAPI, Depends
from fastapi.responses import PlainTextResponse
from fastapi.requests import Request
from typing import Dict
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.ai import router as ai_router
from app.dependencies.auth import get_current_user
from app.models.user import UserRead
import time
import json
import sys
import traceback
from app.database import engine, Base
from app.seed_data import seed_database

# Create database tables
Base.metadata.create_all(bind=engine)

# Seed database with demo data
seed_database()

app = FastAPI()

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(ai_router)


# In-memory metrics storage
metrics: Dict[str, int] = {"requests": 0, "errors": 0}


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start_time = time.time()
    metrics["requests"] += 1
    
    user_id = None
    # Try to extract userId from JWT if present
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            from app.core.security import decode_token
            payload = decode_token(token)
            user_id = payload.get("sub") if payload else None
        except Exception:
            user_id = None
    
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "userId": user_id,
    }
    
    try:
        response = await call_next(request)
        latency = time.time() - start_time
        log_data.update({
            "status_code": response.status_code,
            "latency_ms": int(latency * 1000),
        })
        print(json.dumps(log_data), file=sys.stdout)
        return response
    except Exception as exc:
        metrics["errors"] += 1
        latency = time.time() - start_time
        log_data.update({
            "status_code": 500,
            "latency_ms": int(latency * 1000),
            "error": str(exc),
            "stack": traceback.format_exc()
        })
        print(json.dumps(log_data), file=sys.stdout)
        raise


@app.get("/metrics", response_class=PlainTextResponse)
def get_metrics():
    lines = [
        f"requests_total {metrics['requests']}",
        f"errors_total {metrics['errors']}"
    ]
    return "\n".join(lines)


@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user=Depends(get_current_user)):
    return {"username": current_user.username}
