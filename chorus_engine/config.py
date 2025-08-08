# Filename: chorus_engine/config.py
import sys
import json
import logging
import os
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
    Log level is controlled by the LOG_LEVEL environment variable.
    """
    log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout,
        force=True
    )
    logging.info(f"Root logger configured with level: {log_level_name}")

    sli_logger = logging.getLogger('sli')
    sli_logger.setLevel(logging.INFO)
    sli_logger.propagate = False

    if sli_logger.hasHandlers():
        sli_logger.handlers.clear()

    # THE DEFINITIVE FIX: Make file logging resilient to permission errors.
    try:
        sli_log_path = LOG_DIR / 'sli.log'
        file_handler = logging.FileHandler(sli_log_path)
        file_handler.setFormatter(JsonFormatter())
        sli_logger.addHandler(file_handler)
    except PermissionError:
        logging.warning(
            "Could not open sli.log due to a permission error. "
            "SLI metrics will not be written to a file. "
            "This is common if the ./logs directory on the host is owned by root."
        )

    if log_level > logging.DEBUG:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("kafka").setLevel(logging.WARNING)

def setup_path():
    """Adds the project root to the Python path."""
    sys.path.insert(0, str(PROJECT_ROOT))

setup_path()