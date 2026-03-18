from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol, cast

import httpx

from devprod_api.config import Settings
from devprod_api.exceptions import ServiceUnavailableError
from devprod_api.knowledge import KnowledgeRepository
from devprod_api.models import (
    CorrelatedChange,
    EvidenceItem,
    Hypothesis,
    IncidentSummary,
    InvestigationResult,
    PostmortemSummary,
    RemediationStep,
    WorkflowTraceStep,
)
from devprod_api.repository import IncidentRepository


class WorkflowProvider(Protocol):
    provider_mode: str

    def run(self, incident_payload: dict[str, Any]) -> InvestigationResult:
        ...

    def readiness(self) -> tuple[str, str]:
        ...


@dataclass
class DemoWorkflowProvider:
    knowledge_repository: KnowledgeRepository
    provider_mode: str = "demo"

    def run(self, incident_payload: dict[str, Any]) -> InvestigationResult:
        incident = IncidentSummary(**IncidentRepository._to_summary(incident_payload))
        evidence = [EvidenceItem(**item) for item in incident_payload["evidence"]]
        changes = [CorrelatedChange(**item) for item in incident_payload["changes"]]
        knowledge = self.knowledge_repository.list_for_incident()
        hypotheses = [
            Hypothesis(
                id="hyp-1",
                statement=incident_payload["expectedOutcome"]["rootCause"],
                confidence=0.93,
                rationale=(
                    "Deployment timing, issuer mismatch logs, and the config change all point to "
                    "a production issuer misconfiguration."
                ),
                supportingEvidenceIds=["ev-1", "ev-2", "ev-3"],
            )
        ]
        remediation = [
            RemediationStep(
                id="rem-1",
                action="Rollback or correct the AUTH_ISSUER configuration in production.",
                owner="incident commander",
                priority="immediate",
            ),
            RemediationStep(
                id="rem-2",
                action="Add token issuer validation against production after config changes.",
                owner="platform team",
                priority="follow-up",
            ),
        ]
        postmortem = PostmortemSummary(
            title=f"{incident.title} postmortem draft",
            impact="Checkout authentication failed for customers during the incident window.",
            rootCause=incident_payload["expectedOutcome"]["rootCause"],
            followUps=[
                "Add deployment validation for production auth issuer values.",
                "Require config diff review before checkout releases.",
            ],
        )
        trace = [
            WorkflowTraceStep(agent="triage", status="completed", summary="Classified incident as critical auth outage."),
            WorkflowTraceStep(agent="evidence", status="completed", summary="Structured alert, log, and metric evidence."),
            WorkflowTraceStep(agent="change-correlation", status="completed", summary="Matched auth issue to deploy and config drift."),
            WorkflowTraceStep(agent="retrieval", status="completed", summary="Retrieved runbook and prior incident knowledge."),
            WorkflowTraceStep(agent="hypothesis", status="completed", summary="Ranked issuer mismatch as primary root cause."),
            WorkflowTraceStep(agent="remediation", status="completed", summary="Drafted rollback and validation steps."),
            WorkflowTraceStep(agent="postmortem", status="completed", summary="Prepared postmortem summary and follow-ups."),
            WorkflowTraceStep(agent="policy-review", status="completed", summary="Confirmed no unsafe autonomous actions are proposed."),
        ]
        return InvestigationResult(
            incident=incident,
            evidence=evidence,
            changes=changes,
            knowledge=knowledge,
            hypotheses=hypotheses,
            remediation=remediation,
            postmortem=postmortem,
            trace=trace,
            evaluationScore=0,
        )

    def readiness(self) -> tuple[str, str]:
        return ("pass", "Demo provider is active.")


