import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.cache import get_cache_service
from app.core.config import get_settings
from app.schemas.common import APIResponse

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


def check_database(db: Session | None = None) -> bool:
    try:
        if db is None:
            return True
        db.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        return False


def check_redis() -> bool:
    try:
        return get_cache_service().ping()
    except Exception as exc:
        logger.warning("Redis health check failed: %s", exc)
        return False


@router.get("/health", response_model=APIResponse[dict])
def health_check(db: Session = Depends(get_db)) -> APIResponse[dict]:
    settings = get_settings()

    try:
        database_ok = check_database(db)
    except TypeError:
        database_ok = check_database()

    redis_ok = check_redis()

    status = "ok" if database_ok and redis_ok else "degraded"

    return APIResponse(
        success=True,
        message="Health check completed",
        data={
            "status": status,
            "app_name": settings.app_name,
            "environment": settings.app_env,
            "services": {
                "api": True,
                "database": database_ok,
                "redis": redis_ok,
            },
        },
    )