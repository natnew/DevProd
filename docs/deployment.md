# Deployment

## Local Run Commands

Run the API only:

```bash
npm run dev:api
```

Run the web app only:

```bash
npm run dev:web
```

Run the full local stack with Docker Compose:

```bash
npm run dev
```

The local endpoints are:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`

## Local Environment

Create `.env` from `.env.example`.

For local development, use:

```bash
APP_BASE_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000
INTERNAL_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
DEMO_MODE=true
```

## DigitalOcean App Platform

The App Platform spec is at:

- `.do/app.yaml`

Before deploying, replace:

- `REPLACE_WITH_GITHUB_OWNER/REPLACE_WITH_GITHUB_REPO`
- `https://devprod.example.com`
- `REPLACE_WITH_GRADIENT_MODEL_ACCESS_KEY`

The spec deploys:

- `apps/api` as the `/api` service
- `apps/web` as the root web service

The web service uses:

- `INTERNAL_API_BASE_URL=http://api:8000` for server-side requests inside App Platform
- `NEXT_PUBLIC_API_BASE_URL=/api` for browser requests through the shared public domain

## Deploy With doctl

Create the app from the spec:

```bash
doctl apps create --spec .do/app.yaml
```

Update an existing app:

```bash
doctl apps update <app-id> --spec .do/app.yaml
```

## Notes

- The API currently uses SQLite for local/demo run history. In App Platform, the spec points it to `/tmp/devprod_history.sqlite3`, which is suitable for demo deployments, not durable production history.
- `DEMO_MODE=true` keeps the current seeded local orchestration path active. For live provider execution, set `DEMO_MODE=false` and populate the Gradient env vars.

## Pre-Deploy Checklist

Run this checklist before the first real deployment:

### Repo Hygiene

- Confirm `.env` is not committed and production secrets are not present in tracked files.
- Confirm generated files are ignored:
  - `apps/api/*.sqlite3`
  - `apps/api/test-history-*.sqlite3`
  - `apps/api/eval-history.sqlite3`
  - `arena/intake/`
- Run `git status` and make sure only intentional source/config changes remain.

### Local Verification

- Run API tests:

```bash
npm run test:api
```

- Run web tests:

```bash
npm test
```

- Run web typecheck:

```bash
npm run typecheck
```

- Optionally run the full stack locally:

```bash
npm run dev
```

### App Platform Spec

- Replace placeholder repo values in `.do/app.yaml`.
- Replace `https://devprod.example.com` with the real public domain or initial App Platform hostname.
- Set `GRADIENT_MODEL_ACCESS_KEY` as a real secret if deploying live mode.
- Decide whether the first deployment should stay in `DEMO_MODE=true` or switch to `DEMO_MODE=false`.

### Runtime Expectations

- Accept that run history is ephemeral in the current App Platform spec because it uses `/tmp/devprod_history.sqlite3`.
- Confirm `DEVPROD_ALLOWED_ORIGINS` matches the deployed frontend domain.
- Confirm the web service uses:
  - `NEXT_PUBLIC_API_BASE_URL=/api`
  - `INTERNAL_API_BASE_URL=http://api:8000`

### First Deployment Sequence

1. Create or update the app from `.do/app.yaml`.
2. Wait for both `api` and `web` components to become healthy.
3. Open the deployed web URL.
4. Verify the inbox loads and a seeded investigation run succeeds.
5. Confirm `/readiness` returns `ready`.
