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
import redis
import requests

pytestmark = pytest.mark.e2e

# --- Configuration ---
E2E_QUERY = "E2E Test: Analyze the strategic implications of advancements in hypersonic missile technology."
MAX_WAIT_SECONDS = 600  # 10 minutes
POLL_INTERVAL_SECONDS = 15
WEB_UI_URL = "http://chorus-web:5001/" # Use the internal Docker service name

requires_api_key = pytest.mark.skipif(
    not os.getenv("GOOGLE_API_KEY"),
    reason="This E2E test requires a live GOOGLE_API_KEY to be set in the environment."
)

# --- Fixtures ---

@pytest.fixture(scope="module")
def db_connection_for_cleanup():
    """Provides a DB connection ONLY for cleaning up before the test."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            port=os.getenv("DB_PORT", 5432),
            user=os.getenv("DB_USER", "trident_user"),
            password=os.getenv("DB_PASSWORD", "abcd1234"),
            dbname=os.getenv("DB_NAME", "trident_analysis_test")
        )
        yield conn
        conn.close()
    except psycopg2.OperationalError as e:
        pytest.fail(f"Failed to connect to the database for E2E test cleanup: {e}")

@pytest.fixture(scope="module")
def redis_client():
    """Provides a Redis client for polling the UI's true data source."""
    try:
        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )
        r.ping()
        return r
    except redis.exceptions.ConnectionError as e:
        pytest.fail(f"Failed to connect to Redis for E2E test polling: {e}")

# --- Helper Functions ---

def queue_task_via_http(db_conn, query_text):
    """Initiates the E2E test by making a real HTTP POST request."""
    query_data = {"query": query_text, "mode": "deep_dive"}
    expected_hash = hashlib.md5(json.dumps(query_data, sort_keys=True).encode()).hexdigest()

    with db_conn.cursor() as cursor:
        print(f"\n[*] Cleaning up database for query_hash: {expected_hash}")
        cursor.execute("DELETE FROM director_briefings WHERE query_hash = %s", (expected_hash,))
        cursor.execute("DELETE FROM analyst_reports WHERE query_hash = %s", (expected_hash,))
        cursor.execute("DELETE FROM task_progress WHERE query_hash = %s", (expected_hash,))
        cursor.execute("DELETE FROM query_state WHERE query_hash = %s", (expected_hash,))
        cursor.execute("DELETE FROM task_queue WHERE query_hash = %s", (expected_hash,))
    db_conn.commit()

    print(f"[*] Making HTTP POST to {WEB_UI_URL} for query: '{query_text}'")
    try:
        response = requests.post(
            WEB_UI_URL,
            data={'query_text': query_text, 'mode': 'deep_dive'},
            allow_redirects=False,
            timeout=10
        )
        assert response.status_code == 302
        redirect_location = response.headers.get('Location')
        assert redirect_location and f'/query/{expected_hash}' in redirect_location
        print(f"[+] UI interaction successful. Redirected to {redirect_location}.")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to connect to the web UI at {WEB_UI_URL}. Error: {e}")

    return expected_hash

def wait_for_final_status_in_redis(redis_cli, query_hash):
    """
    Polls Redis until the task reaches a terminal state (COMPLETED or FAILED).
    This correctly simulates the user experience and verifies the CDC pipeline.
    """
    start_time = time.time()
    final_status = None
    redis_key = f"task:{query_hash}"

    while time.time() - start_time < MAX_WAIT_SECONDS:
        time.sleep(POLL_INTERVAL_SECONDS)
        task_state = redis_cli.hgetall(redis_key)
        status = task_state.get('status', 'PENDING')

        elapsed_time = int(time.time() - start_time)
        print(f"  - [{elapsed_time}s] Current Status (from Redis): {status}")

        if status in ["COMPLETED", "FAILED"]:
            final_status = status
            break

    return final_status

# --- The Test ---

@requires_api_key
def test_e2e_full_adversarial_pipeline(db_connection_for_cleanup, redis_client):
    """
    Verifies the entire E2E pipeline via a true, black-box HTTP request,
    and validates the outcome by polling the UI's data source (Redis).
    """
    query_hash = queue_task_via_http(db_connection_for_cleanup, E2E_QUERY)
    print(f"\n--- [E2E Test: Full Pipeline & CDC Verification for {query_hash}] ---")

    final_status = wait_for_final_status_in_redis(redis_client, query_hash)

    if final_status == "COMPLETED":
        print("\n[+] SUCCESS: E2E pipeline finished in a COMPLETED state in Redis.")
    elif final_status == "FAILED":
        pytest.fail(f"E2E pipeline failed. Final status in Redis was FAILED.")
    else:
        pytest.fail(f"E2E pipeline timed out after {MAX_WAIT_SECONDS} seconds. Last known status in Redis was {final_status}.")

    assert final_status == "COMPLETED"