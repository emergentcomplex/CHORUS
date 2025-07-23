# 🔱 CHORUS Command Center
#
# This Makefile provides a single, unified interface for managing the
# CHORUS development lifecycle.

# Use bash for all commands
SHELL := /bin/bash

# Default command when running `make`
.DEFAULT_GOAL := help

# ==============================================================================
# CORE DEVELOPMENT LIFECYCLE
# ==============================================================================

.PHONY: help
help:
	@echo "🔱 CHORUS Command Center"
	@echo "----------------------------------"
	@echo "Usage: make [command]"
	@echo ""
	@echo "Core Commands:"
	@echo "  run              - Start all CHORUS services (UI, Daemons) locally."
	@echo "  stop             - Stop all background CHORUS services."
	@echo "  logs             - Tail the logs for the running daemons."
	@echo "  test             - Run the complete test suite."
	@echo ""
	@echo "Database Management:"
	@echo "  db-reset         - DANGER: Drops all tables and re-initializes the database from schema."
	@echo "  db-populate      - Populates the personas and harvester tasks tables."
	@echo ""
	@echo "Data Pipeline:"
	@echo "  ingest-darpa     - Run the full, multi-stage DARPA ingestion pipeline."
	@echo "  download-model   - Download the sentence-transformer embedding model."
	@echo ""
	@echo "Docker Environment:"
	@echo "  docker-build     - Build the CHORUS Docker images."
	@echo "  docker-up        - Start the full CHORUS stack using Docker Compose."
	@echo "  docker-down      - Stop and remove the Docker containers."

.PHONY: run
run:
	@echo "[*] Starting CHORUS services in the background..."
	@echo "[*] Launching Web UI..."
	python app/web_ui.py &
	@echo "[*] Launching Sentinel Daemon..."
	python chorus_engine/daemons/sentinel.py > sentinel.log 2>&1 &
	@echo "[*] Launching Launcher Daemon..."
	python chorus_engine/daemons/launcher.py > launcher.log 2>&1 &
	@echo "[+] All services started. Use 'make logs' to monitor or 'make stop' to terminate."

.PHONY: stop
stop:
	@echo "[*] Stopping all background CHORUS services..."
	@pkill -f "app/web_ui.py" || true
	@pkill -f "chorus_engine/daemons/sentinel.py" || true
	@pkill -f "chorus_engine/daemons/launcher.py" || true
	@echo "[+] Services stopped."

.PHONY: logs
logs:
	@echo "[*] Tailing logs for Sentinel and Launcher. Press Ctrl+C to exit."
	@tail -f sentinel.log launcher.log

.PHONY: test
test:
	@echo "[*] Running the full CHORUS test suite..."
	python tools/testing/test_usaspending_harvester.py
	python tools/testing/test_newsapi_harvester.py
	python tools/testing/test_arxiv_harvester.py
	# Add other tests here as they are created

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
	@echo "[*] Populating database with personas and harvester tasks..."
	mysql -u $$(grep DB_USER .env | cut -d '=' -f2) -p$$DB_PASSWORD $$(grep DB_NAME .env | cut -d '=' -f2) < tools/setup/populate_personas.sql
	python tools/setup/populate_harvest_tasks.py
	@echo "[+] Database populated."

.PHONY: ingest-darpa
ingest-darpa:
	@echo "[*] Starting full DARPA ingestion pipeline..."
	python tools/ingestion/ingest_1_map_dictionaries.py
	python tools/ingestion/ingest_2_reduce_and_create_dsv_header.py
	python tools/ingestion/ingest_3_generate_dsv_data.py
	python tools/ingestion/ingest_4_populate_vectordb.py --source DARPA
	python tools/ingestion/ingest_5_factor_dsv.py
	@echo "[+] DARPA ingestion complete."

.PHONY: download-model
download-model:
	@echo "[*] Downloading embedding model..."
	python tools/setup/download_embedding_model.py

# ==============================================================================
# DOCKER INTEGRATION
# ==============================================================================

.PHONY: docker-build
docker-build:
	@echo "[*] Building CHORUS Docker images..."
	docker-compose build

.PHONY: docker-up
docker-up:
	@echo "[*] Starting CHORUS stack with Docker Compose..."
	docker-compose up -d

.PHONY: docker-down
docker-down:
	@echo "[*] Stopping CHORUS Docker stack..."
	docker-compose down
