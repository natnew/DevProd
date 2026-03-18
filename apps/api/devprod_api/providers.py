from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
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
from devprod_api.repository import ROOT, IncidentRepository, ScenarioBundle


AGENT_BUNDLE_DIR = ROOT / "agents" / "devprod-workflow"


class WorkflowProvider(Protocol):
    provider_mode: str

    def run(self, bundle: ScenarioBundle) -> InvestigationResult:
        ...

    def readiness(self) -> tuple[str, str]:
        ...


@dataclass
class DemoWorkflowProvider:
    knowledge_repository: KnowledgeRepository
    agent_bundle_dir: Path = AGENT_BUNDLE_DIR
    provider_mode: str = "demo"

    def run(self, bundle: ScenarioBundle) -> InvestigationResult:
        incident = IncidentSummary(**IncidentRepository._to_summary(bundle.incident))
        evidence = self._build_evidence(bundle)
        changes = self._build_changes(bundle)
        retrieval = self.knowledge_repository.retrieve(bundle)

        root_cause = self._root_cause(bundle)
        supporting_ids = [item.id for item in evidence[:3]]
        hypotheses = [
            Hypothesis(
                id="hyp-1",
                statement=root_cause,
                confidence=0.92 if bundle.expected_outcome else 0.56,
                rationale=self._hypothesis_rationale(bundle),
                supportingEvidenceIds=supporting_ids,
            )
        ]

        remediation = self._build_remediation(bundle)
        postmortem = PostmortemSummary(
            title=f"{incident.title} postmortem draft",
            impact=bundle.incident.get("customer_impact")
            or f"{incident.service} experienced customer-visible degradation during the incident window.",
            rootCause=root_cause,
            followUps=self._follow_ups(bundle),
        )
        trace = self._build_trace(bundle, retrieval.documents)

        return InvestigationResult(
            incident=incident,
            evidence=evidence,
            changes=changes,
            knowledge=retrieval.documents,
            hypotheses=hypotheses,
            remediation=remediation,
            postmortem=postmortem,
            trace=trace,
            evaluationScore=0,
        )

    def readiness(self) -> tuple[str, str]:
        return ("pass", "Demo provider is active.")

    def _build_evidence(self, bundle: ScenarioBundle) -> list[EvidenceItem]:
        if bundle.evidence:
            return [EvidenceItem(**item) for item in bundle.evidence]

        synthesized: list[EvidenceItem] = []
        for index, alert in enumerate(bundle.alerts, start=1):
            synthesized.append(
                EvidenceItem(
                    id=alert.get("id", f"ev-alert-{index}"),
                    kind="alert",
                    summary=str(alert.get("summary", "Alert")),
                    detail=str(alert.get("detail", "")),
                    source=str(alert.get("source", "monitoring")),
                )
            )
        for index, signal in enumerate(bundle.incident.get("initial_signals", []), start=1):
            synthesized.append(
                EvidenceItem(
                    id=f"ev-signal-{index}",
                    kind="metric",
                    summary=str(signal),
                    detail=str(signal),
                    source="incident/initial-signals",
                )
            )
        return synthesized

    def _build_changes(self, bundle: ScenarioBundle) -> list[CorrelatedChange]:
        normalized: list[CorrelatedChange] = []
        for index, item in enumerate(bundle.changes, start=1):
            title = item.get("title") or item.get("summary") or f"Change {index}"
            normalized.append(
                CorrelatedChange(
                    id=str(item.get("id", f"chg-{index}")),
                    title=str(title),
                    type=cast(Any, item.get("type", "config")),
                    service=str(item.get("service", bundle.incident["service"])),
                    timestamp=str(item.get("timestamp", IncidentRepository._started_at(bundle.incident))),
                    summary=str(item.get("summary", title)),
                )
            )
        return normalized

    def _root_cause(self, bundle: ScenarioBundle) -> str:
        if bundle.expected_outcome:
            return str(bundle.expected_outcome["root_cause"])
        if bundle.changes:
            return f"Recent change likely caused the incident in {bundle.incident['service']}."
        return f"Further investigation is required to confirm the root cause for {bundle.incident['service']}."

    def _hypothesis_rationale(self, bundle: ScenarioBundle) -> str:
        if bundle.expected_outcome:
            clues = bundle.expected_outcome.get("supporting_evidence", [])
            return " ".join(clues[:2]) or "Observed evidence aligns with the expected failure mode."
        return "The incident timing and available evidence suggest a recent service-local change."

    def _build_remediation(self, bundle: ScenarioBundle) -> list[RemediationStep]:
        if bundle.expected_outcome:
            steps: list[RemediationStep] = []
            for index, action in enumerate(bundle.expected_outcome.get("acceptable_remediations", []), start=1):
                priority: str = "immediate" if index == 1 else "follow-up"
                owner = "incident commander" if index == 1 else "service owner"
                steps.append(
                    RemediationStep(
                        id=f"rem-{index}",
                        action=str(action),
                        owner=owner,
                        priority=cast(Any, priority),
                    )
                )
            return steps
        return [
            RemediationStep(
                id="rem-1",
                action="Inspect the latest service-local change and prepare a safe rollback if customer impact persists.",
                owner="incident commander",
                priority="immediate",
            ),
            RemediationStep(
                id="rem-2",
                action="Capture a reviewed post-incident fix and add regression coverage for the identified failure path.",
                owner="service owner",
                priority="follow-up",
            ),
        ]

    def _follow_ups(self, bundle: ScenarioBundle) -> list[str]:
        if bundle.expected_outcome:
            return [str(item) for item in bundle.expected_outcome.get("acceptable_remediations", [])[1:3]]
        return [
            "Add a benchmark scenario for this failure mode.",
            "Document the investigation path in the retrieval corpus.",
        ]

    def _build_trace(
        self,
        bundle: ScenarioBundle,
        knowledge_documents: list[Any],
    ) -> list[WorkflowTraceStep]:
        agents = self._agent_names()
        trace: list[WorkflowTraceStep] = []
        for agent in agents:
            summary = self._trace_summary(agent, bundle, knowledge_documents)
            trace.append(WorkflowTraceStep(agent=agent, status="completed", summary=summary))
        return trace

    def _agent_names(self) -> list[str]:
        manifest_path = self.agent_bundle_dir / "workflow-manifest.json"
        if not manifest_path.exists():
            return ["triage", "evidence", "retrieval", "hypothesis", "remediation", "postmortem", "policy-review"]
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        return [str(name) for name in payload.get("agents", [])]

    @staticmethod
    def _trace_summary(agent: str, bundle: ScenarioBundle, knowledge_documents: list[Any]) -> str:
        summaries = {
            "triage": f"Classified {bundle.incident['service']} incident and scoped the likely investigation path.",
            "evidence": "Normalized alerts, logs, and timeline clues into structured evidence.",
            "retrieval": f"Retrieved {len(knowledge_documents)} relevant knowledge documents for the incident.",
            "hypothesis": "Ranked the leading hypothesis using change timing and supporting evidence.",
            "remediation": "Drafted safe mitigation and follow-up actions.",
            "postmortem": "Prepared a concise postmortem draft from the reviewed findings.",
            "policy-review": "Checked that the proposed actions stay within safe operational boundaries.",
        }
        return summaries.get(agent, f"Completed {agent} stage.")


