#!/bin/bash
#
# 🔱 CHORUS Unified E2E Test Suite Orchestrator (Definitive)

set -e
cd "$(dirname "$0")/../.."

echo "--- [E2E Orchestrator] Starting Full System Validation ---"

cleanup() {
  echo "--- [E2E Orchestrator] Performing cleanup ---"
  make stop > /dev/null 2>&1
  make docker-down > /dev/null 2>&1
  echo "--- [E2E Orchestrator] Cleanup complete ---"
}
trap cleanup EXIT ERR INT

# --- Stage 1: Deterministic Failure Test (Default) ---
echo "--- [E2E Orchestrator] Stage 1: Verifying deterministic failure path ---"
make docker-up
yes | make db-reset
make docker-register-cdc

# Run Python services with the API key EXPLICITLY UNSET
echo "--- [E2E Orchestrator] Starting Python services in keyless mode... ---"
export GOOGLE_API_KEY="" 
make run
sleep 15
uv run pytest tests/e2e/test_01_e2e_failure_path.py
make stop

# --- Stage 2: Opt-in Live Happy Path Test ---
if [[ "${RUN_LIVE_E2E_TESTS}" == "true" ]]; then
  echo "--- [E2E Orchestrator] Stage 2: Verifying live happy path (RUN_LIVE_E2E_TESTS=true) ---"
  
  # Check if the key is actually present
  if [[ -z "${GOOGLE_API_KEY_REAL}" ]]; then
    echo "[!] ERROR: RUN_LIVE_E2E_TESTS is true, but GOOGLE_API_KEY_REAL is not set in the environment."
    exit 1
  fi
  
  # Run Python services with the REAL API key
  echo "--- [E2E Orchestrator] Starting Python services with live API key... ---"
  export GOOGLE_API_KEY="${GOOGLE_API_KEY_REAL}"
  make run
  sleep 15
  RUN_LIVE_E2E_TESTS=true uv run pytest tests/e2e/test_02_e2e_happy_path.py
  make stop
else
  echo "--- [E2E Orchestrator] Stage 2: Skipping live happy path test (RUN_LIVE_E2E_TESTS not set to 'true') ---"
fi

echo "--- [E2E Orchestrator] SUCCESS: E2E Validation Complete ---"
