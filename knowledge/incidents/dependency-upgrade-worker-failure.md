# Service: billing-worker

Knowledge ID: incident-dependency-upgrade-worker-failure
Owner: Billing Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2025.12

## Summary

A prior billing-worker release upgraded a shared event client incompatibly and caused queue backlog growth until the worker image was rolled back.

## Timeline

- `2025-12-02T10:12:00Z`: Billing queue backlog alert opened.
- `2025-12-02T10:16:00Z`: Worker logs showed event envelope parse failures.
- `2025-12-02T10:22:00Z`: The worker image was rolled back to the prior dependency set.
- `2025-12-02T10:29:00Z`: Queue depth began recovering.

## Root Cause

The worker image included an incompatible shared event client version that rejected the published envelope shape.

## What Helped

- Comparing dependency locks between the current and previous image.
- Ignoring the early database contention hypothesis because database metrics stayed healthy.
- Reprocessing dead-lettered jobs after the rollback.

## Follow-ups

- Pin the event envelope dependency version.
- Add consumer contract tests for event envelope changes.
