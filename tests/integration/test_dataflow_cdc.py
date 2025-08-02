# Filename: tests/integration/test_dataflow_cdc.py
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
    This test is now resilient to the asynchronous nature of the pipeline.
    """
    db_host = os.getenv("DB_HOST", "postgres")
    db_port = os.getenv("DB_PORT", 5432)
    kafka_bootstrap = os.getenv("KAFKA_BROKER", "redpanda:29092")

    unique_input_str = f"cdc-test-{uuid.uuid4().hex}"
    unique_query_hash = hashlib.md5(unique_input_str.encode('utf-8')).hexdigest()
    user_query_data = {"query": f"test query for {unique_input_str}"}

    # --- Act: Insert the record into the database ---
    conn_str = f"dbname='{os.getenv('DB_NAME')}' user='{os.getenv('DB_USER')}' host='{db_host}' port='{db_port}' password='{os.getenv('DB_PASSWORD')}'"
    conn = psycopg2.connect(conn_str)
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO task_queue (user_query, query_hash, status) VALUES (%s, %s, 'PENDING')"
            cursor.execute(sql, (json.dumps(user_query_data), unique_query_hash))
        conn.commit()
    finally:
        if conn: conn.close()

    # --- Assert: Poll Kafka until the event is found or we time out ---
    found_event = None
    start_time = time.time()
    max_wait_seconds = 45
    
    # THE DEFINITIVE FIX: Implement a retry loop to handle CDC latency.
    while time.time() - start_time < max_wait_seconds:
        try:
            consumer = KafkaConsumer(
                "chorus.public.task_queue",
                bootstrap_servers=kafka_bootstrap,
                auto_offset_reset="earliest",
                consumer_timeout_ms=10000, # 10 second timeout per poll attempt
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
            
            print(f"[*] Polling Kafka for CDC event (attempt {int((time.time() - start_time) / 10)})...")
            for message in consumer:
                payload = message.value.get('payload', {})
                if payload and payload.get('op') == 'c':
                    after_state = payload.get('after', {})
                    if after_state and after_state.get('query_hash') == unique_query_hash:
                        print("[+] Found matching event!")
                        found_event = after_state
                        break
            consumer.close()
            if found_event:
                break
        except errors.NoBrokersAvailable:
            print(f"[*] Could not connect to Kafka at {kafka_bootstrap}. Retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"[*] An unexpected error occurred while consuming: {e}. Retrying...")
            time.sleep(5)

    assert found_event is not None, f"CDC event for the new task was not found in Kafka topic after {max_wait_seconds} seconds."
    assert found_event['status'] == 'PENDING'
    assert json.loads(found_event['user_query']) == user_query_data