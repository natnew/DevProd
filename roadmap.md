# DevProd Roadmap

## Status

- Current phase: hosted-readiness foundations
- Current step: hosted-readiness foundations implemented and locally validated
- Quality gate: every implemented layer must have automated validation before proceeding

## Milestones

### 1. Foundations

- [x] Define implementation plan
- [x] Add root workspace tooling and scripts
- [x] Add shared contracts and seed data
- [x] Add backend service scaffolding
- [x] Add frontend app scaffolding

### 2. Vertical Slice

- [x] Incident inbox API and UI
- [x] Investigation execution API and UI
- [x] Deterministic workflow adapters and traces
- [x] Evaluation runner and regression fixtures

### 3. Production Hardening

- [x] Config validation and environment safety
- [x] Public error envelopes and masked failures
- [x] Dockerized local startup
- [x] CI-ready lint, typecheck, and test commands

### 4. Hosted Readiness

- [x] Live provider abstraction and config validation
- [x] Persisted investigation run history
- [x] Readiness endpoint for deploy health checks
- [x] Public URL smoke test runner
- [x] Hosted UI surfacing recent investigation runs

### 5. Public Deployment

- [ ] Provision hosted web and API environments
- [ ] Configure live Gradient provider credentials and endpoint
- [ ] Run `npm run smoke:url` against a public URL
- [ ] Observe stable hosted readiness and run-history behavior
- [ ] Add rollback and incident-monitoring runbooks for the hosted stack

## Progress Log

### 2026-03-16

- Initialized roadmap tracking file to replace README changes.
- Confirmed repository started as a skeleton with placeholder directories only.
- Confirmed Node.js and npm are available locally.
- Identified Python as not available on PATH; `uv` is present but needs a workspace-safe cache path to be usable.
- Added root workspace files, Docker Compose, shared contracts package, and seeded synthetic incident/knowledge fixtures.
- Implemented FastAPI API with strict models, auth and rate-limit controls, deterministic workflow service, and evaluation scoring.
- Implemented Next.js dashboard with inbox, investigation, evidence, knowledge, remediation, and trace panels.
- Upgraded Next.js to `16.1.6` after `15.5.3` reported a security vulnerability during install.
- Added GitHub Actions CI for web and API validation on push and pull request.
- Started hosted-readiness work for provider abstraction, persisted run history, readiness checks, and URL smoke testing.
- Implemented a provider boundary with demo and live modes, plus readiness signaling when live provider config is missing.
- Added SQLite-backed investigation run history and surfaced recent runs in both the API and dashboard.
- Added a public URL smoke runner and optional manual CI smoke job for hosted verification.

## Validation Log

- `npm run lint`: pass
- `npm run typecheck`: pass
- `npm run test`: pass
- `npm run test:contracts`: pass
- `.\apps\api\.venv\Scripts\ruff.exe check apps/api evals`: pass
- `.\apps\api\.venv\Scripts\mypy.exe --config-file apps/api/pyproject.toml apps/api/devprod_api apps/api/tests evals/runners/score_scenarios.py`: pass
- `.\apps\api\.venv\Scripts\python.exe -m pytest apps/api/tests`: pass
- `npm run build --workspace apps/web`: pass
- `npm run smoke:url`: implemented, pending a real `PUBLIC_APP_URL` and `PUBLIC_API_URL`

## Risks And Follow-Ups

- Backend Ruff emits non-failing Windows access warnings in this environment while still returning success.
- Live provider integration is structurally ready but still requires real hosted endpoint details and credentials before it can be exercised.
