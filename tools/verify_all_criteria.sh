#!/bin/bash
#
# 🔱 CHORUS Canonical Verification Protocol (v4 - Maximally Concise)
#
# This script suppresses ALL successful output to produce the smallest possible log.
# It only produces output upon failure.

set -e

LOG_FILE="verification_protocol.log"
> "$LOG_FILE" # Clear previous log file

exec &> >(tee -a "$LOG_FILE")

# --- Helper Functions for Reporting ---
print_header() {
    echo ""
    echo "================================================================================"
    echo "🔱 $1"
    echo "================================================================================"
}

print_success() {
    echo "✅ SUCCESS: $1"
}

print_failure() {
    echo "❌ FAILURE: $1"
    # On failure, dump the logs of the relevant environment for diagnosis.
    env_prefix=$(echo "$1" | sed -n 's/.*(\(.*\)).*/\1/p')
    if [ -n "$env_prefix" ]; then
        echo "[!] DUMPING LOGS FOR FAILED ENVIRONMENT: ${env_prefix}"
        docker compose --env-file ".env.${env_prefix}" -f "docker-compose.${env_prefix}.yml" logs --no-color || echo "Log dump failed."
    fi
    exit 1
}

# ================================================================================
#                       START OF VERIFICATION PROTOCOL
# ================================================================================

print_header "INITIALIZING: Ensuring a clean Docker environment"
echo "[*] Running 'make stop-all' and pruning volumes..."
make stop-all > /dev/null 2>&1
docker volume prune -f > /dev/null 2>&1
print_success "Environment is clean. Beginning verification."

# --- AC-1: Verify Development Environment ---
print_header "AC-1: Verifying Development Environment ('make run-dev')"
echo "[*] Executing 'make run-dev' (output suppressed on success)..."
make run-dev > /dev/null 2>&1
echo "[*] Verifying services and UI..."
if ! docker compose --env-file .env.dev -f docker-compose.dev.yml ps | grep -v 'setup-connector' | grep -q 'running (healthy)'; then
    print_failure "AC-1 (dev): One or more dev services failed to start or are unhealthy."
fi
if [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5002)" -ne 200 ]; then
    print_failure "AC-1 (dev): Dev UI is not accessible on port 5002."
fi
make stop-dev > /dev/null 2>&1
print_success "AC-1 Verification Complete."

# --- AC-2: Verify Production Environment ---
print_header "AC-2: Verifying Production Environment ('make run-prod')"
echo "[*] Executing 'make run-prod' (output suppressed on success)..."
make run-prod > /dev/null 2>&1
echo "[*] Verifying services and UI..."
if ! docker compose --env-file .env.prod -f docker-compose.prod.yml ps | grep -v 'setup-connector' | grep -q 'running (healthy)'; then
    print_failure "AC-2 (prod): One or more prod services failed to start or are unhealthy."
fi
if [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5001)" -ne 200 ]; then
    print_failure "AC-2 (prod): Prod UI is not accessible on port 5001."
fi
make stop-prod > /dev/null 2>&1
print_success "AC-2 Verification Complete."

# --- AC-3: Verify Verification Environment ---
print_header "AC-3: Verifying Verification Environment ('make test')"
echo "[*] Executing the full, hermetic test suite with 'make test'..."
make test
print_success "AC-3 Verification Complete. The full test suite passed."

# --- AC-4: Verify Concurrency ---
print_header "AC-4: Verifying Concurrent Environment Operation"
echo "[*] Starting dev and prod environments simultaneously (output suppressed)..."
make run-dev > /dev/null 2>&1 &
PID_DEV=$!
make run-prod > /dev/null 2>&1 &
PID_PROD=$!
wait $PID_DEV
wait $PID_PROD
echo "[*] Verifying concurrent UI access..."
if [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5001)" -ne 200 ] || \
   [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5002)" -ne 200 ]; then
    print_failure "AC-4 (concurrency): Failed to access both UIs concurrently."
fi
make stop-dev > /dev/null 2>&1
make stop-prod > /dev/null 2>&1
print_success "AC-4 Verification Complete."

# --- AC-5: Verify Test Isolation ---
print_header "AC-5: Verifying Test Isolation"
echo "[*] Starting dev and prod environments (output suppressed)..."
make run-dev > /dev/null 2>&1
make run-prod > /dev/null 2>&1
echo "[*] Running 'make test' while other environments are active..."
make test
make stop-dev > /dev/null 2>&1
make stop-prod > /dev/null 2>&1
print_success "AC-5 Verification Complete."

# --- AC-6: Verify Data Isolation ---
print_header "AC-6: Verifying Data Isolation (Volume Creation)"
echo "[*] Creating and verifying distinct volumes..."
make run-dev > /dev/null 2>&1
make stop-dev > /dev/null 2>&1
make run-prod > /dev/null 2>&1
make stop-prod > /dev/null 2>&1
if ! docker volume ls | grep -q "chorus-dev_postgres_data_dev" || \
   ! docker volume ls | grep -q "chorus-prod_postgres_data_prod"; then
    print_failure "AC-6 (data-isolation): One or both of the required named volumes were not created."
fi
docker volume rm chorus-dev_postgres_data_dev chorus-prod_postgres_data_prod > /dev/null 2>&1
print_success "AC-6 Verification Complete."

# --- AC-7: Verify Final State ---
print_header "AC-7: Verifying Final State (Cleanup)"
echo "[*] Checking for the absence of the old 'docker-compose.yml' file..."
if [ -f "docker-compose.yml" ]; then
    print_failure "AC-7 (cleanup): The obsolete 'docker-compose.yml' file still exists."
fi
print_success "AC-7 Verification Complete."

# --- FINAL SUMMARY ---
print_header "VERIFICATION PROTOCOL COMPLETE"
echo "All 7 Acceptance Criteria have been successfully verified."
echo "The complete log of this verification process is available in: ${LOG_FILE}"
EOF

echo "[+] SUCCESS: Makefile and verification script have been updated for MAXIMALLY CONCISE logging."
echo "[!] Please run the verification script again: ./verify_all_criteria.sh"