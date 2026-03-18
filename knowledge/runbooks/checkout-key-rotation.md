# Service: checkout-api

Knowledge ID: runbook-checkout-key-rotation
Owner: Identity Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2026.03

## Summary

Use this runbook when token verification fails across multiple services during a signing key rotation event. This is not the primary path for isolated issuer mismatch errors.

## Symptoms

- Multiple services fail token validation at the same time.
- Logs mention unknown key IDs, missing JWKS entries, or stale signing keys.
- Identity provider status shows an in-progress or failed key publication event.

## Checks

1. Confirm whether the identity provider published new signing keys recently.
2. Check whether failures affect services other than `checkout-api`.
3. Inspect logs for key ID or JWKS fetch errors instead of issuer mismatch errors.

## Safe Actions

1. Force a JWKS cache refresh if the platform supports it.
2. Confirm the identity provider published the expected signing keys.
3. Escalate to the identity provider owner before making checkout-specific config changes.

## Escalation

Escalate when key-related validation failures span multiple services or when identity provider key publication is incomplete.
