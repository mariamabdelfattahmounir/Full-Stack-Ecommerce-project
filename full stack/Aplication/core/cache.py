import json
import logging
import time
from functools import lru_cache
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from app.core.cache_stats import cache_stats
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class BaseCacheService:
    def get_json(self, key: str) -> Any | None:
        raise NotImplementedError

    def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError

    def delete_many(self, keys: list[str]) -> None:
        raise NotImplementedError

    def delete_prefix(self, prefix: str) -> None:
        raise NotImplementedError

    def ping(self) -> bool:
        raise NotImplementedError


class NoOpCacheService(BaseCacheService):
    def get_json(self, key: str) -> Any | None:
        return None

    def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        return None

    def delete(self, key: str) -> None:
        return None

    def delete_many(self, keys: list[str]) -> None:
        return None

    def delete_prefix(self, prefix: str) -> None:
        return None

    def ping(self) -> bool:
        return False


class RedisCacheService(BaseCacheService):
    def __init__(self, redis_url: str) -> None:
        self.client = Redis.from_url(redis_url, decode_responses=True)

    def get_json(self, key: str) -> Any | None:
        start = time.perf_counter()

        try:
            value = self.client.get(key)
            duration_ms = (time.perf_counter() - start) * 1000

            if value is None:
                cache_stats.record_miss(key, duration_ms)
                return None

            cache_stats.record_hit(key, duration_ms)
            return json.loads(value)

        except (RedisError, json.JSONDecodeError) as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            cache_stats.record_miss(key, duration_ms)
            logger.warning(
                "Redis get_json failed",
                extra={
                    "event": "redis_get_failed",
                    "cache_key": key,
                    "error": str(exc),
                },
            )            
            return None

    def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        start = time.perf_counter()

        try:
            payload = json.dumps(value, default=str)
            self.client.setex(key, ttl_seconds, payload)
            duration_ms = (time.perf_counter() - start) * 1000
            cache_stats.record_set(key, duration_ms)

        except (RedisError, TypeError, ValueError) as exc:
            logger.warning(
                "Redis set_json failed",
                extra={
                    "event": "redis_set_failed",
                    "cache_key": key,
                    "error": str(exc),
                },
            )
    def delete(self, key: str) -> None:
        start = time.perf_counter()

        try:
            self.client.delete(key)
            duration_ms = (time.perf_counter() - start) * 1000
            cache_stats.record_invalidation(key, duration_ms)

        except RedisError as exc:
            logger.warning(
                "Redis delete failed",
                extra={
                    "event": "redis_delete_failed",
                    "cache_key": key,
                    "error": str(exc),
                },
            )
    def delete_many(self, keys: list[str]) -> None:
        if not keys:
            return

        start = time.perf_counter()

        try:
            self.client.delete(*keys)
            duration_ms = (time.perf_counter() - start) * 1000

            for key in keys:
                cache_stats.record_invalidation(key, duration_ms)

        except RedisError as exc:
            logger.warning(
                "Redis delete_many failed",
                extra={
                    "event": "redis_delete_many_failed",
                    "error": str(exc),
                },
            )
    def delete_prefix(self, prefix: str) -> None:
        start = time.perf_counter()

        try:
            keys = list(self.client.scan_iter(match=f"{prefix}*"))
            if keys:
                self.client.delete(*keys)

            duration_ms = (time.perf_counter() - start) * 1000
            cache_stats.record_invalidation(prefix, duration_ms)

        except RedisError as exc:
            logger.warning(
                "Redis delete_prefix failed",
                extra={
                    "event": "redis_delete_prefix_failed",
                    "prefix": prefix,
                    "error": str(exc),
                },
            )
    def ping(self) -> bool:
        try:
            return bool(self.client.ping())
        except RedisError:
            return False


@lru_cache
def get_cache_service() -> BaseCacheService:
    settings = get_settings()

    if not settings.redis_url:
        logger.warning(
            "Redis URL is not configured",
            extra={
                "event": "redis_not_configured",
            },
        )        
        return NoOpCacheService()

    try:
        service = RedisCacheService(settings.redis_url)

        if not service.ping():
            logger.warning("Redis ping failed. Falling back to NoOpCacheService.")
            return NoOpCacheService()

        logger.info(
            "Redis cache service initialized successfully",
            extra={
                "event": "redis_initialized",
            },
        )        
        return service

    except Exception as exc:
        logger.warning("Falling back to NoOpCacheService because Redis init failed: %s", exc)
        return NoOpCacheService()