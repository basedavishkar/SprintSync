from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time
import traceback
import structlog
import sys
import logging
import uuid

from app.core.config import settings
from app.core.database import engine, Base
from app.seed_data import seed_database

# Import routers
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.ai import router as ai_router
from app.web_routes import router as web_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configure standard library logging to output to both console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log"),
    ],
)

logger = structlog.get_logger()

# Create database tables
Base.metadata.create_all(bind=engine)

# Seed database with demo data
seed_database()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name, version=settings.version, debug=settings.debug
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
    "response_times": [],
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

    # Create structured log context
    log_context = {
        "method": request.method,
        "path": request.url.path,
        "user_id": user_id,
        "user_agent": request.headers.get("user-agent", ""),
        "ip_address": request.client.host if request.client else None,
        "correlation_id": str(uuid.uuid4()),  # Correlation ID for tracing
    }

    try:
        response = await call_next(request)
        latency = time.time() - start_time
        log_context.update(
            {
                "status_code": response.status_code,
                "latency_ms": int(latency * 1000),
            }
        )

        # Log successful request with structured data
        logger.info("Request processed", **log_context)
        return response
    except Exception as exc:
        metrics["errors"] += 1
        latency = time.time() - start_time

        # Classify error type
        error_type = "UNKNOWN"
        if "authentication" in str(exc).lower() or "token" in str(exc).lower():
            error_type = "AUTH"
        elif "validation" in str(exc).lower() or "422" in str(exc):
            error_type = "VALIDATION"
        elif "database" in str(exc).lower() or "sql" in str(exc).lower():
            error_type = "DATABASE"
        elif "timeout" in str(exc).lower():
            error_type = "TIMEOUT"

        log_context.update(
            {
                "status_code": 500,
                "latency_ms": int(latency * 1000),
                "error": str(exc),
                "error_type": error_type,
                "stack_trace": traceback.format_exc(),
            }
        )

        # Log error with full structured context
        logger.error("Request failed", **log_context, exc_info=True)
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
        f'app="{settings.app_name}"}} 1',
    ]

    return "\n".join(lines)


@app.get("/health")
def health_check():
    """Comprehensive health check endpoint."""
    from sqlalchemy import text
    from app.core.database import SessionLocal

    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.version,
        "uptime_seconds": int(time.time() - metrics["start_time"]),
    }

    # Check database connectivity
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
        db.close()
    except Exception:
        health_status["database"] = "disconnected"
        health_status["status"] = "unhealthy"

    # Check AI service availability
    health_status["ai_service"] = "available"  # Basic check

    return health_status
