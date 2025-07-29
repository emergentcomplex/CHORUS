# --- BOOTSTRAP ---
# This ensures the script can be run from anywhere and still find the project root.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
# --- END BOOTSTRAP ---

# Filename: chorus_engine/infrastructure/daemons/launcher.py (Self-Contained)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This is the main entry point for the analysis worker daemon. It acts as the
# "Composition Root" of the application, instantiating the concrete adapters
# and use cases, and then running the main processing loop.


import time
import uuid
import logging
from datetime import datetime, timedelta

from chorus_engine.adapters.llm.gemini_adapter import GeminiAdapter
from chorus_engine.adapters.persistence.mariadb_adapter import MariaDBAdapter
from chorus_engine.adapters.persistence.persona_repo import PersonaRepository
from chorus_engine.app.use_cases.run_analysis_pipeline import RunAnalysisPipeline

# ... (rest of the file is unchanged) ...
TASK_TIMEOUT_MINUTES = 10
POLL_INTERVAL_SECONDS = 10

def check_and_reset_stale_tasks(db_adapter: MariaDBAdapter):
    logging.info(f"[{datetime.now()}] [Launcher] Checking for stale analysis tasks...")
    conn = db_adapter._get_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            timeout_threshold = datetime.now() - timedelta(minutes=TASK_TIMEOUT_MINUTES)
            sql = "UPDATE task_queue SET status = 'PENDING', worker_id = NULL, started_at = NULL WHERE status = 'IN_PROGRESS' AND started_at < %s"
            cursor.execute(sql, (timeout_threshold,))
            if cursor.rowcount > 0:
                logging.info(f"[Launcher] Found and reset {cursor.rowcount} stale task(s).")
        conn.commit()
    finally:
        if conn: conn.close()

def main():
    worker_id = f"launcher-{uuid.uuid4().hex[:8]}"
    logging.basicConfig(level=logging.INFO, format=f'%(asctime)s - %(levelname)s - [{worker_id}] - %(message)s')
    
    logging.info("--- CHORUS Launcher Daemon Initializing ---")
    
    try:
        llm_adapter = GeminiAdapter()
        db_adapter = MariaDBAdapter()
        persona_repo = PersonaRepository()

        analysis_pipeline = RunAnalysisPipeline(
            llm_adapter=llm_adapter,
            db_adapter=db_adapter,
            vector_db_adapter=db_adapter,
            persona_repo=persona_repo
        )
        logging.info("--- All adapters and use cases initialized successfully. ---")
    except Exception as e:
        logging.critical(f"FATAL: Could not initialize adapters. Shutting down. Error: {e}", exc_info=True)
        return

    while True:
        check_and_reset_stale_tasks(db_adapter)
        
        logging.info("Searching for a pending analysis task...")
        
        task = db_adapter.claim_analysis_task(worker_id)
        
        if task:
            logging.info(f"Claimed task {task.query_hash}. Executing analysis pipeline...")
            analysis_pipeline.execute(task)
            logging.info(f"Finished processing task {task.query_hash}.")
        else:
            logging.info(f"No pending analysis tasks found. Sleeping for {POLL_INTERVAL_SECONDS} seconds.")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
