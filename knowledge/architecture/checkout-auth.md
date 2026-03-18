# Service: checkout-api

Owner: Identity Platform
Environment: Production
Last Reviewed: 2026-03-18
Version: 2026.03

## Summary

This note describes how `checkout-api` validates customer JWTs in production and where configuration drift can break authentication during deployment.

## Context

`checkout-api` validates JWTs for customer checkout sessions using shared identity platform configuration. Authentication decisions happen before order creation, so configuration drift can block purchases without affecting inventory or payment processors.

## Components

- `checkout-api`: validates JWTs and enforces customer authentication.
- Production identity provider: issues tokens with the production issuer hostname.
- Deployment config layer: injects `AUTH_ISSUER` and related identity settings into the runtime environment.

## Data Flow

1. The client sends a bearer token to `checkout-api`.
2. `checkout-api` reads the configured issuer and token validation settings from the production environment.
3. The service validates token issuer and signature before allowing checkout operations.
4. Requests fail with `401` when the configured issuer does not match the token issuer.

## Failure Modes

- `AUTH_ISSUER` points to staging or another incorrect hostname in production.
- Deployment refactors change issuer selection logic without verifying the production slot value.
- Identity provider key issues affect multiple services at once, usually with key ID or JWKS errors rather than issuer mismatch logs.
