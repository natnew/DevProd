from __future__ import annotations

from devprod_api.models import InvestigationResult
from devprod_api.repository import ScenarioBundle


def score_investigation(bundle: ScenarioBundle, result: InvestigationResult) -> float:
    if bundle.expected_outcome is None:
        return 0.0

    root_cause_score = 0.0
    if result.postmortem.rootCause == bundle.expected_outcome["root_cause"]:
        root_cause_score = 50.0

    required_clues = bundle.expected_outcome.get("supporting_evidence", [])
    evidence_corpus = " ".join(
        [item.summary.lower() + " " + item.detail.lower() for item in result.evidence]
        + [hypothesis.rationale.lower() for hypothesis in result.hypotheses]
    )
    knowledge_hits = sum(
        1
        for document in result.knowledge
        if any(keyword.lower() in document.id.lower() or keyword.lower() in document.title.lower() for keyword in ["runbook", "incident", "architecture"])
    )
    clue_hits = sum(1 for clue in required_clues if any(token in evidence_corpus for token in clue.lower().split()[:3]))
    knowledge_score = min(20.0, float(knowledge_hits * 6 + clue_hits * 2))

    remediation_text = " ".join(step.action.lower() for step in result.remediation)
    remediation_hits = sum(
        1
        for keyword in bundle.expected_outcome.get("acceptable_remediations", [])
        if any(term in remediation_text for term in keyword.lower().split()[:2])
    )
    remediation_score = min(30.0, float(remediation_hits * 10))

    return round(root_cause_score + knowledge_score + remediation_score, 2)
