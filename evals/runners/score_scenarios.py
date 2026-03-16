import json
from pathlib import Path

from devprod_api.knowledge import KnowledgeRepository
from devprod_api.repository import IncidentRepository
from devprod_api.workflow import WorkflowService


def run_regression() -> list[dict[str, object]]:
    service = WorkflowService(IncidentRepository(), KnowledgeRepository())
    result = service.run("inc-auth-001")
    return [{"incidentId": result.incident.id, "evaluationScore": result.evaluationScore}]


if __name__ == "__main__":
    report_path = Path(__file__).resolve().parents[1] / "reports" / "latest.json"
    report_path.write_text(json.dumps(run_regression(), indent=2), encoding="utf-8")
