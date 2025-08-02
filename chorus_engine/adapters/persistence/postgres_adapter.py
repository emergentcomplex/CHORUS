# Filename: chorus_engine/adapters/persistence/postgres_adapter.py (Lazy Init)
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from chorus_engine.config import MODEL_DIR
from chorus_engine.app.interfaces import DatabaseInterface, VectorDBInterface
from chorus_engine.core.entities import AnalysisTask, AnalysisReport, HarvesterTask

log = logging.getLogger(__name__)

class PostgresAdapter(DatabaseInterface, VectorDBInterface):
    _pool = None
    _embedding_model = None
    _connection_params = {}

    def __init__(self, host=None, port=None, dbname=None, user=None, password=None):
        load_dotenv()
        # Store connection params but do not connect immediately.
        self._connection_params = {
            'host': host or os.getenv('DB_HOST', '127.0.0.1'),
            'port': port or os.getenv('DB_PORT', 5432),
            'dbname': dbname or os.getenv('DB_NAME'),
            'user': user or os.getenv('DB_USER'),
            'password': password or os.getenv('DB_PASSWORD')
        }

    def _get_pool(self):
        """Lazy initializer for the connection pool."""
        if self._pool is None:
            try:
                params = self._connection_params
                log.info(f"Creating PostgreSQL connection pool (first use) for {params['user']}@{params['host']}:{params['port']}...")
                conn_str = f"dbname='{params['dbname']}' user='{params['user']}' host='{params['host']}' port='{params['port']}' password='{params['password']}'"
                self._pool = SimpleConnectionPool(1, 10, dsn=conn_str)
            except (psycopg2.OperationalError, TypeError) as e:
                log.critical(f"FATAL: Error creating database connection pool: {e}")
                raise
        return self._pool

    def _get_connection(self):
        return self._get_pool().getconn()

    def _release_connection(self, conn):
        if self._pool:
            self._pool.putconn(conn)

    @classmethod
    def _get_embedding_model(cls):
        if cls._embedding_model is None:
            log.info("Initializing embedding model (first use)...")
            model_path = MODEL_DIR / 'all-mpnet-base-v2'
            if not model_path.exists():
                raise FileNotFoundError(f"Embedding model not found at {model_path}. Please run 'make download-model'.")
            cls._embedding_model = SentenceTransformer(str(model_path))
            log.info("Embedding model loaded.")
        return cls._embedding_model

    def get_available_harvesters(self) -> List[str]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT DISTINCT script_name FROM harvesting_tasks")
                return [row[0] for row in cursor.fetchall()]
        finally:
            self._release_connection(conn)

    def query_similar_documents(self, query: str, limit: int) -> List[Dict[str, Any]]:
        embedding_model = self._get_embedding_model()
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query_vector = embedding_model.encode([query])[0]
                query_vector_str = str(query_vector.tolist())
                sql = "SELECT dsv_line_id, content FROM dsv_embeddings ORDER BY embedding <=> %s ASC LIMIT %s;"
                cursor.execute(sql, (query_vector_str, limit))
                return cursor.fetchall()
        finally:
            self._release_connection(conn)

    def claim_analysis_task(self, worker_id: str) -> Optional[AnalysisTask]:
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT query_hash FROM task_queue WHERE status = 'PENDING' LIMIT 1 FOR UPDATE SKIP LOCKED")
                task_to_claim = cursor.fetchone()
                if task_to_claim:
                    hash_to_claim = task_to_claim['query_hash']
                    update_sql = "UPDATE task_queue SET status = 'IN_PROGRESS', worker_id = %s, started_at = NOW() WHERE query_hash = %s"
                    cursor.execute(update_sql, (worker_id, hash_to_claim))
                    cursor.execute("SELECT query_hash, user_query, status, worker_id FROM task_queue WHERE query_hash = %s", (hash_to_claim,))
                    claimed_task_data = cursor.fetchone()
                    conn.commit()
                    return AnalysisTask(**claimed_task_data)
                conn.rollback()
                return None
        finally:
            self._release_connection(conn)

    def update_analysis_task_completion(self, query_hash: str, report: AnalysisReport) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                sql_task = "UPDATE task_queue SET status = 'COMPLETED', completed_at = NOW() WHERE query_hash = %s"
                cursor.execute(sql_task, (query_hash,))
                report_json_str = report.model_dump_json()
                state_data = {"final_report_with_citations": report_json_str}
                sql_state = "INSERT INTO query_state (query_hash, state_json) VALUES (%s, %s) ON CONFLICT (query_hash) DO UPDATE SET state_json = EXCLUDED.state_json"
                cursor.execute(sql_state, (query_hash, json.dumps(state_data)))
            conn.commit()
        finally:
            self._release_connection(conn)

    def update_analysis_task_failure(self, query_hash: str, error_message: str) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE task_queue SET status = 'FAILED', completed_at = NOW() WHERE query_hash = %s"
                cursor.execute(sql, (query_hash,))
                state_data = {"error": error_message}
                sql_state = "INSERT INTO query_state (query_hash, state_json) VALUES (%s, %s) ON CONFLICT (query_hash) DO UPDATE SET state_json = EXCLUDED.state_json"
                cursor.execute(sql_state, (query_hash, json.dumps(state_data)))
            conn.commit()
        finally:
            self._release_connection(conn)

    def log_progress(self, query_hash: str, message: str) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO task_progress (query_hash, status_message) VALUES (%s, %s)"
                cursor.execute(sql, (query_hash, message))
            conn.commit()
        finally:
            self._release_connection(conn)

    def queue_and_monitor_harvester_tasks(self, query_hash: str, tasks: List[HarvesterTask]) -> bool:
        conn = self._get_connection()
        task_ids_to_monitor = []
        try:
            with conn.cursor() as cursor:
                for task in tasks:
                    sql = "INSERT INTO harvesting_tasks (script_name, associated_keywords, is_dynamic, status) VALUES (%s, %s, %s, %s) RETURNING task_id"
                    cursor.execute(sql, (task.script_name, json.dumps(task.parameters), True, 'IDLE'))
                    task_ids_to_monitor.append(cursor.fetchone()[0])
            conn.commit()
        finally:
            self._release_connection(conn)

        if not task_ids_to_monitor:
            self.log_progress(query_hash, "Phase 2: No valid harvesting tasks were generated.")
            return True

        self.log_progress(query_hash, f"Phase 2: Now monitoring {len(task_ids_to_monitor)} harvesting tasks...")
        while True:
            conn = self._get_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT status FROM harvesting_tasks WHERE task_id = ANY(%s)", (task_ids_to_monitor,))
                    statuses = [row['status'] for row in cursor.fetchall()]
            finally:
                self._release_connection(conn)

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
        
        harvester_prefixes = self.get_available_harvesters()
        if not harvester_prefixes:
            return {}

        for prefix in harvester_prefixes:
            try:
                files = list(datalake_dir.glob(f"{prefix}_*.json"))
                if not files: continue
                latest_file = max(files, key=os.path.getctime)
                with open(latest_file, 'r') as f:
                    datalake_content[prefix] = json.load(f)
            except Exception as e:
                datalake_content[prefix] = {"error": f"Failed to load data: {e}"}
        return datalike_content
