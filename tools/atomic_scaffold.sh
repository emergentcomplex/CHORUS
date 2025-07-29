#!/bin/bash
#
# 🔱 CHORUS Atomic Scaffolding Script (v3 - Idempotent)
# This script performs the entire Phase 0 refactoring atomically.
# It uses 'git mv' to ensure file history is preserved.
# It is safe to run multiple times.

echo "[*] Beginning Atomic Scaffolding for Clean Architecture..."

# --- 1. Create the new directory structure ---
echo "[+] Ensuring layer directories exist..."
mkdir -p chorus_engine/core
mkdir -p chorus_engine/app/use_cases
mkdir -p chorus_engine/app/workers
mkdir -p chorus_engine/adapters/harvesters
mkdir -p chorus_engine/adapters/llm
mkdir -p chorus_engine/adapters/persistence
mkdir -p chorus_engine/infrastructure/daemons
mkdir -p chorus_engine/infrastructure/web

# --- 2. Relocate existing components using git mv ---
# The '[ -f file ] &&' construct makes the move idempotent.
echo "[+] Moving components into their new layers..."
[ -f scripts/trident_launcher.py ] && git mv scripts/trident_launcher.py chorus_engine/infrastructure/daemons/launcher.py
[ -f scripts/trident_sentinel.py ] && git mv scripts/trident_sentinel.py chorus_engine/infrastructure/daemons/sentinel.py
[ -f scripts/persona_worker.py ] && git mv scripts/persona_worker.py chorus_engine/app/workers/persona_worker.py
[ -f scripts/harvester_worker.py ] && git mv scripts/harvester_worker.py chorus_engine/app/workers/harvester_worker.py
[ -f scripts/arxiv_harvester.py ] && git mv scripts/arxiv_harvester.py chorus_engine/adapters/harvesters/arxiv_harvester.py
[ -f scripts/newsapi_harvester.py ] && git mv scripts/newsapi_harvester.py chorus_engine/adapters/harvesters/newsapi_harvester.py
[ -f scripts/usajobs_harvester.py ] && git mv scripts/usajobs_harvester.py chorus_engine/adapters/harvesters/usajobs_harvester.py
[ -f scripts/usaspending_harvester.py ] && git mv scripts/usaspending_harvester.py chorus_engine/adapters/harvesters/usaspending_harvester.py
[ -f scripts/db_connector.py ] && git mv scripts/db_connector.py chorus_engine/adapters/persistence/db_connector.py
[ -f scripts/personas.py ] && git mv scripts/personas.py chorus_engine/adapters/persistence/personas.py
[ -f web_ui.py ] && git mv web_ui.py chorus_engine/infrastructure/web/web_ui.py
[ -d scripts/templates ] && git mv scripts/templates chorus_engine/infrastructure/web/

# --- 3. Create all necessary __init__.py files ---
echo "[+] Ensuring all __init__.py files exist..."
touch chorus_engine/__init__.py
touch chorus_engine/core/__init__.py
touch chorus_engine/app/__init__.py
touch chorus_engine/app/use_cases/__init__.py
touch chorus_engine/app/workers/__init__.py
touch chorus_engine/adapters/__init__.py
touch chorus_engine/adapters/llm/__init__.py
touch chorus_engine/adapters/persistence/__init__.py
touch chorus_engine/adapters/harvesters/__init__.py
touch chorus_engine/infrastructure/__init__.py
touch chorus_engine/infrastructure/daemons/__init__.py
touch chorus_engine/infrastructure/web/__init__.py

# --- 4. Clean up the old, now-empty 'scripts' directory ---
# Check if the directory is empty before trying to remove it.
if [ -d "scripts" ] && [ -z "$(ls -A scripts)" ]; then
    echo "[+] Cleaning up empty 'scripts' directory..."
    git rm -r scripts
fi

echo "[✅] SUCCESS: Atomic Scaffolding complete."
echo "[*] Please run 'git status' to review the changes and then commit them."