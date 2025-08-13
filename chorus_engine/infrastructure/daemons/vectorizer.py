# Filename: chorus_engine/infrastructure/daemons/vectorizer.py
# 🔱 The Scribe: A daemon that watches the datalake and populates the semantic space.

import os
import time
import json
import logging
import requests
import uuid
from datetime import datetime
import psycopg2

# --- Configuration ---
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

DATALAKE_PATH = "/app/datalake"
EMBEDDER_URL = "http://chorus-embedder:5003"
POLL_INTERVAL_SECONDS = 10
PROCESSED_FILES_LOG = os.path.join(DATALAKE_PATH, ".vectorizer_log")

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# --- Helper Functions ---

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            logger.info("✅ Database connection established.")
            return conn
        except psycopg2.OperationalError as e:
            logger.warning(f"Database not ready, retrying in 5 seconds... Error: {e}")
            time.sleep(5)

def initialize_dependencies():
    """Wait for the embedding service to be healthy."""
    health_url = f"{EMBEDDER_URL}/health"
    logger.info("Waiting for embedding service to be healthy...")
    while True:
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200 and response.json().get("model_loaded"):
                logger.info("✅ Embedding service is healthy and model is loaded.")
                break
        except requests.exceptions.RequestException:
            logger.warning("Embedding service not yet available. Retrying...")
        time.sleep(5)

def get_processed_files():
    """Load the set of already processed file identifiers."""
    if not os.path.exists(PROCESSED_FILES_LOG):
        return set()
    with open(PROCESSED_FILES_LOG, 'r') as f:
        return set(line.strip() for line in f)

def log_processed_file(file_identifier):
    """Log a file identifier as processed."""
    with open(PROCESSED_FILES_LOG, 'a') as f:
        f.write(f"{file_identifier}\n")

def get_embeddings(texts):
    """Get embeddings from the dedicated service."""
    embed_url = f"{EMBEDDER_URL}/embed"
    try:
        response = requests.post(embed_url, json={"texts": texts}, timeout=60)
        response.raise_for_status()
        return response.json()["embeddings"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get embeddings: {e}")
        return None

def process_file(filepath, db_cursor):
    """Process a single JSON file from the datalake."""
    filename = os.path.basename(filepath)
    # THE DEFINITIVE FIX #1: Correctly parse the source vertical as a string.
    source_vertical = filename.split('_')[0]
    logger.info(f"Processing file: {filename}")

    with open(filepath, 'r') as f:
        data = json.load(f)

    if not isinstance(data, list):
        logger.warning(f"Skipping {filename}: content is not a list.")
        return

    chunks_to_embed = []
    metadata_for_chunks = []

    for record in data:
        content = record.get("content", "") or record.get("summary", "")
        doc_date_str = record.get("publication_date") or record.get("updated_date") or record.get("published")
        doc_date = None
        if doc_date_str:
            try:
                doc_date = datetime.fromisoformat(doc_date_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                logger.warning(f"Could not parse date '{doc_date_str}' in {filename}")
        
        if not content:
            continue

        temporal_prefix = doc_date.isoformat() if doc_date else "UNKNOWN_DATE"
        content_chunk = f"{temporal_prefix} | {content}"
        
        chunks_to_embed.append(content_chunk)
        metadata_for_chunks.append({
            "source_vertical": source_vertical,
            "source_identifier": record.get("id") or filename,
            "document_date": doc_date,
            "content_chunk": content_chunk
        })

    if not chunks_to_embed:
        logger.info(f"No content to embed in {filename}.")
        return

    embeddings = get_embeddings(chunks_to_embed)
    if not embeddings:
        logger.error(f"Could not generate embeddings for {filename}. Skipping.")
        return

    for meta, embedding in zip(metadata_for_chunks, embeddings):
        db_cursor.execute(
            """
            INSERT INTO semantic_vectors (vector_id, source_vertical, source_identifier, document_date, content_chunk, embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                # THE DEFINITIVE FIX #2: Explicitly cast the UUID to a string for the driver.
                str(uuid.uuid4()),
                meta["source_vertical"],
                meta["source_identifier"],
                meta["document_date"],
                meta["content_chunk"],
                json.dumps(embedding)
            )
        )
    logger.info(f"Successfully inserted {len(embeddings)} vectors from {filename}.")


def main_loop():
    """The main processing loop for the vectorizer daemon."""
    logger.info("Starting vectorizer daemon...")
    initialize_dependencies()
    
    db_conn = get_db_connection()

    while True:
        try:
            processed_files = get_processed_files()
            # THE DEFINITIVE FIX #3: Get a fresh list of files on each iteration to avoid race conditions.
            current_files = os.listdir(DATALAKE_PATH)
            with db_conn.cursor() as cursor:
                for filename in current_files:
                    if filename.endswith(".json") and filename not in processed_files:
                        filepath = os.path.join(DATALAKE_PATH, filename)
                        # Check for file existence immediately before processing.
                        if not os.path.exists(filepath):
                            continue
                        try:
                            process_file(filepath, cursor)
                            db_conn.commit()
                            log_processed_file(filename)
                        except Exception as e:
                            logger.error(f"CRITICAL FAILURE processing file {filename}. Rolling back.", exc_info=True)
                            db_conn.rollback()
        except Exception as e:
            logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            if db_conn.closed:
                db_conn = get_db_connection()

        logger.debug(f"Scan complete. Sleeping for {POLL_INTERVAL_SECONDS} seconds.")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main_loop()