"use client";

import type { IncidentDetail, InvestigationResult } from "@devprod/contracts";
import { useEffect, useState, useTransition } from "react";

import type { DashboardData } from "@/lib/api";
import { getIncidentDetail, runInvestigation } from "@/lib/api";

export function DashboardShell({ initialData }: { initialData: DashboardData }) {
  const [selectedId, setSelectedId] = useState<string>(initialData.incidents[0]?.id ?? "");
  const [incidentDetail, setIncidentDetail] = useState<IncidentDetail | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationResult | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [investigationError, setInvestigationError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    if (!selectedId) {
      return;
    }

    let isMounted = true;
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
        })
        .catch(() => {
          setInvestigationError("Investigation could not be completed.");
        });
    });
  }

  return (
    <main className="page-shell">
      <div className="page-grid">
        <section className="hero">
          <h1>DevProd Control Plane</h1>
          <p>
            Deterministic incident response workflow with evidence, change correlation, retrieval,
            remediation, and evaluation scoring.
          </p>
          <div className="hero-meta">
            <span className="chip">Seeded scenario set</span>
            <span className="chip">Demo-mode agents</span>
            <span className="chip">Traceable evaluation</span>
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
                  <p className="muted">Structured context and operator actions for the selected incident.</p>
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
                {investigation ? (
                  <div className="stack">
                    {investigation.evidence.map((item) => (
                      <article key={item.id}>
                        <strong>{item.summary}</strong>
                        <p>{item.detail}</p>
                      </article>
                    ))}
                    {investigation.changes.map((change) => (
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
                {investigation ? (
                  <div className="stack">
                    {investigation.knowledge.map((doc) => (
                      <article key={doc.id}>
                        <strong>{doc.title}</strong>
                        <p>{doc.excerpt}</p>
                      </article>
                    ))}
                    {investigation.hypotheses.map((hypothesis) => (
                      <article key={hypothesis.id}>
                        <strong>{hypothesis.statement}</strong>
                        <p>{hypothesis.rationale}</p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="muted">Knowledge retrieval and ranked hypotheses appear after investigation.</p>
                )}
              </section>

              <section className="panel">
                <h2>Remediation</h2>
                {investigation ? (
                  <div className="stack">
                    {investigation.remediation.map((step) => (
                      <article key={step.id}>
                        <strong>{step.priority}</strong>
                        <p>{step.action}</p>
                      </article>
                    ))}
                    <article>
                      <strong>{investigation.postmortem.title}</strong>
                      <p>{investigation.postmortem.rootCause}</p>
                    </article>
                  </div>
                ) : (
                  <p className="muted">Remediation guidance is generated by the workflow.</p>
                )}
              </section>

              <section className="panel">
                <h2>Trace And Evaluation</h2>
                {investigationError ? <p role="alert">{investigationError}</p> : null}
                {investigation ? (
                  <div className="stack">
                    <p>
                      Evaluation score: <strong>{investigation.evaluationScore}</strong>
                    </p>
                    <ol className="trace-list">
                      {investigation.trace.map((step) => (
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
            </section>
          </section>
        </section>
      </div>
    </main>
  );
}
