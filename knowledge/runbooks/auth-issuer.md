# Auth Issuer Validation Runbook

If authentication failures spike immediately after deployment, verify the configured token issuer before rotating keys.

1. Confirm `AUTH_ISSUER` matches the production identity provider.
2. Compare the active deployment environment variables to the last known good release.
3. Roll back the config or deployment if the issuer is set to a staging endpoint.
