"""Shared test fixtures.

Two guarantees this file exists to provide:

1. The suite runs in the ``test`` environment before any :class:`Settings` is
   constructed, so a developer's local ``.env`` cannot change test behaviour.
2. Nothing in the default job needs a provider credential or a running service.
   Anything that does is marked ``integration``.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

# Must be set before gkp.core.config is imported anywhere.
os.environ["GKP_ENV"] = "test"
os.environ["GKP_DATABASE_URL"] = "postgresql+asyncpg://gkp:gkp@localhost:5434/gkp"
os.environ["GKP_REDIS_URL"] = "redis://localhost:6381/0"

# These imports deliberately follow the environment setup above.
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A fresh app per test, with the settings cache cleared either side."""
    from gkp.api.main import create_app
    from gkp.core.config import get_settings

    get_settings.cache_clear()
    with TestClient(create_app()) as test_client:
        yield test_client
    get_settings.cache_clear()
