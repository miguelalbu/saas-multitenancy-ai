# Desafio Técnico Backend — Software Engineer (Python / AI)

## Objective

The goal of this challenge is to evaluate your ability to architect and develop modern, secure, performant, and reactive backend solutions. The test simulates the core business of a corporate SaaS platform: multi-tenant, event-oriented, with real-time updates and integrated AI agents (LLMs) for workflow automation.

We are not looking for a 100% finished system, but rather clean code that demonstrates maturity in software architecture, data modeling, asynchronous processing, real-time communication, and intelligent agent development.

## Tech Stack

- **Language:** Python 3.11+
- **Web Framework:** FastAPI (Async, with native WebSocket support)
- **Validation & AI:** Pydantic (v2) and PydanticAI (mandatory for data validation and agent structuring)
- **Database:** PostgreSQL (via ORM: SQLAlchemy)
- **Messaging/Async:** Native `asyncio` (BackgroundTasks + asyncio.create_task)
- **Containerization:** Docker and Docker Compose
- **Code Standard:** Code, commits, documentation and logs strictly in English

> **Note:** This is a 100% Backend-focused test. No frontend is required. Delivery must be validated via interactive API documentation (Swagger/Redoc), WebSocket tests, or an automated test suite.

## Challenge Scope (3 Pillars)

### Pillar 1: Multi-Tenant Isolation & RBAC

The platform serves multiple companies (Organizations) sharing the same infrastructure with strict data isolation.

1. **Multi-tenancy:** Data isolation via `organization_id` column where every API request automatically filters the scope of the logged-in user's organization (authentication simulated via JWT Token or custom header `X-Organization-ID`).
2. **Access Control (RBAC):** Scope-based access group structure. A middleware/decorator on routes validates if the user has the required technical permission to execute the action (e.g., `task:read` to list tasks; `403 Forbidden` if attempting a restricted route without credentials).

### Pillar 2: Conversational AI Agent with PydanticAI & Tool Calling

The platform's AI agent must actively interact with the system ecosystem, generating structured and reliable outputs.

1. **Chat Endpoint (`POST /v1/chat`):** Route that receives the user's message.
2. **Agent Construction:** Mandatory use of PydanticAI framework to orchestrate the intelligent agent (connected to OpenAI API, Gemini API, or local Ollama).
3. **Tool Implementation with Pydantic Validation:** The agent must have access to at least one functional Tool connected to the database.
   - **Test scenario:** If the user types: *"Register an urgent task called 'Review financial report' for the Commercial department"*, the PydanticAI agent must extract entities in a typed manner, validate them using Pydantic schemas, and autonomously trigger the backend function that inserts the task into the database.

### Pillar 3: Automation Engine & Real-Time Updates (WebSockets)

The system allows events to trigger background actions and reactively notify the user.

1. **Webhook/Trigger Endpoint (`POST /v1/webhook/event`):** Route that receives simulated external events (e.g., a financial status update or system alert).
2. **Event-Driven Processing:** The trigger must fire an asynchronous Action (Background Task/Worker) to execute a secondary task in the database (e.g., change a task status to "Overdue" or generate an audit log).
3. **WebSocket Connection (`/v1/ws/notifications`):** When the background Action completes successfully, the backend must send a reactive/push message through the WebSocket to the logged-in client, simulating a real-time update.

## Evaluation Criteria

- **Async Maturity:** Correct use of concurrency with async/await, stable WebSocket connection management, and background tasks.
- **PydanticAI Usage:** Agent organization, clarity in system prompt definitions, and robustness in Tool injection.
- **Error Handling:** Resilience if WebSocket connection drops or LLM API returns corrupted data.
- **Multi-tenant Security:** Guarantee that WebSocket messages or HTTP requests never leak data between different organizations.

## Technical Questionnaire (Senior Architecture Evaluation)

> Answer these questions about high-scale scenarios:

### 1. Contextual Architecture and Graph Databases

In production AI scenarios, we deal with complex context and RAG knowledge relationships. How would you plan the integration of a Graph-Oriented Database (like Neo4j) with the agent's lifecycle to optimize data retrieval and LLM token cost?

**Answer:** _TODO_

### 2. WebSockets at High Scale

Maintaining thousands of simultaneous open WebSocket connections consumes significant microservice memory. How would you architect the infrastructure and backend (e.g., using Redis Pub/Sub or message brokers) to ensure real-time notifications work in a distributed manner across multiple backend API instances?

**Answer:** _TODO_

### 3. Domain Evolution

Looking at the business rules proposed in this challenge, how would you apply Domain-Driven Design (DDD) concepts to clearly separate Bounded Contexts between the conversational AI module and the automation/workflow execution engine?

**Answer:** _TODO_

## Async Strategy Justification

We chose **native `asyncio`** (FastAPI BackgroundTasks + `asyncio.create_task`) as the messaging/async strategy because:

- The challenge scope is limited and doesn't require distributed workers
- Avoids extra infrastructure complexity (RabbitMQ/Kafka containers)
- Demonstrates mastery of Python's native concurrency model
- For WebSocket push, an in-memory `ConnectionManager` partitioned by organization is sufficient
- In production, this could be evolved to Redis Pub/Sub or a message broker for horizontal scaling

## Getting Started

### Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.12+ for local development without Docker

### Running with Docker Compose

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Running Locally (Development)

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # (optional) for testing & linting
```

### Database Migrations (Alembic)

Make sure PostgreSQL is running (either via Docker or locally) and your `.env` has the correct `DATABASE_URL`.

```bash
# Generate a new migration after changing models
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback the last migration
alembic downgrade -1

# Check current migration state
alembic current
```

> **Tip:** If running only the database via Docker, use:
> ```bash
> docker compose up db -d
> ```
> Then set `DATABASE_URL=postgresql+asyncpg://app:app@localhost:5433/desafio` in your `.env` for local development.

### Seed Data

```bash
python -m seed.seed_data
```

### Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Running Tests

```bash
pytest -v
```

## Multi-Tenant Strategy

Data isolation is enforced via a global `organization_id` column present in all tenant-scoped tables. Every database query is automatically filtered through a dependency injection mechanism (`get_current_organization`) that extracts the organization context from the authenticated JWT token or `X-Organization-ID` header.

WebSocket connections are managed by a `ConnectionManager` that partitions active connections by `organization_id`, ensuring notifications are only broadcast to users within the same organization.

## Project Structure

```
app/
├── main.py                  # FastAPI app entrypoint
├── config.py                # Settings (pydantic-settings)
├── api/
│   ├── deps.py              # Shared dependencies (DB session, auth, org)
│   └── v1/
│       ├── router.py        # Route aggregator
│       └── endpoints/       # One file per resource
├── core/
│   ├── security.py          # JWT, password hashing
│   ├── database.py          # AsyncEngine, AsyncSession
│   ├── permissions.py       # RBAC middleware/decorator
│   └── websocket_manager.py # Multi-tenant ConnectionManager
├── models/                  # SQLAlchemy models
├── schemas/                 # Pydantic schemas
├── services/                # Business logic
├── agent/                   # PydanticAI agent, tools, prompts
└── repositories/            # Data access layer
```

## Deliverables

- [x] GitHub repository
- [x] README with Docker Compose instructions, multi-tenant strategy, and technical questionnaire
- [ ] Seed data for immediate testing
- [ ] Functional API endpoints
- [ ] AI Agent with Tool Calling
- [ ] WebSocket real-time notifications
- [ ] Automated tests
