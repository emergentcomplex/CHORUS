# Filename: tests/integration/test_state_machine_flow.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This integration test verifies the correct state transitions of a task
# as it moves through the full "Analyst -> Director -> Judge" pipeline.

import pytest
import os
import json
import hashlib
from unittest.mock import MagicMock

from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter
from chorus_engine.adapters.persistence.persona_repo import PersonaRepository
from chorus_engine.app.use_cases.run_analyst_tier import RunAnalystTier
from chorus_engine.app.use_cases.run_director_tier import RunDirectorTier
from chorus_engine.app.use_cases.run_judge_tier import RunJudgeTier
from chorus_engine.core.entities import AnalysisTask

pytestmark = pytest.mark.integration

# --- Fixtures ---

@pytest.fixture(scope="module")
def db_adapter():
    """Provides a single PostgresAdapter instance for the entire test module."""
    return PostgresAdapter()

@pytest.fixture(scope="module")
def persona_repo():
    """Provides a single PersonaRepository instance."""
    return PersonaRepository()

@pytest.fixture
def mock_llm():
    """Provides a mocked LLM adapter configured for the entire pipeline flow."""
    llm = MagicMock()
    llm.is_configured.return_value = True
    llm.instruct.side_effect = [
        # Analyst Tier: 4x (Planner + Synthesizer)
        "HARVESTER: usaspending_search\nKEYWORDS: test1", "Analyst Report 1",
        "HARVESTER: usaspending_search\nKEYWORDS: test2", "Analyst Report 2",
        "HARVESTER: usaspending_search\nKEYWORDS: test3", "Analyst Report 3",
        "HARVESTER: usaspending_search\nKEYWORDS: test4", "Analyst Report 4",
        # Director Tier
        "This is the Director's synthesized briefing.",
        # Judge Tier
        "[NARRATIVE ANALYSIS]\nFinal Narrative.\n[ARGUMENT MAP]\nFinal Map.\n[INTELLIGENCE GAPS]\nFinal Gaps."
    ]
    return llm

# --- Helper Functions ---

def get_task_status(db_adapter, query_hash):
    """Helper to get the current status of a task from the database."""
    conn = db_adapter._get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT status FROM task_queue WHERE query_hash = %s", (query_hash,))
            result = cursor.fetchone()
            return str(result[0]) if result else None # Cast enum to string
    finally:
        db_adapter._release_connection(conn)

def setup_task(db_adapter, query_text="state machine test"):
    """Helper to clean up and insert a new task for testing."""
    query_data = {"query": query_text, "mode": "deep_dive"}
    query_hash = hashlib.md5(json.dumps(query_data, sort_keys=True).encode()).hexdigest()
    
    conn = db_adapter._get_connection()
    try:
        with conn.cursor() as cursor:
            # Clean up in reverse dependency order
            cursor.execute("DELETE FROM director_briefings WHERE query_hash = %s", (query_hash,))
            cursor.execute("DELETE FROM analyst_reports WHERE query_hash = %s", (query_hash,))
            cursor.execute("DELETE FROM task_progress WHERE query_hash = %s", (query_hash,))
            cursor.execute("DELETE FROM query_state WHERE query_hash = %s", (query_hash,))
            cursor.execute("DELETE FROM task_queue WHERE query_hash = %s", (query_hash,))
            
            sql = "INSERT INTO task_queue (user_query, query_hash, status) VALUES (%s, %s, 'PENDING_ANALYSIS')"
            cursor.execute(sql, (json.dumps(query_data), query_hash))
        conn.commit()
    finally:
        db_adapter._release_connection(conn)
        
    return query_hash

# --- The Test ---

def test_full_pipeline_state_transitions(db_adapter, persona_repo, mock_llm):
    """
    Verifies that a task correctly transitions through all states of the
    adversarial pipeline, from PENDING_ANALYSIS to COMPLETED.
    """
    print("\n--- Testing Full State Machine Flow ---")
    
    # --- Arrange ---
    query_hash = setup_task(db_adapter)
    print(f"[*] Test task created with hash: {query_hash}")

    analyst_tier_uc = RunAnalystTier(mock_llm, db_adapter, db_adapter, persona_repo)
    director_tier_uc = RunDirectorTier(mock_llm, db_adapter, persona_repo)
    judge_tier_uc = RunJudgeTier(mock_llm, db_adapter, persona_repo)
    
    # Mock the harvester monitoring to speed up the test, as we are not testing harvesters here.
    db_adapter.queue_and_monitor_harvester_tasks = MagicMock(return_value=True)

    # --- Act & Assert: Analyst Tier ---
    print("[*] Executing Analyst Tier...")
    task_for_analyst = AnalysisTask(query_hash=query_hash, user_query={"query": "test"}, status="ANALYSIS_IN_PROGRESS")
    analyst_tier_uc.execute(task_for_analyst)
    
    status_after_analyst = get_task_status(db_adapter, query_hash)
    print(f"  -> Status after Analyst Tier: {status_after_analyst}")
    assert status_after_analyst == 'PENDING_SYNTHESIS'

    # --- Act & Assert: Director Tier ---
    print("[*] Executing Director Tier...")
    task_for_director = AnalysisTask(query_hash=query_hash, user_query={"query": "test"}, status="SYNTHESIS_IN_PROGRESS")
    director_tier_uc.execute(task_for_director)

    status_after_director = get_task_status(db_adapter, query_hash)
    print(f"  -> Status after Director Tier: {status_after_director}")
    assert status_after_director == 'PENDING_JUDGMENT'

    # --- Act & Assert: Judge Tier ---
    print("[*] Executing Judge Tier...")
    task_for_judge = AnalysisTask(query_hash=query_hash, user_query={"query": "test"}, status="JUDGMENT_IN_PROGRESS")
    judge_tier_uc.execute(task_for_judge)

    status_after_judge = get_task_status(db_adapter, query_hash)
    print(f"  -> Status after Judge Tier: {status_after_judge}")
    assert status_after_judge == 'COMPLETED'
    
    print("[+] SUCCESS: Task correctly transitioned through all pipeline states.")