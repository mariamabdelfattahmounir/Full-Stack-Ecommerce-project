import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional

@dataclass
class CacheOperationRecord:
    operation: str
    key: str
    timestamp: float
    duration_ms: float
    source: str


@dataclass
class CacheStatsSnapshot:
    total_hits: int = 0
    total_misses: int = 0
    total_sets: int = 0
    total_invalidations: int = 0
    hit_ratio: float = 0.0
    avg_cache_latency_ms: float = 0.0
    avg_db_latency_ms: float = 0.0
    latency_improvement_pct: float = 0.0
    operations_by_source: Dict[str, int] = field(default_factory=dict)
    operations_by_key_prefix: Dict[str, int] = field(default_factory=dict)
    recent_operations: List[Dict] = field(default_factory=list)


class CacheStatsTracker:
    _instance: Optional["CacheStatsTracker"] = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._hits: Dict[str, int] = defaultdict(int)
        self._misses: Dict[str, int] = defaultdict(int)
        self._sets: Dict[str, int] = defaultdict(int)
        self._invalidations: Dict[str, int] = defaultdict(int)
        self._cache_latencies: List[float] = []
        self._db_latencies: List[float] = []
        self._recent_operations: List[CacheOperationRecord] = []
        self._max_recent = 200
        self._operation_lock = Lock()

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._instance = None

    def record_hit(self, key: str, duration_ms: float) -> None:
        prefix = self._get_prefix(key)

        with self._operation_lock:
            self._hits[prefix] += 1
            self._cache_latencies.append(duration_ms)
            self._add_recent("hit", key, duration_ms, "cache")
            self._trim_latencies()
            logger.debug(
                "Cache hit recorded",
                extra={
                    "event": "cache_hit_recorded",
                    "key": key,
                    "duration_ms": duration_ms,
                },
            )  
    def record_miss(self, key: str, duration_ms: float) -> None:
        prefix = self._get_prefix(key)

        with self._operation_lock:
            self._misses[prefix] += 1
            self._db_latencies.append(duration_ms)
            self._add_recent("miss", key, duration_ms, "database")
            self._trim_latencies()
            logger.debug(
                "Cache miss recorded",
                extra={
                    "event": "cache_miss_recorded",
                    "key": key,
                    "duration_ms": duration_ms,
                },
            )
    def record_set(self, key: str, duration_ms: float) -> None:
        prefix = self._get_prefix(key)

        with self._operation_lock:
            self._sets[prefix] += 1
            self._add_recent("set", key, duration_ms, "cache")
            logger.debug(
                "Cache set recorded",
                extra={
                    "event": "cache_set_recorded",
                    "key": key,
                    "duration_ms": duration_ms,
                },
            )
    def record_invalidation(self, key: str, duration_ms: float) -> None:
        prefix = self._get_prefix(key)

        with self._operation_lock:
            self._invalidations[prefix] += 1
            self._add_recent("invalidate", key, duration_ms, "cache")
            logger.debug(
                "Cache invalidation recorded",
                extra={
                    "event": "cache_invalidation_recorded",
                    "key": key,
                    "duration_ms": duration_ms,
                },
            )
    def get_snapshot(self) -> CacheStatsSnapshot:
        with self._operation_lock:
            total_hits = sum(self._hits.values())
            total_misses = sum(self._misses.values())
            total_sets = sum(self._sets.values())
            total_invalidations = sum(self._invalidations.values())
            total_requests = total_hits + total_misses

            hit_ratio = (total_hits / total_requests * 100) if total_requests > 0 else 0.0

            avg_cache = (
                sum(self._cache_latencies) / len(self._cache_latencies)
                if self._cache_latencies
                else 0.0
            )

            avg_db = (
                sum(self._db_latencies) / len(self._db_latencies)
                if self._db_latencies
                else 0.0
            )

            improvement = ((avg_db - avg_cache) / avg_db * 100) if avg_db > 0 and avg_cache > 0 else 0.0

            ops_by_source = {
                "cache": total_hits + total_sets + total_invalidations,
                "database": total_misses,
            }

            ops_by_prefix: Dict[str, int] = defaultdict(int)

            for source in (self._hits, self._misses, self._sets, self._invalidations):
                for prefix, count in source.items():
                    ops_by_prefix[prefix] += count

            recent = [
                {
                    "operation": record.operation,
                    "key": record.key,
                    "timestamp": record.timestamp,
                    "duration_ms": round(record.duration_ms, 3),
                    "source": record.source,
                }
                for record in self._recent_operations[-50:]
            ]

            return CacheStatsSnapshot(
                total_hits=total_hits,
                total_misses=total_misses,
                total_sets=total_sets,
                total_invalidations=total_invalidations,
                hit_ratio=round(hit_ratio, 2),
                avg_cache_latency_ms=round(avg_cache, 3),
                avg_db_latency_ms=round(avg_db, 3),
                latency_improvement_pct=round(improvement, 2),
                operations_by_source=ops_by_source,
                operations_by_key_prefix=dict(ops_by_prefix),
                recent_operations=list(reversed(recent)),
            )

    def clear(self) -> None:
        with self._operation_lock:
            self._hits.clear()
            self._misses.clear()
            self._sets.clear()
            self._invalidations.clear()
            self._cache_latencies.clear()
            self._db_latencies.clear()
            self._recent_operations.clear()

    def _add_recent(self, operation: str, key: str, duration_ms: float, source: str) -> None:
        self._recent_operations.append(
            CacheOperationRecord(
                operation=operation,
                key=key,
                timestamp=time.time(),
                duration_ms=duration_ms,
                source=source,
            )
        )

        if len(self._recent_operations) > self._max_recent:
            self._recent_operations = self._recent_operations[-self._max_recent :]

    def _trim_latencies(self) -> None:
        if len(self._cache_latencies) > 1000:
            self._cache_latencies = self._cache_latencies[-500:]

        if len(self._db_latencies) > 1000:
            self._db_latencies = self._db_latencies[-500:]

    @staticmethod
    def _get_prefix(key: str) -> str:
        parts = key.split(":")
        return ":".join(parts[:2]) if len(parts) >= 2 else key


logger = logging.getLogger(__name__)

cache_stats = CacheStatsTracker()