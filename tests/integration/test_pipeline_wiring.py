# Filename: tests/integration/test_pipeline_wiring.py (Corrected)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# Integration tests to verify that the core components of the application
# can be instantiated and wired together correctly.

import pytest
from unittest.mock import MagicMock


from chorus_engine.adapters.llm.gemini_adapter import GeminiAdapter
from chorus_engine.adapters.persistence.mariadb_adapter import MariaDBAdapter
from chorus_engine.adapters.persistence.persona_repo import PersonaRepository
from chorus_engine.app.use_cases.run_analysis_pipeline import RunAnalysisPipeline

@pytest.mark.integration
def test_composition_root_wiring(mocker):
    """
    Verifies that the main application components can be instantiated and
    injected into the use case without raising errors.

    This test uses a real database adapter but mocks the LLM adapter to
    avoid network calls.
    """
    print("\n--- Testing Application Composition Root ---")
    
    mocker.patch('chorus_engine.adapters.llm.gemini_adapter.GeminiAdapter', return_value=MagicMock())
    
    try:
        print("[*] Instantiating real adapters...")
        llm_adapter = GeminiAdapter()
        db_adapter = MariaDBAdapter()
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
        assert pipeline.db is db_adapter
        assert pipeline.llm is llm_adapter
        assert pipeline.persona is not None

    except Exception as e:
        pytest.fail(f"Failed to wire the application components. Error: {e}")

@pytest.mark.integration
def test_database_connection():
    """
    A simple but vital integration test to confirm that the MariaDBAdapter
    can actually connect to the database specified in the .env file.
    """
    print("\n--- Testing Real Database Connection ---")
    try:
        adapter = MariaDBAdapter()
        conn = adapter._get_connection()
        
        # DEFINITIVE FIX: The presence of a non-None connection object
        # after the call is the indicator of success.
        assert conn is not None
        
        # To be absolutely sure, we can check a simple property like the server version.
        assert conn.server_version is not None
        
        print("[+] SUCCESS: Database connection successful.")
        conn.close()
    except Exception as e:
        pytest.fail(f"MariaDBAdapter failed to connect to the database. Error: {e}")

