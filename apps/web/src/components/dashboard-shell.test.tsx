import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { DashboardShell } from "@/components/dashboard-shell";
import * as api from "@/lib/api";

describe("DashboardShell", () => {
  it("renders the inbox and runs an investigation flow", async () => {
    vi.spyOn(api, "getIncidentDetail").mockResolvedValue({
      id: "deployment-breaks-auth-flow",
      title: "Checkout authentication failures after deployment",
      service: "checkout-api",
      severity: "critical",
      status: "open",
      summary: "Users receive repeated 401 responses from checkout-api immediately after deployment.",
      startedAt: "2026-03-16T08:10:00Z",
      timeline: ["2026-03-16 08:10:00 UTC Alert opened for authentication error spike."],
      environment: "production",
      customerImpact: "Customers cannot complete checkout."
    });

    vi.spyOn(api, "runInvestigation").mockResolvedValue({
      run: {
        id: "run-1",
        incidentId: "deployment-breaks-auth-flow",
        incidentTitle: "Checkout authentication failures after deployment",
        providerMode: "demo",
        evaluationScore: 100,
        rootCause:
          "The production AUTH_ISSUER configuration was changed to a staging issuer during deployment 2026.03.16-1, causing JWT issuer validation to fail in checkout-api.",
        createdAt: "2026-03-18T18:00:00Z"
      },
      result: {
        incident: {
          id: "deployment-breaks-auth-flow",
          title: "Checkout authentication failures after deployment",
          service: "checkout-api",
          severity: "critical",
          status: "open",
          summary:
            "Users receive repeated 401 responses from checkout-api immediately after deployment.",
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
            title: "Service: checkout-api",
            category: "runbook",
            excerpt: "Use this runbook when checkout-api starts returning authentication failures.",
            path: "knowledge/runbooks/auth-issuer.md"
          }
        ],
        hypotheses: [
          {
            id: "hyp-1",
            statement:
              "The production AUTH_ISSUER configuration was changed to a staging issuer during deployment 2026.03.16-1, causing JWT issuer validation to fail in checkout-api.",
            confidence: 0.92,
            rationale: "The incident starts within minutes of the deployment and production config change.",
            supportingEvidenceIds: ["ev-1"]
          }
        ],
        remediation: [
          {
            id: "rem-1",
            action: "Restore AUTH_ISSUER to the production identity provider value.",
            owner: "incident commander",
            priority: "immediate"
          }
        ],
        postmortem: {
          title: "Checkout authentication failures after deployment postmortem draft",
          impact: "Checkout authentication failed for customers during the incident window.",
          rootCause:
            "The production AUTH_ISSUER configuration was changed to a staging issuer during deployment 2026.03.16-1, causing JWT issuer validation to fail in checkout-api.",
          followUps: ["Add deployment validation for production auth issuer values."]
        },
        trace: [
          {
            agent: "triage",
            status: "completed",
            summary: "Classified checkout-api incident and scoped the likely investigation path."
          }
        ],
        evaluationScore: 100
      }
    });

    vi.spyOn(api, "getRecentRuns").mockResolvedValue([
      {
        id: "run-1",
        incidentId: "deployment-breaks-auth-flow",
        incidentTitle: "Checkout authentication failures after deployment",
        providerMode: "demo",
        evaluationScore: 100,
        rootCause:
          "The production AUTH_ISSUER configuration was changed to a staging issuer during deployment 2026.03.16-1, causing JWT issuer validation to fail in checkout-api.",
        createdAt: "2026-03-18T18:00:00Z"
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
              id: "deployment-breaks-auth-flow",
              title: "Checkout authentication failures after deployment",
              service: "checkout-api",
              severity: "critical",
              status: "open",
              summary: "Users receive repeated 401 responses from checkout-api immediately after deployment.",
              startedAt: "2026-03-16T08:10:00Z"
            }
          ]
        }}
      />
    );

    await waitFor(() =>
      expect(
        screen.getByText("2026-03-16 08:10:00 UTC Alert opened for authentication error spike.")
      ).toBeInTheDocument()
    );

    await userEvent.click(screen.getByRole("button", { name: "Run investigation" }));

    await waitFor(() =>
      expect(
        screen.getByText("Restore AUTH_ISSUER to the production identity provider value.")
      ).toBeInTheDocument()
    );
    expect(screen.getByText("Readiness green")).toBeInTheDocument();
    expect(screen.getByText("run-1")).toBeInTheDocument();
    expect(screen.getByText("Customers cannot complete checkout.")).toBeInTheDocument();
  });
});
