# Solution Design and Implementation Plan

This document outlines the technical solution and production deployment strategy for the Multi-Agent Personal Assistant on GCP using WhatsApp, FastAPI, LangGraph, and Gemini Pro.

## 1. Proposed Architecture & Tech Stack

- **Backend Language & Framework:** Python 3.11/3.13 with FastAPI & Uvicorn.
- **Compute Infrastructure:** **Google Cloud Run (Serverless Container Platform)**.
  - Automatically scales from 0 to N instances based on inbound WhatsApp webhooks.
  - Native Google-managed HTTPS endpoint with zero-configuration SSL required for Meta WhatsApp Cloud API webhooks.
- **Database & Memory Store:** **Google Cloud Firestore (Native Mode)**.
  - Document database storing User Profiles, OAuth tokens (encrypted), and LangGraph conversation checkpoint memories.
- **Secrets Management:** **Google Cloud Secret Manager**.
  - Stores `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_VERIFY_TOKEN`, and OAuth Client Credentials.
- **Agent Orchestration Framework:** **LangGraph for Python**.
  - Supervisor model (`SecretaryAgent`) delegating tasks to 8 specialized worker agents.
- **Scheduling System:** **Google Cloud Scheduler**.
  - Triggers periodic cron HTTP POST requests to `/internal/cron/scheduled-tasks` secured with GCP Service Account OIDC tokens.
- **Identity & Access Management (IAM):** **Application Default Credentials (ADC)**.
  - Cloud Run runtime service account automatically authenticates to Vertex AI / Gemini API and Firestore without hardcoded API keys.

---

## 2. Component Design & Production Deployment Strategy

### 2.1 WhatsApp Webhook Receiver (`/webhook/whatsapp`)
- Handled by FastAPI route running on Cloud Run.
- Verification endpoint (`GET /webhook/whatsapp`) validates Meta `hub.verify_token` against Secret Manager.
- Message receiver endpoint (`POST /webhook/whatsapp`) parses incoming messages and validates payloads against `specs/api/whatsapp_webhook.yaml`.

### 2.2 The Secretary Agent (Router)
- Implemented using LangGraph as a supervisor graph.
- Analyzes incoming messages, classifies intent into domain worker agents (`TaskTravelManager`, `NewsCollector`, `EmailAgent`, `StockAgent`, `MoneyManager`, `HealthAgent`, `ShoppingAssistant`, `DocumentManager`), and delegates execution.

### 2.3 Worker Agents (Tools)
- Each worker agent is isolated with specific tools adhering to `specs/agents/worker_tools.yaml`.
- **NewsCollector Agent**: Features two distinct tool capabilities (`get_regional_news` and `get_tech_news`) to pull local news and technology updates respectively.

### 2.4 Automated Scheduling System
- GCP Cloud Scheduler triggers `/internal/cron/scheduled-tasks` periodically.
- Request headers are validated for GCP OIDC JWT claims (`X-CloudScheduler-JobName`).
- Processes user scheduled tasks (e.g. 8 AM daily email digest, weekly tech news summary) and sends proactive messages via WhatsApp.

### 2.5 Agent Process Restart & Circuit Breaker Manager (`agents/process_manager.py`)
- Manages process states (`HEALTHY`, `RESTARTING`, `FAILED_MAX_RETRIES`) for all worker agents.
- Automatically handles process crashes by attempting process restarts up to `max_consecutive_crashes` (limit = 5).
- If an agent process fails to restart after 5 consecutive crashes, process restarts are halted, status is set to `FAILED_MAX_RETRIES`, and a structured failure synthesis is returned to prevent HTTP 500 crashes.


---

## 3. Deployment Pipeline & Containerization

### 3.1 Container Architecture
- **Dockerfile**: Multi-stage lightweight Python container built with `uvicorn` as ASGI server.
- Port binding: Reads dynamic `$PORT` environment variable injected by GCP Cloud Run (default `8080`).

### 3.2 Native GCP Cloud Build Deployment Pipeline (`cloudbuild.yaml`)
- **Authoritative Pipeline**: Production builds and deployments use **Google Cloud Build** directly via `cloudbuild.yaml`.
- **GCP Cloud Build Trigger**: Triggered automatically on commit pushes to `main` branch or manually via `gcloud builds submit`.
- **Zero-Secret IAM Security**: Cloud Build leverages native GCP IAM service accounts without needing external GitHub credentials or secret keys.

#### Cloud Build Command:
```bash
gcloud builds submit --config=cloudbuild.yaml --substitutions=COMMIT_SHA=$(git rev-parse --short HEAD) .
```

#### Automated Deployment Steps in `cloudbuild.yaml`:
1. Build Docker container image tagged with `$COMMIT_SHA` and `latest`.
2. Push container images to GCP Artifact Registry (`us-central1-docker.pkg.dev/$PROJECT_ID/personal-agent/app`).
3. Deploy container image to Google Cloud Run (`personal-agent`) in `us-central1` with secrets mounted from Secret Manager (`WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_VERIFY_TOKEN`).

---

## 4. Testing & Quality Assurance
- **Framework:** `pytest`.
- **Contract Verification:** Automated test suite (`tests/test_contracts.py`) validating OpenAPI specs, JSON schemas, Pydantic data models, and API responses.
- **CI/CD:** GitHub Actions / Cloud Build running `pytest` on every pull request.
