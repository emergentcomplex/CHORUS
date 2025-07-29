cat << 'EOF' > Makefile
# 🔱 CHORUS Command Center
#
# This Makefile provides a single, unified interface for managing the
# CHORUS development lifecycle.

# Use bash for all commands
SHELL := /bin/bash

# Default command when running `make`
.DEFAULT_GOAL := help

# ==============================================================================
# SETUP & CORE LIFECYCLE
# ==============================================================================

.PHONY: help
help:
	@echo "🔱 CHORUS Command Center"
	@echo "----------------------------------"
	@echo "Usage: make [command]"
	@echo ""
	@echo "Setup:"
	@echo "  install          - Install project dependencies and the chorus_engine package."
	@echo ""
	@echo "Core Commands:"
	@echo "  run              - Start all CHORUS services (UI, Daemons) locally."
	@echo "  stop             - Stop all background CHORUS services."
	@echo "  logs             - Tail the logs for the running daemons."
	@echo ""
	@echo "Testing (The Great Verification):"
	@echo "  test             - Run all fast tests (unit & integration). Ideal for CI."
	@echo "  test-e2e         - Run the slow, full end-to-end mission test."
	@echo "  test-arch        - Run only the architectural validation checks."
	@echo ""
	@echo "Database Management:"
	@echo "  db-reset         - DANGER: Drops all tables and re-initializes the database from schema."
	@echo "  db-populate      - Populates the harvester tasks tables."
	@echo ""
	@echo "Data Pipeline:"
	@echo "  ingest-darpa     - Run the full, multi-stage DARPA ingestion pipeline."
	@echo "  download-model   - Download the sentence-transformer embedding model."
	@echo ""
	@echo "Audits:"
	@echo "  audit-philosophy - Run the qualitative LLM-based audit for philosophical alignment."

.PHONY: install
install:
	@echo "[*] Installing dependencies from requirements.txt..."
	pip install -r requirements.txt
	@echo "[*] Installing chorus_engine in editable mode..."
	pip install -e .
	@echo "[+] Installation complete."

.PHONY: run
run:
	@echo "[*] Starting CHORUS services in the background..."
	python3 -m chorus_engine.infrastructure.web.web_ui &
	python3 -m chorus_engine.infrastructure.daemons.sentinel > sentinel.log 2>&1 &
	python3 -m chorus_engine.infrastructure.daemons.launcher > launcher.log 2>&1 &
	@echo "[+] All services started. Use 'make logs' to monitor or 'make stop' to terminate."

.PHONY: stop
stop:
	@echo "[*] Stopping all background CHORUS services..."
	@pkill -f "chorus_engine.infrastructure.web.web_ui" || true
	@pkill -f "chorus_engine.infrastructure.daemons.sentinel" || true
	@pkill -f "chorus_engine.infrastructure.daemons.launcher" || true
	@echo "[+] Services stopped."

.PHONY: logs
logs:
	@echo "[*] Tailing logs for Sentinel and Launcher. Press Ctrl+C to exit."
	@tail -f sentinel.log launcher.log

.PHONY: test
test:
	@echo "[*] Running unit and integration tests..."
	pytest tests/unit/ tests/integration/

.PHONY: test-e2e
test-e2e:
	@echo "[*] Running end-to-end mission test..."
	pytest tests/e2e/

.PHONY: test-arch
test-arch:
	@echo "[*] Running architectural validation..."
	python3 -m tools.testing.validate_architecture

# ==============================================================================
# DATABASE & DATA MANAGEMENT
# ==============================================================================

.PHONY: db-reset
db-reset:
	@read -p "DANGER: This will drop all tables and delete all data. Are you sure? (y/N) " choice; \
	if [[ "$$choice" == "y" || "$$choice" == "Y" ]]; then \
		echo "[*] Resetting database..."; \
		mysql -u $$(grep DB_USER .env | cut -d '=' -f2) -p$$DB_PASSWORD $$(grep DB_NAME .env | cut -d '=' -f2) < tools/setup/schema.sql; \
		echo "[+] Database schema reset successfully."; \
	else \
		echo "Aborted."; \
	fi

.PHONY: db-populate
db-populate:
	@echo "[*] Populating database with harvester tasks..."
	python3 -m tools.setup.populate_harvest_tasks
	@echo "[+] Database populated."

.PHONY: ingest-darpa
ingest-darpa:
	@echo "[*] Starting full DARPA ingestion pipeline..."
	python3 -m tools.ingestion.ingest_1_map_dictionaries
	python3 -m tools.ingestion.ingest_2_reduce_and_create_dsv_header
	python3 -m tools.ingestion.ingest_3_generate_dsv_data
	python3 -m tools.ingestion.ingest_4_populate_vectordb --source DARPA
	python3 -m tools.ingestion.ingest_5_factor_dsv
	@echo "[+] DARPA ingestion complete."

.PHONY: download-model
download-model:
	@echo "[*] Downloading embedding model..."
	python3 -m tools.setup.download_embedding_model

# ==============================================================================
# ARCHITECTURAL & PHILOSOPHICAL AUDITS
# ==============================================================================

.PHONY: audit-philosophy
audit-philosophy:
	@echo "[*] Running qualitative audit for philosophical alignment..."
	python3 -m tools.testing.validate_philosophy
EOF