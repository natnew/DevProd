from __future__ import annotations

from typing import Literal

from devprod_api.config import Settings
from devprod_api.evaluation import score_investigation
from devprod_api.knowledge import KnowledgeRepository
from devprod_api.models import (
    HypothesisResponse,
    HypothesisResult,
    IncidentIntakeRequest,
    IncidentIntakeResponse,
    InvestigationRunResponse,
    InvestigationRunSummary,
    PostmortemResponse,
    ReadinessCheck,
    ReadinessResponse,
    RemediationResponse,
    RemediationResult,
    RetrievalResponse,
)
from devprod_api.providers import WorkflowProvider
from devprod_api.repository import IncidentRepository
from devprod_api.run_history import InvestigationRunStore


class WorkflowService:
    def __init__(
        self,
        settings: Settings,
        incident_repository: IncidentRepository,
        knowledge_repository: KnowledgeRepository,
        provider: WorkflowProvider,
        run_store: InvestigationRunStore,
    ) -> None:
        self._settings = settings
        self._incident_repository = incident_repository
        self._knowledge_repository = knowledge_repository
        self._provider = provider
        self._run_store = run_store

    def ingest_incident(self, payload: IncidentIntakeRequest) -> IncidentIntakeResponse:
        incident = self._incident_repository.create_incident(payload)
        location = f"/v1/incidents/{incident.id}"
        return IncidentIntakeResponse(incident=incident, location=location)

    def run(self, incident_id: str) -> InvestigationRunResponse:
        bundle = self._incident_repository.get_scenario_bundle(incident_id)
        result = self._provider.run(bundle)
        result.evaluationScore = score_investigation(bundle, result)
        run = self._run_store.save(result, provider_mode=self._provider.provider_mode)
        return InvestigationRunResponse(run=run, result=result)

    def list_recent_runs(self, limit: int = 10) -> list[InvestigationRunSummary]:
        return self._run_store.list_recent(limit=limit)

    def get_run(self, run_id: str) -> InvestigationRunResponse:
        run, result = self._run_store.get_run(run_id)
        return InvestigationRunResponse(run=run, result=result)

    def get_retrieval(self, run_id: str) -> RetrievalResponse:
        run, result = self._run_store.get_run(run_id)
        bundle = self._incident_repository.get_scenario_bundle(result.incident.id)
        retrieval = self._knowledge_repository.retrieve(bundle)
        return RetrievalResponse(run=run, retrieval=retrieval)

    def get_hypotheses(self, run_id: str) -> HypothesisResponse:
        run, result = self._run_store.get_run(run_id)
        top = max(result.hypotheses, key=lambda item: item.confidence, default=None)
        bundle = self._incident_repository.get_scenario_bundle(result.incident.id)
        recommended_checks = (
            [str(item) for item in bundle.expected_outcome.get("required_reasoning_steps", [])]
            if bundle.expected_outcome
            else ["Inspect the latest change and retrieve the nearest relevant runbook."]
        )
        confidence = top.confidence if top is not None else 0.0
        payload = HypothesisResult(
            hypotheses=result.hypotheses,
            topHypothesis=top,
            confidence=confidence,
            recommendedChecks=recommended_checks,
        )
        return HypothesisResponse(run=run, hypothesis=payload)

    def get_remediation(self, run_id: str) -> RemediationResponse:
        run, result = self._run_store.get_run(run_id)
        immediate = [step for step in result.remediation if step.priority == "immediate"]
        follow_up = [step for step in result.remediation if step.priority != "immediate"]
        risks = [
            "Production changes require review before execution.",
            "Rollback safety depends on confirming the affected change boundary.",
        ]
        payload = RemediationResult(
            immediateActions=immediate,
            followUpActions=follow_up,
            risks=risks,
            requiresReview=True,
        )
        return RemediationResponse(run=run, remediation=payload)

    def get_postmortem(self, run_id: str) -> PostmortemResponse:
        run, result = self._run_store.get_run(run_id)
        return PostmortemResponse(run=run, postmortem=result.postmortem)

    def readiness(self) -> ReadinessResponse:
        provider_status, provider_detail = self._provider.readiness()
        run_store_status, run_store_detail = self._run_store.readiness()
        provider_state: Literal["pass", "fail"] = "pass" if provider_status == "pass" else "fail"
        run_store_state: Literal["pass", "fail"] = (
            "pass" if run_store_status == "pass" else "fail"
        )
        checks = [
            ReadinessCheck(name="provider", status=provider_state, detail=provider_detail),
            ReadinessCheck(name="run-history", status=run_store_state, detail=run_store_detail),
            ReadinessCheck(
                name="mode",
                status="pass",
                detail=f"Application is running in {'demo' if self._settings.demo_mode else 'live'} mode.",
            ),
        ]
        overall: Literal["ready", "degraded"] = (
            "ready" if all(check.status == "pass" for check in checks) else "degraded"
        )
        return ReadinessResponse(status=overall, checks=checks)
