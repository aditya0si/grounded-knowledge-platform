"""Structured logging.

JSON in production (machine-parseable, one object per line), human-readable in
development. Request-scoped context is carried via structlog contextvars so a
request ID survives across the API, the retrieval layer, and the worker.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from gkp.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure stdlib logging and structlog. Idempotent."""
    level = logging.DEBUG if settings.debug else logging.INFO

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level, force=True)
    # These are chatty at INFO and drown out application events.
    for noisy in ("sqlalchemy.engine", "httpx", "httpcore", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    renderer: Any = (
        structlog.processors.JSONRenderer()
        if settings.env == "prod"
        else structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty())
    )
    processors.append(renderer)

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Return a bound logger. Typed loosely because structlog's proxy is dynamic."""
    return structlog.get_logger(name)
