import logging
logger = logging.getLogger(__name__)
from prometheus_client import Counter, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "Total count of HTTP requests by method, endpoint, and status",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

http_errors_total = Counter(
    "http_errors_total",
    "Total count of HTTP errors by method, endpoint, and status",
    ["method", "endpoint", "status_code"],
)


def _safe_int(value: float) -> int:
    return int(value or 0)


def record_request_metrics(
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float,
) -> None:
    status_text = str(status_code)
    method_text = method.upper()

    http_requests_total.labels(
        method=method_text,
        endpoint=endpoint,
        status_code=status_text,
    ).inc()

    http_request_duration_seconds.labels(
        method=method_text,
        endpoint=endpoint,
    ).observe(duration_ms / 1000.0)

    if status_code >= 500:
        http_errors_total.labels(
            method=method_text,
            endpoint=endpoint,
            status_code=status_text,
        ).inc()


def get_error_rate() -> dict:
    try:
        total_requests = 0
        total_errors = 0

        for metric in http_requests_total.collect():
            for sample in metric.samples:
                if sample.name.endswith("_total"):
                    total_requests += _safe_int(sample.value)

        for metric in http_errors_total.collect():
            for sample in metric.samples:
                if sample.name.endswith("_total"):
                    total_errors += _safe_int(sample.value)

        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0

        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate_pct": round(error_rate, 2),
        }

    except Exception as exc:
        logger.exception(
            "Failed to calculate metrics",
        )        
        return {
            "total_requests": 0,
            "total_errors": 0,
            "error_rate_pct": 0.0,
            "error": str(exc),
        }


def get_request_count_by_status() -> dict:
    try:
        status_counts: dict[str, int] = {}

        for metric in http_requests_total.collect():
            for sample in metric.samples:
                if not sample.name.endswith("_total"):
                    continue

                status_code = sample.labels.get("status_code", "0")
                family = f"{status_code[0]}xx"
                status_counts[family] = status_counts.get(family, 0) + _safe_int(sample.value)

        return status_counts

    except Exception as exc:
        logger.exception(
            "Failed to calculate metrics",
        )        
        return {"error": str(exc)}