# Filename: tests/integration/test_vector_capabilities.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This integration test proves the new vector storage and query capabilities
# of the PostgresAdapter. This version is 100% deterministic.

import pytest
import numpy as np

from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter

pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def db_adapter():
    """Provides a real PostgresAdapter instance for the test module."""
    return PostgresAdapter()

def test_save_and_query_embeddings(db_adapter, monkeypatch):
    """
    Verifies the end-to-end functionality of saving and querying vector embeddings
    in a fully deterministic way.
    """
    print("\n--- Testing Vector Capabilities: Save and Query ---")
    
    # 1. Arrange: Create sample data with embeddings of the correct dimension (768).
    vec1 = np.zeros(768)
    vec1[0] = 1.0  # A distinct vector for "quantum"

    vec2 = np.zeros(768)
    vec2[1] = 1.0  # A distinct vector for "hypersonic"
    
    records_to_save = [
        {"id": "vec_test_1", "content": "This document is about quantum computing.", "embedding": vec1},
        {"id": "vec_test_2", "content": "This document is about hypersonic missiles.", "embedding": vec2}
    ]

    # 2. Act: Save the embeddings to the database.
    print("[*] Saving test embeddings to the database...")
    db_adapter.save_embeddings(records_to_save)
    print("[+] Save operation completed.")

    # 3. Act: Query for a document similar to our first vector.
    # We create a query vector that is mathematically closest to vec1.
    query_embedding = np.zeros(768)
    query_embedding[0] = 0.98
    
    # THE DEFINITIVE FIX: Use monkeypatch to correctly replace the class attribute.
    # This ensures our MockModel is used instead of the real SentenceTransformer.
    class MockModel:
        def encode(self, query_text):
            # This mock completely ignores the input text and returns our deterministic vector.
            return query_embedding
            
    monkeypatch.setattr(PostgresAdapter, '_embedding_model', MockModel())

    print("[*] Querying for documents with a deterministic vector...")
    similar_docs = db_adapter.query_similar_documents("A query about quantum computing", limit=1)
    print(f"[+] Query returned {len(similar_docs)} document(s).")

    # 4. Assert: The most similar document MUST be the one about quantum computing.
    assert len(similar_docs) == 1, "Expected exactly one document to be returned."
    
    top_result = similar_docs[0]
    print(f"  -> Top result: '{top_result['content']}' with distance {top_result['distance']:.4f}")
    
    assert top_result['content'] == "This document is about quantum computing.", \
        "The returned document was not the expected one."
    
    print("[+] SUCCESS: Vector save and query functionality is verified deterministically.")