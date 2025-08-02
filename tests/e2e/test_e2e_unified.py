# Filename: tests/e2e/test_e2e_unified.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This End-to-End test validates the entire multi-tier adversarial pipeline,
# starting from a true, black-box user interaction with the Web UI service.

import pytest
import time
import json
import hashlib
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import requests # Use requests for true black-box testing

pytestmark = pytest.mark.e2e

# --- Configuration ---
E2E_QUERY = "E2E Test: Analyze the strategic implications of advancements in hypersonic missile technology."
MAX_WAIT_SECONDS = 600  # 10 minutes
POLL_INTERVAL_SECONDS = 15
WEB_UI_URL = "http://chorus-web:5001/" # Use the internal Docker service name

# This marker skips the test if the GOOGLE_API_KEY is not present or is an empty string.
requires_api_key = pytest.mark.skipif(
    not os.getenv("GOOGLE_API_KEY"),
    reason="This E2E test requires a live GOOGLE_API_KEY to be set in the environment."
)

# --- Fixtures ---

@pytest.fixture(scope="module")
def db_connection():
    """Provides a single, module-scoped database connection for polling."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            port=os.getenv("DB_PORT", 5432),
            user=os.getenv("DB_USER", "trident_user"),
            password=os.getenv("DB_PASSWORD", "abcd1234"),
            dbname=os.getenv("DB_NAME", "trident_analysis")
        )
        yield conn
        conn.close()
    except psycopg2.OperationalError as e:
        pytest.fail(f"Failed to connect to the database for E2E test setup: {e}")

# --- Helper Functions ---

def queue_task_via_http(db_conn, query_text):
    """
    THE DEFINITIVE FIX: Initiates the E2E test by making a real HTTP POST request
    to the running chorus-web service.
    """
    query_data = {"query": query_text, "mode": "deep_dive"}
    expected_hash = hashlib.md5(json.dumps(query_data, sort_keys=True).encode()).hexdigest()

    # 1. Clean up any previous test data from the database
    with db_conn.cursor() as cursor:
        print(f"\n[*] Cleaning up database for query_hash: {expected_hash}")
        cursor.execute("DELETE FROM director_briefings WHERE query_hash = %s", (expected_hash,))
        cursor.execute("DELETE FROM analyst_reports WHERE query_hash = %s", (expected_hash,))
        cursor.execute("DELETE FROM task_progress WHERE query_hash = %s", (expected_hash,))
        cursor.execute("DELETE FROM query_state WHERE query_hash = %s", (expected_hash,))
        cursor.execute("DELETE FROM task_queue WHERE query_hash = %s", (expected_hash,))
    db_conn.commit()

    # 2. Make the HTTP POST request to the live web service
    print(f"[*] Making HTTP POST to {WEB_UI_URL} for query: '{query_text}'")
    try:
        response = requests.post(
            WEB_UI_URL,
            data={'query_text': query_text, 'mode': 'deep_dive'},
            allow_redirects=False, # We want to inspect the redirect response
            timeout=10
        )
        # Assert the UI interaction was successful
        assert response.status_code == 302, f"Expected a 302 Redirect, but got {response.status_code}. The UI write path is broken."
        redirect_location = response.headers.get('Location')
        assert redirect_location is not None and f'/query/{expected_hash}' in redirect_location, f"Expected redirect to details page for hash {expected_hash}, but got {redirect_location}."
        print(f"[+] UI interaction successful. Service responded with redirect to {redirect_location}.")
    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Failed to connect to the web UI at {WEB_UI_URL}. Is the service running? Error: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during the HTTP request: {e}")


    # 3. Return the hash for the polling function to use
    return expected_hash


def wait_for_final_status(conn, query_hash):
    """
    Polls the database until the task reaches a terminal state (COMPLETED or FAILED).
    """
    start_time = time.time()
    final_status = None

    while time.time() - start_time < MAX_WAIT_SECONDS:
        time.sleep(POLL_INTERVAL_SECONDS)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT status FROM task_queue WHERE query_hash = %s", (query_hash,))
            result = cursor.fetchone()
            status = result['status'] if result else 'UNKNOWN'

            elapsed_time = int(time.time() - start_time)
            print(f"  - [{elapsed_time}s] Current Status: {status}")

            if status in ["COMPLETED", "FAILED"]:
                final_status = status
                break

    return final_status

# --- The Test ---

@requires_api_key
def test_e2e_full_adversarial_pipeline(db_connection):
    """
    Verifies the entire E2E adversarial pipeline via a true, black-box
    HTTP request to the web UI.
    """
    # The new test flow: queue via HTTP, then wait for backend completion.
    query_hash = queue_task_via_http(db_connection, E2E_QUERY)
    print(f"\n--- [E2E Test: Full Pipeline Verification for {query_hash}] ---")

    final_status = wait_for_final_status(db_connection, query_hash)

    if final_status == "COMPLETED":
        print("\n[+] SUCCESS: E2E pipeline finished in a COMPLETED state.")
    elif final_status == "FAILED":
        pytest.fail(f"E2E pipeline failed. Final status was FAILED.")
    else:
        pytest.fail(f"E2E pipeline timed out after {MAX_WAIT_SECONDS} seconds. Last known status was {final_status}.")

    assert final_status == "COMPLETED"
