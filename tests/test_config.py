"""Settings contract.

The load-bearing assertions:

* credentials have no working default;
* a secret cannot reach a log line by way of a rendered settings object;
* the test environment consults no ``.env`` file, so the suite's outcome does not
  depend on the machine it runs on.
"""

from __future__ import annotations

import pytest
from pydantic import SecretStr

from gkp.core.config import Settings, default_env_file

SECRET = "sk-not-a-real-key-0123456789"

PROVIDER_VARS = (
    "GKP_LLM_PROVIDER",
    "GKP_LLM_BASE_URL",
    "GKP_LLM_MODEL",
    "GKP_LLM_API_KEY",
)


@pytest.fixture(autouse=True)
def _isolate_provider_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Belt and braces: even a stray export in the developer's shell is removed."""
    for name in PROVIDER_VARS:
        monkeypatch.delenv(name, raising=False)


def test_test_environment_reads_no_dotenv_file() -> None:
    """The mechanism that keeps the suite machine-independent."""
    assert Settings().env == "test"
    assert default_env_file() is None


def test_provider_credentials_have_no_defaults() -> None:
    settings = Settings()
    assert settings.llm_api_key is None
    assert settings.llm_base_url is None
    assert settings.llm_model is None
    assert settings.llm_configured is False


def test_api_key_cannot_be_rendered_from_a_settings_object() -> None:
    """``SecretStr`` keeps the key out of repr, and therefore out of logs."""
    settings = Settings(llm_api_key=SecretStr(SECRET))
    assert SECRET not in repr(settings)
    assert SECRET not in str(settings)

    assert settings.llm_api_key is not None
    assert settings.llm_api_key.get_secret_value() == SECRET


def test_llm_configured_requires_every_field() -> None:
    key = SecretStr(SECRET)
    assert Settings(llm_api_key=key, llm_model="m").llm_configured is False
    assert Settings(llm_api_key=key, llm_base_url="http://x").llm_configured is False
    assert Settings(llm_api_key=key, llm_model="m", llm_base_url="http://x").llm_configured is True


def test_environment_variable_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GKP_EMBEDDING_DIM", "1024")
    assert Settings().embedding_dim == 1024
