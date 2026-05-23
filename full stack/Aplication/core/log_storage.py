import time
from collections import deque
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Deque, Dict, Optional


@dataclass
class RequestLogEntry:
    request_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    client_ip: str
    timestamp: float
    user_id: Optional[str] = None
    error_message: Optional[str] = None
    query_params: Optional[str] = None


class LogStorage:
    _instance: Optional["LogStorage"] = None
    _lock = Lock()

    def __new__(cls, max_entries: int = 5000):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
                cls._instance._max_entries = max_entries
            return cls._instance

    def __init__(self, max_entries: int = 5000):
        if self._initialized:
            return

        self._initialized = True
        self._max_entries = max_entries
        self._logs: Deque[RequestLogEntry] = deque(maxlen=max_entries)
        self._operation_lock = Lock()

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._instance = None

    def add_log(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: str,
        user_id: Optional[str] = None,
        error_message: Optional[str] = None,
        query_params: Optional[str] = None,
    ) -> None:
        entry = RequestLogEntry(
            request_id=request_id,
            method=method.upper(),
            path=path,
            status_code=status_code,
            duration_ms=round(float(duration_ms), 2),
            client_ip=client_ip,
            timestamp=time.time(),
            user_id=user_id,
            error_message=error_message,
            query_params=query_params,
        )

        with self._operation_lock:
            self._logs.append(entry)

    def get_logs(
        self,
        limit: int = 50,
        offset: int = 0,
        method: Optional[str] = None,
        path_prefix: Optional[str] = None,
        status_code_min: Optional[int] = None,
        status_code_max: Optional[int] = None,
        user_id: Optional[str] = None,
        since: Optional[float] = None,
    ) -> Dict:
        with self._operation_lock:
            logs = list(self._logs)

        filtered = logs

        if method:
            filtered = [entry for entry in filtered if entry.method == method.upper()]

        if path_prefix:
            filtered = [entry for entry in filtered if entry.path.startswith(path_prefix)]

        if status_code_min is not None:
            filtered = [entry for entry in filtered if entry.status_code >= status_code_min]

        if status_code_max is not None:
            filtered = [entry for entry in filtered if entry.status_code <= status_code_max]

        if user_id:
            filtered = [entry for entry in filtered if entry.user_id == user_id]

        if since is not None:
            filtered = [entry for entry in filtered if entry.timestamp >= since]

        filtered.sort(key=lambda entry: entry.timestamp, reverse=True)

        total = len(filtered)
        entries = filtered[offset : offset + limit]

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "entries": [asdict(entry) for entry in entries],
        }

    def get_error_logs(self, limit: int = 50) -> Dict:
        return self.get_logs(
            limit=limit,
            status_code_min=400,
        )

    def get_slow_requests(
        self,
        threshold_ms: float = 1000,
        limit: int = 50,
    ) -> Dict:
        with self._operation_lock:
            logs = list(self._logs)

        slow_requests = [entry for entry in logs if entry.duration_ms >= threshold_ms]
        slow_requests.sort(key=lambda entry: entry.duration_ms, reverse=True)

        entries = slow_requests[:limit]

        return {
            "total": len(slow_requests),
            "threshold_ms": threshold_ms,
            "limit": limit,
            "entries": [asdict(entry) for entry in entries],
        }

    def get_summary(self) -> Dict:
        with self._operation_lock:
            logs = list(self._logs)

        if not logs:
            return {
                "total_requests": 0,
                "avg_duration_ms": 0,
                "max_duration_ms": 0,
                "min_duration_ms": 0,
                "error_count": 0,
                "error_rate": 0.0,
                "methods": {},
                "status_codes": {},
                "top_paths": {},
            }

        durations = [entry.duration_ms for entry in logs]
        errors = [entry for entry in logs if entry.status_code >= 400]

        methods: Dict[str, int] = {}
        status_codes: Dict[str, int] = {}
        top_paths: Dict[str, int] = {}

        for entry in logs:
            methods[entry.method] = methods.get(entry.method, 0) + 1

            status_family = f"{entry.status_code // 100}xx"
            status_codes[status_family] = status_codes.get(status_family, 0) + 1

            top_paths[entry.path] = top_paths.get(entry.path, 0) + 1

        top_paths = dict(
            sorted(
                top_paths.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:10]
        )

        return {
            "total_requests": len(logs),
            "avg_duration_ms": round(sum(durations) / len(durations), 2),
            "max_duration_ms": round(max(durations), 2),
            "min_duration_ms": round(min(durations), 2),
            "error_count": len(errors),
            "error_rate": round((len(errors) / len(logs)) * 100, 2),
            "methods": methods,
            "status_codes": status_codes,
            "top_paths": top_paths,
        }

    def clear(self) -> None:
        with self._operation_lock:
            self._logs.clear()


log_storage = LogStorage()