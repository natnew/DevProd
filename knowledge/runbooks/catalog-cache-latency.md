# Service: catalog-api

Knowledge ID: runbook-catalog-cache-latency
Owner: Catalog Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2026.03

## Summary

Use this runbook when `catalog-api` latency spikes while traffic stays normal and cache hit ratio falls. Check cache-path configuration before scaling downstream systems.

## Symptoms

- p95 latency climbs above the normal browsing threshold.
- Cache hit ratio drops and Redis timeout warnings appear.
- Traffic volume remains close to baseline.

## Checks

1. Confirm the hot cache flags and TTL settings in production.
2. Review recent config rollouts that changed cache path behavior.
3. Inspect whether latency is caused by cache misses or downstream traffic saturation.

## Safe Actions

1. Restore the last known good cache configuration.
2. Verify cache hit ratio and end-user latency after the rollback.
3. Add guardrails for disabling cache paths in production.

## Escalation

Escalate to the caching platform owner if Redis remains degraded after the cache path is restored.
