from fastapi import APIRouter
from sqlalchemy import text

from app.core.cache import get_cache_service
from app.db.session import SessionLocal

router = APIRouter(
    tags=["Health Monitoring"],
)


@router.get("/health")
def health_check() -> dict:

    return {
        "success": True,
        "status": "healthy",
        "service": "ecommerce-api",
    }


@router.get("/health/db")
def database_health_check() -> dict:

    db = SessionLocal()

    try:

        db.execute(text("SELECT 1"))

        return {
            "success": True,
            "database": "healthy",
        }

    except Exception as exc:

        return {
            "success": False,
            "database": "unhealthy",
            "error": str(exc),
        }

    finally:

        db.close()


@router.get("/health/cache")
def cache_health_check() -> dict:

    cache = get_cache_service()

    try:

        cache_ok = cache.ping()

        return {
            "success": cache_ok,
            "cache": (
                "healthy"
                if cache_ok
                else "unhealthy"
            ),
        }

    except Exception as exc:

        return {
            "success": False,
            "cache": "unhealthy",
            "error": str(exc),
        }