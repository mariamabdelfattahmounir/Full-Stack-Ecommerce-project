import logging
from app.tasks.cleanup_tasks import (
    cleanup_expired_refresh_tokens,
)
from app.db.session import SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from slowapi.errors import (
    RateLimitExceeded,
)
from slowapi.middleware import (
    SlowAPIMiddleware,
)

from app.api.v1.router import (
    api_router,
)

from app.core.config import (
    get_settings,
)

from app.core.exceptions import (
    register_exception_handlers,
)

from app.core.logging import (
    configure_logging,
)


from app.middlewares.rate_limit import (
    limiter,
    rate_limit_exceeded_handler,
)

from app.middlewares.request_context import (
    RequestContextMiddleware,
)

from app.middlewares.request_logging import (
    RequestLoggingMiddleware,
)

from app.middlewares.security_headers import (
    SecurityHeadersMiddleware,
)

from app.monitoring.prometheus import (
    router as prometheus_router,
)
from app.monitoring.health import (
    router as health_router,
)

configure_logging()

logger = logging.getLogger(__name__)

settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
register_exception_handlers(app)


# =========================
# Middleware
# =========================

if settings.app_env != "test":

    app.add_middleware(
        SlowAPIMiddleware
    )
if settings.app_env != "test":
    app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        settings.backend_cors_origins
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SecurityHeadersMiddleware
)

app.add_middleware(
    RequestContextMiddleware
)

app.add_middleware(
    RequestLoggingMiddleware
)

# =========================
# Exception Handlers
# =========================
if settings.app_env != "test":

    app.add_exception_handler(
        RateLimitExceeded,
        rate_limit_exceeded_handler,
    )


# =========================
# Routers
# =========================

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    prometheus_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    health_router,
)

# =========================
# Root Endpoint
# =========================

@app.get(
    "/",
    tags=["Root"],
)
def root() -> dict:

    return {
        "success": True,
        "message": (
            "Professional E-Commerce API "
            "is running"
        ),
        "data": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "api_prefix": (
                settings.api_v1_prefix
            ),
            "health": (
                f"{settings.api_v1_prefix}"
                "/health"
            ),
            "metrics": "/metrics",
        },
    }


# =========================
# Startup Event
# =========================

@app.on_event(
    "startup"
)
def on_startup() -> None:

    logger.info(
        "Application startup completed",
        extra={
            "app_name": (
                settings.app_name
            ),
            "environment": (
                settings.environment
            ),
            "api_prefix": (
                settings.api_v1_prefix
            ),
        },
    )

    db = SessionLocal()

    try:

        deleted_tokens = (
            cleanup_expired_refresh_tokens(
                db
            )
        )

        logger.info(
            "Expired tokens cleanup completed",
            extra={
                "deleted_tokens": (
                    deleted_tokens
                ),
            },
        )

    except Exception as exc:

        logger.exception(
            "Startup cleanup failed",
            extra={
                "error": str(exc),
            },
        )

    finally:

        db.close()


# =========================
# Shutdown Event
# =========================

@app.on_event(
    "shutdown"
)
def on_shutdown() -> None:

    logger.info(
        "Application shutdown completed",
        extra={
            "app_name": (
                settings.app_name
            ),
        },
    )
