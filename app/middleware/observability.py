"""
Observability middleware for request logging, metrics, and error tracking.
"""
import time
import traceback
import uuid
import structlog
from fastapi import Request
from app.core.security import decode_token

logger = structlog.get_logger()

# Metrics storage
metrics = {
    "requests": 0,
    "errors": 0,
    "start_time": time.time(),
    "response_times": [],
}


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


def get_metrics():
    """Get application metrics in Prometheus format."""
    from app.core.config import settings

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
