from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time
import json
import sys
import traceback

from app.core.config import settings
from app.core.database import engine, Base
from app.seed_data import seed_database

# Import routers
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.ai import router as ai_router
from app.web_routes import router as web_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Seed database with demo data
seed_database()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(ai_router)
app.include_router(web_router)


# Metrics storage
metrics = {"requests": 0, "errors": 0}


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Middleware for request logging and metrics."""
    start_time = time.time()
    metrics["requests"] += 1

    # Extract user ID from JWT if present
    user_id = None
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


@app.get("/metrics")
def get_metrics():
    """Get application metrics."""
    lines = [
        f"requests_total {metrics['requests']}",
        f"errors_total {metrics['errors']}"
    ]
    return "\n".join(lines)
