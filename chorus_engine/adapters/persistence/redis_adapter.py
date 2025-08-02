# Filename: chorus_engine/adapters/persistence/redis_adapter.py (Definitively Corrected Error Handling)
#
# A dedicated adapter for querying the derived data store in Redis.

import os
import redis
import logging
from typing import List, Dict, Any, Optional

log = logging.getLogger(__name__)

class RedisAdapter:
    _client = None

    def _get_client(self):
        """Lazy initialization for the Redis client."""
        if self._client is None:
            try:
                log.info("Initializing Redis client (first use)...")
                client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    db=0,
                    decode_responses=True
                )
                client.ping()
                self._client = client
                log.info("Redis client connected successfully.")
            except redis.exceptions.ConnectionError as e:
                log.critical(f"FATAL: Could not connect to Redis: {e}")
                raise
        return self._client

    def get_all_tasks_sorted_by_time(self) -> List[Dict[str, Any]]:
        """Retrieves all task keys, fetches their data, and sorts them by creation time."""
        try:
            client = self._get_client()
            task_keys = client.keys("task:*")
            if not task_keys:
                return []

            pipeline = client.pipeline()
            for key in task_keys:
                pipeline.hgetall(key)
            
            all_tasks_data = pipeline.execute()
            all_tasks_data.sort(key=lambda t: t.get('created_at', '1970-01-01 00:00:00'), reverse=True)
            
            return all_tasks_data
        # THE DEFINITIVE FIX: Catch the generic Exception to handle any client failure.
        except Exception as e:
            log.error(f"Error retrieving tasks from Redis: {e}")
            return []

    def get_task_by_hash(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single task's state by its query hash."""
        try:
            client = self._get_client()
            return client.hgetall(f"task:{query_hash}")
        # THE DEFINITIVE FIX: Catch the generic Exception to handle any client failure.
        except Exception as e:
            log.error(f"Error retrieving task {query_hash} from Redis: {e}")
            return None
