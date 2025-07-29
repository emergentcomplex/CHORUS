# Filename: tests/unit/test_use_cases.py (Corrected)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# Unit tests for the Application layer (Use Cases). These tests are the most
# critical as they prove our core business logic is decoupled and testable in
# isolation. We use mock implementations of our interfaces to achieve this.

import pytest
from unittest.mock import MagicMock


from chorus_engine.app.use_cases.run_analysis_pipeline import RunAnalysisPipeline
from chorus_engine.app.interfaces import (
    LLMInterface, DatabaseInterface, VectorDBInterface, PersonaRepositoryInterface
)
from chorus_engine.core.entities import AnalysisTask, Persona

# ==============================================================================
# RunAnalysisPipeline Unit Tests
# ==============================================================================

@pytest.fixture
def mock_adapters():
    """A fixture that creates mock objects for all required interfaces."""
    mock_llm = MagicMock(spec=LLMInterface)
    mock_db = MagicMock(spec=DatabaseInterface)
    mock_vector_db = MagicMock(spec=VectorDBInterface)
    mock_persona_repo = MagicMock(spec=PersonaRepositoryInterface)
    
    mock_persona = Persona(
        id="director_alpha",
        name="Test Director",
        worldview="A test worldview.",
        axioms=["Test axiom 1."]
    )
    mock_persona_repo.get_persona_by_id.return_value = mock_persona
    
    return {
        "llm": mock_llm,
        "db": mock_db,
        "vector_db": mock_vector_db,
        "persona_repo": mock_persona_repo
    }

def test_run_analysis_pipeline_successful_execution(mock_adapters):
    """
    Tests the entire use case execution path for a successful run.
    """
    # --- Arrange ---
    pipeline = RunAnalysisPipeline(
        llm_adapter=mock_adapters["llm"],
        db_adapter=mock_adapters["db"],
        vector_db_adapter=mock_adapters["vector_db"],
        persona_repo=mock_adapters["persona_repo"]
    )

    # DEFINITIVE FIX: Pass a dictionary for user_query, not a JSON string.
    task = AnalysisTask(
        query_hash="test_hash",
        user_query={"query": "test query"},
        status="IN_PROGRESS"
    )

    mock_adapters["vector_db"].query_similar_documents.return_value = [{"content": "doc1"}]
    mock_adapters["llm"].instruct.side_effect = [
        "HARVESTER: usaspending_search\nKEYWORDS: test",
        "[NARRATIVE ANALYSIS]\nNarrative.\n[ARGUMENT MAP]\nMap.\n[INTELLIGENCE GAPS]\nGaps."
    ]
    mock_adapters["db"].queue_and_monitor_harvester_tasks.return_value = True
    mock_adapters["db"].load_data_from_datalake.return_value = {"news": "some data"}

    # --- Act ---
    pipeline.execute(task)

    # --- Assert ---
    mock_adapters["db"].log_progress.assert_any_call("test_hash", "Starting analysis pipeline...")
    mock_adapters["vector_db"].query_similar_documents.assert_called_once_with("Quantum Computing", limit=200)
    assert mock_adapters["llm"].instruct.call_count == 2
    mock_adapters["db"].queue_and_monitor_harvester_tasks.assert_called_once()
    mock_adapters["db"].load_data_from_datalake.assert_called_once()
    mock_adapters["db"].update_analysis_task_completion.assert_called_once()
    mock_adapters["db"].update_analysis_task_failure.assert_not_called()

def test_run_analysis_pipeline_handles_failure(mock_adapters):
    """
    Tests that if any step in the pipeline raises an exception, the use case
    correctly calls the 'update_analysis_task_failure' interface method.
    """
    # --- Arrange ---
    pipeline = RunAnalysisPipeline(
        llm_adapter=mock_adapters["llm"],
        db_adapter=mock_adapters["db"],
        vector_db_adapter=mock_adapters["vector_db"],
        persona_repo=mock_adapters["persona_repo"]
    )
    
    # DEFINITIVE FIX: Pass a dictionary for user_query, not a JSON string.
    task = AnalysisTask(
        query_hash="test_hash_fail",
        user_query={"query": "test query"},
        status="IN_PROGRESS"
    )
    
    mock_adapters["vector_db"].query_similar_documents.side_effect = Exception("Vector DB is down")

    # --- Act ---
    pipeline.execute(task)

    # --- Assert ---
    mock_adapters["db"].update_analysis_task_failure.assert_called_once_with("test_hash_fail", "Vector DB is down")
    mock_adapters["db"].update_analysis_task_completion.assert_not_called()
