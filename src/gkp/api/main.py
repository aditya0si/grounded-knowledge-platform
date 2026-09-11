"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from gkp.api.health import router as health_router
from gkp.core.config import get_settings
from gkp.core.logging import configure_logging, get_logger
from gkp.core.redis import close_redis
from gkp.db.session import dispose_engine

DESCRIPTION = """
ACL-enforced hybrid retrieval over an internal-docs corpus.

Retrieval quality is measured against gold chunk labels and gated in CI;
permission boundaries are enforced inside the retrieval predicate rather than
filtered after the fact.
"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    log = get_logger(__name__)
    settings = get_settings()
    log.info("startup", env=settings.env, version=settings.version)
    try:
        yield
    finally:
        await close_redis()
        await dispose_engine()
        log.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title="Grounded Knowledge Platform",
        description=DESCRIPTION,
        version=settings.version,
        lifespan=lifespan,
    )
    app.include_router(health_router)
    return app


app = create_app()
