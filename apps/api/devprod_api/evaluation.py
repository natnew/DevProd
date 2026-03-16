import json
from pathlib import Path
from typing import Any, cast

from devprod_api.models import InvestigationResult


ROOT = Path(__file__).resolve().parents[3]
OUTCOME_DIR = ROOT / "arena" / "expected-outcomes"
RUBRIC_PATH = ROOT / "arena" / "rubrics" / "default.json"


def score_investigation(result: InvestigationResult) -> float:
    outcome = _load_expected_outcome(result.incident.id)
    rubric = _load_json(RUBRIC_PATH)

    root_cause_score = 0.0
    if result.postmortem.rootCause == outcome["expectedRootCause"]:
        root_cause_score = float(rubric["rootCauseWeight"])

    knowledge_ids = {document.id for document in result.knowledge}
    matched_knowledge = sum(1 for value in outcome["requiredKnowledgeIds"] if value in knowledge_ids)
    knowledge_score = (
        float(rubric["knowledgeWeight"]) * matched_knowledge / len(outcome["requiredKnowledgeIds"])
    )

    remediation_text = " ".join(step.action.lower() for step in result.remediation)
    remediation_hits = sum(
        1 for keyword in outcome["acceptableRemediationKeywords"] if keyword in remediation_text
    )
    remediation_score = (
        float(rubric["remediationWeight"])
        * remediation_hits
        / len(outcome["acceptableRemediationKeywords"])
    )

    return round(root_cause_score + knowledge_score + remediation_score, 2)


def _load_expected_outcome(incident_id: str) -> dict[str, Any]:
    for path in OUTCOME_DIR.glob("*.json"):
        outcome = _load_json(path)
        if outcome["incidentId"] == incident_id:
            return outcome
    raise FileNotFoundError(f"No expected outcome defined for {incident_id}.")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return cast(dict[str, Any], json.load(handle))
