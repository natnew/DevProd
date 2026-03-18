from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from devprod_api.exceptions import NotFoundError
from devprod_api.models import IncidentDetail, IncidentIntakeRequest, IncidentSummary


ROOT = Path(__file__).resolve().parents[3]
SCENARIOS_DIR = ROOT / "arena" / "scenarios"
INTAKE_DIR = ROOT / "arena" / "intake"


@dataclass
class ScenarioBundle:
    incident: dict[str, Any]
    expected_outcome: dict[str, Any] | None
    rubric_text: str | None
    evidence: list[dict[str, Any]]
    changes: list[dict[str, Any]]
    alerts: list[dict[str, Any]]
    retrieval_context: str | None
    scenario_path: Path


class IncidentRepository:
    def __init__(
        self,
        scenarios_dir: Path = SCENARIOS_DIR,
        intake_dir: Path = INTAKE_DIR,
    ) -> None:
        self._scenarios_dir = scenarios_dir
        self._intake_dir = intake_dir
        self._intake_dir.mkdir(parents=True, exist_ok=True)

    def list_incidents(self) -> list[IncidentSummary]:
        incidents = [self._load_scenario_dir(path) for path in self._scenario_dirs()]
        return [IncidentSummary(**self._to_summary(bundle.incident)) for bundle in incidents]

    def get_incident(self, incident_id: str) -> IncidentDetail:
        bundle = self.get_scenario_bundle(incident_id)
        return IncidentDetail(**self._to_detail(bundle.incident))

    def create_incident(self, payload: IncidentIntakeRequest) -> IncidentSummary:
        incident_id = self._slugify(f"{payload.service}-{payload.title}")
        scenario_dir = self._intake_dir / incident_id
        suffix = 1
        while scenario_dir.exists():
            suffix += 1
            scenario_dir = self._intake_dir / f"{incident_id}-{suffix}"
        scenario_dir.mkdir(parents=True, exist_ok=False)

        started_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        timeline = payload.timeline or [f"{started_at} incident submitted through intake API"]
        incident = {
            "id": scenario_dir.name,
            "title": payload.title,
            "service": payload.service,
            "severity": payload.severity,
            "summary": payload.summary,
            "environment": payload.environment,
            "customer_impact": payload.customerImpact,
            "initial_signals": payload.initialSignals,
            "timeline": [
                {"timestamp": started_at, "event": entry}
                for entry in timeline
            ],
            "suspected_components": payload.suspectedComponents,
            "artifacts": [],
        }
        self._write_json(scenario_dir / "incident.json", incident)
        return IncidentSummary(**self._to_summary(incident))

    def get_scenario_bundle(self, incident_id: str) -> ScenarioBundle:
        for scenario_dir in self._scenario_dirs():
            incident_path = scenario_dir / "incident.json"
            if not incident_path.exists():
                continue
            incident = self._load_json(incident_path)
            if incident["id"] == incident_id:
                return self._load_scenario_dir(scenario_dir)
        raise NotFoundError(f"Incident '{incident_id}' was not found.")

    def _scenario_dirs(self) -> list[Path]:
        roots = [self._scenarios_dir, self._intake_dir]
        scenario_dirs: list[Path] = []
        for root in roots:
            if not root.exists():
                continue
            for path in sorted(root.iterdir()):
                if path.is_dir():
                    scenario_dirs.append(path)
        return scenario_dirs

    def _load_scenario_dir(self, scenario_dir: Path) -> ScenarioBundle:
        incident = self._load_json(scenario_dir / "incident.json")
        expected_path = scenario_dir / "expected-outcome.json"
        expected_outcome = self._load_json(expected_path) if expected_path.exists() else None
        rubric_path = scenario_dir / "rubric.md"
        evidence_path = scenario_dir / "evidence.json"
        changes_path = scenario_dir / "change-log.json"
        alerts_path = scenario_dir / "alerts.json"
        retrieval_context_path = scenario_dir / "retrieval-context.md"

        return ScenarioBundle(
            incident=incident,
            expected_outcome=expected_outcome,
            rubric_text=rubric_path.read_text(encoding="utf-8") if rubric_path.exists() else None,
            evidence=self._load_json_list(evidence_path) if evidence_path.exists() else [],
            changes=self._load_json_list(changes_path) if changes_path.exists() else [],
            alerts=self._load_json_list(alerts_path) if alerts_path.exists() else [],
            retrieval_context=(
                retrieval_context_path.read_text(encoding="utf-8")
                if retrieval_context_path.exists()
                else None
            ),
            scenario_path=scenario_dir,
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return cast(dict[str, Any], json.load(handle))

    @staticmethod
    def _load_json_list(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            return cast(list[dict[str, Any]], json.load(handle))

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def _normalize_severity(value: str) -> str:
        mapping = {
            "SEV1": "critical",
            "SEV2": "high",
            "SEV3": "medium",
            "SEV4": "low",
        }
        return mapping.get(value.upper(), value.lower())

    @staticmethod
    def _timeline_strings(payload: dict[str, Any]) -> list[str]:
        timeline = payload.get("timeline", [])
        values: list[str] = []
        for entry in timeline:
            if isinstance(entry, str):
                values.append(entry)
                continue
            timestamp = entry.get("timestamp", "").replace("T", " ").replace("Z", " UTC").strip()
            event = entry.get("event", "")
            values.append(f"{timestamp} {event}".strip())
        return values

    @staticmethod
    def _started_at(payload: dict[str, Any]) -> str:
        timeline = payload.get("timeline", [])
        for entry in timeline:
            if isinstance(entry, dict) and entry.get("timestamp"):
                return str(entry["timestamp"])
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @classmethod
    def _to_summary(cls, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": payload["id"],
            "title": payload["title"],
            "service": payload["service"],
            "severity": cls._normalize_severity(str(payload["severity"])),
            "status": payload.get("status", "open"),
            "summary": payload["summary"],
            "startedAt": payload.get("startedAt", cls._started_at(payload)),
        }

    @classmethod
    def _to_detail(cls, payload: dict[str, Any]) -> dict[str, Any]:
        detail = cls._to_summary(payload)
        detail["timeline"] = cls._timeline_strings(payload)
        detail["environment"] = payload.get("environment")
        detail["customerImpact"] = payload.get("customer_impact")
        return detail

    @staticmethod
    def _slugify(value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return normalized[:64] or "incident"
