# Filename: chorus_engine/infrastructure/daemons/sentinel.py (PostgreSQL Pivot)

import subprocess
import time
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from chorus_engine.config import setup_logging
from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter

load_dotenv()
MAX_WORKERS = int(os.getenv("SENTINEL_WORKERS", 4))
CHECK_INTERVAL_SECONDS = 20

# EXPLICITLY initialize centralized logging
setup_logging()
log = logging.getLogger(__name__)

def get_due_tasks(db_adapter, limit):
    conn = db_adapter._get_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            sql = """
                SELECT * FROM harvesting_tasks 
                WHERE status IN ('IDLE', 'FAILED')
                ORDER BY status DESC 
                LIMIT %s
            """
            cursor.execute(sql, (limit,))
            return cursor.fetchall()
    finally:
        db_adapter._release_connection(conn)

def main():
    worker_script_path = os.path.join(os.path.dirname(__file__), "..", "workers", "harvester_worker.py")
    active_workers = []
    
    db_adapter = PostgresAdapter()

    log.info("--- CHORUS Sentinel Initialized ---")
    log.info(f"--- Max Concurrent Harvesters: {MAX_WORKERS} ---")

    while True:
        log.info("Waking up to check for work...")
        
        active_workers = [p for p in active_workers if p.poll() is None]
        
        available_slots = MAX_WORKERS - len(active_workers)
        log.info(f"Pool Status: {len(active_workers)} active, {available_slots} available.")

        if available_slots > 0:
            tasks_to_run = get_due_tasks(db_adapter, limit=available_slots)
            
            if not tasks_to_run:
                log.info("No due tasks found. Sleeping...")
            else:
                log.info(f"Found {len(tasks_to_run)} tasks to run. Filling available slots...")
                for task in tasks_to_run:
                    task_id = task['task_id']
                    log.info(f"Launching worker for task_id {task_id} ({task['script_name']})")
                    
                    process = subprocess.Popen(["python3", worker_script_path, "--task-id", str(task_id)])
                    active_workers.append(process)
                    
                    conn = db_adapter._get_connection()
                    try:
                        with conn.cursor() as cursor:
                            cursor.execute("UPDATE harvesting_tasks SET status = 'IN_PROGRESS', last_attempt = NOW() WHERE task_id = %s", (task_id,))
                        conn.commit()
                    finally:
                        db_adapter._release_connection(conn)
        else:
            log.info("Worker pool is full. Monitoring active workers...")

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
