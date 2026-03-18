import json
import shutil
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

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
def clear_state(monkeypatch: pytest.MonkeyPatch) -> None:
    history_path = ROOT / "apps" / "api" / f"test-history-{uuid4()}.sqlite3"
    intake_root = ROOT / "arena" / "intake"
    if intake_root.exists():
        for path in intake_root.iterdir():
            if path.is_dir():
                shutil.rmtree(path)
    monkeypatch.setenv("DEVPROD_RUN_HISTORY_DB_PATH", str(history_path))
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


def test_readiness(client: TestClient) -> None:
    response = client.get("/readiness")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert {check["name"] for check in body["checks"]} == {"provider", "run-history", "mode"}


def test_list_incidents_contract(client: TestClient) -> None:
    response = client.get("/v1/incidents")
    assert response.status_code == 200
    _validate_schema("incident-list-response.schema.json", response.json())
    ids = [incident["id"] for incident in response.json()["incidents"]]
    assert ids == [
        "deployment-breaks-auth-flow",
        "latency-spike-after-cache-config-change",
        "queue-workers-fail-after-dependency-upgrade",
    ]


def test_get_incident_detail_contract(client: TestClient) -> None:
    response = client.get("/v1/incidents/deployment-breaks-auth-flow")
    assert response.status_code == 200
    _validate_schema("incident-detail.schema.json", response.json())
    assert response.json()["timeline"]


def test_incident_intake_contract(client: TestClient) -> None:
    response = client.post(
        "/v1/incidents",
        json={
            "title": "Checkout login degraded after release",
            "service": "checkout-api",
            "severity": "high",
            "summary": "Synthetic intake for local API testing."
        },
    )
    assert response.status_code == 200
    _validate_schema("incident-intake-response.schema.json", response.json())
    assert response.json()["incident"]["status"] == "open"


def test_not_found_is_masked_domain_error(client: TestClient) -> None:
    response = client.get("/v1/incidents/missing")
    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Incident 'missing' was not found."}
    }


def test_run_investigation_and_step_endpoints(client: TestClient) -> None:
    response = client.post("/v1/investigations", json={"incidentId": "deployment-breaks-auth-flow"})
    assert response.status_code == 200
    _validate_schema("investigation-run-response.schema.json", response.json())
    run_id = response.json()["run"]["id"]
    assert response.json()["result"]["evaluationScore"] >= 90

    run_response = client.get(f"/v1/investigations/{run_id}")
    assert run_response.status_code == 200
    _validate_schema("investigation-run-response.schema.json", run_response.json())

    retrieval_response = client.get(f"/v1/investigations/{run_id}/retrieval")
    assert retrieval_response.status_code == 200
    _validate_schema("retrieval-response.schema.json", retrieval_response.json())
    assert retrieval_response.json()["retrieval"]["documents"]

    hypothesis_response = client.get(f"/v1/investigations/{run_id}/hypotheses")
    assert hypothesis_response.status_code == 200
    _validate_schema("hypothesis-response.schema.json", hypothesis_response.json())
    assert hypothesis_response.json()["hypothesis"]["topHypothesis"]["statement"]

    remediation_response = client.get(f"/v1/investigations/{run_id}/remediation")
    assert remediation_response.status_code == 200
    _validate_schema("remediation-response.schema.json", remediation_response.json())
    assert remediation_response.json()["remediation"]["requiresReview"] is True

    postmortem_response = client.get(f"/v1/investigations/{run_id}/postmortem")
    assert postmortem_response.status_code == 200
    _validate_schema("postmortem-response.schema.json", postmortem_response.json())


def test_recent_runs_persist_after_investigation(client: TestClient) -> None:
    run_response = client.post("/v1/investigations", json={"incidentId": "deployment-breaks-auth-flow"})
    assert run_response.status_code == 200

    history_response = client.get("/v1/investigations/runs")
    assert history_response.status_code == 200
    body = history_response.json()
    assert len(body["runs"]) == 1
    assert body["runs"][0]["incidentId"] == "deployment-breaks-auth-flow"
    assert body["runs"][0]["providerMode"] == "demo"


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


def test_runtime_config_includes_provider_mode(client: TestClient) -> None:
    response = client.get("/v1/config")
    assert response.status_code == 200
    assert response.json()["providerMode"] == "demo"


def _validate_schema(schema_name: str, payload: dict[str, object]) -> None:
    registry = Registry()
    for schema_path in SCHEMA_ROOT.glob("*.json"):
        with schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))

    with (SCHEMA_ROOT / schema_name).open("r", encoding="utf-8") as handle:
        schema = json.load(handle)

    validator = Draft202012Validator(
        schema,
        registry=registry,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    validator.validate(payload)
