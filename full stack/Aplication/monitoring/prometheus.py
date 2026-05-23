import time
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi import Depends
from fastapi import APIRouter
from fastapi.responses import Response
from app.api.deps import require_role
from app.core.roles import Role
from app.models.user import User

router = APIRouter(
    tags=["Prometheus Monitoring"],
)


# =========================
# Request Metrics
# =========================

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "app_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

ACTIVE_REQUESTS = Gauge(
    "app_active_requests",
    "Number of active requests",
)
APP_UPTIME = Gauge(
    "app_uptime_seconds",
    "Application uptime in seconds",
)

APP_UPTIME.set(time.time())

# =========================
# Cache Metrics
# =========================

CACHE_HITS = Counter(
    "app_cache_hits_total",
    "Total cache hits",
)

CACHE_MISSES = Counter(
    "app_cache_misses_total",
    "Total cache misses",
)

CACHE_INVALIDATIONS = Counter(
    "app_cache_invalidations_total",
    "Total cache invalidations",
)


# =========================
# Order Metrics
# =========================

ORDERS_CREATED = Counter(
    "app_orders_created_total",
    "Total created orders",
)

ORDERS_CANCELLED = Counter(
    "app_orders_cancelled_total",
    "Total cancelled orders",
)

ORDER_REVENUE = Counter(
    "app_order_revenue_total",
    "Total order revenue",
)


# =========================
# Cart Metrics
# =========================

CART_ITEMS_ADDED = Counter(
    "app_cart_items_added_total",
    "Total cart items added",
)

CART_ITEMS_REMOVED = Counter(
    "app_cart_items_removed_total",
    "Total cart items removed",
)


# =========================
# Product Metrics
# =========================

PRODUCTS_CREATED = Counter(
    "app_products_created_total",
    "Total products created",
)

PRODUCTS_UPDATED = Counter(
    "app_products_updated_total",
    "Total products updated",
)

PRODUCTS_DELETED = Counter(
    "app_products_deleted_total",
    "Total products deleted",
)


# =========================
# Monitoring Endpoint
# =========================

@router.get(
    "/metrics",
    include_in_schema=False,
)
async def metrics(
    _: User = Depends(
        require_role(Role.ADMIN)
    ),
):

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )