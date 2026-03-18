# Service: checkout-api

Knowledge ID: runbook-auth-issuer
Owner: Identity Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2026.03

## Summary

Use this runbook when `checkout-api` starts returning authentication failures immediately after a deployment or production config change. Prioritize issuer validation before rotating keys or restarting unrelated systems.

## Symptoms

- `checkout-api` returns a sudden spike of `401` responses.
- Logs contain messages about JWT issuer mismatch or issuer validation failure.
- The error rate increases within minutes of a deploy or environment variable update.

## Checks

1. Confirm `AUTH_ISSUER` matches the production identity provider hostname.
2. Compare the active production environment variables against the last known good release.
3. Review deployment metadata for changes to issuer selection logic or configuration wiring.
4. Check whether other services using the same identity provider are healthy. If they are healthy, prefer service-local config drift over identity provider outage.

## Safe Actions

1. Restore `AUTH_ISSUER` to the production value if it points to staging or another incorrect issuer.
2. Roll back the config or deployment if the correct value cannot be restored safely in place.
3. Validate a successful token flow in production after the fix.
4. Add or enforce deployment checks that reject staging issuer values in production.

## Escalation

Escalate to Identity Platform or the on-call release engineer if production config cannot be inspected directly, or if issuer validation still fails after the known-good value is restored.
