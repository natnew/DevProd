import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { DashboardShell } from "@/components/dashboard-shell";
import * as api from "@/lib/api";

describe("DashboardShell", () => {
  it("renders the inbox and runs an investigation flow", async () => {
    vi.spyOn(api, "getIncidentDetail").mockResolvedValue({
      id: "inc-auth-001",
      title: "Checkout authentication failures after deployment",
      service: "checkout-api",
      severity: "critical",
      status: "open",
      summary: "Users receive repeated 401 responses after the latest checkout deployment.",
      startedAt: "2026-03-16T08:10:00Z",
      timeline: ["08:10 UTC alert opened for auth error rate spike"]
    });

    vi.spyOn(api, "runInvestigation").mockResolvedValue({
      incident: {
        id: "inc-auth-001",
        title: "Checkout authentication failures after deployment",
        service: "checkout-api",
        severity: "critical",
        status: "open",
        summary: "Users receive repeated 401 responses after the latest checkout deployment.",
        startedAt: "2026-03-16T08:10:00Z"
      },
      evidence: [
        {
          id: "ev-1",
          kind: "alert",
          summary: "Authentication error rate above threshold",
          detail: "401 responses increased from 0.5% to 38% over 5 minutes.",
          source: "monitoring/auth-errors"
        }
      ],
      changes: [
        {
          id: "chg-1",
          title: "Deploy checkout-api 2026.03.16-1",
          type: "deploy",
          service: "checkout-api",
          timestamp: "2026-03-16T08:15:00Z",
          summary: "Rolled out auth configuration refactor for issuer selection."
        }
      ],
      knowledge: [
        {
          id: "runbook-auth-issuer",
          title: "Auth Issuer Validation Runbook",
          category: "runbook",
          excerpt: "Verify the configured token issuer.",
          path: "knowledge/runbooks/auth-issuer.md"
        }
      ],
      hypotheses: [
        {
          id: "hyp-1",
          statement: "Production AUTH_ISSUER points to the staging issuer after the latest deployment.",
          confidence: 0.93,
          rationale: "Logs and deploy timing align with auth config drift.",
          supportingEvidenceIds: ["ev-1"]
        }
      ],
      remediation: [
        {
          id: "rem-1",
          action: "Rollback or correct the AUTH_ISSUER configuration in production.",
          owner: "incident commander",
          priority: "immediate"
        }
      ],
      postmortem: {
        title: "Checkout authentication failures after deployment postmortem draft",
        impact: "Checkout authentication failed for customers during the incident window.",
        rootCause: "Production AUTH_ISSUER points to the staging issuer after the latest deployment.",
        followUps: ["Add deployment validation for production auth issuer values."]
      },
      trace: [
        {
          agent: "triage",
          status: "completed",
          summary: "Classified incident as critical auth outage."
        }
      ],
      evaluationScore: 100
    });

    vi.spyOn(api, "getRecentRuns").mockResolvedValue([
      {
        id: "run-1",
        incidentId: "inc-auth-001",
        incidentTitle: "Checkout authentication failures after deployment",
        providerMode: "demo",
        evaluationScore: 100,
        rootCause: "Production AUTH_ISSUER points to the staging issuer after the latest deployment.",
        createdAt: "2026-03-16T08:20:00Z"
      }
    ]);

    render(
      <DashboardShell
        initialData={{
          readiness: {
            status: "ready",
            checks: [
              { name: "provider", status: "pass", detail: "Demo provider is active." },
              { name: "run-history", status: "pass", detail: "Run history database is ready." },
              { name: "mode", status: "pass", detail: "Application is running in demo mode." }
            ]
          },
          recentRuns: [],
          incidents: [
            {
              id: "inc-auth-001",
              title: "Checkout authentication failures after deployment",
              service: "checkout-api",
              severity: "critical",
              status: "open",
              summary:
                "Users receive repeated 401 responses after the latest checkout deployment.",
              startedAt: "2026-03-16T08:10:00Z"
            }
          ]
        }}
      />
    );

    await waitFor(() =>
      expect(screen.getByText("08:10 UTC alert opened for auth error rate spike")).toBeInTheDocument()
    );

    await userEvent.click(screen.getByRole("button", { name: "Run investigation" }));

    await waitFor(() =>
      expect(
        screen.getByText("Rollback or correct the AUTH_ISSUER configuration in production.")
      ).toBeInTheDocument()
    );
    expect(screen.getByText("Readiness green")).toBeInTheDocument();
    expect(screen.getByText("Evaluation score:")).toBeInTheDocument();
    expect(
      screen.getAllByText("Checkout authentication failures after deployment").length
    ).toBeGreaterThan(0);
  });
});
