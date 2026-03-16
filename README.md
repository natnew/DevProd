# DevProd

**DevProd** is an agentic engineering control plane for modern software teams.

It helps engineers investigate incidents, correlate operational signals with recent changes, retrieve relevant runbooks and prior incidents, rank root-cause hypotheses, propose remediation steps, and draft postmortems.

Unlike traditional coding assistants, DevProd is built for the next era of software engineering: **engineers supervising systems of agents** rather than spending their time manually stitching together logs, dashboards, commits, and tribal knowledge.

## Core idea

Software development is moving up a level.

The frontier is no longer just “AI that writes code”. The frontier is **AI that monitors, diagnoses, coordinates, evaluates, and improves engineering workflows**.

DevProd is designed for that future.

It combines:

- a **live incident-response control plane**
- a **multi-agent reasoning workflow**
- a **knowledge-backed retrieval system**
- a **bounded improvement loop** inspired by autoresearch-style experimentation

That means DevProd does not merely analyse incidents. It can also **evaluate and improve its own operational playbook** against a benchmark suite of synthetic engineering incidents.

---

## Why DevProd exists

Today’s engineering teams lose time during incidents because the relevant context is fragmented across:

- logs
- alerts
- recent commits and deployments
- architecture docs
- runbooks
- prior postmortems
- team memory

DevProd reduces that fragmentation.

Given an incident, it can:

1. classify the issue
2. gather and structure evidence
3. correlate likely causal changes
4. retrieve relevant operational knowledge
5. generate ranked hypotheses
6. recommend next actions
7. explain its reasoning
8. draft a postmortem after review

This makes DevProd an **agentic reliability engineer** for software teams.

---

## Why this project is different

DevProd is **not**:

- a generic chat interface for developers
- a code autocomplete tool
- a toy “AI debugger”
- a prototype with a nice landing page and no operational depth

DevProd **is**:

- a working AI-powered application
- a multi-agent operational system
- a live dashboard for incident investigation
- a benchmarked and reviewable engineering workflow
- a foundation for future self-improving reliability agents

---

## How it works

### Live operations layer

When an incident arrives, DevProd runs a structured workflow:

1. **Triage Agent** classifies the issue, severity, and likely investigation path  
2. **Evidence Agent** parses logs, alerts, and stack traces into structured facts  
3. **Change Correlation Agent** identifies recent commits, config changes, or deployments likely connected to the issue  
4. **Knowledge Retrieval Agent** searches runbooks, architecture notes, and prior incidents  
5. **Hypothesis Agent** ranks likely root causes with supporting evidence  
6. **Remediation Agent** drafts recommended next steps  
7. **Postmortem Agent** prepares a concise incident summary and postmortem draft  
8. **Policy / Review Agent** applies safety and workflow constraints before surfacing actions to the user  

### Improvement layer

DevProd also includes a bounded optimisation loop inspired by autoresearch-style experimentation.

Instead of letting an agent make arbitrary edits across the system, DevProd constrains the editable surface to one or more operational policies such as:

- routing rules
- retrieval strategy
- hypothesis ranking rubric
- remediation policy
- control instructions for the agent workflow

Each candidate policy is tested against a fixed benchmark suite of synthetic incidents.  
If the workflow improves on the benchmark, DevProd promotes the change.  
If it regresses, the change is rejected.

This turns DevProd into a **self-improving agentic engineering system**, not just a static app.

---

## Why DigitalOcean Gradient™ AI

DevProd is built on DigitalOcean Gradient™ AI because the platform supports the pieces needed for a production-grade agent workflow:

- agent deployment and orchestration
- knowledge bases
- multi-agent routing
- serverless inference
- guardrails
- evaluations
- logs, insights, and traces

This project is intentionally designed to use those capabilities as part of the product, not as an afterthought.

---

## Architecture

### Frontend
- Next.js dashboard
- incident inbox
- investigation view
- evidence panel
- hypothesis board
- remediation panel
- trace and evaluation views

