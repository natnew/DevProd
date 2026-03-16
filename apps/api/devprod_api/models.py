from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
IncidentStatus = Literal["open", "investigating", "resolved"]
EvidenceKind = Literal["log", "alert", "metric", "stack-trace"]
ChangeType = Literal["deploy", "config", "dependency", "commit"]
KnowledgeCategory = Literal["runbook", "incident", "postmortem", "architecture"]
RemediationPriority = Literal["immediate", "next", "follow-up"]
TraceStatus = Literal["completed", "skipped"]


class IncidentSummary(BaseModel):
    id: str
    title: str
    service: str
    severity: Severity
    status: IncidentStatus
    summary: str
    startedAt: str


class IncidentDetail(IncidentSummary):
    timeline: list[str]


class EvidenceItem(BaseModel):
    id: str
    kind: EvidenceKind
    summary: str
    detail: str
    source: str


class CorrelatedChange(BaseModel):
    id: str
    title: str
    type: ChangeType
    service: str
    timestamp: str
    summary: str


class KnowledgeDocument(BaseModel):
    id: str
    title: str
    category: KnowledgeCategory
    excerpt: str
    path: str


class Hypothesis(BaseModel):
    id: str
    statement: str
    confidence: float = Field(ge=0, le=1)
    rationale: str
    supportingEvidenceIds: list[str]


class RemediationStep(BaseModel):
    id: str
    action: str
    owner: str
    priority: RemediationPriority


class PostmortemSummary(BaseModel):
    title: str
    impact: str
    rootCause: str
    followUps: list[str]


class WorkflowTraceStep(BaseModel):
    agent: str
    status: TraceStatus
    summary: str


class InvestigationResult(BaseModel):
    incident: IncidentSummary
    evidence: list[EvidenceItem]
    changes: list[CorrelatedChange]
    knowledge: list[KnowledgeDocument]
    hypotheses: list[Hypothesis]
    remediation: list[RemediationStep]
    postmortem: PostmortemSummary
    trace: list[WorkflowTraceStep]
    evaluationScore: float = Field(ge=0, le=100)


class IncidentListResponse(BaseModel):
    incidents: list[IncidentSummary]


class RunInvestigationRequest(BaseModel):
    incidentId: str


class RuntimeConfigResponse(BaseModel):
    demoMode: bool
    authEnabled: bool
    rateLimitPerMinute: int


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
