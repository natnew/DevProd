# Service: checkout-api

Owner: Checkout Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2026.03

## Summary

An environment configuration drift introduced a staging token issuer into the production `checkout-api` service. The issue blocked authenticated checkout traffic until the production issuer value was restored.

## Timeline

- `2026-03-16T08:10:00Z`: Alert opened for checkout authentication failures.
- `2026-03-16T08:13:00Z`: Production `AUTH_ISSUER` value changed during deployment prep.
- `2026-03-16T08:15:00Z`: Release `2026.03.16-1` completed.
- `2026-03-16T08:17:00Z`: Logs showed JWT issuer mismatch errors.
- `2026-03-16T08:24:00Z`: On-call restored the production issuer value.

## Root Cause

Deployment-time configuration drift changed `AUTH_ISSUER` from the production identity hostname to the staging issuer hostname, causing token issuer validation to fail.

## What Helped

- Correlating the incident start with the config and deployment timestamps.
- Retrieving the auth issuer runbook and the prior issuer rollback incident.
- Rejecting the signing key rotation warning as a distractor because the logs showed issuer mismatch, not key ID failure.

## Follow-ups

- Add a deployment gate that blocks staging issuer values in production.
- Require post-deploy token validation for `checkout-api`.
- Add this failure pattern to the synthetic incident arena and prompt bundle tests.
