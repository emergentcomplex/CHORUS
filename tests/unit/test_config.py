# Filename: tests/unit/test_config.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# Unit tests for the configuration and logging setup.

import json
import logging

from chorus_engine.config import JsonFormatter

def test_json_formatter_serializes_standard_fields():
    """
    Tests that the JsonFormatter correctly serializes the basic
    attributes of a LogRecord.
    """
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name='test_logger',
        level=logging.INFO,
        pathname='/path/to/test.py',
        lineno=10,
        msg='This is a test message',
        args=(),
        exc_info=None
    )

    json_string = formatter.format(record)
    data = json.loads(json_string)

    assert data['name'] == 'test_logger'
    assert data['level'] == 'INFO'
    assert data['message'] == 'This is a test message'
    assert 'timestamp' in data

def test_json_formatter_includes_extra_data():
    """
    Tests that the JsonFormatter correctly includes 'extra' data
    passed to the logger, which is critical for our SLI metrics.
    """
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name='sli_logger',
        level=logging.INFO,
        pathname='/path/to/pipeline.py',
        lineno=50,
        msg='pipeline_success_rate',
        args=(),
        exc_info=None
    )
    # Add extra data, simulating an SLI log call
    record.pipeline_name = 'J-ANLZ'
    record.success = True
    record.latency_seconds = 123.45

    json_string = formatter.format(record)
    data = json.loads(json_string)

    assert data['message'] == 'pipeline_success_rate'
    assert data['pipeline_name'] == 'J-ANLZ'
    assert data['success'] is True
    assert data['latency_seconds'] == 123.45
