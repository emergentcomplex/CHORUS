# Filename: Makefile
# 🔱 CHORUS Command Center (v46 - Isolated State Machine Test)
SHELL := /bin/bash

# --- Environment-Specific Compose Commands ---
DOCKER_COMPOSE_DEV := docker compose --env-file .env.dev -f docker-compose.dev.yml
DOCKER_COMPOSE_PROD := docker compose --env-file .env.prod -f docker-compose.prod.yml
DOCKER_COMPOSE_TEST := docker compose --env-file .env.test -f docker-compose.test.yml
DOCKER_COMPOSE_RAG_TEST := docker compose --env-file .env.test -f docker-compose.rag.yml
DOCKER_COMPOSE_STATE_TEST := docker compose --env-file .env.test -f docker-compose.state.yml
DOCKER_COMPOSE_SETUP_DEV := docker compose --env-file .env.dev -f docker-compose.setup.yml
DOCKER_COMPOSE_SETUP_PROD := docker compose --env-file .env.prod -f docker-compose.setup.yml
DOCKER_COMPOSE_SETUP_TEST := docker compose --env-file .env.test -f docker-compose.setup.yml

.DEFAULT_GOAL := help

.PHONY: help run-dev run-prod stop-dev stop-prod logs-dev logs-prod rebuild-dev rebuild-prod test test-fast test-rag test-state stop-all build-base validate

help:
	@echo "🔱 CHORUS Command Center"
	@echo ""
	@echo "--- Environment Management ---"
	@echo "  run-dev        - Start the DEVELOPMENT environment (UI on port 5002)."
	@echo "  run-prod       - Start the PRODUCTION environment (UI on port 5001)."
	@echo "  stop-dev       - Stop and REMOVE the DEVELOPMENT environment."
	@echo "  stop-prod      - Stop and REMOVE the PRODUCTION environment."
	@echo "  stop-all       - Force-stop and REMOVE all CHORUS containers and networks."
	@echo ""
	@echo "--- Verification & Testing ---"
	@echo "  validate       - Run the full Constitutional Guardian suite to verify programmatic axioms."
	@echo "  test           - Run the full, hermetic test suite for CI/CD (includes validation)."
	@echo "  test-fast      - Run fast unit tests against the running DEV environment (includes validation)."
	@echo "  test-rag       - Run an isolated, fast integration test for the RAG ingestion pipeline."
	@echo "  test-state     - Run an isolated, fast integration test for the core state machine."
	@echo "  test-journey   - Verify the complete user journey from UI to Redis (includes validation)."

# --- CORE BUILD STEP ---
build-base:
	@echo "[*] Building the stable base image (chorus-base:latest)..."
	@docker build -f Dockerfile.base -t chorus-base:latest .

# --- DEVELOPMENT ENVIRONMENT ---
run-dev: validate build-base
	@echo "[*] Ensuring a clean slate for the DEVELOPMENT environment..."
	@$(DOCKER_COMPOSE_DEV) down --remove-orphans
	@echo "[*] Building and starting DEVELOPMENT services..."
	@$(DOCKER_COMPOSE_DEV) up -d --build --wait
	@echo "[*] Configuring the Debezium connector for DEVELOPMENT..."
	@$(DOCKER_COMPOSE_SETUP_DEV) run --rm setup-connector

stop-dev:
	@echo "[*] Tearing down DEVELOPMENT environment..."
	@$(DOCKER_COMPOSE_DEV) down --remove-orphans

rebuild-dev:
	@echo "[*] Rebuilding DEVELOPMENT environment from a clean slate..."
	@$(DOCKER_COMPOSE_DEV) down --volumes --remove-orphans
	@make run-dev

logs-dev:
	@echo "[*] Tailing logs for DEVELOPMENT environment..."
	@$(DOCKER_COMPOSE_DEV) logs -f

# --- PRODUCTION ENVIRONMENT ---
run-prod: build-base
	@echo "[*] Ensuring a clean slate for the PRODUCTION environment..."
	@$(DOCKER_COMPOSE_PROD) down --remove-orphans
	@echo "[*] Building and starting PRODUCTION services..."
	@$(DOCKER_COMPOSE_PROD) up -d --build --wait
	@echo "[*] Configuring the Debezium connector for PRODUCTION..."
	@$(DOCKER_COMPOSE_SETUP_PROD) run --rm setup-connector

