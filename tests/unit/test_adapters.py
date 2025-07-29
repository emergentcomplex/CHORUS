# Filename: tests/unit/test_adapters.py (Definitive & Isolated)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# Unit tests for the Adapters layer. These tests use mocks to isolate the
# adapters from external services (LLMs, databases), verifying only the
# internal logic of the adapter classes themselves.

import pytest
from unittest.mock import MagicMock, patch


from chorus_engine.adapters.llm.gemini_adapter import GeminiAdapter
from chorus_engine.adapters.persistence.mariadb_adapter import MariaDBAdapter
from chorus_engine.core.entities import AnalysisReport

# ==============================================================================
# GeminiAdapter Unit Tests
# ==============================================================================

@pytest.fixture
def mock_gemini_env(mocker):
    mocker.patch('os.getenv', return_value="fake_api_key")

@pytest.fixture
def gemini_adapter(mock_gemini_env, mocker):
    """Provides a fully initialized GeminiAdapter with a mocked client."""
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "Test response"
    mock_client_instance = MagicMock()
    mock_client_instance.models.get.return_value = mock_model
    mocker.patch('google.genai.Client', return_value=mock_client_instance)
    return GeminiAdapter()

def test_gemini_adapter_initialization_success(gemini_adapter):
    assert gemini_adapter.client is not None

def test_gemini_adapter_initialization_failure(mocker):
    mocker.patch('os.getenv', return_value=None)
    with pytest.raises(ValueError, match="GOOGLE_API_KEY not found"):
        GeminiAdapter()

def test_gemini_adapter_instruct_success(gemini_adapter):
    response = gemini_adapter.instruct("Test prompt", "gemini-1.5-pro")
    assert response == "Test response"
    gemini_adapter.client.models.get.assert_called_with("models/gemini-1.5-pro")

# ==============================================================================
# MariaDBAdapter Unit Tests
# ==============================================================================

@pytest.fixture
def mocked_mariadb_adapter(mocker):
    """
    DEFINITIVE FIX: This fixture provides a fully mocked MariaDBAdapter instance,
    ensuring true isolation for each test function that uses it.
    """
    # 1. Reset the class-level attributes before each test to prevent state leakage
    MariaDBAdapter._pool = None
    MariaDBAdapter._embedding_model = None

    # 2. Mock all external dependencies
    mocker.patch('os.getenv', side_effect=lambda key, default=None: {
        "DB_USER": "test_user", "DB_PASSWORD": "test_password",
        "DB_HOST": "localhost", "DB_PORT": "3306", "DB_NAME": "test_db"
    }.get(key, default))
    
    mocker.patch('chorus_engine.adapters.persistence.mariadb_adapter.Path.exists', return_value=True)
    mocker.patch('chorus_engine.adapters.persistence.mariadb_adapter.SentenceTransformer')

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    
    mock_pool_instance = MagicMock()
    mock_pool_instance.get_connection.return_value = mock_connection
    mocker.patch('mariadb.ConnectionPool', return_value=mock_pool_instance)

    # 3. Yield the adapter and the mock cursor for assertions
    adapter = MariaDBAdapter()
    yield adapter, mock_cursor

def test_mariadb_adapter_initialization(mocked_mariadb_adapter):
    """Tests that the adapter initializes its pool and model correctly."""
    adapter, _ = mocked_mariadb_adapter
    assert adapter._pool is not None
    assert adapter._embedding_model is not None

def test_mariadb_adapter_update_completion(mocked_mariadb_adapter):
    """Tests the logic for updating a task to COMPLETED."""
    adapter, mock_cursor = mocked_mariadb_adapter
    
    report = AnalysisReport(
        narrative_analysis="narrative",
        argument_map="map",
        intelligence_gaps="gaps",
        raw_text="raw"
    )
    adapter.update_analysis_task_completion("some_hash", report)

    # Assert that the mock cursor (from the yielded fixture) was used
    assert mock_cursor.execute.call_count == 2
    
    # Verify the SQL calls
    update_task_call = mock_cursor.execute.call_args_list[0]
    assert "UPDATE task_queue" in update_task_call.args[0]
    assert update_task_call.args[1] == ("some_hash",)

    update_state_call = mock_cursor.execute.call_args_list[1]
    assert "INSERT INTO query_state" in update_state_call.args[0]
    assert update_state_call.args[1][0] == "some_hash"
