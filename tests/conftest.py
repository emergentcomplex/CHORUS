# Filename: tests/conftest.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This file defines project-wide fixtures for the pytest suite.

import pytest
from dotenv import load_dotenv
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    A session-wide fixture that runs once automatically to load
    the .env file from the project root before any tests are run.
    """
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        print(f"\nWarning: .env file not found at {env_path}. Integration tests requiring API keys may fail.")
