# Filename: scripts/harvester_worker.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# The main worker process for executing data harvesting tasks.
# This version is upgraded to handle 'arxiv_search' tasks.

import argparse
import json
import logging
import os
import socket
import traceback
from datetime import datetime
from pathlib import Path

from db_connector import get_db_connection
from usajobs_harvester import USAJobsHarvester
from usaspending_harvester import USASpendingHarvester
from newsapi_harvester import NewsAPIHarvester
from arxiv_harvester import ArxivHarvester # <-- IMPORT THE FINAL HARVESTER

# --- CONFIGURATION ---
DATA_LAKE_DIR = Path(__file__).resolve().parent.parent / 'datalake'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [HarvesterWorker] - %(message)s')

def update_task_status(task_id, status, worker_id=None):
    """Updates the status of a task in the database."""
    conn = get_db_connection()
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
        logging.info(f"Updated task {task_id} status to {status}.")
    except Exception as e:
        logging.error(f"Failed to update status for task {task_id}: {e}")
    finally:
        conn.close()

def main(task_id):
    worker_id = f"harvester-{socket.gethostname()}-{os.getpid()}"
    logging.info(f"Worker started for task_id: {task_id}")

    conn = get_db_connection()
    if not conn: return

    task = None
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM harvesting_tasks WHERE task_id = %s", (task_id,))
            task = cursor.fetchone()
    finally:
        conn.close()

    if not task:
        logging.error(f"Task ID {task_id} not found. Aborting.")
        return

    update_task_status(task_id, 'IN_PROGRESS', worker_id)

    try:
        script_name = task['script_name']
        params = json.loads(task['associated_keywords']) if task['associated_keywords'] else {}
        
        result_list = []
        
        # --- ROUTING LOGIC ---
        if script_name == 'usajobs_live_search':
            user_agent = os.getenv("USAJOBS_EMAIL")
            auth_key = os.getenv("USAJOBS_API_KEY")
            harvester = USAJobsHarvester(user_agent=user_agent, auth_key=auth_key)
            results = list(harvester.get_live_jobs(search_params=params))
            result_list = [r.model_dump() for r in results]

        elif script_name == 'usaspending_search':
            harvester = USASpendingHarvester()
            keyword = params.get('Keyword')
            if not keyword: raise ValueError("'Keyword' not found in parameters")
            results = list(harvester.search_awards(keyword=keyword))
            result_list = [r.model_dump() for r in results]

        elif script_name == 'newsapi_search':
            api_key = os.getenv("NEWS_API_KEY")
            harvester = NewsAPIHarvester(api_key=api_key)
            search_params = params.copy()
            if 'Keyword' in search_params:
                search_params['q'] = search_params.pop('Keyword')
            results = list(harvester.search_articles(search_params))
            result_list = [r.model_dump() for r in results]

        # --- NEW HANDLER FOR ARXIV ---
        elif script_name == 'arxiv_search':
            harvester = ArxivHarvester()
            query = params.get('Keyword') # Personas will pass the query string in 'Keyword'
            if not query: raise ValueError("'Keyword' not found in parameters for arxiv_search")
            
            results = list(harvester.search_articles(search_query=query))
            result_list = [r.model_dump() for r in results]

        else:
            raise NotImplementedError(f"No handler implemented for script: {script_name}")

        # --- Save results to Data Lake ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        keyword_str = params.get('Keyword', 'no_keyword').replace(' ', '_').replace('"', '')
        # Sanitize filename further
        keyword_str = "".join(c for c in keyword_str if c.isalnum() or c in ('_')).rstrip()
        
        filename = f"{script_name}_{keyword_str[:50]}_{timestamp}.json"
        filepath = DATA_LAKE_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(result_list, f, indent=2)
        
        logging.info(f"Successfully harvested {len(result_list)} records and saved to {filename}.")
        update_task_status(task_id, 'COMPLETED', worker_id)

    except Exception as e:
        logging.error(f"An unexpected error occurred while processing task {task_id}: {e}")
        logging.error(traceback.format_exc())
        update_task_status(task_id, 'FAILED', worker_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CHORUS Harvester Worker")
    parser.add_argument("--task-id", required=True, type=int, help="The task_id from the harvesting_tasks table to execute.")
    args = parser.parse_args()
    main(args.task_id)