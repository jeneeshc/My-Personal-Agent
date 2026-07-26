# AGENTS.md - Workspace AI Guidelines & Spec-Driven Development (SDD)

## Core Philosophy: Hybrid Spec-Driven Development (Hybrid SDD)

All AI agents and developer tools working on this codebase **MUST strictly follow the Hybrid Spec-Driven Development (SDD) methodology**.

### 1. The Single Source of Truth
- All API contracts, domain models, inter-agent protocols, and external interfaces live in the `specs/` directory.
- The `specs/` directory is the **authoritative single source of truth**. Code must conform to specs, never the other way around without prior spec update.

### 2. Contract Boundaries vs. Prompt Flexibility
- **Strict Contracts (SDD Required)**:
  - Public API Endpoints (OpenAPI specifications in `specs/api/`).
  - Domain Data Schemas (JSON Schemas in `specs/domain/`).
  - Inter-Agent Delegation & Messaging Protocols (YAML/JSON specs in `specs/agents/`).
  - External Service Interfaces (WhatsApp Webhooks, Google OAuth, Firestore schemas).
- **Flexible Tuning (Permitted)**:
  - Internal prompt templates, system prompts, LLM temperature settings, and worker logic heuristics are allowed to iterate flexibly **provided they respect input/output contract schemas**.

### 3. Mandatory Development Workflow (Spec -> Test -> Code -> Verify)
Whenever adding a feature, modifying an API, or introducing a new agent capability:
1. **Spec First**: Modify or create the corresponding specification file in `specs/` BEFORE changing codebase handlers or models.
2. **Contract Models**: Update/create Pydantic models in `models/` to strictly mirror specification contracts.
3. **Mandatory Test Case Creation**: BEFORE declaring any feature or edit complete, write or update unit/integration test cases in `tests/` specifically covering the new capability (e.g. `test_contracts.py`, `test_agents.py`, `test_api.py`).
4. **Implementation**: Implement the feature in `api/`, `services/`, or `agents/`.
5. **Automated Verification**: Run `python -m pytest tests/` to verify zero regressions across the entire suite.
6. **No Declaration Without Passing Tests**: NEVER claim a feature is complete without running `pytest` and demonstrating 100% passing tests.

### 4. Regression Test Suite Policy
- Every single feature must increase or maintain test coverage in `tests/`.
- Never delete, swallow, or comment out failing tests to mask errors.
- Test modularity:
  - `tests/test_contracts.py`: Validates spec YAML files, JSON schemas, Pydantic data models.
  - `tests/test_agents.py`: Validates Secretary routing logic, intent classification, worker delegation.
  - `tests/test_api.py`: Validates FastAPI route handlers, webhooks, and internal cron endpoints.

### 5. Living Documentation Standard
- Keep `docs/Business_Requirement_Document.md` and `docs/Solution_Design_Document.md` aligned with architectural changes.
- Never write ad-hoc, untyped dictionaries for inter-agent or API payloads. Always use validated contract models.
