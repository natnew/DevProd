import json
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from devprod_api.config import get_settings
from devprod_api.main import app
from devprod_api.security import rate_limiter


ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = ROOT / "packages" / "contracts" / "schemas"


@pytest.fixture(autouse=True)
def clear_state() -> None:
    get_settings.cache_clear()
    rate_limiter._buckets.clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_incidents_contract(client: TestClient) -> None:
    response = client.get("/v1/incidents")
    assert response.status_code == 200
    _validate_schema("incident-list-response.schema.json", response.json())


def test_get_incident(client: TestClient) -> None:
    response = client.get("/v1/incidents/inc-auth-001")
    assert response.status_code == 200
    assert response.json()["timeline"]


def test_not_found_is_masked_domain_error(client: TestClient) -> None:
    response = client.get("/v1/incidents/missing")
    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Incident 'missing' was not found."}
    }


def test_run_investigation_contract(client: TestClient) -> None:
    response = client.post("/v1/investigations", json={"incidentId": "inc-auth-001"})
    assert response.status_code == 200
    _validate_schema("investigation-result.schema.json", response.json())
    assert response.json()["evaluationScore"] == 100


def test_requires_api_key_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEVPROD_ENABLE_AUTH", "true")
    monkeypatch.setenv("DEVPROD_API_KEY", "secret")
    get_settings.cache_clear()

    with TestClient(app) as client:
        response = client.get("/v1/incidents")
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "unauthorized"


def test_rate_limit_returns_retry_after(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEVPROD_RATE_LIMIT_PER_MINUTE", "1")
    get_settings.cache_clear()

    with TestClient(app) as client:
        first = client.get("/v1/incidents")
        second = client.get("/v1/incidents")
    assert first.status_code == 200
    assert second.status_code == 429
    assert second.headers["Retry-After"] == "60"


def _validate_schema(schema_name: str, payload: dict[str, object]) -> None:
    with (SCHEMA_ROOT / schema_name).open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    with (SCHEMA_ROOT / "incident-summary.schema.json").open("r", encoding="utf-8") as handle:
        incident_summary = json.load(handle)
    registry = Registry().with_resource(
        incident_summary["$id"],
        Resource.from_contents(incident_summary),
    )
    validator = Draft202012Validator(
        schema,
        registry=registry,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    validator.validate(payload)
