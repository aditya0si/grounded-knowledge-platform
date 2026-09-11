"""Liveness and readiness.

These answer two different questions and are deliberately separate:

* ``/health``      — "is this process alive?"  Never touches a downstream
  service, so it cannot fail for a reason the process cannot control.
* ``/health/ready`` — "should this instance receive traffic?"  Allowed to fail.
  A 503 here is correct behaviour, not an outage, and the body names the
  component that failed so the failure is diagnosable from the response alone.
"""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from gkp.core.config import get_settings
from gkp.core.redis import check_redis
from gkp.db.session import check_database

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
async def liveness() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "version": settings.version, "env": settings.env}


@router.get("/health/ready", summary="Readiness probe")
async def readiness(response: Response) -> dict[str, object]:
    settings = get_settings()
    db_ok, db_err = await check_database(settings)
    redis_ok, redis_err = await check_redis(settings)

    ready = db_ok and redis_ok
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if ready else "not_ready",
        "components": {
            "database": {"ok": db_ok, "error": db_err},
            "redis": {"ok": redis_ok, "error": redis_err},
        },
    }
