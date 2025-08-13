# Filename: tests/integration/test_state_machine_flow.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This integration test validates the core state machine logic of the
# analysis pipeline, ensuring tasks transition through their lifecycle
# states correctly based on database operations.

import pytest
import uuid
import json
from unittest.mock import MagicMock
from chorus_engine.app.use_cases.run_analyst_tier import RunAnalystTier

pytestmark = pytest.mark.integration

# --- Helper Functions ---

def create_initial_task(adapter, query_hash, user_query):
    """Helper to insert a new task into the queue."""
    with adapter.connection.cursor() as cursor:
        cursor.execute("DELETE FROM task_queue WHERE query_hash = %s", (query_hash,))
        cursor.execute(
            "INSERT INTO task_queue (query_hash, user_query, status) VALUES (%s, %s, 'PENDING')",
            (query_hash, json.dumps(user_query))
        )
    adapter.connection.commit()

def get_task_status(adapter, query_hash):
    """Helper to fetch the current status of a task."""
    with adapter.connection.cursor() as cursor:
        cursor.execute("SELECT status FROM task_queue WHERE query_hash = %s", (query_hash,))
        result = cursor.fetchone()
        return result[0] if result else None

# --- The Test ---

def test_full_pipeline_state_transitions(db_adapter, mocker):
    """
    Verifies that a task correctly transitions from PENDING to
    ANALYSIS_IN_PROGRESS and finally to PENDING_SYNTHESIS upon
    successful completion of the Analyst Tier use case.
    """
    print("\n--- Testing State Machine Flow ---")
    query_hash = uuid.uuid4().hex
    user_query = {"query": "test"}

    # Mock dependencies for the use case
    mock_llm = MagicMock()
    mock_persona_repo = MagicMock()
    mock_persona_repo.get_persona.return_value = MagicMock()
    
    # THE DEFINITIVE FIX: Mock the correct method name on the adapter.
    mocker.patch.object(db_adapter, 'query_similar_documents', return_value=[])
    
    mock_task_data = {
        'query_hash': query_hash,
        'user_query': user_query,
        'status': 'PENDING'
    }
    mocker.patch.object(db_adapter, 'get_task', return_value=mock_task_data)

    # 1. ARRANGE: Create the initial task in a PENDING state.
    create_initial_task(db_adapter, query_hash, user_query)
    assert get_task_status(db_adapter, query_hash) == "PENDING"
    print(f"[+] Task {query_hash} created in PENDING state.")

    # 2. ACT: Execute the Analyst Tier use case.
    analyst_use_case = RunAnalystTier(
        llm_adapter=mock_llm,
        db_adapter=db_adapter,
        vector_db_adapter=db_adapter,
        persona_repo=mock_persona_repo
    )
    analyst_use_case.execute(query_hash)
    print(f"[*] Executed Analyst Tier for task {query_hash}.")

    # 3. ASSERT: Verify the task has transitioned to the next state.
    final_status = get_task_status(db_adapter, query_hash)
    assert final_status == "PENDING_SYNTHESIS"
    print(f"[+] SUCCESS: Task {query_hash} correctly transitioned to {final_status}.")