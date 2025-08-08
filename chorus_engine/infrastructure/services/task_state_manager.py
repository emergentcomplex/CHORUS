# Filename: chorus_engine/infrastructure/services/task_state_manager.py
#
# A stream processing service that maintains a real-time view of the task queue
# state in a fast, derived data store (Redis). Now with a non-blocking, resilient consumer.

import json
import logging
import time
import os
import redis
from pathlib import Path

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from chorus_engine.config import setup_logging

# --- CONFIGURATION ---
# THE DEFINITIVE FIX: Use the correct Docker service name for the Kafka broker.
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "redpanda:29092")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CDC_TOPIC = "chorus.public.task_queue"
HEALTH_FILE = Path("/tmp/stream-processor.healthy")
CONSUMER_TIMEOUT_MS = 10000 # 10 seconds

# Initialize centralized logging
setup_logging()
log = logging.getLogger(__name__)

def get_kafka_consumer():
    """Establishes a resilient connection to the Kafka broker."""
    while True:
        try:
            consumer = KafkaConsumer(
                CDC_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda v: json.loads(v.decode('utf-8')) if v else None,
                auto_offset_reset='earliest',
                consumer_timeout_ms=CONSUMER_TIMEOUT_MS
            )
            log.info(f"Successfully connected to Kafka and subscribed to topic '{CDC_TOPIC}'.")
            return consumer
        except NoBrokersAvailable:
            log.warning(f"Could not connect to Kafka broker at {KAFKA_BROKER}. Retrying in 15 seconds...")
            time.sleep(15)
        except Exception as e:
            log.error(f"An unexpected error occurred during Kafka consumer creation: {e}")
            time.sleep(15)

def get_redis_client():
    """Establishes a resilient connection to the Redis server."""
    while True:
        try:
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
            r.ping()
            log.info(f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}.")
            return r
        except redis.exceptions.ConnectionError as e:
            log.warning(f"Could not connect to Redis: {e}. Retrying in 15 seconds...")
            time.sleep(15)

def main():
    """Main function to run the consumer and update the Redis cache."""
    log.info("--- CHORUS Task State Manager Service Initializing ---")
    
    consumer = get_kafka_consumer()
    redis_client = get_redis_client()

    log.info("--- Starting event consumption loop ---")
    while True:
        HEALTH_FILE.touch()
        
        for message in consumer:
            if not message or not message.value:
                continue
            
            try:
                payload = message.value.get('payload', {})
                if not payload:
                    continue

                op = payload.get('op')
                data = payload.get('after') if op in ['c', 'u'] else payload.get('before')

                if not data or 'query_hash' not in data:
                    continue

                query_hash = data['query_hash']
                redis_key = f"task:{query_hash}"

                if op in ['c', 'u']:
                    task_state = {}
                    for k, v in data.items():
                        if v is None:
                            continue
                        if isinstance(v, dict):
                            task_state[k] = json.dumps(v)
                        else:
                            task_state[k] = v
                    
                    if task_state:
                        redis_client.hset(redis_key, mapping=task_state)
                        log.info(f"UPSERTED state for task '{query_hash}' in Redis.")
                
                elif op == 'd':
                    redis_client.delete(redis_key)
                    log.info(f"DELETED state for task '{query_hash}' from Redis.")

            except Exception as e:
                log.error(f"An unexpected error occurred in the consumption loop: {e}", exc_info=True)
        
        log.debug("Consumer timed out. Looping to update health file.")

if __name__ == "__main__":
    main()