@dataclass
class GradientWorkflowProvider:
    settings: Settings
    timeout_seconds: float = 20.0
    provider_mode: str = "live"

    def run(self, incident_payload: dict[str, Any]) -> InvestigationResult:
        self._ensure_configured()
        assert self.settings.gradient_api_base_url is not None
        assert self.settings.gradient_model_access_key is not None
        request_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": self._build_prompt(incident_payload),
                }
            ],
            "temperature": 0.2,
            "stream": False,
            "max_completion_tokens": 1800,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.gradient_model_access_key}",
            "Content-Type": "application/json",
        }
        endpoint = f"{self.settings.gradient_api_base_url.rstrip('/')}/api/v1/chat/completions"
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(endpoint, json=request_payload, headers=headers)
        if response.status_code in {401, 403}:
            raise ServiceUnavailableError(
                "Live provider rejected the request. Check the hosted agent model and access key."
            )
        if response.status_code >= 500:
            raise ServiceUnavailableError("Live provider is temporarily unavailable.")
        if response.status_code >= 400:
            raise ServiceUnavailableError("Live provider rejected the investigation request.")
        return self._parse_result(cast(dict[str, Any], response.json()))

    def readiness(self) -> tuple[str, str]:
        missing = self._missing_fields()
        if missing:
            return ("fail", f"Missing live provider settings: {', '.join(missing)}.")
        return ("pass", "Live provider configuration is present.")

    def _ensure_configured(self) -> None:
        missing = self._missing_fields()
        if missing:
            raise ServiceUnavailableError(
                f"Live provider is not configured: missing {', '.join(missing)}."
            )

    def _missing_fields(self) -> list[str]:
        missing: list[str] = []
        if not self.settings.gradient_api_base_url:
            missing.append("GRADIENT_API_BASE_URL")
        if not self.settings.gradient_model_access_key:
            missing.append("GRADIENT_MODEL_ACCESS_KEY")
        return missing

    @staticmethod
    def _build_prompt(incident_payload: dict[str, Any]) -> str:
        contract = {
            "incident": {
                "id": "string",
                "title": "string",
                "service": "string",
                "severity": "critical|high|medium|low",
                "status": "open|investigating|resolved",
                "summary": "string",
                "startedAt": "string",
            },
            "evidence": [
                {
                    "id": "string",
                    "kind": "log|alert|metric|stack-trace",
                    "summary": "string",
                    "detail": "string",
                    "source": "string",
                }
            ],
            "changes": [
                {
                    "id": "string",
                    "title": "string",
                    "type": "deploy|config|dependency|commit",
                    "service": "string",
                    "timestamp": "string",
                    "summary": "string",
                }
            ],
            "knowledge": [
                {
                    "id": "string",
                    "title": "string",
                    "category": "runbook|incident|postmortem|architecture",
                    "excerpt": "string",
                    "path": "string",
                }
            ],
            "hypotheses": [
                {
                    "id": "string",
                    "statement": "string",
                    "confidence": 0.0,
                    "rationale": "string",
                    "supportingEvidenceIds": ["string"],
                }
            ],
            "remediation": [
                {
                    "id": "string",
                    "action": "string",
                    "owner": "string",
                    "priority": "immediate|next|follow-up",
                }
            ],
            "postmortem": {
                "title": "string",
                "impact": "string",
                "rootCause": "string",
                "followUps": ["string"],
            },
            "trace": [
                {
                    "agent": "string",
                    "status": "completed|skipped",
                    "summary": "string",
                }
            ],
            "evaluationScore": 0,
        }
        return (
            "You are returning a machine-consumable investigation result for DevProd. "
            "Respond with JSON only. Do not use markdown fences. "
            "Match this exact schema shape and field names:\n"
            f"{json.dumps(contract)}\n"
            "Use the incident payload below as the source of truth. "
            "Prefer conservative inferences and keep the result internally consistent.\n"
            f"{json.dumps(incident_payload)}"
        )

    @staticmethod
    def _parse_result(response_payload: dict[str, Any]) -> InvestigationResult:
        try:
            content = cast(
                str,
                response_payload["choices"][0]["message"]["content"],
            )
        except (KeyError, IndexError, TypeError) as exc:
            raise ServiceUnavailableError("Live provider returned an invalid response payload.") from exc

        normalized = content.strip()
        if normalized.startswith("```"):
            normalized = normalized.strip("`")
            if normalized.startswith("json"):
                normalized = normalized[4:].lstrip()
        try:
            payload = json.loads(normalized)
        except json.JSONDecodeError as exc:
            raise ServiceUnavailableError("Live provider returned non-JSON investigation content.") from exc
        try:
            return InvestigationResult(**cast(dict[str, Any], payload))
        except Exception as exc:
            raise ServiceUnavailableError("Live provider returned an incompatible investigation result.") from exc


def build_workflow_provider(
    settings: Settings, knowledge_repository: KnowledgeRepository
) -> WorkflowProvider:
    if settings.demo_mode:
        return DemoWorkflowProvider(knowledge_repository=knowledge_repository)
    return GradientWorkflowProvider(settings=settings)