@dataclass
class GradientWorkflowProvider:
    settings: Settings
    timeout_seconds: float = 20.0
    provider_mode: str = "live"

    def run(self, bundle: ScenarioBundle) -> InvestigationResult:
        self._ensure_configured()
        assert self.settings.gradient_api_base_url is not None
        assert self.settings.gradient_model_access_key is not None
        request_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": self._build_prompt(bundle),
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
    def _build_prompt(bundle: ScenarioBundle) -> str:
        payload = {
            "incident": IncidentRepository._to_detail(bundle.incident),
            "evidence": bundle.evidence,
            "changes": bundle.changes,
            "alerts": bundle.alerts,
            "expectedOutcome": bundle.expected_outcome,
        }
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
            "evidence": [{"id": "string", "kind": "log|alert|metric|stack-trace", "summary": "string", "detail": "string", "source": "string"}],
            "changes": [{"id": "string", "title": "string", "type": "deploy|config|dependency|commit", "service": "string", "timestamp": "string", "summary": "string"}],
            "knowledge": [{"id": "string", "title": "string", "category": "runbook|incident|postmortem|architecture", "excerpt": "string", "path": "string"}],
            "hypotheses": [{"id": "string", "statement": "string", "confidence": 0.0, "rationale": "string", "supportingEvidenceIds": ["string"]}],
            "remediation": [{"id": "string", "action": "string", "owner": "string", "priority": "immediate|next|follow-up"}],
            "postmortem": {"title": "string", "impact": "string", "rootCause": "string", "followUps": ["string"]},
            "trace": [{"agent": "string", "status": "completed|skipped", "summary": "string"}],
            "evaluationScore": 0,
        }
        return (
            "You are returning a machine-consumable investigation result for DevProd. "
            "Respond with JSON only. Do not use markdown fences. "
            "Match this exact schema shape and field names:\n"
            f"{json.dumps(contract)}\n"
            "Use the incident payload below as the source of truth. "
            "Prefer conservative inferences and keep the result internally consistent.\n"
            f"{json.dumps(payload)}"
        )

    @staticmethod
    def _parse_result(response_payload: dict[str, Any]) -> InvestigationResult:
        try:
            content = cast(str, response_payload["choices"][0]["message"]["content"])
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
        except Exception as exc:  # pragma: no cover - defensive masking around provider output
            raise ServiceUnavailableError("Live provider returned an incompatible investigation result.") from exc


def build_workflow_provider(
    settings: Settings, knowledge_repository: KnowledgeRepository
) -> WorkflowProvider:
    if settings.demo_mode:
        return DemoWorkflowProvider(knowledge_repository=knowledge_repository)
    return GradientWorkflowProvider(settings=settings)
