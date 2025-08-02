# Filename: chorus_engine/infrastructure/daemons/launcher.py (Definitively Corrected)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This is the main entry point for the analysis worker daemon.

import time
import uuid
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv # THE DEFINITIVE FIX

from chorus_engine.config import setup_logging
from chorus_engine.adapters.llm.gemini_adapter import GeminiAdapter
from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter
from chorus_engine.adapters.persistence.persona_repo import PersonaRepository
from chorus_engine.app.use_cases.run_analysis_pipeline import RunAnalysisPipeline

TASK_TIMEOUT_MINUTES = 10
POLL_INTERVAL_SECONDS = 10

# EXPLICITLY initialize centralized logging
setup_logging()

def check_and_reset_stale_tasks(db_adapter: PostgresAdapter):
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
        db_adapter._release_connection(conn)

def main():
    # THE DEFINITIVE FIX: The application entry point is responsible for loading the environment.
    load_dotenv()
    worker_id = f"launcher-{uuid.uuid4().hex[:8]}"
    log = logging.getLogger(__name__)
    log.info(f"--- CHORUS Launcher Daemon Initializing (Worker ID: {worker_id}) ---")
    
    try:
        llm_adapter = GeminiAdapter()
        db_adapter = PostgresAdapter()
        persona_repo = PersonaRepository()

        analysis_pipeline = RunAnalysisPipeline(
            llm_adapter=llm_adapter,
            db_adapter=db_adapter,
            vector_db_adapter=db_adapter,
            persona_repo=persona_repo
        )
        log.info("--- All adapters and use cases initialized successfully. ---")
    except Exception as e:
        log.critical(f"FATAL: Could not initialize adapters. Shutting down. Error: {e}", exc_info=True)
        return

    while True:
        check_and_reset_stale_tasks(db_adapter)
        
        log.info("Searching for a pending analysis task...")
        
        task = db_adapter.claim_analysis_task(worker_id)
        
        if task:
            log.info(f"Claimed task {task.query_hash}. Executing analysis pipeline...")
            analysis_pipeline.execute(task)
            log.info(f"Finished processing task {task.query_hash}.")
        else:
            log.info(f"No pending analysis tasks found. Sleeping for {POLL_INTERVAL_SECONDS} seconds.")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
