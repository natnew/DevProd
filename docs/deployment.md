# Deployment

This document covers both the local demo path used for the hackathon submission and the intended DigitalOcean deployment path.

## Deployment Targets

DevProd is structured as two services:

- `web`: Next.js frontend
- `api`: FastAPI backend

The intended cloud topology is:

- DigitalOcean App Platform for the `web` and `api` services
- DigitalOcean Gradient AI for live AI-backed workflow execution

For the current submission, the most reliable path is local demo mode with `DEMO_MODE=true`.

## Local Development

### Environment

Create a local `.env` from [`.env.example`](../.env.example).

Recommended local values:

```bash
APP_BASE_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000
INTERNAL_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
DEMO_MODE=true
DEVPROD_ENABLE_AUTH=false
DEVPROD_ALLOWED_ORIGINS=http://localhost:3000
DEVPROD_RUN_HISTORY_DB_PATH=apps/api/devprod_history.sqlite3
```

### Start the API

```bash
npm run dev:api
```

### Start the web app

In a second terminal:

```bash
npm run dev:web
```

### Start the full local stack with Docker Compose

```bash
npm run dev
```

Local endpoints:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`

## Containerized Local Stack

The local Docker Compose file is [`docker-compose.yml`](../docker-compose.yml).

It provides:

- API service on port `8000`
- web service on port `3000`
- internal service-to-service communication from `web` to `api`

Important local compose environment choices:

- `INTERNAL_API_BASE_URL=http://api:8000`
- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
- `DEVPROD_RUN_HISTORY_DB_PATH=/app/devprod_history.sqlite3`

## DigitalOcean App Platform Spec

The deployment spec is [`../.do/app.yaml`](../.do/app.yaml).

It defines:

- `api` as a Dockerfile-based web service from `apps/api/Dockerfile`
- `web` as a Dockerfile-based web service from `apps/web/Dockerfile`
- ingress routing:
  - `/api` -> `api`
  - `/` -> `web`

### Current spec assumptions

- first deploy is demo-safe
- API auth is enabled in the spec
- browser traffic reaches the API through `/api`
- server-side web requests use `http://api:8000`
- run history is ephemeral and stored in `/tmp/devprod_history.sqlite3`

### Values to update after app creation

After App Platform gives you the generated hostname, replace:

- `APP_BASE_URL`
- `API_BASE_URL`
- `DEVPROD_ALLOWED_ORIGINS`
- web `API_BASE_URL`

Example target values:

```bash
APP_BASE_URL=https://your-app.ondigitalocean.app
API_BASE_URL=https://your-app.ondigitalocean.app/api
DEVPROD_ALLOWED_ORIGINS=https://your-app.ondigitalocean.app
```

## Deploy With `doctl`

### Install and authenticate

Install `doctl` from the official docs:

- <https://docs.digitalocean.com/reference/doctl/how-to/install/>

Authenticate:

```bash
doctl auth init
```

Verify:

```bash
doctl account get
```

### Create the app

```bash
doctl apps create --spec .do/app.yaml
```

### Update an existing app

```bash
doctl apps update <app-id> --spec .do/app.yaml
```

### Inspect the deployed app

```bash
doctl apps list
doctl apps get <app-id>
doctl apps list-deployments <app-id>
```

## Demo Mode vs Live Mode

### Demo mode

Set:

```bash
DEMO_MODE=true
```

In this mode:

- the local `DemoWorkflowProvider` is used
- seeded scenario artifacts drive the workflow
- no external AI service is required

This is the primary mode for the hackathon submission and local review.

### Live mode

Set:

```bash
DEMO_MODE=false
GRADIENT_API_BASE_URL=<your-gradient-endpoint>
GRADIENT_MODEL_ACCESS_KEY=<your-secret>
```

In this mode:

- the backend uses `GradientWorkflowProvider`
- a machine-readable investigation prompt is sent to a Gradient AI endpoint
- the returned JSON is validated against the backend contract

## Operational Notes

- The current run history store is SQLite.
- In local mode it is stored under `apps/api/devprod_history.sqlite3` unless overridden.
- In App Platform it is configured to use `/tmp/devprod_history.sqlite3`.
- `/tmp` is not durable storage, so investigation history is ephemeral across restarts and redeploys.

That is acceptable for a hackathon demo deployment, but not for a persistent production deployment.

## Verification Checklist

Before submission or deployment:

1. Run API tests:

```bash
npm run test:api
```

2. Run web tests:

```bash
npm test
```

3. Run the web typecheck:

```bash
npm run typecheck
```

4. Start the app locally and verify:

- incident inbox loads
- seeded incidents are visible
- an investigation run completes
- retrieval, hypotheses, remediation, and postmortem panels render

5. If deploying to App Platform, verify after deployment:

- the root web URL loads
- `/api/readiness` responds
- the inbox loads through the deployed frontend
- a seeded investigation run succeeds end-to-end

## Known Limitations

- public cloud deployment was not completed before the hackathon deadline
- live Gradient mode is included as an integration path, but demo mode is the default reviewed path
- run history is not yet backed by durable managed storage
