# Solution Design and Implementation Plan

This document outlines the technical solution and implementation plan for the Multi-Agent Personal Assistant on GCP using WhatsApp and Gemini Pro.

## 1. Proposed Architecture & Tech Stack
- **Backend Language:** Python (FastAPI). Python is the industry standard for LLM integrations (LangGraph) and has excellent Google Cloud/Gemini SDK support.
- **Compute:** Google Cloud Run. It provides a scalable serverless environment suitable for handling WhatsApp Webhooks and long-running agent processes.
- **Database:** Google Cloud Firestore (NoSQL). Ideal for storing unstructured conversation history, user profiles, and agent memory (context).
- **Authentication:** Google OAuth 2.0. We will build a simple web flow hosted on Cloud Run where users authenticate and grant scopes. Tokens will be securely encrypted and stored.
- **Agent Orchestration Framework:** LangGraph for Python. LangGraph is excellent for building multi-agent workflows where a "Supervisor" (Secretary) routes tasks to "Workers" (Sub-agents).
- **Scheduling:** Google Cloud Scheduler. This will trigger periodic HTTP endpoints on Cloud Run to execute scheduled tasks (e.g., weekly news, daily email summaries).

## 2. Component Design

### 2.1 WhatsApp Webhook Receiver
- An endpoint (`/webhook/whatsapp`) to receive incoming messages from the WhatsApp Business API.
- Authenticates the incoming request, parses the text, and looks up the User Profile in Firestore.

### 2.2 The Secretary Agent (Router)
- Implemented as the primary LLM chain.
- Analyzes the user's intent and determines if it requires a specific worker agent (e.g., Money Manager) or if it's a general query.
- Passes context to the appropriate worker, awaits the response, and formulates the final WhatsApp reply.

### 2.3 Worker Agents (Tools)
Each worker agent will be a distinct LangChain agent equipped with specific tools:
- **Email/Calendar Agent:** Tools for Gmail API (Search, Read) and Google Calendar API (List Events, Create Event).
- **Money Manager Agent:** Tools to parse receipts from Gmail using specific regex/LLM extraction.
- **News/Info Agent:** Tools to search the web and fetch RSS feeds.

### 2.4 Automated Scheduling System
- User preferences for scheduled tasks (frequency, time) are saved in Firestore.
- A Cloud Scheduler job runs periodically, calling an internal endpoint (`/internal/cron/scheduled-tasks`).
- The system checks which users need a summary, triggers the Secretary Agent to compile it, and proactively sends a WhatsApp message.

## 3. Testing & Quality Assurance
- **Framework:** `pytest`.
- **Unit Tests:** Mocking Google APIs and WhatsApp API to ensure the Secretary agent routes correctly.
- **Regression Suite:** Automated integration tests simulating full WhatsApp message payloads.
- **CI/CD:** Automated pipelines to run tests on every commit.
