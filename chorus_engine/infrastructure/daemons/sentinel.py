# Filename: scripts/trident_sentinel.py (v2.0 - Pool Manager)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# v2.0: Upgrades the Sentinel to a true worker pool manager. It now
#       respects the SENTINEL_WORKERS limit, preventing the "thundering herd"
#       problem and ensuring stable operation under heavy load.

import subprocess
import time
import os
from datetime import datetime
from db_connector import get_db_connection
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
# This now acts as a strict concurrency limit
MAX_WORKERS = int(os.getenv("SENTINEL_WORKERS", 4))
CHECK_INTERVAL_SECONDS = 20 # Check more frequently

def get_due_tasks(limit):
    """
    Finds tasks that are due to be run, up to the specified limit.
    It prioritizes IDLE tasks to ensure new work is picked up.
    """
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            # Prioritize IDLE tasks, but also pick up failed tasks for retry
            sql = """
                SELECT * FROM harvesting_tasks 
                WHERE status IN ('IDLE', 'FAILED')
                ORDER BY status DESC 
                LIMIT %s
            """
            cursor.execute(sql, (limit,))
            return cursor.fetchall()
    finally:
        conn.close()

def main():
    """The main loop for the Sentinel daemon."""
    worker_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "harvester_worker.py")
    active_workers = []

    print("--- CHORUS Sentinel (v2.0 - Pool Manager) Initialized ---")
    print(f"--- Max Concurrent Harvesters: {MAX_WORKERS} ---")

    while True:
        print(f"\n[{datetime.now()}] [Sentinel] Waking up to check for work...")
        
        # 1. Clean up completed workers from the pool
        active_workers = [p for p in active_workers if p.poll() is None]
        
        # 2. Check if there are available slots in the worker pool
        available_slots = MAX_WORKERS - len(active_workers)
        print(f"[Sentinel] Pool Status: {len(active_workers)} active, {available_slots} available.")

        if available_slots > 0:
            # 3. Fetch due tasks to fill the available slots
            tasks_to_run = get_due_tasks(limit=available_slots)
            
            if not tasks_to_run:
                print("[Sentinel] No due tasks found. Sleeping...")
            else:
                print(f"[Sentinel] Found {len(tasks_to_run)} tasks to run. Filling available slots...")
                for task in tasks_to_run:
                    task_id = task['task_id']
                    print(f"[Sentinel] Launching worker for task_id {task_id} ({task['script_name']})")
                    
                    # Launch the worker process
                    process = subprocess.Popen(["python3", worker_script_path, "--task-id", str(task_id)])
                    active_workers.append(process)
                    
                    # Immediately mark the task as IN_PROGRESS so it's not picked up again
                    conn = get_db_connection()
                    try:
                        with conn.cursor() as cursor:
                            cursor.execute("UPDATE harvesting_tasks SET status = 'IN_PROGRESS', last_attempt = NOW() WHERE task_id = %s", (task_id,))
                        conn.commit()
                    finally:
                        conn.close()
        else:
            print("[Sentinel] Worker pool is full. Monitoring active workers...")

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()