# Filename: chorus_engine/adapters/persistence/mariadb_adapter.py (Import Corrected)
import mariadb
import os
import json
import time
import logging
from pathlib import Path # DEFINITIVE FIX: Add missing import
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from chorus_engine.config import MODEL_DIR
from chorus_engine.app.interfaces import DatabaseInterface, VectorDBInterface
from chorus_engine.core.entities import AnalysisTask, AnalysisReport, HarvesterTask

class MariaDBAdapter(DatabaseInterface, VectorDBInterface):
    _pool = None
    _embedding_model = None

    def __init__(self):
        load_dotenv()
        self._get_connection_pool()

    def _get_connection_pool(self):
        if MariaDBAdapter._pool is None:
            try:
                MariaDBAdapter._pool = mariadb.ConnectionPool(
                    user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
                    host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT", 3306)),
                    database=os.getenv("DB_NAME"), pool_name="chorus_pool", pool_size=10
                )
            except (mariadb.Error, TypeError) as e:
                logging.critical(f"FATAL: Error creating database connection pool: {e}")
                raise
        return MariaDBAdapter._pool

    def _get_connection(self):
        try:
            return self._get_connection_pool().get_connection()
        except mariadb.PoolError as e:
            logging.error(f"Failed to get connection from pool: {e}")
            return None

    @classmethod
    def _get_embedding_model(cls):
        if cls._embedding_model is None:
            logging.info("Initializing embedding model (first use)...")
            model_path = MODEL_DIR / 'all-mpnet-base-v2'
            if not model_path.exists():
                raise FileNotFoundError(f"Embedding model not found at {model_path}. Please run 'make download-model'.")
            cls._embedding_model = SentenceTransformer(str(model_path))
            logging.info("Embedding model loaded.")
        return cls._embedding_model
    
    def query_similar_documents(self, query: str, limit: int) -> List[Dict[str, Any]]:
        embedding_model = self._get_embedding_model()
        conn = self._get_connection()
        if not conn: return []
        try:
            with conn.cursor(dictionary=True) as cursor:
                query_vector = embedding_model.encode([query])[0]
                query_vector_str = json.dumps(query_vector.tolist())
                sql = "SELECT dsv_line_id, content FROM dsv_embeddings ORDER BY VEC_DISTANCE_COSINE(embedding, VEC_FromText(%s)) ASC LIMIT %s;"
                cursor.execute(sql, (query_vector_str, limit))
                return cursor.fetchall()
        except mariadb.Error as e:
            logging.error(f"VectorDB query failed: {e}")
            return []
        finally:
            if conn: conn.close()

    def claim_analysis_task(self, worker_id: str) -> Optional[AnalysisTask]:
        conn = self._get_connection()
        if not conn: return None
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT query_hash FROM task_queue WHERE status = 'PENDING' LIMIT 1 FOR UPDATE")
                task_to_claim = cursor.fetchone()
                if task_to_claim:
                    hash_to_claim = task_to_claim['query_hash']
                    update_sql = "UPDATE task_queue SET status = 'IN_PROGRESS', worker_id = %s, started_at = NOW() WHERE query_hash = %s"
                    cursor.execute(update_sql, (worker_id, hash_to_claim))
                    cursor.execute("SELECT query_hash, user_query, status, worker_id FROM task_queue WHERE query_hash = %s", (hash_to_claim,))
                    claimed_task_data = cursor.fetchone()
                    conn.commit()
                    logging.info(f"[{worker_id}] Successfully claimed task: {claimed_task_data['query_hash']}")
                    claimed_task_data['user_query'] = json.loads(claimed_task_data['user_query'])
                    return AnalysisTask(**claimed_task_data)
                conn.rollback()
                return None
        except (mariadb.Error, json.JSONDecodeError) as e:
            logging.error(f"[{worker_id}] Error claiming task: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if conn: conn.close()

    def update_analysis_task_completion(self, query_hash: str, report: AnalysisReport) -> None:
        conn = self._get_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                sql_task = "UPDATE task_queue SET status = 'COMPLETED', completed_at = NOW() WHERE query_hash = %s"
                cursor.execute(sql_task, (query_hash,))
                report_json_str = report.model_dump_json()
                state_data = {"final_report_with_citations": report_json_str}
                sql_state = "INSERT INTO query_state (query_hash, state_json) VALUES (%s, %s) ON DUPLICATE KEY UPDATE state_json = %s"
                cursor.execute(sql_state, (query_hash, json.dumps(state_data), json.dumps(state_data)))
            conn.commit()
            logging.info(f"Task {query_hash} marked as COMPLETED and report saved.")
        except mariadb.Error as e:
            logging.error(f"Error updating task completion for {query_hash}: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()

    def update_analysis_task_failure(self, query_hash: str, error_message: str) -> None:
        conn = self._get_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE task_queue SET status = 'FAILED', completed_at = NOW() WHERE query_hash = %s"
                cursor.execute(sql, (query_hash,))
                state_data = {"error": error_message}
                sql_state = "INSERT INTO query_state (query_hash, state_json) VALUES (%s, %s) ON DUPLICATE KEY UPDATE state_json = %s"
                cursor.execute(sql_state, (query_hash, json.dumps(state_data), json.dumps(state_data)))
            conn.commit()
            logging.info(f"Task {query_hash} marked as FAILED.")
        except mariadb.Error as e:
            logging.error(f"Error updating task failure for {query_hash}: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()

    def log_progress(self, query_hash: str, message: str) -> None:
        conn = self._get_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO task_progress (query_hash, status_message) VALUES (%s, %s)"
                cursor.execute(sql, (query_hash, message))
            conn.commit()
        except mariadb.Error as e:
            logging.warning(f"Could not log progress for {query_hash}: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()

    def queue_and_monitor_harvester_tasks(self, query_hash: str, tasks: List[HarvesterTask]) -> bool:
        conn = self._get_connection()
        if not conn: return False
        task_ids_to_monitor = []
        try:
            with conn.cursor() as cursor:
                for task in tasks:
                    sql = "INSERT INTO harvesting_tasks (script_name, associated_keywords, is_dynamic, status) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (task.script_name, json.dumps(task.parameters), 1, 'IDLE'))
                    task_ids_to_monitor.append(cursor.lastrowid)
            conn.commit()
        finally:
            if conn: conn.close()

        if not task_ids_to_monitor:
            self.log_progress(query_hash, "Phase 2: No valid harvesting tasks were generated.")
            return True

        self.log_progress(query_hash, f"Phase 2: Now monitoring {len(task_ids_to_monitor)} harvesting tasks...")
        while True:
            conn = self._get_connection()
            if not conn: time.sleep(30); continue
            try:
                with conn.cursor(dictionary=True) as cursor:
                    query_ids_str = ','.join(map(str, task_ids_to_monitor))
                    cursor.execute(f"SELECT status FROM harvesting_tasks WHERE task_id IN ({query_ids_str})")
                    statuses = [row['status'] for row in cursor.fetchall()]
            finally:
                if conn: conn.close()

            if all(s == 'COMPLETED' for s in statuses):
                self.log_progress(query_hash, "Phase 2: All harvesting tasks completed successfully.")
                return True
            if any(s == 'FAILED' for s in statuses):
                self.log_progress(query_hash, "Phase 2: One or more harvesting tasks failed. Proceeding with available data.")
                return False
            time.sleep(30)

    def load_data_from_datalake(self) -> Dict[str, Any]:
        datalake_content = {}
        datalake_dir = Path(__file__).resolve().parents[3] / 'datalake'
        known_prefixes = ['usajobs_live_search', 'usaspending_search', 'newsapi_search', 'arxiv_search']
        for prefix in known_prefixes:
            try:
                files = list(datalake_dir.glob(f"{prefix}_*.json"))
                if not files: continue
                latest_file = max(files, key=os.path.getctime)
                logging.info(f"Loading latest '{prefix}' file: {latest_file.name}")
                with open(latest_file, 'r') as f:
                    datalake_content[prefix] = json.load(f)
            except Exception as e:
                logging.error(f"Error loading data for prefix {prefix}: {e}")
                datalake_content[prefix] = {"error": f"Failed to load data: {e}"}
        return datalake_content
