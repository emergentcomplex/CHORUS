# Filename: chorus_engine/infrastructure/daemons/synthesis_daemon.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This daemon is the entry point for the Synthesis (Director) and Judgment tiers.

import time
import uuid
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

from chorus_engine.config import setup_logging
from chorus_engine.adapters.llm.gemini_adapter import GeminiAdapter
from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter
from chorus_engine.adapters.persistence.persona_repo import PersonaRepository
from chorus_engine.app.use_cases.run_director_tier import RunDirectorTier
from chorus_engine.app.use_cases.run_judge_tier import RunJudgeTier

TASK_TIMEOUT_MINUTES = 15
POLL_INTERVAL_SECONDS = 10
INIT_RETRY_SECONDS = 15

setup_logging()
log = logging.getLogger(__name__)

def check_and_reset_stale_tasks(db_adapter: PostgresAdapter):
    """Resets synthesis or judgment tasks that have been in-progress for too long."""
    log.info(f"[{datetime.now()}] [SynthesisDaemon] Checking for stale tasks...")
    conn = db_adapter._get_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            timeout_threshold = datetime.now() - timedelta(minutes=TASK_TIMEOUT_MINUTES)
            sql = """
                UPDATE task_queue SET 
                    status = CASE 
                               WHEN status = 'SYNTHESIS_IN_PROGRESS' THEN 'PENDING_SYNTHESIS'::task_status_enum
                               WHEN status = 'JUDGMENT_IN_PROGRESS' THEN 'PENDING_JUDGMENT'::task_status_enum
                             END, 
                    worker_id = NULL, 
                    started_at = NULL 
                WHERE status IN ('SYNTHESIS_IN_PROGRESS', 'JUDGMENT_IN_PROGRESS') AND started_at < %s
            """
            cursor.execute(sql, (timeout_threshold,))
            if cursor.rowcount > 0:
                log.warning(f"[SynthesisDaemon] Found and reset {cursor.rowcount} stale task(s).")
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

            director_tier_uc = RunDirectorTier(
                llm_adapter=llm_adapter, db_adapter=db_adapter, persona_repo=persona_repo
            )
            judge_tier_uc = RunJudgeTier(
                llm_adapter=llm_adapter, db_adapter=db_adapter, persona_repo=persona_repo
            )
            
            log.info("--- All adapters and use cases initialized successfully. ---")
            return db_adapter, director_tier_uc, judge_tier_uc
        except Exception as e:
            log.warning(f"Failed to initialize dependencies due to: {e}. Retrying in {INIT_RETRY_SECONDS}s...")
            time.sleep(INIT_RETRY_SECONDS)

def main():
    load_dotenv()
    worker_id = f"synth-{uuid.uuid4().hex[:8]}"
    log.info(f"--- CHORUS Synthesis & Judgment Daemon Initializing (Worker ID: {worker_id}) ---")
    
    db_adapter, director_tier_uc, judge_tier_uc = initialize_dependencies()

    while True:
        check_and_reset_stale_tasks(db_adapter)
        
        log.info("Searching for a task awaiting synthesis or judgment...")
        
        task = db_adapter.claim_synthesis_task(worker_id)
        
        if task:
            if task.status == 'SYNTHESIS_IN_PROGRESS':
                log.info(f"Claimed task {task.query_hash} for Director Tier.")
                director_tier_uc.execute(task)
                log.info(f"Finished processing Director Tier for task {task.query_hash}.")
            
            elif task.status == 'JUDGMENT_IN_PROGRESS':
                log.info(f"Claimed task {task.query_hash} for Judge Tier.")
                judge_tier_uc.execute(task)
                log.info(f"Finished processing Judge Tier for task {task.query_hash}.")

            else:
                log.warning(f"Claimed task {task.query_hash} with unexpected status: {task.status}")

        else:
            log.info(f"No tasks awaiting synthesis or judgment found. Sleeping for {POLL_INTERVAL_SECONDS} seconds.")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
