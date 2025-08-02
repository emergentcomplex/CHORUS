# Filename: tests/integration/test_pipeline_wiring.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This integration test verifies that the main application components can be
# instantiated and wired together correctly for the new multi-tier pipeline.

import pytest
from unittest.mock import MagicMock

from chorus_engine.adapters.llm.gemini_adapter import GeminiAdapter
from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter
from chorus_engine.adapters.persistence.persona_repo import PersonaRepository
from chorus_engine.app.use_cases.run_analyst_tier import RunAnalystTier
from chorus_engine.app.use_cases.run_director_tier import RunDirectorTier
from chorus_engine.app.use_cases.run_judge_tier import RunJudgeTier

pytestmark = pytest.mark.integration

@pytest.fixture(scope="function") # THE DEFINITIVE FIX: Changed scope from "module" to "function"
def real_adapters(mocker):
    """
    A fixture that instantiates the real adapters needed for wiring,
    but mocks the external LLM dependency to avoid API calls.
    """
    mocker.patch('chorus_engine.adapters.llm.gemini_adapter.GeminiAdapter', return_value=MagicMock())
    return {
        "llm": GeminiAdapter(),
        "db": PostgresAdapter(),
        "persona_repo": PersonaRepository()
    }

def test_composition_root_wiring_for_all_tiers(real_adapters):
    """
    Verifies that all three tiers of the analysis pipeline can be
    instantiated and wired together with the core adapters.
    """
    print("\n--- Testing Application Composition Root for Multi-Tier Pipeline ---")
    try:
        print("[*] Instantiating Analyst Tier...")
        analyst_tier = RunAnalystTier(
            llm_adapter=real_adapters["llm"],
            db_adapter=real_adapters["db"],
            vector_db_adapter=real_adapters["db"],
            persona_repo=real_adapters["persona_repo"]
        )
        assert analyst_tier is not None
        print("[+] Analyst Tier wired successfully.")

        print("[*] Instantiating Director Tier...")
        director_tier = RunDirectorTier(
            llm_adapter=real_adapters["llm"],
            db_adapter=real_adapters["db"],
            persona_repo=real_adapters["persona_repo"]
        )
        assert director_tier is not None
        print("[+] Director Tier wired successfully.")

        print("[*] Instantiating Judge Tier...")
        judge_tier = RunJudgeTier(
            llm_adapter=real_adapters["llm"],
            db_adapter=real_adapters["db"],
            persona_repo=real_adapters["persona_repo"]
        )
        assert judge_tier is not None
        print("[+] Judge Tier wired successfully.")

        print("\n[✅] SUCCESS: All pipeline components instantiated and wired together.")

    except Exception as e:
        pytest.fail(f"Failed to wire the application components. Error: {e}")

def test_database_connection():
    """
    A simple but vital integration test to confirm that the PostgresAdapter
    can actually connect to the database started by Docker Compose.
    """
    print("\n--- Testing Real Database Connection ---")
    try:
        adapter = PostgresAdapter()
        conn = adapter._get_connection()
        assert conn is not None and not conn.closed
        print("[+] SUCCESS: Database connection successful.")
        adapter._release_connection(conn)
    except Exception as e:
        pytest.fail(f"PostgresAdapter failed to connect to the database. Error: {e}")