# Filename: tests/e2e/test_e2e_unified.py
import pytest
import time
import json
import hashlib
import os
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

pytestmark = pytest.mark.e2e

HAPPY_PATH_QUERY = "E2E Happy Path: Quantum Computing"
UNHAPPY_PATH_QUERY = "E2E Unhappy Path: Forced Failure"
MAX_WAIT_SECONDS = 120
POLL_INTERVAL_SECONDS = 10

# This marker skips the test if the GOOGLE_API_KEY is not present or is an empty string
requires_api_key = pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="This test requires a live GOOGLE_API_KEY.")

@pytest.fixture(scope="function")
def db_connection():
    """Provides a database connection for the test function."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", 5432),
        user=os.getenv("DB_USER", "trident_user"),
        password=os.getenv("DB_PASSWORD", "abcd1234"),
        dbname=os.getenv("DB_NAME", "trident_analysis")
    )
    yield conn
    conn.close()

def queue_task(conn, query_text):
    """Helper function to clean up and queue a new task."""
    query_data = {"query": query_text, "mode": "deep_dive"}
    query_hash = hashlib.md5(json.dumps(query_data, sort_keys=True).encode()).hexdigest()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM task_progress WHERE query_hash = %s", (query_hash,))
        cursor.execute("DELETE FROM query_state WHERE query_hash = %s", (query_hash,))
        cursor.execute("DELETE FROM task_queue WHERE query_hash = %s", (query_hash,))
        conn.commit()
        sql = "INSERT INTO task_queue (user_query, query_hash, status) VALUES (%s, %s, 'PENDING')"
        cursor.execute(sql, (json.dumps(query_data), query_hash))
        conn.commit()
    return query_hash

def wait_for_final_status(conn, query_hash):
    """Polls the database until a final status (COMPLETED or FAILED) is reached."""
    start_time = time.time()
    final_status = None
    while time.time() - start_time < MAX_WAIT_SECONDS:
        time.sleep(POLL_INTERVAL_SECONDS)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT status FROM task_queue WHERE query_hash = %s", (query_hash,))
            result = cursor.fetchone()
            status = result['status'] if result else 'UNKNOWN'
            print(f"  - [{int(time.time() - start_time)}s] Status: {status}")
            if status in ["COMPLETED", "FAILED"]:
                final_status = status
                break
    return final_status

def test_e2e_unhappy_path_mission(db_connection):
    """
    Verifies the E2E failure path. This test runs when no API key is provided.
    """
    if os.getenv("GOOGLE_API_KEY"):
        pytest.skip("Skipping unhappy path test because GOOGLE_API_KEY is set.")
    
    query_hash = queue_task(db_connection, UNHAPPY_PATH_QUERY)
    print(f"\n--- [E2E Unhappy Path: {query_hash}] ---")
    final_status = wait_for_final_status(db_connection, query_hash)
    assert final_status == "FAILED"
    print("[+] SUCCESS: Unhappy path mission failed as expected.")

@requires_api_key
def test_e2e_happy_path_mission(db_connection):
    """
    Verifies the E2E happy path. This test is skipped if no API key is provided.
    """
    query_hash = queue_task(db_connection, HAPPY_PATH_QUERY)
    print(f"\n--- [E2E Happy Path: {query_hash}] ---")
    final_status = wait_for_final_status(db_connection, query_hash)
    assert final_status == "COMPLETED"
    print("[+] SUCCESS: Happy path mission completed as expected.")
