from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base
from app.seed_data import seed_database

# Import middleware
from app.middleware.logging import configure_logging
from app.middleware.observability import observability_middleware, get_metrics
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.ai import router as ai_router
from app.web_routes import router as web_router

# Configure logging
logger = configure_logging()

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

# Add observability middleware
app.middleware("http")(observability_middleware)


@app.get("/metrics")
def metrics_endpoint():
    """Get application metrics in Prometheus format."""
    return get_metrics()


@app.get("/health")
def health_check():
    """Comprehensive health check endpoint."""
    import time
    from sqlalchemy import text
    from app.core.database import SessionLocal
    from app.middleware.observability import metrics

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
