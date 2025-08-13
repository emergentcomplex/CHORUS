# Filename: tests/conftest.py
# 🔱 CHORUS Test Configuration (v3 - Resilient Teardown)

import pytest
import os
import psycopg2
from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter

# --- Canonical Database Fixtures ---

@pytest.fixture(scope="module")
def get_db_connection():
    """
    A module-scoped fixture that provides a raw, direct psycopg2 connection
    to the test database. It ensures the connection is closed after all
    tests in the module have run.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            port=os.getenv("DB_PORT", 5432),
            user=os.getenv("DB_USER", "trident_user"),
            password=os.getenv("DB_PASSWORD", "abcd1234"),
            dbname=os.getenv("DB_NAME", "trident_analysis_test")
        )
        print(f"\n[*] Integration DB '{os.getenv('DB_NAME')}' connection confirmed for module.")
        yield conn
    except psycopg2.OperationalError as e:
        pytest.fail(f"Failed to connect to the test database: {e}")
    finally:
        if conn:
            conn.close()

@pytest.fixture(scope="function")
def db_adapter(get_db_connection):
    """
    The new, canonical function-scoped fixture for providing a PostgresAdapter.
    It depends on the module-level connection and ensures that each test
    function gets a fresh adapter instance but shares the underlying connection
    for efficiency. It also handles transaction rollback for test isolation.
    """
    # Start a new transaction for the test
    get_db_connection.autocommit = False
    
    yield PostgresAdapter(get_db_connection)
    
    # THE DEFINITIVE FIX: Make the teardown resilient.
    # Only try to rollback if the connection wasn't explicitly closed by a test.
    if not get_db_connection.closed:
        get_db_connection.rollback()