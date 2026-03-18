import json
from pathlib import Path

from devprod_api.config import Settings
from devprod_api.knowledge import KnowledgeRepository
from devprod_api.providers import build_workflow_provider
from devprod_api.repository import IncidentRepository
from devprod_api.run_history import InvestigationRunStore
from devprod_api.workflow import WorkflowService

ROOT = Path(__file__).resolve().parents[2]


def run_regression() -> list[dict[str, object]]:
    settings = Settings(
        DEMO_MODE=True,
        DEVPROD_RUN_HISTORY_DB_PATH=str(ROOT / "apps" / "api" / "eval-history.sqlite3"),
    )
    incidents = IncidentRepository()
    knowledge = KnowledgeRepository()
    service = WorkflowService(
        settings=settings,
        incident_repository=incidents,
        knowledge_repository=knowledge,
        provider=build_workflow_provider(settings, knowledge),
        run_store=InvestigationRunStore(settings.devprod_run_history_db_path),
    )
    report: list[dict[str, object]] = []
    for incident in incidents.list_incidents():
        run = service.run(incident.id)
        report.append(
            {
                "incidentId": run.result.incident.id,
                "evaluationScore": run.result.evaluationScore,
            }
        )
    return report


if __name__ == "__main__":
    report_path = Path(__file__).resolve().parents[1] / "reports" / "latest.json"
    report_path.write_text(json.dumps(run_regression(), indent=2), encoding="utf-8")
