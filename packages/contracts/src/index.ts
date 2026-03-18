export type Severity = "critical" | "high" | "medium" | "low";
export type IncidentStatus = "open" | "investigating" | "resolved";
export type TraceStatus = "completed" | "skipped";

export interface IncidentSummary {
  id: string;
  title: string;
  service: string;
  severity: Severity;
  status: IncidentStatus;
  summary: string;
  startedAt: string;
}

export interface IncidentDetail extends IncidentSummary {
  timeline: string[];
  environment?: string | null;
  customerImpact?: string | null;
}

export interface IncidentIntakeRequest {
  title: string;
  service: string;
  severity: Severity;
  summary: string;
  environment?: string;
  customerImpact?: string | null;
  initialSignals?: string[];
  timeline?: string[];
  suspectedComponents?: string[];
}

export interface IncidentIntakeResponse {
  incident: IncidentSummary;
  location: string;
}

export interface EvidenceItem {
  id: string;
  kind: "log" | "alert" | "metric" | "stack-trace";
  summary: string;
  detail: string;
  source: string;
}

export interface CorrelatedChange {
  id: string;
  title: string;
  type: "deploy" | "config" | "dependency" | "commit";
  service: string;
  timestamp: string;
  summary: string;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  category: "runbook" | "incident" | "postmortem" | "architecture";
  excerpt: string;
  path: string;
}

export interface RetrievalResult {
  documents: KnowledgeDocument[];
  distractors: KnowledgeDocument[];
  coverageGaps: string[];
}

export interface Hypothesis {
  id: string;
  statement: string;
  confidence: number;
  rationale: string;
  supportingEvidenceIds: string[];
}

export interface HypothesisResult {
  hypotheses: Hypothesis[];
  topHypothesis: Hypothesis | null;
  confidence: number;
  recommendedChecks: string[];
}

export interface RemediationStep {
  id: string;
  action: string;
  owner: string;
  priority: "immediate" | "next" | "follow-up";
}

export interface RemediationResult {
  immediateActions: RemediationStep[];
  followUpActions: RemediationStep[];
  risks: string[];
  requiresReview: boolean;
}

export interface PostmortemSummary {
  title: string;
  impact: string;
  rootCause: string;
  followUps: string[];
}

export interface WorkflowTraceStep {
  agent: string;
  status: TraceStatus;
  summary: string;
}

export interface InvestigationResult {
  incident: IncidentSummary;
  evidence: EvidenceItem[];
  changes: CorrelatedChange[];
  knowledge: KnowledgeDocument[];
  hypotheses: Hypothesis[];
  remediation: RemediationStep[];
  postmortem: PostmortemSummary;
  trace: WorkflowTraceStep[];
  evaluationScore: number;
}

export interface InvestigationRunSummary {
  id: string;
  incidentId: string;
  incidentTitle: string;
  providerMode: "demo" | "live";
  evaluationScore: number;
  rootCause: string;
  createdAt: string;
}

export interface InvestigationRunResponse {
  run: InvestigationRunSummary;
  result: InvestigationResult;
}

export interface InvestigationRunListResponse {
  runs: InvestigationRunSummary[];
}

export interface RetrievalResponse {
  run: InvestigationRunSummary;
  retrieval: RetrievalResult;
}

export interface HypothesisResponse {
  run: InvestigationRunSummary;
  hypothesis: HypothesisResult;
}

export interface RemediationResponse {
  run: InvestigationRunSummary;
  remediation: RemediationResult;
}

export interface PostmortemResponse {
  run: InvestigationRunSummary;
  postmortem: PostmortemSummary;
}

export interface RunInvestigationRequest {
  incidentId: string;
}

export interface ReadinessResponse {
  status: "ready" | "degraded";
  checks: {
    name: string;
    status: "pass" | "fail";
    detail: string;
  }[];
}

export interface ErrorEnvelope {
  error: {
    code: string;
    message: string;
  };
}
