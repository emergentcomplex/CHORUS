# Filename: chorus_engine/infrastructure/services/task_event_logger.py
#
# A simple stream processing service that consumes Change Data Capture (CDC)
# events for the task_queue table and logs them. This serves as a proof-of-concept
# for the end-to-end dataflow architecture.

import json
import logging
import time
import os

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from chorus_engine.config import setup_logging

# --- CONFIGURATION ---
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
# THE DEFINITIVE FIX: Align the topic with Debezium's default naming convention.
CDC_TOPIC = "chorus.public.task_queue"

# Initialize centralized logging
setup_logging()
log = logging.getLogger(__name__)

def main():
    """Main function to run the consumer service."""
    log.info("--- CHORUS Task Event Logger Service Initializing ---")
    log.info(f"Attempting to connect to Kafka broker at {KAFKA_BROKER}...")

    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(
                CDC_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest',
                consumer_timeout_ms=10000 # 10 seconds
            )
            log.info(f"Successfully connected to Kafka and subscribed to topic '{CDC_TOPIC}'.")
        except NoBrokersAvailable:
            log.warning("Could not connect to Kafka broker. Retrying in 15 seconds...")
            time.sleep(15)
        except Exception as e:
            log.error(f"An unexpected error occurred during consumer creation: {e}")
            time.sleep(15)

    log.info("--- Starting event consumption loop ---")
    for message in consumer:
        try:
            payload = message.value.get('payload', {})
            if not payload:
                continue

            op = payload.get('op') # Operation: c=create, u=update, d=delete
            before = payload.get('before')
            after = payload.get('after')

            if op == 'c' and after:
                log.info(f"[CDC EVENT] CREATE: New task queued. Hash: {after.get('query_hash')}, Status: {after.get('status')}")
            elif op == 'u' and before and after:
                if before.get('status') != after.get('status'):
                    log.info(f"[CDC EVENT] UPDATE: Task status changed for hash {after.get('query_hash')}: {before.get('status')} -> {after.get('status')}")
                else:
                    # Log other changes if needed, e.g., worker_id assignment
                    log.info(f"[CDC EVENT] UPDATE: Task record updated for hash {after.get('query_hash')}")
            elif op == 'd' and before:
                log.info(f"[CDC EVENT] DELETE: Task record removed. Hash: {before.get('query_hash')}")

        except (json.JSONDecodeError, AttributeError) as e:
            log.error(f"Failed to process message: {e}. Raw value: {message.value}")
        except Exception as e:
            log.error(f"An unexpected error occurred in the consumption loop: {e}")

if __name__ == "__main__":
    main()