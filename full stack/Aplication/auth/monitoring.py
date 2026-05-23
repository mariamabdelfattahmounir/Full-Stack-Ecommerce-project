from typing import Optional
import logging
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import require_role
from app.core.cache_stats import cache_stats
from app.core.log_storage import log_storage
from app.core.roles import Role
from app.models.user import User
from app.schemas.common import APIResponse
from app.metrics.request_metrics import get_error_rate, get_request_count_by_status

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])
logger = logging.getLogger(__name__)

@router.get(
    "/dashboard",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get complete monitoring dashboard data",
)
async def get_dashboard(
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[dict]:
    cache_snapshot = cache_stats.get_snapshot()
    request_summary = log_storage.get_summary()
    error_logs = log_storage.get_error_logs(limit=10)
    slow_requests = log_storage.get_slow_requests(threshold_ms=500, limit=10)
    error_rate_data = get_error_rate()

    data = {
        "system_health": {
            "status": "healthy",
            "monitoring": "enabled",
            "cache": "enabled",
            "logging": "enabled",
        },
        "request_count": request_summary.get("total_requests", 0),
        "total_requests": request_summary.get("total_requests", 0),
        "average_response_time_ms": request_summary.get("avg_duration_ms", 0),
        "avg_response_time_ms": request_summary.get("avg_duration_ms", 0),
        "error_count": request_summary.get("error_count", 0),
        "error_rate": request_summary.get("error_rate", 0.0),
        "recent_errors": error_logs.get("entries", [])[:10],
        "cache": {
            "total_hits": cache_snapshot.total_hits,
            "total_misses": cache_snapshot.total_misses,
            "total_sets": cache_snapshot.total_sets,
            "total_invalidations": cache_snapshot.total_invalidations,
            "hit_ratio": cache_snapshot.hit_ratio,
            "avg_cache_latency_ms": cache_snapshot.avg_cache_latency_ms,
            "avg_db_latency_ms": cache_snapshot.avg_db_latency_ms,
            "latency_improvement_pct": cache_snapshot.latency_improvement_pct,
            "operations_by_source": cache_snapshot.operations_by_source,
            "operations_by_key_prefix": cache_snapshot.operations_by_key_prefix,
            "recent_operations": cache_snapshot.recent_operations[:20],
        },
        "requests": request_summary,
        "errors": {
            "total": error_logs.get("total", 0),
            "recent": error_logs.get("entries", [])[:10],
        },
        "slow_requests": {
            "total": slow_requests.get("total", 0),
            "threshold_ms": slow_requests.get("threshold_ms", 500),
            "recent": slow_requests.get("entries", [])[:10],
        },
        "metrics": {
            "error_rate": error_rate_data,
            "status_distribution": get_request_count_by_status(),
        },
        "status_distribution": get_request_count_by_status(),
    }
    logger.info(
        "Monitoring dashboard accessed",
        extra={
            "endpoint": "/monitoring/dashboard",
        },
    )
    return APIResponse(
        success=True,
        message="Monitoring dashboard data retrieved successfully",
        data=data,
    )


@router.get(
    "/cache",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get cache performance statistics",
)
async def get_cache_stats(
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[dict]:
    snapshot = cache_stats.get_snapshot()

    data = {
        "total_hits": snapshot.total_hits,
        "total_misses": snapshot.total_misses,
        "total_sets": snapshot.total_sets,
        "total_invalidations": snapshot.total_invalidations,
        "hit_ratio": snapshot.hit_ratio,
        "avg_cache_latency_ms": snapshot.avg_cache_latency_ms,
        "avg_db_latency_ms": snapshot.avg_db_latency_ms,
        "latency_improvement_pct": snapshot.latency_improvement_pct,
        "operations_by_source": snapshot.operations_by_source,
        "operations_by_key_prefix": snapshot.operations_by_key_prefix,
        "recent_operations": snapshot.recent_operations,
    }
    logger.info(
        "Cache statistics accessed",
        extra={
            "endpoint": "/monitoring/cache",
        },
    )
    return APIResponse(
        success=True,
        message="Cache statistics retrieved successfully",
        data=data,
    )


@router.get(
    "/logs",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get request logs with filters",
)
async def get_request_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    path_prefix: Optional[str] = Query(None, description="Filter by path prefix"),
    status_code_min: Optional[int] = Query(None, ge=100, le=599),
    status_code_max: Optional[int] = Query(None, ge=100, le=599),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    since: Optional[float] = Query(None, description="Unix timestamp; logs after this time"),
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[dict]:
    data = log_storage.get_logs(
        limit=limit,
        offset=offset,
        method=method,
        path_prefix=path_prefix,
        status_code_min=status_code_min,
        status_code_max=status_code_max,
        user_id=user_id,
        since=since,
    )
    logger.info(
        "Request logs accessed",
        extra={
            "endpoint": "/monitoring/logs",
            "limit": limit,
        },
    )
    return APIResponse(
        success=True,
        message="Request logs retrieved successfully",
        data=data,
    )


@router.get(
    "/errors",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get recent error logs",
)
async def get_error_logs(
    limit: int = Query(50, ge=1, le=200),
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[dict]:
    data = log_storage.get_error_logs(limit=limit)
    logger.info(
        "Error logs accessed",
        extra={
            "endpoint": "/monitoring/errors",
            "limit": limit,
        },
    )
    return APIResponse(
        success=True,
        message="Error logs retrieved successfully",
        data=data,
    )


@router.get(
    "/slow-requests",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get slow request logs",
)
async def get_slow_requests(
    threshold_ms: float = Query(1000, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[dict]:
    data = log_storage.get_slow_requests(
        threshold_ms=threshold_ms,
        limit=limit,
    )
    logger.info(
        "Slow requests accessed",
        extra={
            "endpoint": "/monitoring/slow-requests",
            "threshold_ms": threshold_ms,
        },
    )
    return APIResponse(
        success=True,
        message="Slow request logs retrieved successfully",
        data=data,
    )


@router.get(
    "/request-summary",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get request statistics summary",
)
async def get_request_summary(
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[dict]:
    data = log_storage.get_summary()
    logger.info(
        "Request summary accessed",
        extra={
            "endpoint": "/monitoring/request-summary",
        },
    )
    return APIResponse(
        success=True,
        message="Request summary retrieved successfully",
        data=data,
    )


@router.get(
    "/error-rate",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get current error rate",
)
async def get_error_rate_endpoint(
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[dict]:
    data = get_error_rate()
    logger.info(
        "Error rate accessed",
        extra={
            "endpoint": "/monitoring/error-rate",
        },
    )
    return APIResponse(
        success=True,
        message="Error rate retrieved successfully",
        data=data,
    )