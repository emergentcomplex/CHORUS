# Filename: chorus_engine/adapters/persistence/postgres_adapter.py
# 🔱 CHORUS Persistence Adapter for PostgreSQL (v5 - Final Interface Alignment)

import logging
import os
import psycopg2
import requests
import json
from psycopg2.extras import RealDictCursor
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PostgresAdapter:
    def __init__(self, connection):
        self.connection = connection

    def get_task(self, query_hash: str) -> Dict[str, Any] | None:
        """Fetches a single task's details and prepares it for the application layer."""
        query = "SELECT query_hash, user_query, status, worker_id, created_at, started_at, completed_at FROM task_queue WHERE query_hash = %s"
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (query_hash,))
                task_data = cursor.fetchone()
                if task_data and isinstance(task_data.get('user_query'), str):
                    task_data['user_query'] = json.loads(task_data['user_query'])
                return task_data
        except Exception as e:
            logger.error(f"Failed to get task for {query_hash}: {e}")
            return None

    def log_progress(self, query_hash: str, message: str):
        """Inserts a progress update into the task_progress table."""
        query = "INSERT INTO task_progress (query_hash, status_message) VALUES (%s, %s)"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (query_hash, message))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to log progress for {query_hash}: {e}")
            self.connection.rollback()

    def update_task_status(self, query_hash: str, status: str):
        """Updates the status of a task in the task_queue table."""
        query = "UPDATE task_queue SET status = %s WHERE query_hash = %s"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (status, query_hash))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to update status for {query_hash} to {status}: {e}")
            self.connection.rollback()

    # THE DEFINITIVE FIX: Rename the method to match the VectorDBInterface contract.
    def query_similar_documents(self, query: str, limit: int = 5) -> list[dict]:
        """Queries the semantic_vectors table for the most similar documents."""
        logger.info(f"Querying semantic space for: '{query[:50]}...'")
        embed_url = "http://chorus-embedder:5003/embed"
        try:
            response = requests.post(embed_url, json={"texts": [query]}, timeout=15)
            response.raise_for_status()
            query_embedding = response.json()["embeddings"][0]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get embedding for query '{query}': {e}")
            return []

        sql_query = """
            SELECT content_chunk, embedding <=> %s AS distance
            FROM semantic_vectors ORDER BY distance ASC LIMIT %s;
        """
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql_query, (json.dumps(query_embedding), limit))
                results = cursor.fetchall()
                logger.info(f"Found {len(results)} similar documents for query.")
                return results
        except Exception as e:
            logger.error(f"Database error during semantic query: {e}", exc_info=True)
            self.connection.rollback()
            return []

    def get_task_progress(self, query_hash: str) -> list:
        query = "SELECT * FROM task_progress WHERE query_hash = %s ORDER BY timestamp ASC"
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (query_hash,))
            return cursor.fetchall()

    def get_analyst_reports(self, query_hash: str) -> list:
        query = "SELECT * FROM analyst_reports WHERE query_hash = %s"
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (query_hash,))
            return cursor.fetchall()

    def get_director_briefing(self, query_hash: str) -> dict:
        query = "SELECT * FROM director_briefings WHERE query_hash = %s"
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (query_hash,))
            return cursor.fetchone()

    def get_final_report_data(self, query_hash: str) -> dict:
        query = "SELECT state_json FROM query_state WHERE query_hash = %s"
        with self.connection.cursor() as cursor:
            cursor.execute(query, (query_hash,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else None