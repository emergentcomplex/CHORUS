# Filename: tools/diagnostics/test_touch.py
# A minimal script to test the Path.touch() functionality inside the container.

import sys
from pathlib import Path
import logging

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HEALTH_FILE = Path("/tmp/test_touch.healthy")

def main():
    """
    Attempts to create a file in /tmp and reports success or failure.
    """
    logging.info(f"--- [Diagnostic] Testing Path.touch() ---")
    logging.info(f"Attempting to create liveness file at: {HEALTH_FILE}")
    try:
        HEALTH_FILE.touch()
        if HEALTH_FILE.exists():
            logging.info(f"✅ SUCCESS: Liveness file created successfully at {HEALTH_FILE}.")
            sys.exit(0)
        else:
            logging.error(f"❌ FAILURE: Path.touch() did not raise an error, but the file does not exist.")
            sys.exit(1)
    except Exception as e:
        logging.error(f"❌ FATAL: Path.touch() raised an exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
