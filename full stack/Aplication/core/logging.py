import logging
import logging.handlers
import os
import sys

from pythonjsonlogger import jsonlogger

from app.core.config import get_settings
from app.utils.request_context import get_request_id
LOG_FILE_MAX_BYTES = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 5

class RequestIdFilter(logging.Filter):

    def filter(
        self,
        record: logging.LogRecord,
    ) -> bool:

        record.request_id = (
            get_request_id()
        )
        default_fields = {
            "response_time": None,
            "status_code": None,
            "method": None,
            "path": None,
            "event": None,
            "user_id": None,
            "client_ip": None,
            "query_params": None,
            "error": None,
        } 
        for field, default in default_fields.items():

            if not hasattr(record, field):
                setattr(record, field, default)
        if not hasattr(record, "status_code"):
            record.status_code = None

        if not hasattr(record, "method"):
            record.method = None

        if not hasattr(record, "path"):
            record.path = None

        return True


class SensitiveDataFilter(
    logging.Filter
):

    SENSITIVE_FIELDS = {
        "password",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "secret",
        "api_key",
        "client_secret",
        "cookie",
        "session",
    }

    def filter(
        self,
        record: logging.LogRecord,
    ) -> bool:

        if hasattr(record, "__dict__"):

            for field in self.SENSITIVE_FIELDS:

                if field in record.__dict__:
                    record.__dict__[field] = "***"

        return True


def configure_logging() -> None:

    settings = get_settings()

    os.makedirs(
        "logs",
        exist_ok=True,
    )

    root_logger = logging.getLogger()
    access_logger = logging.getLogger(
        "app.access"
    )
    audit_logger = logging.getLogger(
        "app.audit"
    )

    access_logger.handlers.clear()
    audit_logger.handlers.clear()
    root_logger.handlers.clear()
    root_logger.propagate = False
    root_logger.setLevel(
        settings.log_level.upper()
    )

    request_filter = (
        RequestIdFilter()
    )

    sensitive_filter = (
        SensitiveDataFilter()
    )

    if settings.log_json:

        formatter = (
            jsonlogger.JsonFormatter(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(request_id)s "
            "%(method)s "
            "%(path)s "
            "%(status_code)s "
            "%(response_time)s "
            "%(event)s "
            "%(message)s"             
            )
        )

    else:

        formatter = logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "request_id=%(request_id)s | "
            "method=%(method)s | "
            "path=%(path)s | "
            "status_code=%(status_code)s | "
            "response_time=%(response_time)s | "
            "event=%(event)s | "
            "%(message)s"
        )

    console_handler = (
        logging.StreamHandler(
            sys.stdout
        )
    )

    console_handler.setLevel(
        settings.log_level.upper()
    )

    console_handler.addFilter(
        request_filter
    )

    console_handler.addFilter(
        sensitive_filter
    )

    console_handler.setFormatter(
        formatter
    )

    file_handler = (
        logging.handlers.RotatingFileHandler(
            filename="logs/app.log",
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
    )

    file_handler.setLevel(
        settings.log_level.upper()
    )

    file_handler.addFilter(
        request_filter
    )

    file_handler.addFilter(
        sensitive_filter
    )

    file_handler.setFormatter(
        formatter
    )

    error_file_handler = (
        logging.handlers.RotatingFileHandler(
            filename="logs/error.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
    )

    error_file_handler.setLevel(
        logging.ERROR
    )

    error_file_handler.addFilter(
        request_filter
    )

    error_file_handler.addFilter(
        sensitive_filter
    )

    error_file_handler.setFormatter(
        formatter
    )

    root_logger.addHandler(
        console_handler
    )

    root_logger.addHandler(
        file_handler
    )

    root_logger.addHandler(
        error_file_handler
    )
    access_logger.addHandler(
        console_handler
    )

    access_logger.addHandler(
        file_handler
    )

    access_logger.setLevel(
        settings.log_level.upper()
    )
    audit_logger.addHandler(
        file_handler
    )

    audit_logger.setLevel(
        logging.INFO
    )

    audit_logger.propagate = False    
    access_logger.propagate = False
    logging.getLogger(
        "uvicorn.access"
    ).disabled = True
    logging.getLogger(
        "httpx"
    ).setLevel(logging.WARNING)

    logging.getLogger(
        "asyncio"
    ).setLevel(logging.WARNING)
    logging.getLogger(
        "sqlalchemy.engine"
    ).setLevel(
        logging.WARNING
    )

    root_logger.info(
        "Logging configured successfully",
        extra={
            "event": "logging_configured",
            "log_level": (
                settings.log_level.upper()
            ),
            "log_json": (
                settings.log_json
            ),
            "environment": (
                settings.environment
            ),
        },
    )