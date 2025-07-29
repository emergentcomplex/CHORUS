# Filename: tests/e2e/test_full_mission.py (Definitive & Venv-Aware)
import pytest
import subprocess
import time
import json
import hashlib
import os
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer

from chorus_engine.config import PROJECT_ROOT, MODEL_DIR
from chorus_engine.adapters.persistence.mariadb_adapter import MariaDBAdapter

pytestmark = pytest.mark.e2e

TEST_QUERY = "Investigate DARPA funding for quantum computing"
MAX_WAIT_SECONDS = 420
POLL_INTERVAL_SECONDS = 15
MODEL_NAME = 'all-mpnet-base-v2'
MODEL_PATH = MODEL_DIR / MODEL_NAME

@pytest.fixture(scope="module")
def db_adapter():
    return MariaDBAdapter()

@pytest.fixture(scope="module", autouse=True)
def ensure_embedding_model():
    if not MODEL_PATH.exists():
        print("\n--- [E2E Pre-requisite] ---")
        print(f"[*] Embedding model not found. Downloading '{MODEL_NAME}'...")
        try:
            MODEL_DIR.mkdir(exist_ok=True)
            SentenceTransformer(MODEL_NAME).save(str(MODEL_PATH))
            print("[+] Model downloaded successfully.")
        except Exception as e:
            pytest.fail(f"Failed to download embedding model. Error: {e}")

@pytest.fixture
def clean_db_and_queue_task(db_adapter):
    print("\n--- [E2E Setup] ---")
    query_data = {"query": TEST_QUERY, "mode": "deep_dive"}
    query_hash = hashlib.md5(json.dumps(query_data, sort_keys=True).encode()).hexdigest()

    conn = db_adapter._get_connection()
    try:
        with conn.cursor() as cursor:
            print(f"[*] Cleaning up previous test data for hash: {query_hash}")
            cursor.execute("DELETE FROM task_progress WHERE query_hash = %s", (query_hash,))
            cursor.execute("DELETE FROM query_state WHERE query_hash = %s", (query_hash,))
            cursor.execute("DELETE FROM task_queue WHERE query_hash = %s", (query_hash,))
            cursor.execute("DELETE FROM harvesting_tasks WHERE is_dynamic = 1")
            conn.commit()

            print(f"[*] Queuing new analysis task: '{TEST_QUERY}'")
            sql = "INSERT INTO task_queue (user_query, query_hash, status) VALUES (%s, %s, 'PENDING')"
            cursor.execute(sql, (json.dumps(query_data), query_hash))
            conn.commit()
    finally:
        if conn: conn.close()
    
    yield query_hash

    print("\n--- [E2E Teardown] ---")
    print("[*] E2E test finished.")


def test_full_analysis_mission(clean_db_and_queue_task, db_adapter):
    query_hash = clean_db_and_queue_task
    
    launcher_path = PROJECT_ROOT / "chorus_engine/infrastructure/daemons/launcher.py"
    sentinel_path = PROJECT_ROOT / "chorus_engine/infrastructure/daemons/sentinel.py"

    python_executable = sys.executable

    launcher_proc, sentinel_proc = None, None
    try:
        print("\n--- [E2E Execution] ---")
        print(f"[*] Using Python interpreter: {python_executable}")
        print("[*] Launching Sentinel and Launcher daemons...")
        
        sentinel_log = open("sentinel_e2e.log", "w")
        launcher_log = open("launcher_e2e.log", "w")

        sentinel_proc = subprocess.Popen(
            [python_executable, str(sentinel_path)], preexec_fn=os.setsid,
            stdout=sentinel_log, stderr=subprocess.STDOUT
        )
        launcher_proc = subprocess.Popen(
            [python_executable, str(launcher_path)], preexec_fn=os.setsid,
            stdout=launcher_log, stderr=subprocess.STDOUT
        )
        
        start_time = time.time()
        final_status = None
        
        print("[*] Monitoring task progress in database...")
        while time.time() - start_time < MAX_WAIT_SECONDS:
            time.sleep(POLL_INTERVAL_SECONDS)
            
            if sentinel_proc.poll() is not None or launcher_proc.poll() is not None:
                pytest.fail("A daemon process terminated unexpectedly. Check e2e logs.")

            conn = db_adapter._get_connection()
            try:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT status FROM task_queue WHERE query_hash = %s", (query_hash,))
                    result = cursor.fetchone()
                    current_status = result['status'] if result else 'UNKNOWN'
                    print(f"  - [{int(time.time() - start_time)}s] Task status: {current_status}")
                    
                    if current_status in ["COMPLETED", "FAILED"]:
                        final_status = current_status
                        break
            finally:
                if conn: conn.close()

        assert final_status == "COMPLETED", f"Task did not complete successfully. Final status was '{final_status}'."

        print("[*] Verifying final report state...")
        conn = db_adapter._get_connection()
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT state_json FROM query_state WHERE query_hash = %s", (query_hash,))
                state_row = cursor.fetchone()
                assert state_row is not None, "No final state was saved to the query_state table."
                
                state_data = json.loads(state_row['state_json'])
                assert "error" not in state_data, f"The final state contained an error: {state_data.get('error')}"
                assert "final_report_with_citations" in state_data, "Final report is missing from state."
        finally:
            if conn: conn.close()

    finally:
        print("\n--- [E2E Cleanup] ---")
        if sentinel_proc and sentinel_proc.poll() is None:
            print("[*] Terminating Sentinel process group...")
            os.killpg(os.getpgid(sentinel_proc.pid), 15)
        if launcher_proc and launcher_proc.poll() is None:
            print("[*] Terminating Launcher process group...")
            os.killpg(os.getpgid(launcher_proc.pid), 15)
        
        if 'sentinel_log' in locals(): sentinel_log.close()
        if 'launcher_log' in locals(): launcher_log.close()
        
        print("[*] Daemons terminated. Check sentinel_e2e.log and launcher_e2e.log for daemon output.")
