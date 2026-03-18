from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from devprod_api.models import InvestigationResult, InvestigationRunSummary


class InvestigationRunStore:
    def __init__(self, database_path: str) -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._database_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS investigation_runs (
                    id TEXT PRIMARY KEY,
                    incident_id TEXT NOT NULL,
                    incident_title TEXT NOT NULL,
                    provider_mode TEXT NOT NULL,
                    evaluation_score REAL NOT NULL,
                    root_cause TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def save(self, result: InvestigationResult, provider_mode: str) -> InvestigationRunSummary:
        record = InvestigationRunSummary(
            id=str(uuid4()),
            incidentId=result.incident.id,
            incidentTitle=result.incident.title,
            providerMode="demo" if provider_mode == "demo" else "live",
            evaluationScore=result.evaluationScore,
            rootCause=result.postmortem.rootCause,
            createdAt=datetime.now(timezone.utc).isoformat(),
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO investigation_runs (
                    id, incident_id, incident_title, provider_mode,
                    evaluation_score, root_cause, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.incidentId,
                    record.incidentTitle,
                    record.providerMode,
                    record.evaluationScore,
                    record.rootCause,
                    record.createdAt,
                ),
            )
            connection.commit()
        return record

    def list_recent(self, limit: int = 10) -> list[InvestigationRunSummary]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, incident_id, incident_title, provider_mode,
                       evaluation_score, root_cause, created_at
                FROM investigation_runs
                ORDER BY rowid DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            InvestigationRunSummary(
                id=row[0],
                incidentId=row[1],
                incidentTitle=row[2],
                providerMode=row[3],
                evaluationScore=row[4],
                rootCause=row[5],
                createdAt=row[6],
            )
            for row in rows
        ]

    def readiness(self) -> tuple[str, str]:
        try:
            self._initialize()
        except sqlite3.Error as exc:
            return ("fail", f"Run history database is not writable: {exc}.")
        return ("pass", f"Run history database is ready at {self._database_path}.")
