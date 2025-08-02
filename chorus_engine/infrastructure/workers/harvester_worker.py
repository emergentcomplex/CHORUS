# Filename: chorus_engine/infrastructure/workers/harvester_worker.py (PostgreSQL Pivot)

import argparse
import json
import logging
import uuid
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
import psycopg2.extras

from chorus_engine.config import setup_logging
from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter
from chorus_engine.adapters.harvesters.usajobs_harvester import USAJobsHarvester
from chorus_engine.adapters.harvesters.usaspending_harvester import USASpendingHarvester
from chorus_engine.adapters.harvesters.arxiv_harvester import ArxivHarvester
from chorus_engine.adapters.harvesters.govinfo_harvester import GovInfoHarvester

# --- CONFIGURATION ---
DATA_LAKE_DIR = Path(__file__).resolve().parents[3] / 'datalake'
DATA_LAKE_DIR.mkdir(exist_ok=True)

# --- Centralized Logging ---
setup_logging()
log = logging.getLogger(__name__)
sli_logger = logging.getLogger('sli')

def update_task_status(db_adapter, task_id, status, worker_id=None):
    """Updates the status of a task in the database using the adapter."""
    conn = db_adapter._get_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            if status == 'COMPLETED':
                sql = "UPDATE harvesting_tasks SET status = %s, worker_id = %s, last_successful_scrape = NOW() WHERE task_id = %s"
                cursor.execute(sql, (status, worker_id, task_id))
            else:
                sql = "UPDATE harvesting_tasks SET status = %s, worker_id = %s WHERE task_id = %s"
                cursor.execute(sql, (status, worker_id, task_id))
        conn.commit()
        log.info(f"Updated task {task_id} status to {status}.")
    except Exception as e:
        log.error(f"Failed to update status for task {task_id}: {e}")
    finally:
        db_adapter._release_connection(conn)

def main(task_id):
    worker_id = f"harvester-{uuid.uuid4().hex[:12]}"
    log.info(f"Worker {worker_id} started for task_id: {task_id}")

    db_adapter = PostgresAdapter()
    conn = db_adapter._get_connection()
    if not conn:
        log.error("Could not connect to the database. Aborting.")
        return

    task = None
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM harvesting_tasks WHERE task_id = %s", (task_id,))
            task = cursor.fetchone()
    finally:
        db_adapter._release_connection(conn)

    if not task:
        log.error(f"Task ID {task_id} not found. Aborting.")
        return

    update_task_status(db_adapter, task_id, 'IN_PROGRESS', worker_id)
    
    start_time = time.perf_counter()
    script_name = task.get('script_name', 'unknown_script')
    component_name = "J-HARV (Single Task)"

    try:
        params = task['associated_keywords'] if task['associated_keywords'] else {}
        
        result_list = []
        
        if script_name == 'usajobs_live_search':
            auth_key = os.getenv("USAJOBS_API_KEY")
            harvester = USAJobsHarvester(auth_key=auth_key)
            results = list(harvester.get_live_jobs(search_params=params))
            result_list = [r.model_dump() for r in results]

        elif script_name == 'usaspending_search':
            harvester = USASpendingHarvester()
            keyword = params.get('Keyword')
            if not keyword: raise ValueError("'Keyword' not found in parameters")
            results = list(harvester.search_awards(keyword=keyword))
            result_list = [r.model_dump() for r in results]

        elif script_name == 'arxiv_search':
            harvester = ArxivHarvester()
            query = params.get('Keyword')
            if not query: raise ValueError("'Keyword' not found in parameters for arxiv_search")
            results = list(harvester.search_articles(search_query=query))
            result_list = [r.model_dump() for r in results]

        elif script_name == 'govinfo_search':
            api_key = os.getenv("GOVINFO_API_KEY")
            harvester = GovInfoHarvester(api_key=api_key)
            query = params.get('Keyword')
            if not query: raise ValueError("'Keyword' not found in parameters for govinfo_search")
            results = list(harvester.search_publications(query=query))
            result_list = [r.model_dump() for r in results]

        else:
            raise NotImplementedError(f"No handler implemented for script: {script_name}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        keyword_str = params.get('Keyword', 'no_keyword').replace(' ', '_').replace('"', '')
        keyword_str = "".join(c for c in keyword_str if c.isalnum() or c in ('_')).rstrip()
        
        filename = f"{script_name}_{keyword_str[:50]}_{timestamp}.json"
        filepath = DATA_LAKE_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(result_list, f, indent=2)
        
        log.info(f"Successfully harvested {len(result_list)} records and saved to {filename}.")
        update_task_status(db_adapter, task_id, 'COMPLETED', worker_id)

        # --- SLI Logging: Success ---
        latency_seconds = time.perf_counter() - start_time
        sli_logger.info(
            'pipeline_success_rate',
            extra={
                'component': component_name,
                'harvester_name': script_name,
                'success': True,
                'latency_seconds': round(latency_seconds, 2)
            }
        )

    except Exception as e:
        log.error(f"An unexpected error occurred while processing task {task_id}: {e}")
        log.error(traceback.format_exc())
        update_task_status(db_adapter, task_id, 'FAILED', worker_id)

        # --- SLI Logging: Failure ---
        latency_seconds = time.perf_counter() - start_time
        sli_logger.error(
            'pipeline_success_rate',
            extra={
                'component': component_name,
                'harvester_name': script_name,
                'success': False,
                'latency_seconds': round(latency_seconds, 2),
                'error': str(e)
            }
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CHORUS Harvester Worker")
    parser.add_argument("--task-id", required=True, type=int, help="The task_id from the harvesting_tasks table to execute.")
    args = parser.parse_args()
    main(args.task_id)
