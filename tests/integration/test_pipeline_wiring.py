# Filename: tests/integration/test_pipeline_wiring.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This integration test suite validates the fundamental "wiring" of the
# system's core components, ensuring they can be instantiated and can
# connect to their essential dependencies like the database.

import pytest
from unittest.mock import MagicMock
from chorus_engine.app.use_cases.run_analyst_tier import RunAnalystTier
from chorus_engine.adapters.llm.gemini_adapter import GeminiAdapter
from chorus_engine.adapters.persistence.persona_repo import PersonaRepository

pytestmark = pytest.mark.integration

# --- Fixtures ---

@pytest.fixture(scope="function")
def real_adapters(mocker, db_adapter):
    """
    A fixture that instantiates the real adapters needed for wiring,
    but mocks the external LLM dependency to avoid API calls.
    """
    mocker.patch('chorus_engine.adapters.llm.gemini_adapter.GeminiAdapter', return_value=MagicMock())
    return {
        "llm": GeminiAdapter(),
        "db": db_adapter,
        "persona_repo": PersonaRepository()
    }

# --- Tests ---

def test_composition_root_wiring_for_all_tiers(real_adapters):
    """
    Verifies that the main use case classes can be instantiated with their
    real dependencies (or mocks), confirming the composition root is valid.
    """
    print("\n--- Testing Composition Root Wiring ---")
    try:
        # Test Analyst Tier wiring
        analyst_use_case = RunAnalystTier(
            llm_adapter=real_adapters["llm"],
            db_adapter=real_adapters["db"],
            vector_db_adapter=real_adapters["db"], # Pass the same adapter for both roles
            persona_repo=real_adapters["persona_repo"]
        )
        assert isinstance(analyst_use_case, RunAnalystTier)
        print("[+] SUCCESS: RunAnalystTier wired successfully.")

    except Exception as e:
        pytest.fail(f"Failed to wire the composition root. Error: {e}")

def test_database_connection(db_adapter):
    """
    A simple but vital integration test to confirm that the PostgresAdapter
    can actually connect to the database started by Docker Compose.
    """
    print("\n--- Testing Real Database Connection ---")
    try:
        with db_adapter.connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
        print("[+] SUCCESS: Database connection and query successful.")
    except Exception as e:
        pytest.fail(f"PostgresAdapter failed to connect to the database. Error: {e}")