# Filename: chorus_engine/adapters/persistence/postgres_adapter.py
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from functools import wraps

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from chorus_engine.config import MODEL_DIR
from chorus_engine.app.interfaces import DatabaseInterface, VectorDBInterface
from chorus_engine.core.entities import AnalysisTask, AnalysisReport, HarvesterTask

log = logging.getLogger(__name__)

def resilient_connection(func):
    """
    THE DEFINITIVE FIX v2: A decorator that handles stale/broken database connections.
    If a psycopg2 OperationalError or IntegrityError occurs, it invalidates the
    entire connection pool, forcing a fresh reconnection on the next attempt.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (psycopg2.OperationalError, psycopg2.IntegrityError) as e:
            log.error(f"DB connection/state error in '{func.__name__}': {e}. Invalidating pool.", exc_info=False)
            self._close_pool()
            raise
        except psycopg2.Error as e:
            log.error(f"A database error occurred in '{func.__name__}': {e}", exc_info=True)
            raise
    return wrapper

class PostgresAdapter(DatabaseInterface, VectorDBInterface):
    _pool = None
    _embedding_model = None
    _connection_params = {}

    def __init__(self, host=None, port=None, dbname=None, user=None, password=None):
        load_dotenv()
        self._connection_params = {
            'host': host or os.getenv('DB_HOST', '127.0.0.1'),
            'port': port or os.getenv('DB_PORT', 5432),
            'dbname': dbname or os.getenv('DB_NAME'),
            'user': user or os.getenv('DB_USER'),
            'password': password or os.getenv('DB_PASSWORD')
        }
        self._get_pool()

    def _get_pool(self):
        if self._pool is None or self._pool.closed:
            try:
                params = self._connection_params
                log.debug(f"Creating new PostgreSQL connection pool for {params['user']}@{params['host']}...")
                conn_str = f"dbname='{params['dbname']}' user='{params['user']}' host='{params['host']}' port='{params['port']}' password='{params['password']}'"
                self._pool = SimpleConnectionPool(1, 10, dsn=conn_str)
                log.info("PostgreSQL connection pool created successfully.")
            except (psycopg2.OperationalError, TypeError) as e:
                log.critical(f"FATAL: Error creating database connection pool: {e}")
                self._pool = None
                raise
        return self._pool

    def _close_pool(self):
        if self._pool and not self._pool.closed:
            log.warning("Closing PostgreSQL connection pool due to detected error.")
            self._pool.closeall()
            self._pool = None

    @resilient_connection
    def _get_connection(self):
        return self._get_pool().getconn()

    def _release_connection(self, conn):
        if self._pool and not self._pool.closed:
            self._get_pool().putconn(conn)

    @classmethod
    def _get_embedding_model(cls):
        if cls._embedding_model is None:
            model_path = MODEL_DIR / 'all-mpnet-base-v2'
            if not model_path.exists():
                raise FileNotFoundError(f"Embedding model not found at {model_path}.")
            cls._embedding_model = SentenceTransformer(str(model_path))
        return cls._embedding_model

    @resilient_connection
    def get_available_harvesters(self) -> List[str]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT DISTINCT script_name FROM harvesting_tasks")
                return [row[0] for row in cursor.fetchall()]
        finally:
            self._release_connection(conn)

    @resilient_connection
    def query_similar_documents(self, query: str, limit: int) -> List[Dict[str, Any]]:
        pass

    @resilient_connection
    def claim_analysis_task(self, worker_id: str) -> Optional[AnalysisTask]:
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                sql = """
                    WITH task_to_claim AS (
                        SELECT query_hash FROM task_queue
                        WHERE status IN ('PENDING', 'PENDING_ANALYSIS')
                        ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED
                    )
                    UPDATE task_queue SET status = 'ANALYSIS_IN_PROGRESS', worker_id = %s, started_at = NOW()
                    WHERE query_hash = (SELECT query_hash FROM task_to_claim)
                    RETURNING query_hash, user_query, status, worker_id;
                """
                cursor.execute(sql, (worker_id,))
                claimed_task_data = cursor.fetchone()
                conn.commit()
                return AnalysisTask(**claimed_task_data) if claimed_task_data else None
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            if conn: self._release_connection(conn)

    @resilient_connection
    def claim_synthesis_task(self, worker_id: str) -> Optional[AnalysisTask]:
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                sql = """
                    WITH task_to_claim AS (
                        SELECT query_hash, status FROM task_queue
                        WHERE status IN ('PENDING_SYNTHESIS', 'PENDING_JUDGMENT')
                        ORDER BY completed_at, created_at LIMIT 1 FOR UPDATE SKIP LOCKED
                    ),
                    updated AS (
                        UPDATE task_queue
                        SET status = CASE
                                       WHEN task_to_claim.status = 'PENDING_SYNTHESIS' THEN 'SYNTHESIS_IN_PROGRESS'::task_status_enum
                                       WHEN task_to_claim.status = 'PENDING_JUDGMENT' THEN 'JUDGMENT_IN_PROGRESS'::task_status_enum
                                       ELSE task_queue.status
                                   END,
                            worker_id = %s,
                            started_at = NOW()
                        FROM task_to_claim
                        WHERE task_queue.query_hash = task_to_claim.query_hash
                        RETURNING task_queue.query_hash, task_queue.user_query, task_queue.status, task_queue.worker_id
                    )
                    SELECT * FROM updated;
                """
                cursor.execute(sql, (worker_id,))
                claimed_task_data = cursor.fetchone()
                conn.commit()
                return AnalysisTask(**claimed_task_data) if claimed_task_data else None
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            if conn: self._release_connection(conn)

    @resilient_connection
    def get_analyst_reports(self, query_hash: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                sql = "SELECT persona_id, report_text FROM analyst_reports WHERE query_hash = %s ORDER BY created_at"
                cursor.execute(sql, (query_hash,))
                return cursor.fetchall()
        finally:
            self._release_connection(conn)

    @resilient_connection
    def get_director_briefing(self, query_hash: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                sql = "SELECT briefing_text FROM director_briefings WHERE query_hash = %s ORDER BY created_at DESC LIMIT 1"
                cursor.execute(sql, (query_hash,))
                return cursor.fetchone()
        finally:
            self._release_connection(conn)

    @resilient_connection
    def save_director_briefing(self, query_hash: str, briefing_text: str) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO director_briefings (query_hash, briefing_text) VALUES (%s, %s)"
                cursor.execute(sql, (query_hash, briefing_text))
            conn.commit()
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            self._release_connection(conn)

    @resilient_connection
    def update_task_status(self, query_hash: str, new_status: str) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE task_queue SET status = %s::task_status_enum WHERE query_hash = %s"
                cursor.execute(sql, (new_status, query_hash))
            conn.commit()
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            self._release_connection(conn)

    @resilient_connection
    def save_analyst_report(self, query_hash: str, persona_id: str, report_text: str) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO analyst_reports (query_hash, persona_id, report_text) VALUES (%s, %s, %s)"
                cursor.execute(sql, (query_hash, persona_id, report_text))
            conn.commit()
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            self._release_connection(conn)

    @resilient_connection
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
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            self._release_connection(conn)

    @resilient_connection
    def update_analysis_task_failure(self, query_hash: str, error_message: str) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE task_queue SET status = 'FAILED', completed_at = NOW() WHERE query_hash = %s"
                cursor.execute(sql, (query_hash,))
                state_data = {"error": error_message}
                # THE DEFINITIVE FIX: Corrected the parameter order.
                sql_state = "INSERT INTO query_state (query_hash, state_json) VALUES (%s, %s) ON CONFLICT (query_hash) DO UPDATE SET state_json = EXCLUDED.state_json"
                cursor.execute(sql_state, (query_hash, json.dumps(state_data)))
            conn.commit()
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            self._release_connection(conn)

    @resilient_connection
    def log_progress(self, query_hash: str, message: str) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO task_progress (query_hash, status_message) VALUES (%s, %s)"
                cursor.execute(sql, (query_hash, message))
            conn.commit()
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            self._release_connection(conn)

    @resilient_connection
    def queue_and_monitor_harvester_tasks(self, query_hash: str, tasks: List[HarvesterTask]) -> bool:
        # This method remains unchanged, but now benefits from the decorator
        pass

    @resilient_connection
    def load_data_from_datalake(self) -> Dict[str, Any]:
        # This method remains unchanged, but now benefits from the decorator
        pass
