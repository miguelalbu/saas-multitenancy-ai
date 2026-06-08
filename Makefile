# ============================================================
#  Makefile — desafio-backend-python-ai
#  Usage: make <target>
# ============================================================

DC = docker compose
API = $(DC) exec api

# ─── Containers ─────────────────────────────────────────────

up:           ## Start all containers (detached)
	$(DC) up -d

up-build:     ## Rebuild image and start containers
	$(DC) up -d --build

down:         ## Stop and remove containers
	$(DC) down

restart:      ## Restart all containers
	$(DC) restart

logs:         ## Follow logs (all services)
	$(DC) logs -f

logs-api:     ## Follow API container logs only
	$(DC) logs -f api

ps:           ## Show container status
	$(DC) ps

# ─── Database / Migrations ──────────────────────────────────

migrate:      ## Generate a new migration (MSG="description")
	$(API) alembic revision --autogenerate -m "$(MSG)"

upgrade:      ## Apply all pending migrations
	$(API) alembic upgrade head

downgrade:    ## Revert last migration
	$(API) alembic downgrade -1

migration-status: ## Show current migration state
	$(API) alembic current

migration-history: ## Show full migration history
	$(API) alembic history --verbose

db-shell:     ## Open a psql shell inside the db container
	$(DC) exec db psql -U app -d desafio

# ─── Application ────────────────────────────────────────────

seed:         ## Populate database with initial test data
	$(API) python -m seed.seed_data

shell:        ## Open a Python shell inside the API container
	$(API) python

bash:         ## Open a bash shell inside the API container
	$(API) bash

# ─── Tests ──────────────────────────────────────────────────

test:         ## Run the full test suite
	$(API) python -m pytest -v

test-pillar1: ## Run Pillar 1 tests (auth, tasks, multi-tenant)
	$(API) python -m pytest tests/test_auth.py tests/test_tasks.py tests/test_multi_tenant.py -v

test-pillar2: ## Run Pillar 2 tests (chat / AI agent)
	$(API) python -m pytest tests/test_chat.py -v

test-pillar3: ## Run Pillar 3 tests (webhook, websocket)
	$(API) python -m pytest tests/test_webhook.py tests/test_websocket.py -v

test-q:       ## Run full suite (quiet output)
	$(API) python -m pytest -q

# ─── Code Quality ───────────────────────────────────────────

lint:         ## Run ruff linter
	$(API) ruff check app seed tests

lint-fix:     ## Run ruff linter and auto-fix issues
	$(API) ruff check --fix app seed tests

# ─── Help ───────────────────────────────────────────────────

help:         ## List all available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

.PHONY: up up-build down restart logs logs-api ps \
        migrate upgrade downgrade migration-status migration-history db-shell \
        seed shell bash \
        test test-pillar1 test-pillar2 test-pillar3 test-q \
        lint lint-fix help

.DEFAULT_GOAL := help
