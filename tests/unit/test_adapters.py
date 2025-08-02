# Filename: tests/unit/test_adapters.py (Definitively Corrected)
import pytest
from unittest.mock import MagicMock, patch
import os

from chorus_engine.adapters.llm.gemini_adapter import GeminiAdapter
from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter
from chorus_engine.adapters.persistence.redis_adapter import RedisAdapter
from chorus_engine.core.entities import AnalysisReport

# ==============================================================================
# GeminiAdapter Unit Tests
# ==============================================================================

@pytest.fixture
def mock_gemini_dependencies(mocker):
    """A single fixture to mock all external dependencies for the GeminiAdapter."""
    mocker.patch('google.generativeai.configure')
    mocker.patch('google.generativeai.client.get_default_generative_client', return_value=True)
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value.text = "Test response"
    mocker.patch('google.generativeai.GenerativeModel', return_value=mock_model_instance)

def test_gemini_adapter_initialization_success(mock_gemini_dependencies, mocker):
    """Tests successful initialization when an API key is present."""
    # THE DEFINITIVE FIX: Use a dictionary for side_effect to avoid recursion.
    mock_values = {
        "GOOGLE_API_KEY": "fake_api_key",
        "LLM_MAX_RETRIES": "5",
        "LLM_BASE_BACKOFF": "2.0"
    }
    mocker.patch('os.getenv', lambda key, default=None: mock_values.get(key, default))
    adapter = GeminiAdapter()
    assert adapter is not None
    assert adapter.is_configured() is True

def test_gemini_adapter_initialization_no_key_is_not_fatal(mock_gemini_dependencies, mocker, caplog):
    """Tests that the adapter can be initialized without an API key and logs a warning."""
    mock_values = {
        "LLM_MAX_RETRIES": "5",
        "LLM_BASE_BACKOFF": "2.0"
    }
    mocker.patch('os.getenv', lambda key, default=None: mock_values.get(key, default))
    adapter = GeminiAdapter()
    assert adapter is not None
    assert adapter.is_configured() is False
    assert "GOOGLE_API_KEY not found" in caplog.text

def test_gemini_adapter_instruct_success(mock_gemini_dependencies):
    """Tests a successful call to the instruct method."""
    adapter = GeminiAdapter()
    adapter._is_configured = True # Ensure configured state for this test
    response = adapter.instruct("Test prompt", "gemini-1.5-pro")
    assert response == "Test response"

def test_gemini_adapter_instruct_fails_gracefully_if_no_key(mock_gemini_dependencies):
    """Tests that instruct() returns None if the adapter was initialized without a key."""
    adapter = GeminiAdapter()
    adapter._is_configured = False # Ensure unconfigured state for this test
    response = adapter.instruct("Test prompt", "gemini-1.5-pro")
    assert response is None

# ==============================================================================
# PostgresAdapter Unit Tests
# ==============================================================================

@pytest.fixture
def mocked_postgres_adapter(mocker):
    mocker.patch('chorus_engine.adapters.persistence.postgres_adapter.PostgresAdapter._get_pool', return_value=MagicMock())
    adapter = PostgresAdapter()
    adapter._pool = MagicMock()
    mocker.patch.object(PostgresAdapter, '_get_embedding_model', return_value=MagicMock())
    return adapter

# ==============================================================================
# RedisAdapter Unit Tests
# ==============================================================================

@pytest.fixture
def mocked_redis_adapter(mocker):
    mock_redis_client = mocker.patch('chorus_engine.adapters.persistence.redis_adapter.redis.Redis').return_value
    adapter = RedisAdapter()
    return adapter, mock_redis_client

def test_redis_adapter_get_all_tasks_sorted(mocked_redis_adapter):
    adapter, mock_redis_client = mocked_redis_adapter
    mock_redis_client.keys.return_value = ['task:hash2', 'task:hash1']
    mock_redis_client.pipeline.return_value.execute.return_value = [
        {'query_hash': 'hash2', 'created_at': '2025-01-01T10:00:00'},
        {'query_hash': 'hash1', 'created_at': '2025-01-01T12:00:00'}
    ]
    sorted_tasks = adapter.get_all_tasks_sorted_by_time()
    assert len(sorted_tasks) == 2
    assert sorted_tasks[0]['query_hash'] == 'hash1'

def test_redis_adapter_get_task_by_hash(mocked_redis_adapter):
    adapter, mock_redis_client = mocked_redis_adapter
    mock_redis_client.hgetall.return_value = {'query_hash': 'some_hash'}
    result = adapter.get_task_by_hash('some_hash')
    mock_redis_client.hgetall.assert_called_once_with('task:some_hash')
    assert result['query_hash'] == 'some_hash'

def test_redis_adapter_handles_redis_error(mocked_redis_adapter, caplog):
    adapter, mock_redis_client = mocked_redis_adapter
    mock_redis_client.keys.side_effect = Exception("Redis is down")
    result_list = adapter.get_all_tasks_sorted_by_time()
    assert result_list == []
    assert "Error retrieving tasks from Redis" in caplog.text
