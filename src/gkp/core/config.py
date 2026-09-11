"""Application settings.

Design rules:

* **No credential has a usable default.** The test suite must pass with every
  provider variable unset *and* must not break when one is present, which is why
  the test environment consults no ``.env`` file at all.
* **Missing infrastructure is reported, not fatal.** A process that refuses to
  boot cannot tell you why it refused to boot. Readiness reports component
  status instead (see ``gkp.api.health``).
* **Secrets are ``SecretStr``.** They are excluded from ``repr`` and therefore
  from log lines that render a settings object. A `str` field would leak the key
  into any traceback or structured log that includes the settings object.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

Env = Literal["dev", "test", "prod"]


def default_env_file() -> str | None:
    """Return the dotenv file to load, or ``None`` in the test environment.

    A developer's local ``.env`` must not be able to change test outcomes: a
    suite whose results depend on the machine it runs on is not a suite. In dev
    and prod the file is loaded as usual.

    Resolved once at import. ``GKP_ENV`` must therefore be set before this module
    is imported, which ``tests/conftest.py`` guarantees.
    """
    return None if os.environ.get("GKP_ENV", "dev") == "test" else ".env"


class Settings(BaseSettings):
    """Environment-backed configuration, prefixed ``GKP_``."""

    model_config = SettingsConfigDict(
        env_file=default_env_file(),
        env_file_encoding="utf-8",
        env_prefix="GKP_",
        extra="ignore",
        case_sensitive=False,
    )

    # -- runtime ------------------------------------------------------------
    env: Env = "dev"
    debug: bool = False
    version: str = "0.1.0"

    # -- infrastructure -----------------------------------------------------
    database_url: str = "postgresql+asyncpg://gkp:gkp@localhost:5434/gkp"
    redis_url: str = "redis://localhost:6381/0"
    db_connect_timeout_s: float = 3.0
    redis_connect_timeout_s: float = 3.0

    # -- retrieval ----------------------------------------------------------
    # bge-small (384 dims) is the starting point: it is an ONNX model with no
    # torch dependency, so the whole retrieval stack installs and runs on a
    # laptop and in CI without a multi-gigabyte download. Larger models are an
    # M3 ablation, not an assumption.
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384
    #: Where the embedding model is cached. Unset means the library's default
    #: (a temp directory), which re-downloads after any temp cleanup. Setting it
    #: makes the cache cacheable in CI and stable across runs.
    embedding_cache_dir: str | None = None
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # -- generation (optional) ----------------------------------------------
    # Absent by design. Retrieval evaluation (M1/M2) makes no LLM calls, so the
    # entire measured-retrieval story is reproducible without spend.
    llm_provider: str | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None
    llm_api_key: SecretStr | None = None

    @property
    def llm_configured(self) -> bool:
        """True only when every field a generation call needs is present."""
        return bool(self.llm_base_url and self.llm_model and self.llm_api_key)

    @property
    def is_test(self) -> bool:
        return self.env == "test"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor. Call ``get_settings.cache_clear()`` in tests."""
    return Settings()
