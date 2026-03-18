# Service: search-frontend

Knowledge ID: runbook-search-traffic-spike
Owner: Search Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2026.03

## Summary

Use this runbook when demand spikes drive request volume and latency together across the search stack.

## Symptoms

- Request volume rises well above normal traffic bands.
- Autoscaling events and CPU pressure appear across several search services.
- Cache hit ratio may remain healthy even while latency increases.

## Checks

1. Compare request volume against seasonal baselines.
2. Inspect autoscaling and edge traffic metrics.
3. Confirm whether cache hit ratio actually degraded before changing cache config.

## Safe Actions

1. Scale the affected read path if approved.
2. Coordinate with traffic management for rate shaping if needed.
3. Preserve cache configuration unless evidence shows a cache regression.

## Escalation

Escalate when the traffic spike is platform-wide or tied to an external campaign.
