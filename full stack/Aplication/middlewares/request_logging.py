"""
Request Logging Middleware
"""

import logging
import time
import uuid
from typing import Any
from app.metrics.request_metrics import (
 record_request_metrics,
)
from fastapi.responses import JSONResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.requests import (
    Request,
)
from starlette.responses import (
    Response,
)

from app.core.log_storage import (
    log_storage,
)

from app.utils.request_context import (
    reset_request_id,
    set_request_id,
)

logger = logging.getLogger(
    "app.access"
)

audit_logger = logging.getLogger(
    "app.audit"
)
SLOW_REQUEST_THRESHOLD_MS = 1000
MAX_QUERY_LENGTH = 500

class RequestLoggingMiddleware(
    BaseHTTPMiddleware
):

    async def dispatch(
        self,
        request: Request,
        call_next: Any,
    ) -> Response:

        request_id = (
            request.headers.get(
                "X-Request-ID"
            )
            or str(uuid.uuid4())
        )

        token = set_request_id(
            request_id
        )

        start_time = (
            time.perf_counter()
        )

        response: (
            Response | None
        ) = None

        error_message: (
            str | None
        ) = None

        skip_paths = (
            "/metrics",
            "/health",
            "/api/v1/monitoring",
            "/favicon.ico",
        )
        path = request.url.path.rstrip("/") or "/"
        should_log = not any(
            path.startswith(skip_path)
            for skip_path in skip_paths
            )

        
        try:

            logger.info(
                "Incoming request",
                extra={
                    "event": "incoming_request",
                    "request_id": (
                        request_id
                    ),
                    "method": (
                        request.method
                    ),
                    "path": (
                        path
                    ),
                    "client_ip": (
                        request.client.host
                        if request.client
                        else "unknown"
                    ),
                },
            )
            auth_paths = (
                "/auth/login",
                "/auth/register",
                "/auth/logout",
                "/auth/refresh",
            )

            if any(auth_path in path for auth_path in auth_paths):

                audit_logger.info(
                    "Authentication endpoint accessed",
                    extra={
                        "event": "auth_event",
                        "request_id": request_id,
                        "path": path,
                        "method": request.method,
                        "client_ip": (
                            request.client.host
                            if request.client
                            else "unknown"
                        ),
                    },
                )
            response = await call_next(
                request
            )

            return response
        except Exception as exc:

            logger.exception(
                "Unhandled request exception",
                extra={
                    "event": "unhandled_request_exception",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                },
            )

            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "internal_server_error",
                        "message": "An unexpected error occurred",
                        "details": [],
                    },
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Process-Time": str(
                        round(duration_ms / 1000, 4)
                    ),
                },
            )

            raise

        finally:

            duration_ms = (
                (
                    time.perf_counter()
                    - start_time
                )
                * 1000
            )

            status_code = (
                response.status_code
                if response is not None
                else 500
            )

            client_ip = (
                request.client.host
                if request.client
                else "unknown"
            )
            user_agent = request.headers.get(
                "user-agent",
                "unknown",
            )
            content_length = request.headers.get(
                "content-length",
                "0",
            )            
            response_size = (
                response.headers.get(
                    "content-length",
                    "0",
                )
                if response is not None
                else "0"
            )            
            user_id = getattr(
                request.state,
                "user_id",
                None,
            )
            if user_id:

                audit_logger.info(
                    "Authenticated request",
                    extra={
                        "event": "authenticated_request",
                        "request_id": request_id,
                        "user_id": str(user_id),
                        "method": request.method,
                        "path": path,
                        "status_code": status_code,
                    },
                )
            crud_event = None

            if request.method == "POST":
                crud_event = "create_operation"

            elif request.method == "PUT":
                crud_event = "update_operation"

            elif request.method == "PATCH":
                crud_event = "partial_update_operation"

            elif request.method == "DELETE":
                crud_event = "delete_operation"

            if crud_event:

                audit_logger.info(
                    "CRUD operation detected",
                    extra={
                        "event": crud_event,
                        "request_id": request_id,
                        "method": request.method,
                        "path": path,
                        "user_id": (
                            str(user_id)
                            if user_id
                            else None
                        ),
                    },
                )                
            if response is not None:
                response.headers["X-Process-Time"] = str(
                    round(duration_ms / 1000, 4)
                )

                response.headers[
                    "X-Request-ID"
                ] = request_id

            if should_log:

                log_level = (
                    logging.ERROR
                    if status_code >= 500
                    else logging.WARNING
                    if status_code >= 400
                    else logging.INFO
                )
                query_params = str(
                    request.query_params
                )
                if len(query_params) > MAX_QUERY_LENGTH:
                    query_params = (
                        query_params[:MAX_QUERY_LENGTH]
                        + "..."
                    )
                sensitive_keywords = (
                    "token=",
                    "password=",
                    "secret=",
                    "api_key=",
                )
                if any(
                    keyword in query_params.lower()
                    for keyword in sensitive_keywords
                ):
                    query_params = "***masked***"
                logger.log(
                    log_level,
                    "HTTP request completed",
                    extra={
                        "event": "http_request_completed",
                        "user_agent": user_agent,
                        "content_length": content_length,
                        "response_size": response_size,
                        "request_id": (
                            request_id
                        ),
                        "method": (
                            request.method
                        ),
                        "path": (
                           path
                        ),
                        "status_code": (
                            status_code
                        ),
                        "response_time": round(
                            duration_ms,
                            2,
                        ),
                        "client_ip": (
                            client_ip
                        ),
                        "user_id": (
                            str(user_id)
                            if user_id
                            else None
                        ),
                        "query_params": (
                            query_params
                            if request.query_params
                            else None
                        ),
                        
                    },
                )
                if status_code >= 500:

                    audit_logger.error(
                        "Server error detected",
                        extra={
                            "event": "server_error",
                            "request_id": request_id,
                            "path": path,
                            "status_code": status_code,
                        },
                    )
                if duration_ms > SLOW_REQUEST_THRESHOLD_MS:

                    logger.warning(
                        "Slow request detected",
                        extra={
                            "event": "slow_request_detected",
                            "request_id": (
                                request_id
                            ),
                            "path": (
                               path
                            ),
                            "response_time": round(
                                duration_ms,
                                2,
                            ),
                        },
                    )
            if should_log:
                log_storage.add_log(
                    request_id=request_id,
                    method=request.method,
                    path=path,
                    status_code=status_code,
                    duration_ms=round(
                        duration_ms,
                        2,
                    ),
                    client_ip=client_ip,
                    user_id=(
                        str(user_id)
                        if user_id
                        else None
                    ),
                    error_message=(
                        error_message
                    ),
                    query_params=(
                        query_params
                        if request.query_params
                        else None
                    ),
                )

            try:


                record_request_metrics(
                    method=request.method,
                    endpoint=path,
                    status_code=status_code,
                    duration_ms=duration_ms,
                )

            except Exception:

                logger.debug(
                    "Failed to record request metrics",
                    exc_info=True,
                    extra={
                        "request_id": (
                            request_id
                        ),
                    },
                )

            reset_request_id(
                token
            )
            logger.debug(
                "Request context reset",
                extra={
                    "event": "request_context_reset",
                    "request_id": request_id,
                },
            )            