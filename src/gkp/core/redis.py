"""Redis client and readiness probe.

Redis backs rate limiting, caching, and the ingestion queue (M4). None of those
are on the M0-M2 critical path, so an absent Redis degrades readiness rather than
blocking retrieval evaluation.
"""

from __future__ import annotations

import asyncio

from redis.asyncio import Redis

from gkp.core.config import Settings

_client: Redis | None = None


def get_redis(settings: Settings) -> Redis:
    global _client  # noqa: PLW0603 - process-wide client, intentionally a singleton
    if _client is None:
        _client = Redis.from_url(settings.redis_url, decode_responses=True)
    return _client


async def check_redis(settings: Settings) -> tuple[bool, str | None]:
    """Probe Redis. Returns ``(ok, error)`` and never raises."""
    try:
        async with asyncio.timeout(settings.redis_connect_timeout_s):
            await get_redis(settings).ping()
    except Exception as exc:  # noqa: BLE001 - any failure is a readiness failure
        return False, f"{type(exc).__name__}: {exc}"[:300]
    return True, None


async def close_redis() -> None:
    """Release the connection pool on shutdown."""
    global _client  # noqa: PLW0603
    if _client is not None:
        await _client.aclose()
    _client = None
