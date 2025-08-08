# Filename: Makefile
# 🔱 CHORUS Command Center (v29 - Zsh Safe)
SHELL := /bin/bash

# --- Environment-Specific Compose Commands ---
DOCKER_COMPOSE_DEV := docker compose --env-file .env.dev -f docker-compose.dev.yml
DOCKER_COMPOSE_PROD := docker compose --env-file .env.prod -f docker-compose.prod.yml
DOCKER_COMPOSE_TEST := docker compose --env-file .env.test -f docker-compose.test.yml
DOCKER_COMPOSE_SETUP_DEV := docker compose --env-file .env.dev -f docker-compose.setup.yml
DOCKER_COMPOSE_SETUP_PROD := docker compose --env-file .env.prod -f docker-compose.setup.yml
DOCKER_COMPOSE_SETUP_TEST := docker compose --env-file .env.test -f docker-compose.setup.yml

.DEFAULT_GOAL := help

.PHONY: help run-dev run-prod stop-dev stop-prod logs-dev logs-prod rebuild-dev rebuild-prod test test-fast stop-all

help:
	@echo "🔱 CHORUS Command Center"
	@echo ""
	@echo "--- Environment Management (Can be run concurrently) ---"
	@echo "  run-dev        - Start the DEVELOPMENT environment (UI on port 5002)."
	@echo "  run-prod       - Start the PRODUCTION environment (UI on port 5001)."
	@echo "  stop-dev       - Stop and REMOVE the DEVELOPMENT environment."
	@echo "  stop-prod      - Stop and REMOVE the PRODUCTION environment."
	@echo "  stop-all       - Force-stop and REMOVE all CHORUS containers and networks."
	@echo "  logs-dev       - Tail logs from the DEVELOPMENT environment."
	@echo "  logs-prod      - Tail logs from the PRODUCTION environment."
	@echo "  rebuild-dev    - Rebuild the DEV environment from a clean slate (deletes DB data)."
	@echo "  rebuild-prod   - Rebuild the PROD environment from a clean slate (DELETES ALL DATA)."
	@echo ""
	@echo "--- Verification Workflow ---"
	@echo "  test           - Run the full, hermetic test suite (can run concurrently with dev/prod)."
	@echo "  test-fast      - Run fast unit tests against the running DEV environment."

# --- DEVELOPMENT ENVIRONMENT ---
run-dev:
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
run-prod:
	@echo "[*] Building and starting PRODUCTION services..."
	@$(DOCKER_COMPOSE_PROD) up -d --build --wait
	@echo "[*] Configuring the Debezium connector for PRODUCTION..."
	@$(DOCKER_COMPOSE_SETUP_PROD) run --rm setup-connector

stop-prod:
	@echo "[*] Tearing down PRODUCTION environment..."
	@$(DOCKER_COMPOSE_PROD) down --remove-orphans

rebuild-prod:
	@echo "[WARNING] This will permanently delete the PRODUCTION database volume."
	@read -p "    Are you sure you want to continue? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "[*] Rebuilding PRODUCTION environment from a clean slate..."; \
		$(DOCKER_COMPOSE_PROD) down --volumes --remove-orphans; \
		make run-prod; \
	else \
		echo "[*] Rebuild aborted."; \
	fi

logs-prod:
	@echo "[*] Tailing logs for PRODUCTION environment..."
	@$(DOCKER_COMPOSE_PROD) logs -f

# --- UTILITY ---
stop-all:
	@echo "[*] Tearing down ALL CHORUS environments completely..."
	@$(DOCKER_COMPOSE_DEV) down --remove-orphans > /dev/null 2>&1 || true
	@$(DOCKER_COMPOSE_PROD) down --remove-orphans > /dev/null 2>&1 || true
	@$(DOCKER_COMPOSE_TEST) down --remove-orphans > /dev/null 2>&1 || true
	@echo "All CHORUS environments have been torn down."

# --- VERIFICATION WORKFLOW ---
test-fast:
	@echo "[*] Running fast unit tests against the DEVELOPMENT environment..."
	@$(DOCKER_COMPOSE_DEV) exec chorus-web pytest --quiet tests/unit

test:
	@echo "[*] VERIFICATION: Starting full test suite run..."
	@echo "[INFO] This will create and destroy a temporary, isolated test environment."
	
	@trap '$(DOCKER_COMPOSE_TEST) down --volumes --remove-orphans > /dev/null 2>&1' EXIT
	
	@$(DOCKER_COMPOSE_TEST) build
	@$(DOCKER_COMPOSE_TEST) up -d --wait
	
	@echo "[*] Configuring the Debezium connector for the test environment..."
	@$(DOCKER_COMPOSE_SETUP_TEST) run --rm setup-connector
	
	@echo "[*] Executing the full test suite in order (Unit -> Integration -> E2E)..."
	@$(DOCKER_COMPOSE_TEST) exec chorus-tester pytest --quiet tests/unit
	@$(DOCKER_COMPOSE_TEST) exec chorus-tester pytest --quiet tests/integration
	@$(DOCKER_COMPOSE_TEST) exec chorus-tester pytest --quiet tests/e2e
	
	@echo "\n✅ === FULL VERIFICATION SUITE PASSED === ✅"