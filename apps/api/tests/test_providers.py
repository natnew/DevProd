import json

import pytest

from devprod_api.config import Settings
from devprod_api.exceptions import ServiceUnavailableError
from devprod_api.providers import GradientWorkflowProvider


def _settings() -> Settings:
    return Settings(
        APP_BASE_URL="http://localhost:3000",
        API_BASE_URL="http://localhost:8000",
        DEMO_MODE=False,
        GRADIENT_API_BASE_URL="https://example.agents.do-ai.run",
        GRADIENT_AGENT_ID="unused-agent-id",
        GRADIENT_MODEL_ACCESS_KEY="secret",
    )


def test_parse_result_accepts_plain_json() -> None:
    payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "incident": {
                                "id": "inc-auth-001",
                                "title": "Checkout authentication failures after deployment",
                                "service": "checkout-api",
                                "severity": "critical",
                                "status": "open",
                                "summary": "Users receive repeated 401 responses after the latest checkout deployment.",
                                "startedAt": "2026-03-16T08:10:00Z",
                            },
                            "evidence": [],
                            "changes": [],
                            "knowledge": [],
                            "hypotheses": [],
                            "remediation": [],
                            "postmortem": {
                                "title": "Checkout authentication failures after deployment postmortem draft",
                                "impact": "Checkout authentication was unavailable.",
                                "rootCause": "AUTH_ISSUER points to staging.",
                                "followUps": ["Add production config validation."],
                            },
                            "trace": [],
                            "evaluationScore": 0,
                        }
                    )
                }
            }
        ]
    }

    result = GradientWorkflowProvider._parse_result(payload)

    assert result.incident.id == "inc-auth-001"
    assert result.postmortem.rootCause == "AUTH_ISSUER points to staging."


def test_parse_result_accepts_fenced_json() -> None:
    payload = {
        "choices": [
            {
                "message": {
                    "content": """```json
{"incident":{"id":"inc-auth-001","title":"t","service":"svc","severity":"critical","status":"open","summary":"s","startedAt":"2026-03-16T08:10:00Z"},"evidence":[],"changes":[],"knowledge":[],"hypotheses":[],"remediation":[],"postmortem":{"title":"p","impact":"i","rootCause":"r","followUps":["f"]},"trace":[],"evaluationScore":0}
```"""
                }
            }
        ]
    }

    result = GradientWorkflowProvider._parse_result(payload)

    assert result.postmortem.rootCause == "r"


def test_parse_result_rejects_non_json_content() -> None:
    payload = {"choices": [{"message": {"content": "not json"}}]}

    with pytest.raises(ServiceUnavailableError):
        GradientWorkflowProvider._parse_result(payload)


def test_readiness_requires_only_live_endpoint_and_key() -> None:
    settings = _settings()
    settings.gradient_agent_id = None

    status, detail = GradientWorkflowProvider(settings=settings).readiness()

    assert status == "pass"
    assert "configuration is present" in detail
