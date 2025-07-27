from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time
import sys
import traceback
import logging
from datetime import datetime

from app.core.config import settings
from app.core.database import engine, Base
from app.seed_data import seed_database

# Import routers
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.ai import router as ai_router
from app.web_routes import router as web_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')  # Also log to file for production
    ]
)
logger = logging.getLogger(__name__)

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
metrics = {
    "requests": 0,
    "errors": 0,
    "start_time": time.time(),
    "response_times": []
}


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Middleware for request logging and metrics."""
    start_time = time.time()
    metrics["requests"] += 1

    # Extract user ID from JWT if present (try both cookie and header)
    user_id = None
    token = None

    # Try cookie first (for web interface)
    token = request.cookies.get("token")

    # Try Authorization header (for API calls)
    if not token:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

    if token:
        try:
            from app.core.security import decode_token
            payload = decode_token(token)
            user_id = payload.get("sub") if payload else None
        except Exception:
            user_id = None

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "userId": user_id,
        "user_agent": request.headers.get("user-agent", ""),
        "ip_address": request.client.host if request.client else None,
    }

    try:
        response = await call_next(request)
        latency = time.time() - start_time
        log_data.update({
            "status_code": response.status_code,
            "latency_ms": int(latency * 1000),
            "level": "INFO"
        })
        
        # Use proper structured logging
        logger.info("Request processed", extra=log_data)
        return response
    except Exception as exc:
        metrics["errors"] += 1
        latency = time.time() - start_time
        log_data.update({
            "status_code": 500,
            "latency_ms": int(latency * 1000),
            "error": str(exc),
            "stack_trace": traceback.format_exc(),
            "level": "ERROR"
        })
        
        # Log error with full context
        logger.error("Request failed", extra=log_data, exc_info=True)
        raise


@app.get("/metrics")
def get_metrics():
    """Get application metrics in Prometheus format."""
    current_time = time.time()
    uptime = current_time - metrics["start_time"]

    lines = [
        "# HELP requests_total Total number of requests",
        "# TYPE requests_total counter",
        f"requests_total {metrics['requests']}",
        "",
        "# HELP errors_total Total number of errors",
        "# TYPE errors_total counter",
        f"errors_total {metrics['errors']}",
        "",
        "# HELP app_uptime_seconds Application uptime in seconds",
        "# TYPE app_uptime_seconds gauge",
        f"app_uptime_seconds {uptime}",
        "",
        "# HELP app_version_info Application version information",
        "# TYPE app_version_info gauge",
        f'app_version_info{{version="{settings.version}",'
        f'app="{settings.app_name}"}} 1'
    ]

    return "\n".join(lines)


@app.get("/health")
def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy", "timestamp": time.time()}
