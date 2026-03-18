# Service: billing-worker

Knowledge ID: runbook-billing-worker-backlog
Owner: Billing Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2026.03

## Summary

Use this runbook when `billing-worker` queue depth rises rapidly after a deployment. Prioritize worker deserialization and event contract checks before database tuning.

## Symptoms

- Billing queue depth rises quickly after a worker rollout.
- Workers restart but backlog continues to grow.
- Logs mention event envelope parse or constructor errors.

## Checks

1. Compare the worker image or lockfile against the last known good release.
2. Check logs for envelope field mismatches or deserialization failures.
3. Confirm whether database lock and CPU metrics are healthy before blaming persistence.

## Safe Actions

1. Roll back the worker image or dependency change if the failure aligns with a rollout.
2. Pin the compatible event envelope client version.
3. Reprocess failed jobs only after workers successfully deserialize messages again.

## Escalation

Escalate to the event platform owner if the schema change came from a shared event library or producer rollout.
