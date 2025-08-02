# Filename: tests/unit/test_use_cases.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This is the consolidated and corrected unit test file for all use cases.

import pytest
from unittest.mock import MagicMock, ANY

from chorus_engine.app.use_cases.run_analyst_tier import RunAnalystTier
from chorus_engine.app.use_cases.run_director_tier import RunDirectorTier
from chorus_engine.app.use_cases.run_judge_tier import RunJudgeTier
from chorus_engine.app.interfaces import (
    LLMInterface, DatabaseInterface, VectorDBInterface, PersonaRepositoryInterface
)
from chorus_engine.core.entities import AnalysisTask, Persona, AnalysisReport

# ==============================================================================
# Centralized Fixtures for All Use Case Tests
# ==============================================================================

@pytest.fixture
def mock_llm():
    """Provides a mocked LLM adapter that returns a string by default."""
    llm = MagicMock(spec=LLMInterface)
    llm.is_configured.return_value = True
    llm.instruct.return_value = "Default LLM response"
    return llm

@pytest.fixture
def mock_db():
    """
    Provides a mocked DatabaseInterface with autospec=True.
    This is the definitive fix for the AttributeError, as it enforces
    that all calls to the mock must match the actual interface definition.
    """
    return MagicMock(spec=DatabaseInterface, autospec=True)

@pytest.fixture
def mock_persona_repo():
    """Provides a mocked PersonaRepositoryInterface."""
    repo = MagicMock(spec=PersonaRepositoryInterface)
    repo.get_persona_by_id.return_value = Persona(id="test_id", name="Test", worldview="None", axioms=[])
    return repo

# ==============================================================================
# RunAnalystTier Unit Tests
# ==============================================================================

def test_run_analyst_tier_successful_execution(mock_llm, mock_db, mock_persona_repo):
    mock_persona_repo.get_persona_by_id.side_effect = [
        Persona(id=f"analyst_{i}", name=f"Test Analyst {i}", worldview="None", axioms=[]) for i in range(4)
    ]
    pipeline = RunAnalystTier(
        llm_adapter=mock_llm, db_adapter=mock_db,
        vector_db_adapter=MagicMock(spec=VectorDBInterface), persona_repo=mock_persona_repo
    )
    task = AnalysisTask(query_hash="test_hash_analyst", user_query={"query": "test"}, status="ANALYSIS_IN_PROGRESS")
    
    pipeline.execute(task)

    assert mock_persona_repo.get_persona_by_id.call_count == 4
    assert mock_db.save_analyst_report.call_count == 4
    mock_db.update_task_status.assert_called_once_with("test_hash_analyst", 'PENDING_SYNTHESIS')
    mock_db.update_analysis_task_failure.assert_not_called()

def test_run_analyst_tier_handles_llm_failure(mock_llm, mock_db, mock_persona_repo):
    mock_llm.instruct.side_effect = Exception("LLM is down")
    pipeline = RunAnalystTier(
        llm_adapter=mock_llm, db_adapter=mock_db,
        vector_db_adapter=MagicMock(spec=VectorDBInterface), persona_repo=mock_persona_repo
    )
    task = AnalysisTask(query_hash="analyst_fail", user_query={"query": "q"}, status="ANALYSIS_IN_PROGRESS")

    pipeline.execute(task)

    mock_db.update_analysis_task_failure.assert_called_once_with("analyst_fail", "LLM is down")
    mock_db.update_task_status.assert_not_called()

# ==============================================================================
# RunDirectorTier Unit Tests
# ==============================================================================

def test_run_director_tier_successful_execution(mock_llm, mock_db, mock_persona_repo):
    mock_db.get_analyst_reports.return_value = [{"persona_id": "a", "report_text": "b"}]
    mock_llm.instruct.return_value = "Director briefing"
    pipeline = RunDirectorTier(llm_adapter=mock_llm, db_adapter=mock_db, persona_repo=mock_persona_repo)
    task = AnalysisTask(query_hash="test_hash_director", user_query={"query": "test"}, status="SYNTHESIS_IN_PROGRESS")

    pipeline.execute(task)

    mock_db.get_analyst_reports.assert_called_once_with("test_hash_director")
    mock_db.save_director_briefing.assert_called_once_with("test_hash_director", "Director briefing")
    mock_db.update_task_status.assert_called_once_with("test_hash_director", 'PENDING_JUDGMENT')
    mock_db.update_analysis_task_failure.assert_not_called()

def test_run_director_tier_handles_no_analyst_reports(mock_llm, mock_db, mock_persona_repo):
    mock_db.get_analyst_reports.return_value = []
    pipeline = RunDirectorTier(llm_adapter=mock_llm, db_adapter=mock_db, persona_repo=mock_persona_repo)
    task = AnalysisTask(query_hash="director_fail", user_query={"query": "q"}, status="SYNTHESIS_IN_PROGRESS")

    pipeline.execute(task)

    mock_db.update_analysis_task_failure.assert_called_once_with("director_fail", "No analyst reports found to synthesize.")
    mock_db.save_director_briefing.assert_not_called()

# ==============================================================================
# RunJudgeTier Unit Tests
# ==============================================================================

def test_run_judge_tier_successful_execution(mock_llm, mock_db, mock_persona_repo):
    mock_db.get_director_briefing.return_value = {"briefing_text": "This is the briefing."}
    mock_llm.instruct.return_value = "[NARRATIVE ANALYSIS]\nN\n[ARGUMENT MAP]\nM\n[INTELLIGENCE GAPS]\nG"
    pipeline = RunJudgeTier(llm_adapter=mock_llm, db_adapter=mock_db, persona_repo=mock_persona_repo)
    task = AnalysisTask(query_hash="test_hash_judge", user_query={"query": "test"}, status="JUDGMENT_IN_PROGRESS")

    pipeline.execute(task)

    mock_db.get_director_briefing.assert_called_once_with("test_hash_judge")
    mock_db.update_analysis_task_completion.assert_called_once_with("test_hash_judge", ANY)
    mock_db.update_analysis_task_failure.assert_not_called()

def test_run_judge_tier_handles_parsing_failure(mock_llm, mock_db, mock_persona_repo):
    mock_db.get_director_briefing.return_value = {"briefing_text": "This is the briefing."}
    mock_llm.instruct.return_value = "MALFORMED LLM OUTPUT"
    pipeline = RunJudgeTier(llm_adapter=mock_llm, db_adapter=mock_db, persona_repo=mock_persona_repo)
    task = AnalysisTask(query_hash="test_hash_judge_fail", user_query={"query": "test"}, status="JUDGMENT_IN_PROGRESS")

    pipeline.execute(task)

    mock_db.update_analysis_task_completion.assert_not_called()
    mock_db.update_analysis_task_failure.assert_called_once()
    failure_call_args = mock_db.update_analysis_task_failure.call_args[0]
    assert failure_call_args[0] == "test_hash_judge_fail"
    assert "Failed to parse the AI's final report text" in failure_call_args[1]