stop-prod:
	@echo "[*] Tearing down PRODUCTION environment..."
	@$(DOCKER_COMPOSE_PROD) down --remove-orphans

# --- UTILITY ---
stop-all:
	@echo "[*] Tearing down ALL CHORUS environments completely..."
	@$(DOCKER_COMPOSE_DEV) down --remove-orphans > /dev/null 2>&1 || true
	@$(DOCKER_COMPOSE_PROD) down --remove-orphans > /dev/null 2>&1 || true
	@$(DOCKER_COMPOSE_TEST) down --remove-orphans > /dev/null 2>&1 || true
	@$(DOCKER_COMPOSE_RAG_TEST) down --volumes --remove-orphans > /dev/null 2>&1 || true
	@$(DOCKER_COMPOSE_STATE_TEST) down --volumes --remove-orphans > /dev/null 2>&1 || true
	@echo "All CHORUS environments have been torn down."

# --- VERIFICATION WORKFLOW ---
validate:
	@echo "[*] Invoking the Office of the Constitutional Guardian..."
	@python3 tools/testing/validate_constitution.py

test-fast: validate
	@echo "[*] Running fast unit tests against the DEVELOPMENT environment..."
	@$(DOCKER_COMPOSE_DEV) exec chorus-web pytest --quiet tests/unit

test-journey: validate
	@echo "[*] FINAL VERIFICATION: Testing the complete user journey..."
	@$(DOCKER_COMPOSE_DEV) exec chorus-web python3 tools/diagnostics/verify_user_journey.py

test: validate stop-all build-base
	@echo "[*] VERIFICATION: Starting full test suite run..."
	@echo "[INFO] This will create and destroy a temporary, isolated test environment."
	@trap '$(DOCKER_COMPOSE_TEST) down --volumes --remove-orphans > /dev/null 2>&1' EXIT
	@echo "[*] Starting all test services in the background..."
	@$(DOCKER_COMPOSE_TEST) up -d --build
	@echo "[*] Waiting for services to be application-ready by running the resilient setup script..."
	@$(DOCKER_COMPOSE_SETUP_TEST) run --rm setup-connector
	@echo "[*] Executing the full test suite in order (Unit -> Integration -> E2E)..."
	@$(DOCKER_COMPOSE_TEST) exec chorus-tester pytest --quiet tests/unit
	@$(DOCKER_COMPOSE_TEST) exec chorus-tester pytest --quiet tests/integration
	@echo "\n✅ === FULL VERIFICATION SUITE PASSED === ✅"

test-rag: validate stop-all build-base
	@echo "[*] RAG VERIFICATION: Starting isolated RAG pipeline test..."
	@trap '$(DOCKER_COMPOSE_RAG_TEST) down --volumes --remove-orphans > /dev/null 2>&1' EXIT
	@echo "[*] Starting minimal RAG services..."
	@$(DOCKER_COMPOSE_RAG_TEST) up -d --build --wait
	@echo "[*] Executing the RAG pipeline integration test..."
	@$(DOCKER_COMPOSE_RAG_TEST) exec chorus-tester pytest --quiet tests/integration/test_rag_pipeline.py \
	|| (echo "\n\n[!] TEST FAILED. DUMPING VECTORIZER LOGS FOR ANALYSIS:\n" && $(DOCKER_COMPOSE_RAG_TEST) logs chorus-vectorizer && exit 1)
	@echo "\n✅ === RAG PIPELINE VERIFIED === ✅"

test-state: validate stop-all build-base
	@echo "[*] STATE MACHINE VERIFICATION: Starting isolated state machine test..."
	@trap '$(DOCKER_COMPOSE_STATE_TEST) down --volumes --remove-orphans > /dev/null 2>&1' EXIT
	@echo "[*] Starting minimal services for state machine test..."
	@$(DOCKER_COMPOSE_STATE_TEST) up -d --build --wait
	@echo "[*] Executing the state machine integration test..."
	@$(DOCKER_COMPOSE_STATE_TEST) exec chorus-tester pytest --quiet tests/integration/test_state_machine_flow.py
	@echo "\n✅ === STATE MACHINE VERIFIED === ✅"