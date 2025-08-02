# Filename: Makefile
# 🔱 CHORUS Command Center (v28 - Canonical Init)
SHELL := /bin/bash
UV := uv

DOCKER_COMPOSE := docker compose $(if $(wildcard .env),--env-file .env,)

.DEFAULT_GOAL := help

# ==============================================================================
# HELP
# ==============================================================================
.PHONY: help
help:
	@echo "🔱 CHORUS Command Center (Final)"
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "--------------------------------------------------------------------------"
	@echo " CORE DEVELOPMENT LIFECYCLE"
	@echo "--------------------------------------------------------------------------"
	@echo "  install          - Sync host dependencies for local tooling (e.g., IDEs)."
	@echo "  rebuild          - (Slow Loop) Stop, rebuild the base image, and start."
	@echo "  run              - (Fast Loop) Start all services with live code mounting."
	@echo "  stop             - Stop and remove all CHORUS services and volumes."
	@echo "  logs             - Tail logs for all running services."
	@echo ""
	@echo "--------------------------------------------------------------------------"
	@echo " VERIFICATION & ITERATION"
	@echo "--------------------------------------------------------------------------"
	@echo "  test             - (CI/CD) Run the full, self-contained test suite from a clean slate."
	@echo "  test-fast        - (Local Dev) Run the full test suite against the ALREADY RUNNING dev stack."

# ==============================================================================
# CORE DEVELOPMENT LIFECYCLE
# ==============================================================================
.PHONY: install build rebuild run stop logs
install:
	@echo "[*] Syncing host dependencies for local tooling (e.g., IDEs)..."
	$(UV) sync

build:
	@echo "[*] Building the base Docker image with all dependencies..."
	$(DOCKER_COMPOSE) build

rebuild: stop build run
	@echo "[+] Rebuild complete. Development environment is running."

run:
	@echo "[*] Starting all services in DEV mode (with live code mounting)..."
	$(DOCKER_COMPOSE) up -d --remove-orphans

stop:
	@echo "[*] Stopping and removing all CHORUS services and volumes..."
	$(DOCKER_COMPOSE) down -v

logs:
	@echo "[*] Tailing logs for all running services..."
	$(DOCKER_COMPOSE) logs -f

# ==============================================================================
# VERIFICATION (CI/CD - SLOW, HERMETIC)
# ==============================================================================
.PHONY: test
test:
	@echo "[*] VERIFICATION: Starting full, self-contained test run..."
	@echo "[+] Building images if necessary..."
	$(DOCKER_COMPOSE) build
	@echo "[+] Starting full stack (DB will auto-init if volume is new)..."
	$(DOCKER_COMPOSE) up -d --wait --remove-orphans
	@echo "[+] Running full test suite IN CONTAINER..."
	$(DOCKER_COMPOSE) exec chorus-tester make test-fast
	@echo "[*] VERIFICATION: Tearing down stack..."
	$(DOCKER_COMPOSE) down -v
	@echo "\n✅ === FULL VERIFICATION SUITE PASSED === ✅"

# ==============================================================================
# ITERATION (LOCAL DEVELOPMENT - FAST)
# ==============================================================================
.PHONY: test-fast test-unit test-int test-e2e
test-fast: test-unit test-int test-e2e
	@echo "\n✅ === FAST ITERATION SUITE PASSED === ✅"

test-unit:
	@echo "[*] Running unit tests..."
	pytest tests/unit/

test-int:
	@echo "[*] Running integration tests..."
	make db-reset
	make docker-register-cdc-internal
	pytest tests/integration/

test-e2e:
	@echo "[*] Running E2E tests..."
	make db-reset
	make docker-register-cdc-internal
	pytest tests/e2e/

# ==============================================================================
# DOCKER & DATABASE UTILITIES (for internal use by the test runner)
# ==============================================================================
.PHONY: db-reset docker-register-cdc-internal
db-reset:
	@echo "[*] Resetting database schema for iterative testing..."
	# THE DEFINITIVE FIX: This command now ONLY runs the schema script.
	# One-time setup (permissions, extensions) is handled by the container's
	# entrypoint on first run.
	@cat infrastructure/postgres/init.sql | psql -h postgres -U "$$DB_USER" -d "$$DB_NAME" -v ON_ERROR_STOP=1 > /dev/null
	@echo "[+] Database schema reset."

docker-register-cdc-internal:
	@echo "[*] Registering Debezium CDC connector..."
	@curl -s -o /dev/null -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://kafka-connect:8083/connectors/ -d @infrastructure/debezium/register-postgres-connector.json
