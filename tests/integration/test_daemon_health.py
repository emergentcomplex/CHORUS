# Filename: tests/integration/test_daemon_health.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This integration test performs a "smoke test" on all standalone daemons
# to ensure they can initialize and start without immediately crashing.

import pytest
import subprocess
import sys
import os

pytestmark = pytest.mark.integration

# List of all standalone, long-running daemon entry points.
# We get the absolute path to the python executable to ensure we run it
# from the container's virtual environment.
PYTHON_EXEC = sys.executable
DAEMON_SCRIPTS = [
    [PYTHON_EXEC, "-m", "chorus_engine.infrastructure.daemons.launcher"],
    [PYTHON_EXEC, "-m", "chorus_engine.infrastructure.daemons.sentinel"],
    [PYTHON_EXEC, "-m", "chorus_engine.infrastructure.daemons.synthesis_daemon"],
]

@pytest.mark.parametrize("daemon_command", DAEMON_SCRIPTS)
def test_daemon_starts_without_crashing(daemon_command):
    """
    Starts a daemon as a subprocess, lets it run for a few seconds,
    and asserts that it does not exit with an error.
    """
    script_name = daemon_command[-1]
    print(f"\n--- Smoke Test: Starting {script_name} ---")

    # We pass the environment variables from the test runner to the subprocess,
    # which is crucial for database connections, etc.
    process = subprocess.Popen(
        daemon_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ
    )

    # Let the daemon run for a short period to see if it crashes on startup.
    try:
        stdout, stderr = process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        # This is the SUCCESS case. The daemon is still running.
        print(f"[+] SUCCESS: {script_name} did not crash after 10 seconds.")
        process.terminate()
        return

    # If we get here, the process terminated before the timeout.
    # We must check if it exited with an error.
    if process.returncode != 0 and process.returncode != -15: # -15 is SIGTERM, which is ok
        pytest.fail(
            f"Daemon {script_name} crashed on startup with exit code {process.returncode}.\n"
            f"--- STDERR ---\n{stderr}\n"
            f"--- STDOUT ---\n{stdout}"
        )
    
    print(f"[+] SUCCESS: {script_name} exited cleanly.")