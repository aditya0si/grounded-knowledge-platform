"""Postgres engine, session factory, and readiness probe.

The engine is created lazily and connectionless: constructing it never fails, so
an unreachable database surfaces at readiness or first query rather than at
import time.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from gkp.core.config import Settings

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine(settings: Settings) -> AsyncEngine:
    global _engine  # noqa: PLW0603 - process-wide pool, intentionally a singleton
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            pool_size=5,
            max_overflow=5,
            pool_pre_ping=True,
            echo=False,
        )
    return _engine


def get_sessionmaker(settings: Settings) -> async_sessionmaker[AsyncSession]:
    global _sessionmaker  # noqa: PLW0603
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            get_engine(settings),
            expire_on_commit=False,
            autoflush=False,
        )
    return _sessionmaker


@asynccontextmanager
async def session_scope(settings: Settings) -> AsyncIterator[AsyncSession]:
    """Transactional session scope: commit on success, roll back on error."""
    factory = get_sessionmaker(settings)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_database(settings: Settings) -> tuple[bool, str | None]:
    """Probe the database.

    Returns ``(ok, error)`` and never raises: readiness reports failures, it does
    not propagate them.
    """
    try:
        async with asyncio.timeout(settings.db_connect_timeout_s):
            engine = get_engine(settings)
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - any failure is a readiness failure
        return False, f"{type(exc).__name__}: {exc}"[:300]
    return True, None


async def dispose_engine() -> None:
    """Close pooled connections on shutdown."""
    global _engine, _sessionmaker  # noqa: PLW0603
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _sessionmaker = None
