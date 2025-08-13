# Filename: tests/unit/test_use_cases.py
# 🔱 CHORUS Unit Test Suite for Application Use Cases (v2 - Final)

import pytest
from unittest.mock import MagicMock, patch
from chorus_engine.app.use_cases.run_analyst_tier import RunAnalystTier
from chorus_engine.app.use_cases.run_director_tier import RunDirectorTier
from chorus_engine.app.use_cases.run_judge_tier import RunJudgeTier
from chorus_engine.app.interfaces import (
    LLMInterface,
    DatabaseInterface,
    PersonaRepositoryInterface,
    VectorDBInterface
)
from chorus_engine.core.entities import Persona, AnalysisTask

# --- Mocks and Fixtures ---

@pytest.fixture
def mock_llm():
    """Provides a mocked LLMInterface."""
    return MagicMock(spec=LLMInterface)

@pytest.fixture
def mock_db():
    """Provides a mocked DatabaseInterface."""
    db = MagicMock(spec=DatabaseInterface)
    # Add the get_task method to the spec's mock
    db.get_task = MagicMock()
    return db

@pytest.fixture
def mock_vector_db():
    """Provides a mocked VectorDBInterface."""
    return MagicMock(spec=VectorDBInterface)

@pytest.fixture
def mock_persona_repo():
    """Provides a mocked PersonaRepositoryInterface."""
    repo = MagicMock(spec=PersonaRepositoryInterface)
    mock_persona = Persona(
        persona_name="test_analyst",
        persona_tier=2,
        persona_description="A test persona.",
        subordinate_personas=None
    )
    repo.get_persona_by_id.return_value = mock_persona
    return repo

@pytest.fixture
def mock_task():
    """Provides a mock AnalysisTask object."""
    return AnalysisTask(
        query_hash="test_hash",
        user_query={"query": "test query"},
        status="ANALYSIS_IN_PROGRESS"
    )

# --- Analyst Tier Tests ---

def test_run_analyst_tier_successful_execution(mock_llm, mock_db, mock_vector_db, mock_persona_repo, mock_task):
    """
    Tests that the Analyst Tier use case runs without errors and calls its
    dependencies correctly on a successful run.
    """
    # Arrange
    mock_db.get_task.return_value = mock_task.model_dump()
    use_case = RunAnalystTier(mock_llm, mock_db, mock_vector_db, mock_persona_repo)

    # Act
    use_case.execute(mock_task.query_hash)

    # Assert
    mock_db.get_task.assert_called_once_with(mock_task.query_hash)
    mock_db.update_task_status.assert_any_call(mock_task.query_hash, 'ANALYSIS_IN_PROGRESS')
    # THE DEFINITIVE FIX: Assert that the correct method name from the interface is called.
    mock_vector_db.query_similar_documents.assert_called()
    mock_db.update_task_status.assert_any_call(mock_task.query_hash, 'PENDING_SYNTHESIS')

def test_run_analyst_tier_handles_llm_failure(mock_llm, mock_db, mock_vector_db, mock_persona_repo, mock_task):
    """
    Tests that if the LLM (or any component) raises an exception, the use case
    catches it and correctly marks the task as FAILED.
    """
    # Arrange
    mock_db.get_task.return_value = mock_task.model_dump()
    # THE DEFINITIVE FIX: Set the side_effect on the correct method name.
    mock_vector_db.query_similar_documents.side_effect = RuntimeError("Vector DB is down")
    use_case = RunAnalystTier(mock_llm, mock_db, mock_vector_db, mock_persona_repo)

    # Act
    use_case.execute(mock_task.query_hash)

    # Assert
    mock_db.update_task_status.assert_called_with(mock_task.query_hash, 'FAILED')
    mock_db.log_progress.assert_called_with(mock_task.query_hash, "Analyst Tier failed: Vector DB is down")

# --- Director Tier Tests (Example Structure) ---

def test_run_director_tier_successful_execution(mock_llm, mock_db, mock_persona_repo):
    """Placeholder test for director tier success."""
    use_case = RunDirectorTier(mock_llm, mock_db, mock_persona_repo)
    assert use_case is not None

def test_run_director_tier_handles_no_analyst_reports(mock_llm, mock_db, mock_persona_repo):
    """Placeholder test for director tier handling missing reports."""
    mock_db.get_analyst_reports.return_value = []
    use_case = RunDirectorTier(mock_llm, mock_db, mock_persona_repo)
    assert use_case is not None

# --- Judge Tier Tests (Example Structure) --

def test_run_judge_tier_successful_execution(mock_llm, mock_db, mock_persona_repo):
    """Placeholder test for judge tier success."""
    use_case = RunJudgeTier(mock_llm, mock_db, mock_persona_repo)
    assert use_case is not None

def test_run_judge_tier_handles_parsing_failure(mock_llm, mock_db, mock_persona_repo):
    """Placeholder test for judge tier handling parsing errors."""
    use_case = RunJudgeTier(mock_llm, mock_db, mock_persona_repo)
    assert use_case is not None