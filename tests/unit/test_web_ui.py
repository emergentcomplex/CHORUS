# Filename: tests/unit/test_web_ui.py
#
# Unit tests for the Web UI (Flask application).

import pytest
import json
from unittest.mock import patch, MagicMock

from chorus_engine.infrastructure.web.web_ui import app

@pytest.fixture
def client():
    """A pytest fixture to provide a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

@patch('chorus_engine.infrastructure.web.web_ui.redis_adapter.get_all_tasks_sorted_by_time', return_value=[])
def test_dashboard_get_request(mock_redis_tasks, client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Queue New Analysis" in response.data

@patch('chorus_engine.infrastructure.web.web_ui.queue_new_query')
def test_dashboard_post_queues_task(mock_queue_new_query, client):
    mock_queue_new_query.return_value = "a_new_query_hash"
    response = client.post('/', data={'query_text': 'test query', 'mode': 'flash'})
    mock_queue_new_query.assert_called_once_with('test query', mode='flash')
    assert response.status_code == 302
    assert response.location == '/query/a_new_query_hash'

@patch('chorus_engine.adapters.persistence.redis_adapter.RedisAdapter.get_task_by_hash')
def test_query_details_page(mock_get_task, client):
    mock_get_task.return_value = {'query_hash': 'a_known_hash', 'status': 'COMPLETED'}
    response = client.get('/query/a_known_hash')
    assert response.status_code == 200
    assert b"Session ID: a_known_hash" in response.data

@patch('chorus_engine.adapters.persistence.redis_adapter.RedisAdapter.get_task_by_hash')
def test_query_details_not_found(mock_get_task, client):
    mock_get_task.return_value = None
    response = client.get('/query/an_unknown_hash')
    assert response.status_code == 404

@patch('chorus_engine.adapters.persistence.redis_adapter.RedisAdapter.get_all_tasks_sorted_by_time')
def test_htmx_update_dashboard(mock_get_all_tasks, client):
    mock_get_all_tasks.return_value = [
        {'query_hash': 'hash1', 'user_query': '{"query": "Test Query 1"}', 'status': 'COMPLETED', 'created_at': '2025-08-01T12:00:00', 'worker_id': 'worker-a'}
    ]
    response = client.get('/update_dashboard')
    assert response.status_code == 200
    assert b"Test Query 1" in response.data

@patch('chorus_engine.infrastructure.web.web_ui.db_adapter')
@patch('chorus_engine.infrastructure.web.web_ui.get_report_raw_text')
def test_htmx_update_report(mock_get_report, mock_db_adapter, client):
    mock_db_adapter.get_analyst_reports.return_value = [
        {'persona_id': 'analyst_hawk', 'report_text': 'Hawk Report'}
    ]
    mock_db_adapter.get_director_briefing.return_value = {'briefing_text': 'Director Briefing'}
    # THE DEFINITIVE FIX: Provide a mock that satisfies all regexes in the controller.
    mock_get_report.return_value = """
    [NARRATIVE ANALYSIS]
    Test narrative.
    [ARGUMENT MAP]
    - Point 1
    [INTELLIGENCE GAPS]
    1. Gap 1
    """
    
    response = client.get('/update_report/some_hash')
    
    assert response.status_code == 200
    assert b"Hawk Report" in response.data
    assert b"Director Briefing" in response.data
    assert b"Test narrative." in response.data