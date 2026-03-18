from __future__ import annotations

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
        assert self.settings.gradient_agent_id is not None
        assert self.settings.gradient_model_access_key is not None
        request_payload = {"incident": incident_payload}
        headers = {
            "Authorization": f"Bearer {self.settings.gradient_model_access_key}",
            "Content-Type": "application/json",
        }
        endpoint = (
            f"{self.settings.gradient_api_base_url.rstrip('/')}/agents/"
            f"{self.settings.gradient_agent_id}/investigations"
        )
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(endpoint, json=request_payload, headers=headers)
        if response.status_code >= 500:
            raise ServiceUnavailableError("Live provider is temporarily unavailable.")
        if response.status_code >= 400:
            raise ServiceUnavailableError("Live provider rejected the investigation request.")
        return InvestigationResult(**cast(dict[str, Any], response.json()))

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
        if not self.settings.gradient_agent_id:
            missing.append("GRADIENT_AGENT_ID")
        if not self.settings.gradient_model_access_key:
            missing.append("GRADIENT_MODEL_ACCESS_KEY")
        return missing


def build_workflow_provider(
    settings: Settings, knowledge_repository: KnowledgeRepository
) -> WorkflowProvider:
    if settings.demo_mode:
        return DemoWorkflowProvider(knowledge_repository=knowledge_repository)
    return GradientWorkflowProvider(settings=settings)