### Backend
- Python orchestration service
- structured workflow execution
- integration with DigitalOcean Gradient AI
- synthetic incident replay and benchmark runner

### Gradient AI layer
- managed agent workflows
- model inference
- knowledge base retrieval
- evaluations
- traces and logs
- guardrails

---

## Main product screens

### 1. Incident Inbox
A queue of incidents with service, severity, status, and timestamp.

### 2. Investigation View
A focused screen showing:
- parsed evidence
- recent correlated changes
- retrieved runbook context
- ranked hypotheses
- recommended next actions

### 3. Review Panel
Allows engineers to:
- approve or reject recommendations
- trigger a postmortem draft
- mark outcomes
- compare baseline vs improved workflow behaviour

### 4. Trace & Evaluation View
Shows:
- which agents ran
- what evidence was used
- what knowledge was retrieved
- how the workflow scored on benchmark incidents
- whether a workflow variant was promoted or rejected

---

## Why this is “production-ready AI”

DevProd is designed around the idea that real AI systems need more than a prompt and a demo video.

This project emphasises:

- bounded agent roles
- reviewable reasoning
- retrieval over guessing
- measurable evaluation
- guardrails and workflow policy
- deployment to a live URL
- a usable interface for real users
- cost-aware operation

That is the difference between a prototype and an actual application.

---

## Benchmark arena

One of DevProd’s key features is its **synthetic incident arena**.

The arena contains benchmark scenarios such as:

- deployment breaks auth flow
- queue workers fail after dependency upgrade
- latency spike after config change
- repeated 500s caused by malformed environment variables
- outdated runbook retrieval leading to a wrong diagnosis
- conflicting evidence between logs and recent deploy history

Each scenario has:

- structured incident input
- relevant knowledge documents
- distractor context
- expected root cause
- acceptable remediation range
- evaluation rubric

This lets DevProd test whether changes to its workflow actually improve incident analysis.

---

## Why this matters

The direction of the industry is clear:

- more agentic systems
- more orchestration
- more evaluation
- more human oversight at the workflow level
- less direct hand-authoring of every action

DevProd is designed for that shift.

It is an operational interface for the next generation of software engineering:  
**not developers versus AI, but engineers supervising fleets of bounded, observable, improvable agents.**

---

## MVP scope

The MVP includes:

- a working incident dashboard
- synthetic incident ingestion
- multi-agent analysis workflow
- knowledge-backed retrieval
- ranked hypotheses and remediation suggestions
- postmortem drafting
- trace and evaluation screens
- a bounded self-improvement loop
- a public demo deployment

The MVP deliberately avoids:

- direct production write access
- autonomous merges to live systems
- destructive infra actions
- unnecessary integration sprawl
- expensive custom model training

---

## Tech stack

### Application
- Next.js
- TypeScript
- Python
- FastAPI
- Docker

### AI / orchestration
- DigitalOcean Gradient™ AI
- Agent Development Kit (ADK)
- knowledge bases
- agent evaluations
- traces and logs
- serverless inference

### Demo data
- synthetic incidents
- synthetic runbooks
- synthetic postmortems
- optional GitHub commit metadata for demo mode

---

## Deployment

DevProd is intended to be deployed as a live web application.

### Recommended deployment
- **Frontend**: DigitalOcean App Platform
- **Backend / API**: DigitalOcean App Platform or container service
- **AI workflow**: DigitalOcean Gradient™ AI hosted agents and inference
- **Public demo URL**: `https://devprod.<your-domain>`

This keeps the architecture simple, cheap, and easy for judges to access.

---

## Setup

### Prerequisites
- DigitalOcean account
- Gradient AI access enabled
- Node.js 20+
- Python 3.10+
- Git

### Environment variables

Create a `.env` file using `.env.example`.

Required variables:

```bash
DIGITALOCEAN_ACCESS_TOKEN=
GRADIENT_MODEL_ACCESS_KEY=
APP_BASE_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000
DEMO_MODE=true