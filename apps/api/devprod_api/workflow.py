from typing import Literal

from devprod_api.config import Settings
from devprod_api.evaluation import score_investigation
from devprod_api.models import (
    InvestigationResult,
    InvestigationRunSummary,
    ReadinessCheck,
    ReadinessResponse,
)
from devprod_api.providers import WorkflowProvider
from devprod_api.repository import IncidentRepository
from devprod_api.run_history import InvestigationRunStore


class WorkflowService:
    def __init__(
        self,
        settings: Settings,
        incident_repository: IncidentRepository,
        provider: WorkflowProvider,
        run_store: InvestigationRunStore,
    ) -> None:
        self._settings = settings
        self._incident_repository = incident_repository
        self._provider = provider
        self._run_store = run_store

    def run(self, incident_id: str) -> InvestigationResult:
        payload = self._incident_repository.get_incident_payload(incident_id)
        result = self._provider.run(payload)
        result.evaluationScore = score_investigation(result)
        self._run_store.save(result, provider_mode=self._provider.provider_mode)
        return result

    def list_recent_runs(self, limit: int = 10) -> list[InvestigationRunSummary]:
        return self._run_store.list_recent(limit=limit)

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
