# Business Requirement Document (BRD): Multi-Agent Personal Assistant

## 1. Executive Summary
This document outlines the business requirements for developing a Multi-Agent Personal Assistant AI. The system will leverage a WhatsApp Bot interface to interact with users, coordinating tasks through a central "Secretary Agent" that delegates to specialized worker agents. Designed for deployment on Google Cloud Platform (GCP), it supports multi-user onboarding with strict guardrails for data privacy and security.

## 2. Project Objectives
- Create a highly accessible personal assistant via WhatsApp.
- Implement a multi-agent architecture for specialized task execution.
- Provide a seamless onboarding experience using Google Workspace integrations (OAuth).
- Ensure strict data privacy, ensuring user data is isolated and protected.

## 3. Agent Roles and Responsibilities
### 3.1 Core Agents
- **Secretary Agent (Supervisor):** Acts as the central orchestrator. Interprets user messages on WhatsApp, maintains context, delegates sub-tasks to worker agents, and synthesizes their responses into a coherent reply to the user. This agent executes scheduled actions (e.g., weekly news summaries, daily email summaries) at user-defined frequencies. Additionally, it handles ad-hoc user queries at any time by processing the request and invoking the appropriate worker agent to formulate an answer.
- **Task, Travel, and Calendar Manager:** Integrates with Google Calendar and Tasks. Manages scheduling, sets reminders, and coordinates travel itineraries.
  - *Capabilities:* `get_calendar_events`, `schedule_event`, `suggest_itinerary`, `search_flights`.
- **News, Updates, and Information Collector:** Gathers customized news feeds, tracks specific topics of interest, and provides daily summaries.
  - *Capabilities:* `get_regional_news`, `get_tech_news`, `get_top_news`, `search_topic`, `get_weather`.
- **Email Reading and Summarizing Agent:** Connects to Gmail. Reads, categorizes, and summarizes important emails, filtering out spam or low-priority messages.
  - *Capabilities:* `fetch_unread_emails`, `summarize_thread`, `draft_reply`.
- **Business Updates & Stock Performance Agent:** Tracks market trends, portfolio performance, and relevant business news.
  - *Capabilities:* `get_stock_price`, `get_company_news`.
- **Money Manager Agent:** Reads text messages and emails (via Gmail) to filter receipts and payment details. Uses this data to track expenses, monitor subscriptions, and provide financial health checks.
  - *Capabilities:* `extract_receipt`, `calculate_spending`, `list_subscriptions`.
- **Health & Wellness Agent:** Tracks fitness goals, integrates with Google Fit/Apple Health, and suggests healthy habits or meal plans.
  - *Capabilities:* `log_workout`, `suggest_meal_plan`.
- **E-commerce & Shopping Assistant:** Tracks price drops for wish-listed items, manages grocery lists, and automates routine purchases.
  - *Capabilities:* `manage_grocery_list`, `check_product_price`.
- **Document & Knowledge Manager:** Integrates with Google Drive to quickly retrieve files, summarize documents, and organize personal records.
  - *Capabilities:* `search_drive`, `summarize_document`.

## 4. User Journey and Onboarding
- **Registration:** User initiates interaction via a specific WhatsApp number.
- **Authentication:** The bot sends a secure, one-time link for Google (Gmail) OAuth login.
- **Consent Form:** User is presented with a web-based onboarding form to grant specific permissions (Gmail, Calendar, Drive). The form will explain exactly what data is accessed and why.
- **Context Establishment:** The system builds an initial user profile based on the granted data, enabling agents to operate with context.

## 5. Technology Stack & Architecture (High-Level)
- **Cloud Infrastructure:** Google Cloud Platform (GCP) for hosting, database (Cloud SQL/Firestore), and serverless functions (Cloud Run/Cloud Functions).
- **Interface:** WhatsApp Business API (using provided existing account details).
- **Identity & Access Management:** Google Identity Services (OAuth 2.0).
- **AI Framework:** LLM-based agent orchestration powered by Google Gemini Pro.

## 6. Security, Privacy, and Guardrails (Non-Functional Requirements)
- **Data Isolation:** Each user's data and context must be strictly siloed.
- **PII Redaction:** Sensitive personal information (e.g., full account numbers) should be masked in logs and agent memories where possible.
- **Audit Logging:** Maintain logs of what data each agent accessed and when.
- **Revocation of Access:** Users must be able to instantly revoke Google permissions and delete their data via a simple WhatsApp command (e.g., "/delete-my-data").
- **Agent Process Fault Tolerance:** Worker agent processes must auto-recover from transient errors up to 5 consecutive crashes. If an agent process fails to restart after 5 consecutive crashes, the supervisor must quarantine the worker process, prevent crash loops, and return a clean failure response.


## 7. Development & Quality Assurance Principles
- **Living Documentation:** All documentation must be continuously updated as each feature is developed to ensure the context remains current and accurate.
- **Automated Regression Testing:** Every newly developed feature must include automated test cases. These tests will be integrated into a central suite for full regression testing to guarantee system stability over time.
