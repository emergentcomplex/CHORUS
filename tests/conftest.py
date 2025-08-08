# Filename: tests/conftest.py
# This file contains shared fixtures for the CHORUS test suite.

import pytest
import os
import psycopg2
import time

from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter

@pytest.fixture(scope="session")
def integration_db_ready():
    """
    A session-scoped fixture that waits for the test database to become
    available. It is NOT auto-used and will only be activated by fixtures
    or tests that explicitly depend on it (e.g., integration tests).
    This prevents it from running during the 'test-fast' unit test workflow.
    """
    test_db_name = os.getenv("DB_NAME", "trident_analysis_test")
    
    conn_params = {
        "host": os.getenv("DB_HOST", "postgres"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "user": os.getenv("DB_USER", "trident_user"),
        "password": os.getenv("DB_PASSWORD", "abcd1234"),
        "dbname": test_db_name
    }

    # Wait for the database service to be available and accept connections.
    retries = 12 # Wait up to 60 seconds
    for i in range(retries):
        try:
            conn = psycopg2.connect(**conn_params)
            conn.close()
            print(f"\n[*] Integration DB '{test_db_name}' connection confirmed.")
            yield
            return
        except psycopg2.OperationalError:
            if i < retries - 1:
                time.sleep(5)
            else:
                pytest.fail(f"Could not connect to integration DB '{test_db_name}' after {retries} retries.")

@pytest.fixture(scope="function")
def db_adapter(integration_db_ready):
    """
    Provides a function-scoped PostgresAdapter instance.
    By depending on 'integration_db_ready', it ensures the database is
    available before any integration test that uses this fixture is run.
    """
    adapter = PostgresAdapter(dbname=os.getenv("DB_NAME", "trident_analysis_test"))
    yield adapter
    adapter.close_all_connections()