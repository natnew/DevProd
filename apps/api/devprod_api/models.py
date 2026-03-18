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
    environment: str | None = None
    customerImpact: str | None = None


class IncidentIntakeRequest(BaseModel):
    title: str
    service: str
    severity: Severity
    summary: str
    environment: str = "production"
    customerImpact: str | None = None
    initialSignals: list[str] = Field(default_factory=list)
    timeline: list[str] = Field(default_factory=list)
    suspectedComponents: list[str] = Field(default_factory=list)


class IncidentIntakeResponse(BaseModel):
    incident: IncidentSummary
    location: str


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


class RetrievalResult(BaseModel):
    documents: list[KnowledgeDocument]
    distractors: list[KnowledgeDocument]
    coverageGaps: list[str]


class Hypothesis(BaseModel):
    id: str
    statement: str
    confidence: float = Field(ge=0, le=1)
    rationale: str
    supportingEvidenceIds: list[str]


class HypothesisResult(BaseModel):
    hypotheses: list[Hypothesis]
    topHypothesis: Hypothesis | None = None
    confidence: float = Field(ge=0, le=1)
    recommendedChecks: list[str]


class RemediationStep(BaseModel):
    id: str
    action: str
    owner: str
    priority: RemediationPriority


class RemediationResult(BaseModel):
    immediateActions: list[RemediationStep]
    followUpActions: list[RemediationStep]
    risks: list[str]
    requiresReview: bool


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


class InvestigationRunSummary(BaseModel):
    id: str
    incidentId: str
    incidentTitle: str
    providerMode: Literal["demo", "live"]
    evaluationScore: float = Field(ge=0, le=100)
    rootCause: str
    createdAt: str


class InvestigationRunResponse(BaseModel):
    run: InvestigationRunSummary
    result: InvestigationResult


class InvestigationRunListResponse(BaseModel):
    runs: list[InvestigationRunSummary]


class RetrievalResponse(BaseModel):
    run: InvestigationRunSummary
    retrieval: RetrievalResult


class HypothesisResponse(BaseModel):
    run: InvestigationRunSummary
    hypothesis: HypothesisResult


class RemediationResponse(BaseModel):
    run: InvestigationRunSummary
    remediation: RemediationResult


class PostmortemResponse(BaseModel):
    run: InvestigationRunSummary
    postmortem: PostmortemSummary


class IncidentListResponse(BaseModel):
    incidents: list[IncidentSummary]


class RunInvestigationRequest(BaseModel):
    incidentId: str


class RuntimeConfigResponse(BaseModel):
    demoMode: bool
    authEnabled: bool
    rateLimitPerMinute: int
    providerMode: Literal["demo", "live"]


class ReadinessCheck(BaseModel):
    name: str
    status: Literal["pass", "fail"]
    detail: str


class ReadinessResponse(BaseModel):
    status: Literal["ready", "degraded"]
    checks: list[ReadinessCheck]


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
