# Service: shared-database

Knowledge ID: runbook-database-lock-contention
Owner: Data Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2026.03

## Summary

Use this runbook when queue workers slow down because database lock waits or transaction contention spike across multiple services.

## Symptoms

- Database lock wait time rises sharply.
- CPU or transaction time spikes on the primary database.
- Multiple services report slow writes or blocked jobs.

## Checks

1. Inspect lock wait dashboards and blocked transactions.
2. Confirm whether the issue affects services beyond a single worker deployment.
3. Look for deadlocks or long-running transactions.

## Safe Actions

1. Cancel or isolate the blocking transaction if approved.
2. Reduce write concurrency for the impacted workload.
3. Coordinate with the database owner before restarting workers.

## Escalation

Escalate when lock contention spans multiple services or the blocking transaction owner is unknown.
