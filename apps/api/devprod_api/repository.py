import json
from pathlib import Path
from typing import Any, cast

from devprod_api.exceptions import NotFoundError
from devprod_api.models import IncidentDetail, IncidentSummary


ROOT = Path(__file__).resolve().parents[3]
INCIDENTS_DIR = ROOT / "arena" / "incidents"


class IncidentRepository:
    def __init__(self, incidents_dir: Path = INCIDENTS_DIR) -> None:
        self._incidents_dir = incidents_dir

    def list_incidents(self) -> list[IncidentSummary]:
        incidents = [self._load_file(path) for path in sorted(self._incidents_dir.glob("*.json"))]
        return [IncidentSummary(**self._to_summary(incident)) for incident in incidents]

    def get_incident(self, incident_id: str) -> IncidentDetail:
        for path in self._incidents_dir.glob("*.json"):
            incident = self._load_file(path)
            if incident["id"] == incident_id:
                return IncidentDetail(**self._to_detail(incident))
        raise NotFoundError(f"Incident '{incident_id}' was not found.")

    def get_incident_payload(self, incident_id: str) -> dict[str, Any]:
        for path in self._incidents_dir.glob("*.json"):
            incident = self._load_file(path)
            if incident["id"] == incident_id:
                return incident
        raise NotFoundError(f"Incident '{incident_id}' was not found.")

    @staticmethod
    def _load_file(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return cast(dict[str, Any], json.load(handle))

    @staticmethod
    def _to_summary(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": payload["id"],
            "title": payload["title"],
            "service": payload["service"],
            "severity": payload["severity"],
            "status": payload["status"],
            "summary": payload["summary"],
            "startedAt": payload["startedAt"],
        }

    @staticmethod
    def _to_detail(payload: dict[str, Any]) -> dict[str, Any]:
        detail = IncidentRepository._to_summary(payload)
        detail["timeline"] = payload["timeline"]
        return detail
