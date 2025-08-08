# Filename: tests/integration/test_daemon_resilience.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This test validates that the PostgresAdapter's connection resilience
# decorator can survive and recover from a simulated database connection error.

import pytest
import psycopg2
from unittest.mock import patch

from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter
from chorus_engine.core.entities import AnalysisTask

pytestmark = pytest.mark.integration

@pytest.fixture(scope="function")
def db_adapter():
    """Provides a fresh PostgresAdapter for each test function."""
    return PostgresAdapter()

def test_adapter_recovers_from_connection_error(db_adapter):
    """
    Verifies that the @resilient_connection decorator correctly handles
    a psycopg2.OperationalError by invalidating the pool and allowing a
    subsequent call to succeed.
    """
    print("\n--- [Resilience Test: Adapter Connection Recovery] ---")

    # 1. First call should succeed, establishing a good connection pool.
    print("[*] Making initial successful call to establish connection...")
    available_harvesters = db_adapter.get_available_harvesters()
    assert isinstance(available_harvesters, list)
    print("[+] Initial call successful.")

    # 2. Simulate a database failure by patching the internal _get_connection
    #    method to raise an OperationalError, just as if the DB had restarted.
    with patch.object(PostgresAdapter, '_get_connection', side_effect=psycopg2.OperationalError("Simulated database connection failure")):
        print("[*] Simulating database failure. Expecting OperationalError...")
        with pytest.raises(psycopg2.OperationalError):
            db_adapter.get_available_harvesters()
        print("[+] Adapter correctly raised OperationalError.")

    # 3. The @resilient_connection decorator should have caught the error and
    #    closed the connection pool. The *next* call should succeed by creating
    #    a new, fresh pool.
    print("[*] Making second call, expecting automatic recovery...")
    try:
        available_harvesters_after_failure = db_adapter.get_available_harvesters()
        assert isinstance(available_harvesters_after_failure, list)
        print("[+] SUCCESS: Adapter recovered and second call was successful.")
    except Exception as e:
        pytest.fail(f"Adapter failed to recover from the connection error. Error: {e}")