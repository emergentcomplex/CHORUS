# Filename: chorus_engine/infrastructure/daemons/launcher.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This is the main entry point for the analysis worker daemon. It now
# orchestrates the new multi-tier analysis pipeline.

import time
import uuid
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

from chorus_engine.config import setup_logging
from chorus_engine.adapters.llm.gemini_adapter import GeminiAdapter
from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter
from chorus_engine.adapters.persistence.persona_repo import PersonaRepository
from chorus_engine.app.use_cases.run_analyst_tier import RunAnalystTier

TASK_TIMEOUT_MINUTES = 20 # Increased timeout for multi-persona analysis
POLL_INTERVAL_SECONDS = 10
INIT_RETRY_SECONDS = 15

# EXPLICITLY initialize centralized logging
setup_logging()
log = logging.getLogger(__name__)

def check_and_reset_stale_tasks(db_adapter: PostgresAdapter):
    """Resets tasks that have been in-progress for too long."""
    log.info(f"[{datetime.now()}] [Launcher] Checking for stale analysis tasks...")
    conn = db_adapter._get_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            timeout_threshold = datetime.now() - timedelta(minutes=TASK_TIMEOUT_MINUTES)
            # Reset tasks stuck in ANALYSIS_IN_PROGRESS back to PENDING_ANALYSIS
            sql = """
                UPDATE task_queue SET status = 'PENDING_ANALYSIS', worker_id = NULL, started_at = NULL 
                WHERE status = 'ANALYSIS_IN_PROGRESS' AND started_at < %s
            """
            cursor.execute(sql, (timeout_threshold,))
            if cursor.rowcount > 0:
                log.warning(f"[Launcher] Found and reset {cursor.rowcount} stale task(s).")
        conn.commit()
    except Exception as e:
        log.error(f"Error checking for stale tasks: {e}")
        if conn: conn.rollback()
    finally:
        if conn: db_adapter._release_connection(conn)

def initialize_dependencies():
    """
    THE DEFINITIVE FIX: A resilient initialization loop that waits for the DB.
    """
    while True:
        try:
            log.info("Initializing dependencies...")
            llm_adapter = GeminiAdapter()
            db_adapter = PostgresAdapter()
            persona_repo = PersonaRepository()

            # Make a test query to ensure DB is ready
            db_adapter.get_available_harvesters()
            
            analyst_tier_uc = RunAnalystTier(
                llm_adapter=llm_adapter,
                db_adapter=db_adapter,
                vector_db_adapter=db_adapter,
                persona_repo=persona_repo
            )
            log.info("--- All adapters and use cases initialized successfully. ---")
            return db_adapter, analyst_tier_uc
        except Exception as e:
            log.warning(f"Failed to initialize dependencies due to: {e}. Retrying in {INIT_RETRY_SECONDS}s...")
            time.sleep(INIT_RETRY_SECONDS)

def main():
    load_dotenv()
    worker_id = f"launcher-{uuid.uuid4().hex[:8]}"
    log.info(f"--- CHORUS Launcher Daemon Initializing (Worker ID: {worker_id}) ---")
    
    db_adapter, analyst_tier_uc = initialize_dependencies()

    while True:
        check_and_reset_stale_tasks(db_adapter)
        
        log.info("Searching for a pending analysis task...")
        
        task = db_adapter.claim_analysis_task(worker_id)
        
        if task:
            log.info(f"Claimed task {task.query_hash}. Executing Analyst Tier...")
            analyst_tier_uc.execute(task)
            log.info(f"Finished processing Analyst Tier for task {task.query_hash}.")
        else:
            log.info(f"No pending analysis tasks found. Sleeping for {POLL_INTERVAL_SECONDS} seconds.")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
