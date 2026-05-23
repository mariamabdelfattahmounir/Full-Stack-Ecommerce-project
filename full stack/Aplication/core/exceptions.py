import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppException(Exception):

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str = "app_error",
        details: Any | None = None,
    ) -> None:

        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details

        super().__init__(message)


def app_exception_handler(
    _: Request,
    exc: AppException,
) -> JSONResponse:

    logger.warning(
        "Application exception raised",
        extra={
            "event": "application_exception",
            "code": exc.code,
            "status_code": exc.status_code,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


def http_exception_handler(
    _: Request,
    exc: HTTPException,
) -> JSONResponse:

    logger.warning(
        "HTTP exception raised",
        extra={
            "event": "http_exception",
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "http_error",
                "message": exc.detail,
            },
        },
    )


def not_found_handler(
    _: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:

    logger.warning(
        "Route not found",
        extra={
            "event": "route_not_found",
            "status_code": exc.status_code,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "http_error",
                "message": exc.detail or "Not Found",
            },
        },
    )


def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:

    formatted_errors = []

    for error in exc.errors():

        formatted_errors.append(
            {
                "field": ".".join(
                    str(item)
                    for item in error.get("loc", [])
                ),
                "message": error.get(
                    "msg",
                    "Validation error",
                ),
                "type": error.get(
                    "type",
                    "validation_error",
                ),
            }
        )

    logger.warning(
        "Validation exception raised",
        extra={
            "event": "validation_exception",
            "errors_count": len(formatted_errors),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": formatted_errors,
            },
        },
    )


def integrity_exception_handler(
    _: Request,
    exc: IntegrityError,
) -> JSONResponse:

    logger.exception(
        "Database integrity error",
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": "database_integrity_error",
                "message": "Database integrity error",
            },
        },
    )


def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:

    request_id = getattr(
        request.state,
        "request_id",
        "-",
    )

    logger.exception(
        "Unhandled exception occurred",
        extra={
            "event": "unhandled_exception",
            "path": request.url.path,
            "request_id": request_id,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "internal_server_error",
                "message": (
                    "An unexpected error occurred"
                ),
                "details": [
                    {
                        "request_id": request_id,
                    }
                ],
            },
        },
    )


def register_exception_handlers(
    app: FastAPI,
) -> None:

    app.add_exception_handler(
        AppException,
        app_exception_handler,
    )

    app.add_exception_handler(
        HTTPException,
        http_exception_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )

    app.add_exception_handler(
        IntegrityError,
        integrity_exception_handler,
    )

    app.add_exception_handler(
        StarletteHTTPException,
        not_found_handler,
    )

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )