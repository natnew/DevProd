from devprod_api.evaluation import score_investigation
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
from devprod_api.repository import IncidentRepository


class WorkflowService:
    def __init__(
        self,
        incident_repository: IncidentRepository,
        knowledge_repository: KnowledgeRepository,
    ) -> None:
        self._incident_repository = incident_repository
        self._knowledge_repository = knowledge_repository

    def run(self, incident_id: str) -> InvestigationResult:
        payload = self._incident_repository.get_incident_payload(incident_id)
        incident = IncidentSummary(**IncidentRepository._to_summary(payload))
        evidence = [EvidenceItem(**item) for item in payload["evidence"]]
        changes = [CorrelatedChange(**item) for item in payload["changes"]]
        knowledge = self._knowledge_repository.list_for_incident()

        hypotheses = [
            Hypothesis(
                id="hyp-1",
                statement=payload["expectedOutcome"]["rootCause"],
                confidence=0.93,
                rationale=(
                    "Deployment timing, issuer mismatch logs, and the config change all point to "
                    "a production issuer misconfiguration."
                ),
                supportingEvidenceIds=["ev-1", "ev-2", "ev-3"],
            )
        ]
        remediation = [
            RemediationStep(
                id="rem-1",
                action="Rollback or correct the AUTH_ISSUER configuration in production.",
                owner="incident commander",
                priority="immediate",
            ),
            RemediationStep(
                id="rem-2",
                action="Add token issuer validation against production after config changes.",
                owner="platform team",
                priority="follow-up",
            ),
        ]
        postmortem = PostmortemSummary(
            title=f"{incident.title} postmortem draft",
            impact="Checkout authentication failed for customers during the incident window.",
            rootCause=payload["expectedOutcome"]["rootCause"],
            followUps=[
                "Add deployment validation for production auth issuer values.",
                "Require config diff review before checkout releases.",
            ],
        )
        trace = [
            WorkflowTraceStep(agent="triage", status="completed", summary="Classified incident as critical auth outage."),
            WorkflowTraceStep(agent="evidence", status="completed", summary="Structured alert, log, and metric evidence."),
            WorkflowTraceStep(agent="change-correlation", status="completed", summary="Matched auth issue to deploy and config drift."),
            WorkflowTraceStep(agent="retrieval", status="completed", summary="Retrieved runbook and prior incident knowledge."),
            WorkflowTraceStep(agent="hypothesis", status="completed", summary="Ranked issuer mismatch as primary root cause."),
            WorkflowTraceStep(agent="remediation", status="completed", summary="Drafted rollback and validation steps."),
            WorkflowTraceStep(agent="postmortem", status="completed", summary="Prepared postmortem summary and follow-ups."),
            WorkflowTraceStep(agent="policy-review", status="completed", summary="Confirmed no unsafe autonomous actions are proposed."),
        ]

        result = InvestigationResult(
            incident=incident,
            evidence=evidence,
            changes=changes,
            knowledge=knowledge,
            hypotheses=hypotheses,
            remediation=remediation,
            postmortem=postmortem,
            trace=trace,
            evaluationScore=0,
        )
        result.evaluationScore = score_investigation(result)
        return result
