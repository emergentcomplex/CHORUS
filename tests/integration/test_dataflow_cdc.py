# Filename: tests/integration/test_dataflow_cdc.py (Unified Stack Edition v2)
import pytest
import json
import uuid
import hashlib
import os
import time
import psycopg2
from kafka import KafkaConsumer, errors

pytestmark = pytest.mark.integration

def test_database_change_produces_kafka_event():
    """
    Verifies the CDC pipeline: PostgreSQL -> Debezium -> Redpanda.
    Assumes the full stack is running and accessible via service names.
    """
    # THE DEFINITIVE FIX: Default to service names for in-container networking.
    db_host = os.getenv("DB_HOST", "postgres")
    db_port = os.getenv("DB_PORT", 5432)
    kafka_bootstrap = os.getenv("KAFKA_BROKER", "redpanda:29092")

    unique_input_str = f"cdc-test-{uuid.uuid4().hex}"
    unique_query_hash = hashlib.md5(unique_input_str.encode('utf-8')).hexdigest()
    user_query_data = {"query": f"test query for {unique_input_str}"}

    try:
        consumer = KafkaConsumer(
            "chorus.public.task_queue",
            bootstrap_servers=kafka_bootstrap,
            auto_offset_reset="earliest",
            consumer_timeout_ms=30000,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
    except errors.NoBrokersAvailable:
        pytest.fail(f"Could not connect to Kafka at {kafka_bootstrap}. Check service name and network.")

    conn_str = f"dbname='{os.getenv('DB_NAME')}' user='{os.getenv('DB_USER')}' host='{db_host}' port='{db_port}' password='{os.getenv('DB_PASSWORD')}'"
    conn = psycopg2.connect(conn_str)
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO task_queue (user_query, query_hash, status) VALUES (%s, %s, %s)"
            cursor.execute(sql, (json.dumps(user_query_data), unique_query_hash, 'PENDING'))
        conn.commit()
    finally:
        if conn: conn.close()

    found_event = None
    for message in consumer:
        payload = message.value.get('payload', {})
        if payload and payload.get('op') == 'c':
            after_state = payload.get('after', {})
            if after_state and after_state.get('query_hash') == unique_query_hash:
                found_event = after_state
                break
    consumer.close()

    assert found_event is not None, "CDC event for the new task was not found in Kafka topic."
    assert found_event['status'] == 'PENDING'
    assert json.loads(found_event['user_query']) == user_query_data
