# Service: catalog-api

Knowledge ID: incident-cache-ttl-regression
Owner: Catalog Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2025.10

## Summary

A previous catalog incident increased latency after a cache-related config change reduced effective cache coverage.

## Timeline

- `2025-10-14T12:02:00Z`: Catalog latency alert opened.
- `2025-10-14T12:06:00Z`: Cache hit ratio dropped below 15 percent.
- `2025-10-14T12:11:00Z`: The last known good cache config was restored.
- `2025-10-14T12:17:00Z`: Latency recovered.

## Root Cause

A production cache configuration change reduced effective cache coverage and overloaded the fallback path.

## What Helped

- Correlating latency with cache miss ratio rather than traffic volume.
- Rolling back the config before scaling unrelated systems.
- Validating hit ratio after the restore.

## Follow-ups

- Add cache-path config validation in deployment review.
- Add a benchmark scenario for cache config regressions.
