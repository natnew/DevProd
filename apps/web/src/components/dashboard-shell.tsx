"use client";

import type { IncidentDetail, InvestigationRunResponse, InvestigationRunSummary } from "@devprod/contracts";
import { useEffect, useState, useTransition } from "react";

import type { DashboardData } from "@/lib/api";
import { getIncidentDetail, getRecentRuns, runInvestigation } from "@/lib/api";

export function DashboardShell({ initialData }: { initialData: DashboardData }) {
  const [selectedId, setSelectedId] = useState<string>(initialData.incidents[0]?.id ?? "");
  const [incidentDetail, setIncidentDetail] = useState<IncidentDetail | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationRunResponse | null>(null);
  const [recentRuns, setRecentRuns] = useState<InvestigationRunSummary[]>(initialData.recentRuns);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [investigationError, setInvestigationError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    if (!selectedId) {
      return;
    }

    let isMounted = true;
    setDetailError(null);
    getIncidentDetail(selectedId)
      .then((payload) => {
        if (isMounted) {
          setIncidentDetail(payload);
          setInvestigation(null);
        }
      })
      .catch(() => {
        if (isMounted) {
          setDetailError("Failed to load incident detail.");
        }
      });

    return () => {
      isMounted = false;
    };
  }, [selectedId]);

  function handleSelectIncident(incidentId: string) {
    setDetailError(null);
    setInvestigationError(null);
    setSelectedId(incidentId);
  }

  function handleRunInvestigation() {
    if (!selectedId) {
      return;
    }

    setInvestigationError(null);
    startTransition(() => {
      runInvestigation({ incidentId: selectedId })
        .then((payload) => {
          setInvestigation(payload);
          return getRecentRuns();
        })
        .then((runs) => {
          setRecentRuns(runs);
        })
        .catch(() => {
          setInvestigationError("Investigation could not be completed.");
        });
    });
  }

  const result = investigation?.result ?? null;

  return (
    <main className="page-shell">
      <div className="page-grid">
        <section className="hero">
          <h1>DevProd Control Plane</h1>
          <p>
            Local incident workflow stub with scenario-backed evidence, retrieval, ranked
            hypotheses, remediation planning, and benchmark scoring.
          </p>
          <div className="hero-meta">
            <span className="chip">Scenario-backed workflow</span>
            <span className="chip">
              {initialData.readiness.status === "ready" ? "Readiness green" : "Readiness degraded"}
            </span>
            <span className="chip">{initialData.incidents.length} seeded incidents</span>
          </div>
        </section>

        <section className="workspace">
          <aside className="panel" aria-label="Incident inbox">
            <div className="action-row">
              <h2>Incident Inbox</h2>
              <span className="muted">{initialData.incidents.length} active</span>
            </div>
            <div className="incident-list">
              {initialData.incidents.map((incident) => (
                <button
                  key={incident.id}
                  className="incident-card"
                  data-active={incident.id === selectedId}
                  onClick={() => handleSelectIncident(incident.id)}
                  type="button"
                >
                  <div className="incident-topline">
                    <strong>{incident.service}</strong>
                    <span className={`severity-${incident.severity}`}>{incident.severity}</span>
                  </div>
                  <h3>{incident.title}</h3>
                  <p>{incident.summary}</p>
                </button>
              ))}
            </div>
          </aside>

          <section className="detail-grid">
            <section className="panel">
              <div className="action-row">
                <div>
                  <h2>Investigation View</h2>
                  <p className="muted">
                    Structured context and operator actions for the selected incident.
                  </p>
                </div>
                <button
                  className="primary-button"
                  disabled={isPending || !selectedId}
                  onClick={handleRunInvestigation}
                  type="button"
                >
                  {isPending ? "Running workflow..." : "Run investigation"}
                </button>
              </div>

              {detailError ? <p role="alert">{detailError}</p> : null}
              {incidentDetail ? (
                <div className="meta-grid">
                  <div>
                    <h3>{incidentDetail.title}</h3>
                    <p className="muted">
                      {incidentDetail.service} · {incidentDetail.startedAt}
                    </p>
                    {incidentDetail.customerImpact ? (
                      <p>{incidentDetail.customerImpact}</p>
                    ) : null}
                  </div>
                  <div>
                    <h3>Timeline</h3>
                    <ul className="timeline-list">
                      {incidentDetail.timeline.map((entry) => (
                        <li key={entry}>{entry}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <p className="muted">Select an incident to load its detail.</p>
              )}
            </section>

            <section className="panel-grid">
              <section className="panel">
                <h2>Evidence And Changes</h2>
                {result ? (
                  <div className="stack">
                    {result.evidence.map((item) => (
                      <article key={item.id}>
                        <strong>{item.summary}</strong>
                        <p>{item.detail}</p>
                      </article>
                    ))}
                    {result.changes.map((change) => (
                      <article key={change.id}>
                        <strong>{change.title}</strong>
                        <p>{change.summary}</p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="muted">Run the workflow to populate structured evidence.</p>
                )}
              </section>

              <section className="panel">
                <h2>Knowledge And Hypotheses</h2>
                {result ? (
                  <div className="stack">
                    {result.knowledge.map((doc) => (
                      <article key={doc.id}>
                        <strong>{doc.title}</strong>
                        <p>{doc.excerpt}</p>
                      </article>
                    ))}
                    {result.hypotheses.map((hypothesis) => (
                      <article key={hypothesis.id}>
                        <strong>{hypothesis.statement}</strong>
                        <p>{hypothesis.rationale}</p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="muted">
                    Knowledge retrieval and ranked hypotheses appear after investigation.
                  </p>
                )}
              </section>

              <section className="panel">
                <h2>Remediation</h2>
                {result ? (
                  <div className="stack">
                    {result.remediation.map((step) => (
                      <article key={step.id}>
                        <strong>{step.priority}</strong>
                        <p>{step.action}</p>
                      </article>
                    ))}
                    <article>
                      <strong>{result.postmortem.title}</strong>
                      <p>{result.postmortem.rootCause}</p>
                    </article>
                  </div>
                ) : (
                  <p className="muted">Remediation guidance is generated by the workflow.</p>
                )}
              </section>

              <section className="panel">
                <h2>Trace And Evaluation</h2>
                {investigationError ? <p role="alert">{investigationError}</p> : null}
                {investigation && result ? (
                  <div className="stack">
                    <p>
                      Run <strong>{investigation.run.id}</strong> · {investigation.run.providerMode} mode
                    </p>
                    <p>
                      Evaluation score: <strong>{result.evaluationScore}</strong>
                    </p>
                    <ol className="trace-list">
                      {result.trace.map((step) => (
                        <li key={step.agent}>
                          <strong>{step.agent}</strong>: {step.summary}
                        </li>
                      ))}
                    </ol>
                  </div>
                ) : (
                  <p className="muted">Workflow trace and regression score appear after execution.</p>
                )}
              </section>

              <section className="panel">
                <h2>Recent Runs</h2>
                {recentRuns.length > 0 ? (
                  <div className="stack">
                    {recentRuns.map((run) => (
                      <article key={run.id}>
                        <strong>{run.incidentTitle}</strong>
                        <p>
                          {run.providerMode} mode · score {run.evaluationScore} · {run.createdAt}
                        </p>
                        <p>{run.rootCause}</p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="muted">
                    Investigation runs will appear here once the workflow executes.
                  </p>
                )}
              </section>
            </section>
          </section>
        </section>
      </div>
    </main>
  );
}
