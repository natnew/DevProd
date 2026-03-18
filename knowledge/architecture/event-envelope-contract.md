# Service: billing-worker

Owner: Billing Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2026.03

## Summary

This note describes how `billing-worker` consumes shared event envelopes and where version drift can break job deserialization after deployment.

## Context

`billing-worker` processes billing events from a queue and deserializes each message into the shared event envelope contract before business logic runs.

## Components

- `billing-worker`: consumes and handles invoice-related jobs.
- Event envelope client: shared dependency used to parse queue payloads.
- Producer services: publish billing-related events to the queue.

## Data Flow

1. Producers publish a JSON event envelope to the billing queue.
2. `billing-worker` deserializes the envelope using the shared client library.
3. The worker runs billing handlers after the envelope passes validation.

## Failure Modes

- A shared event client version introduces incompatible constructor or field expectations.
- Producers publish a new field without a compatible consumer rollout plan.
- Queue backlog grows when workers fail during deserialization before business logic starts.
