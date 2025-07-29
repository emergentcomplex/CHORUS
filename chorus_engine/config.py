# Filename: chorus_engine/config.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# Centralized configuration and path management for the application.

import sys
from pathlib import Path

# The absolute path to the project's root directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# The path to the directory where embedding models are stored.
MODEL_DIR = PROJECT_ROOT / 'models'

def setup_path():
    """
    Adds the project root to the Python path to ensure modules are importable.
    This is the definitive solution to ModuleNotFoundError issues.
    """
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure the path is set up when this module is imported.
setup_path()
