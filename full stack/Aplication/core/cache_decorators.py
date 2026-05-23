import functools
import hashlib
import json
import logging

import os


from collections.abc import Callable
from typing import Any

from fastapi.encoders import jsonable_encoder

from app.core.cache import (
    BaseCacheService,
    get_cache_service,
)

logger = logging.getLogger(__name__)

def _normalize_cache_value(
    value: Any,
) -> Any:
    if isinstance(
        value,
        (str, int, float, bool, type(None)),
    ):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "__dict__"):
        return str(value)

    return value

def _build_cache_key(
    prefix: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """
    Generate unique cache key
    based on function arguments.
    """

    serialized = json.dumps(
        {
            "args": [
                _normalize_cache_value(arg)
                for arg in args[1:]
            ],            
            "kwargs": {
                key: _normalize_cache_value(value)
                for key, value in kwargs.items()
            },
        },
        sort_keys=True,
        default=str,
    )

    hashed = hashlib.sha256(
        serialized.encode()
    ).hexdigest()

    return f"{prefix}:{hashed}"


def cache_response(
    *,
    prefix: str,
    ttl_seconds: int = 300,
    cache_service: (
        BaseCacheService | None
    ) = None,
) -> Callable:
    """
    Decorator for caching service responses.

    Features:
    - Automatic cache key generation
    - JSON serialization
    - Redis integration
    - Cache-aside pattern
    - Logging support
    """

    cache = (
        cache_service
        or get_cache_service()
    )

    def decorator(
        func: Callable,
    ) -> Callable:

        @functools.wraps(func)
        def wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            if os.getenv("APP_ENV") == "test":
                return func(*args, **kwargs)
            
            cache_key = (
                _build_cache_key(
                    prefix=prefix,
                    args=args,
                    kwargs=kwargs,
                )
            )

            cached_data = (
                cache.get_json(cache_key)
            )

            if cached_data is not None:

                logger.info(
                    "Cache hit",
                    extra={
                        "cache_key": cache_key,
                        "function": func.__name__,
                    },
                )

                return_type = func.__annotations__.get("return")

                try:
                    if return_type:

                        origin = getattr(return_type, "__origin__", None)
                        args_types = getattr(return_type, "__args__", [])

                        # Handle list[Model]
                        if origin is list and args_types:
                            model_class = args_types[0]

                            if hasattr(model_class, "model_validate"):
                                return [
                                    model_class.model_validate(item)
                                    for item in cached_data
                                ]

                        # Handle single model
                        if hasattr(return_type, "model_validate"):
                            return return_type.model_validate(cached_data)

                except Exception:
                    logger.exception(
                        "Failed to rebuild cached response"
                    )

                return cached_data

            logger.info(
                "Cache miss",
                extra={
                    "cache_key": cache_key,
                    "function": func.__name__,
                    "ttl_seconds": ttl_seconds,
                },
            )

            result = func(
                *args,
                **kwargs,
            )

            cache.set_json(
                cache_key,
                jsonable_encoder(result),
                ttl_seconds=ttl_seconds,
            )

            logger.info(
                "Response cached successfully",
                extra={
                    "cache_key": cache_key,
                    "ttl_seconds": ttl_seconds,
                    "function": func.__name__,
                },
            )

            return result

        return wrapper

    return decorator


def invalidate_cache(
    *,
    prefix: str,
    cache_service: (
        BaseCacheService | None
    ) = None,
) -> Callable:
    """
    Decorator for cache invalidation.

    Used after:
    - create
    - update
    - delete
    operations.
    """

    cache = (
        cache_service
        or get_cache_service()
    )

    def decorator(
        func: Callable,
    ) -> Callable:

        @functools.wraps(func)
        def wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> Any:

            result = func(
                *args,
                **kwargs,
            )

            cache.delete_prefix(prefix)

            logger.info(
                "Cache invalidated",
                extra={
                    "prefix": prefix,
                    "function": func.__name__,
                },
            )

            return result

        return wrapper

    return decorator