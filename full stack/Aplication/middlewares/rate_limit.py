import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)


# Create global limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
)


async def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded,
) -> JSONResponse:
    """
    Global handler for rate limit exceeded errors.
    """

    client_ip = get_remote_address(request)

    logger.warning(
        f"[RATE_LIMIT_EXCEEDED] "
        f"ip={client_ip} "
        f"method={request.method} "
        f"path={request.url.path}"
    )

    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "message": "Too many requests. Please try again later.",
            "error": {
                "code": "RATE_LIMIT_EXCEEDED"
            }
        },
    )