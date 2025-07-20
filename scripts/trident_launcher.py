# Filename: scripts/trident_launcher.py (v2.1 - Direct Fetch)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# v2.1: Implements a more robust method for detecting pending tasks.
#       Instead of counting, it directly attempts to fetch a PENDING task,
#       making the logic simpler and less prone to driver inconsistencies.

import subprocess
import time
import os
from datetime import datetime, timedelta
from db_connector import get_db_connection
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
NUM_WORKERS = int(os.getenv("TRIDENT_WORKERS", 3))
TASK_TIMEOUT_MINUTES = 10

def check_and_reset_stale_tasks():
    """Finds and resets stale IN_PROGRESS tasks."""
    print(f"[{datetime.now()}] [Launcher] Checking for stale analysis tasks...")
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            timeout_threshold = datetime.now() - timedelta(minutes=TASK_TIMEOUT_MINUTES)
            sql = "UPDATE task_queue SET status = 'PENDING', worker_id = NULL, started_at = NULL WHERE status = 'IN_PROGRESS' AND started_at < %s"
            cursor.execute(sql, (timeout_threshold,))
            if cursor.rowcount > 0:
                print(f"[Launcher] Found and reset {cursor.rowcount} stale task(s).")
        conn.commit()
    finally:
        conn.close()

def main():
    """The main loop for the CHORUS analysis launcher."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "persona_worker.py")
    workers = []

    while True:
        check_and_reset_stale_tasks()
        workers = [p for p in workers if p.poll() is None]
        
        if len(workers) < NUM_WORKERS:
            # --- THE DEFINITIVE FIX ---
            # Instead of counting, we directly check if a pending task exists.
            # This is a more reliable and direct way to determine if work needs to be done.
            has_pending_tasks = False
            conn = get_db_connection()
            if conn:
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1 FROM task_queue WHERE status = 'PENDING' LIMIT 1")
                        if cursor.fetchone():
                            has_pending_tasks = True
                finally:
                    conn.close()

            if has_pending_tasks:
                needed_workers = min(NUM_WORKERS - len(workers), 1) # Start one worker at a time to be safe
                for _ in range(needed_workers):
                    print(f"[Launcher] Pending tasks found. Starting a new persona worker...")
                    process = subprocess.Popen(["python3", script_path])
                    workers.append(process)
            else:
                print("[Launcher] No pending analysis tasks found.")

        print(f"[Launcher] {len(workers)} persona workers are active. Next check in 10 seconds.")
        time.sleep(10)

if __name__ == "__main__":
    main()