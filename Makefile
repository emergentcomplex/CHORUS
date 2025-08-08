# Filename: Makefile
# 🔱 CHORUS Command Center (v37 - Definitive Lock)
SHELL := /bin/bash
LOCK_DIR := .run.lock

# --- Environment-Specific Compose Commands ---
DOCKER_COMPOSE_DEV := docker compose --env-file .env.dev -f docker-compose.dev.yml
DOCKER_COMPOSE_PROD := docker compose --env-file .env.prod -f docker-compose.prod.yml
DOCKER_COMPOSE_TEST := docker compose --env-file .env.test -f docker-compose.test.yml
DOCKER_COMPOSE_SETUP_DEV := docker compose --env-file .env.dev -f docker-compose.setup.yml
DOCKER_COMPOSE_SETUP_PROD := docker compose --env-file .env.prod -f docker-compose.setup.yml
DOCKER_COMPOSE_SETUP_TEST := docker compose --env-file .env.test -f docker-compose.setup.yml

.DEFAULT_GOAL := help

.PHONY: help run-dev run-prod stop-dev stop-prod logs-dev logs-prod rebuild-dev rebuild-prod test test-fast stop-all build-base

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
	@echo "  test           - Run the full, hermetic test suite for CI/CD."
	@echo "  test-fast      - Run fast unit tests against the running DEV environment."
	@echo "  test-journey   - Verify the complete user journey from UI to Redis."

# --- CORE BUILD STEP ---
build-base:
	@echo "[*] Building the stable base image (chorus-base:latest)..."
	@docker build -f Dockerfile.base -t chorus-base:latest .

# --- DEVELOPMENT ENVIRONMENT ---
run-dev: build-base
	@echo "[DEV] Attempting to acquire lock..."
	@while ! mkdir $(LOCK_DIR) >/dev/null 2>&1; do \
		echo "[DEV] Waiting for another CHORUS operation to complete..."; \
		sleep 5; \
	done
	@trap 'rm -rf $(LOCK_DIR)' EXIT
	@echo "[DEV] Lock acquired. Proceeding with startup."
	@echo "[*] Ensuring a clean slate for the DEVELOPMENT environment..."
	@$(DOCKER_COMPOSE_DEV) down --remove-orphans
	@echo "[*] Building and starting DEVELOPMENT services..."
	@$(DOCKER_COMPOSE_DEV) up -d --build --wait
	@echo "[*] Configuring the Debezium connector for DEVELOPMENT..."
	@$(DOCKER_COMPOSE_SETUP_DEV) run --rm setup-connector
	@echo "[DEV] Startup complete. Releasing lock."

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
	@echo "[PROD] Attempting to acquire lock..."
	@while ! mkdir $(LOCK_DIR) >/dev/null 2>&1; do \
		echo "[PROD] Waiting for another CHORUS operation to complete..."; \
		sleep 5; \
	done
	@trap 'rm -rf $(LOCK_DIR)' EXIT
	@echo "[PROD] Lock acquired. Proceeding with startup."
	@echo "[*] Ensuring a clean slate for the PRODUCTION environment..."
	@$(DOCKER_COMPOSE_PROD) down --remove-orphans
	@echo "[*] Building and starting PRODUCTION services..."
	@$(DOCKER_COMPOSE_PROD) up -d --build --wait
	@echo "[*] Configuring the Debezium connector for PRODUCTION..."
	@$(DOCKER_COMPOSE_SETUP_PROD) run --rm setup-connector
	@echo "[PROD] Startup complete. Releasing lock."

stop-prod:
	@echo "[*] Tearing down PRODUCTION environment..."
	@$(DOCKER_COMPOSE_PROD) down --remove-orphans

# --- UTILITY ---
stop-all:
	@echo "[*] Tearing down ALL CHORUS environments completely..."
	@$(DOCKER_COMPOSE_DEV) down --remove-orphans > /dev/null 2>&1 || true
	@$(DOCKER_COMPOSE_PROD) down --remove-orphans > /dev/null 2>&1 || true
	@$(DOCKER_COMPOSE_TEST) down --remove-orphans > /dev/null 2>&1 || true
	@rm -rf $(LOCK_DIR)
	@echo "All CHORUS environments have been torn down."

# --- VERIFICATION WORKFLOW ---
test-fast:
	@echo "[*] Running fast unit tests against the DEVELOPMENT environment..."
	@$(DOCKER_COMPOSE_DEV) exec chorus-web pytest --quiet tests/unit

test-journey:
	@echo "[*] FINAL VERIFICATION: Testing the complete user journey..."
	@$(DOCKER_COMPOSE_DEV) exec chorus-web python3 tools/diagnostics/verify_user_journey.py

test: build-base
	@echo "[*] VERIFICATION: Starting full test suite run..."
	@echo "[INFO] This will create and destroy a temporary, isolated test environment."
	@trap '$(DOCKER_COMPOSE_TEST) down --volumes --remove-orphans > /dev/null 2>&1' EXIT
	@$(DOCKER_COMPOSE_TEST) up -d --build --wait
	@echo "[*] Configuring the Debezium connector for the test environment..."
	@$(DOCKER_COMPOSE_SETUP_TEST) run --rm setup-connector
	@echo "[*] Executing the full test suite in order (Unit -> Integration -> E2E)..."
	@$(DOCKER_COMPOSE_TEST) exec chorus-tester pytest --quiet tests/unit
	@$(DOCKER_COMPOSE_TEST) exec chorus-tester pytest --quiet tests/integration
	@$(DOCKER_COMPOSE_TEST) exec chorus-tester pytest --quiet tests/e2e
	@echo "\n✅ === FULL VERIFICATION SUITE PASSED === ✅"