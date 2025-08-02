# Filename: tests/integration/test_dataflow_stream_processor.py (Unified Stack Edition v2)
import pytest
import json
import uuid
import time
import os
from kafka import KafkaProducer, errors
import redis

pytestmark = pytest.mark.integration

def test_kafka_event_updates_redis_state():
    """
    Validates the stream processing pipeline: Redpanda -> TaskStateManager -> Redis.
    Assumes the full stack is running and accessible via service names.
    """
    # THE DEFINITIVE FIX: Default to service names for in-container networking.
    kafka_bootstrap = os.getenv("KAFKA_BROKER", "redpanda:29092")
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    unique_query_hash = f"stream-proc-test-{uuid.uuid4().hex}"
    redis_key = f"task:{unique_query_hash}"

    debezium_event = {
        "payload": {
            "op": "c", "before": None,
            "after": {
                "query_hash": unique_query_hash, "user_query": {"query": "test"},
                "status": "PENDING", "worker_id": None, "created_at": "2025-01-01T00:00:00Z",
                "started_at": None, "completed_at": None
            }
        }
    }
    try:
        producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except errors.NoBrokersAvailable:
        pytest.fail(f"Could not connect to Kafka at {kafka_bootstrap}. Check service name and network.")

    redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
    redis_client.delete(redis_key)

    topic = "chorus.public.task_queue"
    producer.send(topic, value=debezium_event)
    producer.flush()
    producer.close()

    redis_state = None
    for _ in range(10):
        redis_state = redis_client.hgetall(redis_key)
        if redis_state: break
        time.sleep(1)

    assert redis_state is not None, "Derived state was not found in Redis."
    assert redis_state.get('query_hash') == unique_query_hash
    assert redis_state.get('status') == "PENDING"
    assert json.loads(redis_state.get('user_query')) == {"query": "test"}
