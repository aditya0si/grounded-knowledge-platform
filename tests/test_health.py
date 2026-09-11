"""Health endpoint contract.

The property under test is not "health returns 200" — it is that liveness is
independent of infrastructure and readiness *degrades* rather than raising.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_liveness_is_ok_with_nothing_running(client: TestClient) -> None:
    """Liveness must not depend on Postgres or Redis."""
    response = client.get("/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["env"] == "test"
    assert body["version"]


def test_readiness_degrades_and_names_the_failed_component(client: TestClient) -> None:
    """503 is valid; so is 200. What must hold is shape and diagnosability."""
    response = client.get("/health/ready")
    assert response.status_code in (200, 503)

    body = response.json()
    assert set(body["components"]) == {"database", "redis"}

    if response.status_code == 503:
        assert body["status"] == "not_ready"
        failed = [name for name, comp in body["components"].items() if not comp["ok"]]
        assert failed, "a 503 response must name at least one failed component"
        for name in failed:
            assert body["components"][name]["error"], f"{name} failed without an error string"
    else:
        assert body["status"] == "ready"


def test_both_health_routes_are_documented_in_openapi(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/health" in schema["paths"]
    assert "/health/ready" in schema["paths"]
