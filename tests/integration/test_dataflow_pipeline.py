# Filename: tests/integration/test_dataflow_pipeline.py
import pytest
import json
import uuid
import hashlib
import os
import time
import psycopg2
import redis

pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def redis_client():
    """Provides a Redis client for polling the UI's true data source."""
    try:
        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )
        r.ping()
        return r
    except redis.exceptions.ConnectionError as e:
        pytest.fail(f"Failed to connect to Redis for dataflow test: {e}")

def test_database_write_materializes_in_redis(db_adapter, redis_client):
    """
    Verifies the complete dataflow pipeline:
    PostgreSQL (write) -> Debezium -> Redpanda -> Stream Processor -> Redis (read)
    This is a high-fidelity integration test of the core system data path.
    """
    # 1. ARRANGE: Define a unique task and ensure it's clean in all systems.
    unique_input_str = f"dataflow-test-{uuid.uuid4().hex}"
    user_query_data = {"query": f"test query for {unique_input_str}"}
    query_hash = hashlib.md5(json.dumps(user_query_data, sort_keys=True).encode('utf-8')).hexdigest()
    redis_key = f"task:{query_hash}"

    # Clean up Redis
    redis_client.delete(redis_key)

    # Clean up and insert into PostgreSQL
    conn = db_adapter._get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM task_queue WHERE query_hash = %s", (query_hash,))
            sql = "INSERT INTO task_queue (user_query, query_hash, status) VALUES (%s, %s, 'PENDING_ANALYSIS')"
            cursor.execute(sql, (json.dumps(user_query_data), query_hash))
        conn.commit()
        print(f"\n[*] Inserted new task {query_hash} into PostgreSQL.")
    finally:
        db_adapter._release_connection(conn)

    # 2. ACT & ASSERT: Poll Redis for the materialized state.
    redis_state = None
    max_wait_seconds = 45
    start_time = time.time()
    
    while time.time() - start_time < max_wait_seconds:
        redis_state = redis_client.hgetall(redis_key)
        if redis_state:
            print(f"[*] Task {query_hash} materialized in Redis after {time.time() - start_time:.2f} seconds.")
            break
        time.sleep(2)

    assert redis_state, f"Dataflow pipeline failed: Task {query_hash} did not materialize in Redis within {max_wait_seconds} seconds."
    
    # Verify the content of the materialized state
    assert redis_state.get('query_hash') == query_hash
    assert redis_state.get('status') == 'PENDING_ANALYSIS'
    assert json.loads(redis_state.get('user_query')) == user_query_data
    print("[+] SUCCESS: End-to-end dataflow pipeline verified.")