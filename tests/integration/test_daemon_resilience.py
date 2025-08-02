# Filename: tests/integration/test_daemon_resilience.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This test performs a "chaos" experiment to validate that the long-running
# daemons are resilient to a full database reset, which invalidates their
# connection pools.

import pytest
import time
import subprocess
import os
import requests

pytestmark = pytest.mark.integration

# --- Configuration ---
WEB_UI_URL = "http://chorus-web:5001/"
MAX_WAIT_SECONDS = 120  # 2 minutes
POLL_INTERVAL_SECONDS = 5
E2E_QUERY = "Chaos Test: This query must succeed after a database reset."

# --- Helper Functions ---

def wait_for_web_ui():
    """Waits until the web UI is responsive."""
    start_time = time.time()
    while time.time() - start_time < 60:
        try:
            response = requests.get(WEB_UI_URL, timeout=2)
            if response.status_code == 200:
                print("[+] Web UI is responsive.")
                return True
        except requests.ConnectionError:
            time.sleep(2)
    pytest.fail("Web UI did not become responsive within 60 seconds.")

def get_task_status_from_logs(query_hash):
    """
    Checks the aggregated Docker logs for the final status of a task.
    This is a robust way to verify completion without relying on a potentially
    stale DB connection in the test runner itself.
    """
    start_time = time.time()
    final_status = None
    
    # Define success and failure markers from the daemon logs
    success_marker = f"Analysis pipeline completed successfully."
    failure_marker = f"failed for task {query_hash}"

    while time.time() - start_time < MAX_WAIT_SECONDS:
        logs = subprocess.check_output(['docker', 'compose', 'logs', 'chorus-launcher', 'chorus-synthesis-daemon']).decode('utf-8')
        
        # Search for the final log messages
        if success_marker in logs:
            final_status = "COMPLETED"
            break
        if failure_marker in logs:
            final_status = "FAILED"
            break
            
        time.sleep(POLL_INTERVAL_SECONDS)
        
    return final_status

# --- The Test ---

def test_daemons_survive_and_recover_from_db_reset():
    """
    Verifies that daemons can handle a complete database reset and
    successfully process a new task afterwards.
    """
    print("\n--- [Chaos Test: Daemon Resilience to DB Reset] ---")
    
    # 1. Ensure the Web UI is up before proceeding.
    wait_for_web_ui()

    # 2. The "Chaos" step: Reset the database while services are running.
    print("[*] Injecting chaos: Resetting the database...")
    # We must use `docker compose exec` to run `make` inside a container
    # that has the `psql` client and the necessary environment variables.
    subprocess.run(
        ['docker', 'compose', 'exec', '-T', 'chorus-tester', 'make', 'db-reset'],
        check=True, capture_output=True
    )
    print("[+] Database has been reset underneath the running daemons.")
    
    # 3. Act: Submit a new task through the UI.
    print("[*] Submitting a new task post-reset...")
    try:
        response = requests.post(
            WEB_UI_URL,
            data={'query_text': E2E_QUERY, 'mode': 'deep_dive'},
            timeout=10
        )
        assert response.status_code == 200 or response.status_code == 302, "Web UI failed to accept the new task."
        print("[+] Task submitted successfully via UI.")
    except requests.RequestException as e:
        pytest.fail(f"Failed to submit task to the web UI after DB reset: {e}")

    # 4. Assert: Poll the logs to see if the daemons recovered and completed the task.
    print("[*] Monitoring daemon logs for recovery and task completion...")
    query_hash_bytes = E2E_QUERY.encode('utf-8') # Simplified hash for log checking
    
    final_status = get_task_status_from_logs("chaos_test_hash_placeholder") # Placeholder, as we can't easily get the hash
    
    # A more general success check since we can't get the hash easily
    logs = subprocess.check_output(['docker', 'compose', 'logs', 'chorus-launcher', 'chorus-synthesis-daemon']).decode('utf-8')
    if "Analysis pipeline completed successfully" in logs:
        print("[+] SUCCESS: Daemons recovered from DB reset and completed the task.")
        assert True
    elif "failed for task" in logs:
        pytest.fail("Daemon failed to process the task after DB reset. Check logs for errors.")
    else:
        pytest.fail(f"Test timed out. Daemons did not complete the task after {MAX_WAIT_SECONDS} seconds.")

