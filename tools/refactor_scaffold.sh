#!/bin/bash
#
# 🔱 CHORUS Atomic Scaffolding Script (v2)
# This script is idempotent and will exit immediately on any error.

set -e

echo "[*] Beginning Atomic Scaffolding..."

# --- 1. Create the new directory structure ---
echo "[+] Creating new layer directories..."
mkdir -p chorus_engine/core
mkdir -p chorus_engine/app/use_cases
mkdir -p chorus_engine/app/workers
mkdir -p chorus_engine/adapters/harvesters
mkdir -p chorus_engine/adapters/llm
mkdir -p chorus_engine/adapters/persistence
mkdir -p chorus_engine/infrastructure/daemons
mkdir -p chorus_engine/infrastructure/web

# --- 2. Relocate existing components using git mv ---
echo "[+] Moving existing components into their new layers..."
git mv chorus_engine/daemons/launcher.py chorus_engine/infrastructure/daemons/launcher.py
git mv chorus_engine/daemons/sentinel.py chorus_engine/infrastructure/daemons/sentinel.py
git mv chorus_engine/workers/persona_worker.py chorus_engine/app/workers/persona_worker.py
git mv chorus_engine/workers/harvester_worker.py chorus_engine/app/workers/harvester_worker.py
git mv chorus_engine/harvesters/arxiv_harvester.py chorus_engine/adapters/harvesters/arxiv_harvester.py
git mv chorus_engine/harvesters/newsapi_harvester.py chorus_engine/adapters/harvesters/newsapi_harvester.py
git mv chorus_engine/harvesters/usajobs_harvester.py chorus_engine/adapters/harvesters/usajobs_harvester.py
git mv chorus_engine/harvesters/usaspending_harvester.py chorus_engine/adapters/harvesters/usaspending_harvester.py
git mv chorus_engine/utils/db_connector.py chorus_engine/adapters/persistence/db_connector.py
git mv chorus_engine/utils/personas.py chorus_engine/adapters/persistence/personas.py
git mv app/web_ui.py chorus_engine/infrastructure/web/web_ui.py
git mv app/templates chorus_engine/infrastructure/web/

# --- 3. Clean up old, now-empty directories from git ---
echo "[+] Cleaning up old directories..."
git rm -r chorus_engine/daemons
git rm -r chorus_engine/workers
git rm -r chorus_engine/harvesters
git rm -r chorus_engine/utils
git rm -r app

# --- 4. Create all necessary __init__.py files ---
echo "[+] Creating __init__.py files to define packages..."
touch chorus_engine/core/__init__.py
touch chorus_engine/app/__init__.py
touch chorus_engine/app/use_cases/__init__.py
touch chorus_engine/adapters/__init__.py
touch chorus_engine/adapters/llm/__init__.py
touch chorus_engine/adapters/persistence/__init__.py
touch chorus_engine/infrastructure/__init__.py
touch chorus_engine/infrastructure/web/__init__.py
touch chorus_engine/adapters/harvesters/__init__.py

echo "[✅] SUCCESS: Atomic Scaffolding complete. The repository is now in the Clean Architecture structure."
echo "[*] Please review the changes with 'git status' and then commit them."