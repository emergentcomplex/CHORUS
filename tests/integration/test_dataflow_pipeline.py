# Filename: tests/integration/test_dataflow_pipeline.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This integration test validates the Change Data Capture (CDC) pipeline,
# ensuring that a write to the PostgreSQL database is correctly captured
# by Debezium, published to Redpanda, and materialized in the Redis cache
# by the stream processor.

import pytest
import os
import json
import uuid
import hashlib
import time
import redis

pytestmark = [pytest.mark.integration, pytest.mark.dataflow]

# --- Fixtures ---

@pytest.fixture(scope="module")
def redis_client():
    """Provides a Redis client for the test module."""
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True
    )
    r.ping()
    return r

# --- The Test ---

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

    # 2. ACT: Insert a new record into the source of truth (PostgreSQL).
    # This now uses the connection from the canonical db_adapter fixture.
    with db_adapter.connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO task_queue (query_hash, user_query, status) VALUES (%s, %s, 'PENDING')",
            (query_hash, json.dumps(user_query_data))
        )
    db_adapter.connection.commit()

    # 3. ASSERT: Poll Redis until the materialized view appears.
    max_wait_seconds = 20
    start_time = time.time()
    final_state = None
    while time.time() - start_time < max_wait_seconds:
        final_state = redis_client.hgetall(redis_key)
        if final_state:
            break
        time.sleep(1)

    assert final_state is not None, "Data did not materialize in Redis within the timeout period."
    assert final_state.get("query_hash") == query_hash
    assert final_state.get("status") == "PENDING"
    assert json.loads(final_state.get("user_query")) == user_query_data
    print("\n[+] SUCCESS: CDC dataflow from PostgreSQL to Redis verified.")