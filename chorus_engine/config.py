# Filename: chorus_engine/config.py (Definitively Corrected Logging)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# Centralized configuration, path management, and logging setup for the application.

import sys
import json
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / 'models'
LOG_DIR = PROJECT_ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)

class JsonFormatter(logging.Formatter):
    """A custom formatter to output log records as structured JSON."""
    RESERVED_ATTRS = {
        'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
        'funcName', 'levelname', 'levelno', 'lineno', 'module', 'msecs',
        'message', 'msg', 'name', 'pathname', 'process', 'processName',
        'relativeCreated', 'stack_info', 'thread', 'threadName'
    }

    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in self.RESERVED_ATTRS and not key.startswith('_'):
                log_data[key] = value
        return json.dumps(log_data)

def setup_logging():
    """
    Configures the logging for the entire application.
    """
    # THE DEFINITIVE FIX: Use force=True to ensure that in any context
    # (main process, subprocess, test runner), the logging is reconfigured
    # exactly as specified here, tearing down any previous handlers.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout,
        force=True
    )

    sli_logger = logging.getLogger('sli')
    sli_logger.setLevel(logging.INFO)
    sli_logger.propagate = False

    # Clear existing handlers to prevent duplicate logs
    if sli_logger.hasHandlers():
        sli_logger.handlers.clear()

    sli_log_path = LOG_DIR / 'sli.log'
    file_handler = logging.FileHandler(sli_log_path)
    file_handler.setFormatter(JsonFormatter())
    sli_logger.addHandler(file_handler)

def setup_path():
    """Adds the project root to the Python path."""
    sys.path.insert(0, str(PROJECT_ROOT))

setup_path()
