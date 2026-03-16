from collections import defaultdict, deque
from time import time

from fastapi import Request

from devprod_api.config import Settings
from devprod_api.exceptions import RateLimitError, UnauthorizedError


class RateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, limit_per_minute: int) -> None:
        now = time()
        bucket = self._buckets[key]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= limit_per_minute:
            raise RateLimitError("Too many requests. Retry later.")
        bucket.append(now)


rate_limiter = RateLimiter()


def resolve_client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def enforce_request_controls(
    request: Request,
    settings: Settings,
    x_api_key: str | None = None,
) -> None:
    rate_limiter.check(resolve_client_key(request), settings.devprod_rate_limit_per_minute)
    if not settings.devprod_enable_auth:
        return
    if x_api_key != settings.devprod_api_key:
        raise UnauthorizedError("Missing or invalid API key.")
