# Service: checkout-api

Knowledge ID: incident-auth-rollback
Owner: Checkout Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2025.11

## Summary

A prior checkout release pointed `AUTH_ISSUER` to a staging issuer and caused a sharp `401` spike until the configuration was rolled back.

## Timeline

- `2025-11-07T14:03:00Z`: Release completed for `checkout-api`.
- `2025-11-07T14:06:00Z`: `401` rate alert opened.
- `2025-11-07T14:12:00Z`: Logs confirmed issuer mismatch against production tokens.
- `2025-11-07T14:19:00Z`: On-call restored the production issuer value and errors dropped.

## Root Cause

Production configuration drift changed `AUTH_ISSUER` to the staging identity hostname during a release rollout.

## What Helped

- Comparing current environment variables to the previous release.
- Using the auth issuer runbook before attempting key rotation.
- Verifying that other services using the identity provider were healthy.

## Follow-ups

- Add a release-time check that rejects staging issuer values in production.
- Record issuer-related auth failures as a named scenario in the incident arena.
