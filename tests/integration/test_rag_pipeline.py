# Filename: tests/integration/test_rag_pipeline.py
# 🔱 The definitive integration test for the Oracle RAG pipeline (v4 - Final Fixture)

import pytest
import os
import json
import time
import uuid
from datetime import datetime, timezone
import logging
from psycopg2.extras import RealDictCursor

pytestmark = pytest.mark.integration
logger = logging.getLogger(__name__)

# --- Fixtures ---

@pytest.fixture(scope="function")
def isolated_test_datalake():
    """
    Provides the path to the isolated test datalake and ensures it's clean.
    This fixture now aggressively cleans the directory to ensure a true
    hermetic test run every time.
    """
    test_datalake_dir = "/app/datalake"
    
    # THE DEFINITIVE FIX: Aggressively clean the datalake directory.
    # This removes the JSON file AND the .vectorizer_log from previous runs.
    for f in os.listdir(test_datalake_dir):
        file_path = os.path.join(test_datalake_dir, f)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.error(f'Failed to delete {file_path}. Reason: {e}')
            
    yield test_datalake_dir

# --- The Test ---

def test_file_in_datalake_is_vectorized(isolated_test_datalake, db_adapter):
    """
    Verifies the end-to-end RAG ingestion pipeline:
    1. A file is placed in the datalake.
    2. The vectorizer daemon is expected to pick it up.
    3. The test polls the database to confirm the file's content has been vectorized
       and stored in the `semantic_vectors` table.
    """
    # 1. Arrange: Create a unique test file and place it in the isolated datalake.
    unique_content = f"Unique test content {uuid.uuid4()}"
    doc_timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    doc_date_iso = doc_timestamp.isoformat()
    
    test_data = [{"id": f"test-doc-{uuid.uuid4()}", "publication_date": doc_date_iso, "content": unique_content}]
    test_filename = f"arxiv_{uuid.uuid4()}.json"
    test_filepath = os.path.join(isolated_test_datalake, test_filename)
    
    with open(test_filepath, 'w') as f:
        json.dump(test_data, f)
        
    logger.info(f"Created test file '{test_filepath}' with content: '{unique_content}'")

    # 2. Act & Assert: Poll the database for the vectorized record.
    max_wait_seconds = 45
    poll_interval = 3
    start_time = time.time()
    record_found = False
    expected_content_chunk = f"{doc_date_iso} | {unique_content}"

    with db_adapter.connection.cursor(cursor_factory=RealDictCursor) as cursor:
        while time.time() - start_time < max_wait_seconds:
            logger.info(f"Polling database... Elapsed: {int(time.time() - start_time)}s")
            cursor.execute("SELECT content_chunk, document_date FROM semantic_vectors WHERE content_chunk = %s", (expected_content_chunk,))
            result = cursor.fetchone()
            
            if result:
                logger.info("Record found in semantic_vectors table!")
                assert result['content_chunk'] == expected_content_chunk
                assert result['document_date'].replace(microsecond=0) == doc_timestamp
                record_found = True
                break
            
            time.sleep(poll_interval)

    if not record_found:
        with db_adapter.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT content_chunk FROM semantic_vectors")
            all_chunks = cursor.fetchall()
            logger.error(f"All chunks in DB: {[c['content_chunk'] for c in all_chunks]}")
        pytest.fail(f"Vectorizer failed to process the test file within {max_wait_seconds} seconds.")