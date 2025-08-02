# Filename: tests/integration/test_pipeline_wiring.py (Unified Stack Edition)
import pytest
from unittest.mock import MagicMock

from chorus_engine.adapters.llm.gemini_adapter import GeminiAdapter
from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter
from chorus_engine.adapters.persistence.persona_repo import PersonaRepository
from chorus_engine.app.use_cases.run_analysis_pipeline import RunAnalysisPipeline

pytestmark = pytest.mark.integration

@pytest.mark.integration
def test_composition_root_wiring(mocker):
    """
    Verifies that the main application components can be instantiated and
    injected into the use case without raising errors. This test assumes
    the database is available on its configured host/port.
    """
    print("\n--- Testing Application Composition Root ---")
    mocker.patch('chorus_engine.adapters.llm.gemini_adapter.GeminiAdapter', return_value=MagicMock())
    try:
        print("[*] Instantiating real adapters...")
        llm_adapter = GeminiAdapter()
        db_adapter = PostgresAdapter() # Reads connection info from environment
        persona_repo = PersonaRepository()

        print("[*] Injecting adapters into the use case...")
        pipeline = RunAnalysisPipeline(
            llm_adapter=llm_adapter,
            db_adapter=db_adapter,
            vector_db_adapter=db_adapter,
            persona_repo=persona_repo
        )
        print("[+] SUCCESS: All components instantiated and wired together successfully.")
        assert pipeline is not None
    except Exception as e:
        pytest.fail(f"Failed to wire the application components. Error: {e}")

@pytest.mark.integration
def test_database_connection():
    """
    A simple but vital integration test to confirm that the PostgresAdapter
    can actually connect to the database started by Docker Compose.
    """
    print("\n--- Testing Real Database Connection ---")
    try:
        adapter = PostgresAdapter() # Reads connection info from environment
        conn = adapter._get_connection()
        assert conn is not None and not conn.closed
        print("[+] SUCCESS: Database connection successful.")
        adapter._release_connection(conn)
    except Exception as e:
        pytest.fail(f"PostgresAdapter failed to connect to the database. Error: {e}")
