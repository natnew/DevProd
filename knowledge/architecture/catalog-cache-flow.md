# Service: catalog-api

Owner: Catalog Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2026.03

## Summary

This note describes the hot cache and Redis fallback path used by `catalog-api` for product listing reads.

## Context

`catalog-api` serves product lists from a fast in-memory hot cache when possible, then falls back to Redis for broader catalog reads.

## Components

- Hot cache: in-process cache for the most requested catalog keys.
- Redis cache: shared fallback for broader catalog key space.
- `catalog-api`: read path that decides whether to use the hot cache.

## Data Flow

1. Requests first check the in-process hot cache.
2. Cache misses fall back to Redis.
3. Redis misses or timeouts trigger slower backend reads and increase user-visible latency.

## Failure Modes

- Production config disables the hot cache path.
- TTL or invalidation changes drive unexpected cache misses.
- Redis timeout pressure appears when too many reads skip the hot cache.
