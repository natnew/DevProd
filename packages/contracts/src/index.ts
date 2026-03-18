export type Severity = "critical" | "high" | "medium" | "low";
export type IncidentStatus = "open" | "investigating" | "resolved";

export interface IncidentSummary {
  id: string;
  title: string;
  service: string;
  severity: Severity;
  status: IncidentStatus;
  summary: string;
  startedAt: string;
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

export interface Hypothesis {
  id: string;
  statement: string;
  confidence: number;
  rationale: string;
  supportingEvidenceIds: string[];
}

export interface RemediationStep {
  id: string;
  action: string;
  owner: string;
  priority: "immediate" | "next" | "follow-up";
}

export interface PostmortemSummary {
  title: string;
  impact: string;
  rootCause: string;
  followUps: string[];
}

export interface WorkflowTraceStep {
  agent: string;
  status: "completed" | "skipped";
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

export interface IncidentDetail extends IncidentSummary {
  timeline: string[];
}

export interface RunInvestigationRequest {
  incidentId: string;
}

export interface InvestigationRunListResponse {
  runs: InvestigationRunSummary[];
}

export interface ErrorEnvelope {
  error: {
    code: string;
    message: string;
  };
}

export interface ReadinessResponse {
  status: "ready" | "degraded";
  checks: {
    name: string;
    status: "pass" | "fail";
    detail: string;
  }[];
}
