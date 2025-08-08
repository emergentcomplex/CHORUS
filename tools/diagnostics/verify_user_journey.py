# Filename: tools/diagnostics/verify_user_journey.py
# A standalone script to verify the complete, end-to-end user journey.

import requests
import redis
import time
import uuid
import json
import hashlib
import os
import sys
import re

# --- CONFIGURATION ---
# THE DEFINITIVE FIX: Use the internal service name and port, not localhost.
WEB_UI_URL = "http://chorus-web:5001/"
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
MAX_WAIT_SECONDS = 20
POLL_INTERVAL_SECONDS = 2

def main():
    """Executes the end-to-end user journey verification."""
    print("🔱 Verifying End-to-End User Journey...")
    
    unique_input_str = f"user-journey-test-{uuid.uuid4().hex}"
    
    try:
        print(f"  -> Making HTTP POST to {WEB_UI_URL}...")
        # This version correctly handles the race condition by not following the redirect.
        response = requests.post(
            WEB_UI_URL,
            data={'query_text': unique_input_str, 'mode': 'deep_dive'},
            timeout=10,
            allow_redirects=False
        )
        
        if response.status_code != 302:
            print(f"❌ FAILURE: Expected a 302 redirect from web service, but got {response.status_code}.")
            sys.exit(1)
        
        location = response.headers.get('Location')
        if not location:
            print("❌ FAILURE: Web service returned a 302 redirect without a 'Location' header.")
            sys.exit(1)

        match = re.search(r'/query/([a-f0-9]{32})', location)
        if not match:
            print(f"❌ FAILURE: Could not parse query hash from redirect location: {location}")
            sys.exit(1)
            
        expected_hash = match.group(1)
        redis_key = f"task:{expected_hash}"
        print(f"  -> Web service accepted task. Got redirect for hash: {expected_hash}")

    except requests.exceptions.RequestException as e:
        print(f"❌ FAILURE: Could not connect to the web UI at {WEB_UI_URL}.")
        print(f"    Error: {e}")
        sys.exit(1)

    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        redis_client.ping()
    except redis.exceptions.ConnectionError as e:
        print(f"❌ FAILURE: Could not connect to Redis at {REDIS_HOST}:{REDIS_PORT}.")
        print(f"    Error: {e}")
        sys.exit(1)

    print(f"  -> Polling Redis for materialization (max {MAX_WAIT_SECONDS}s)...")
    start_time = time.time()
    while time.time() - start_time < MAX_WAIT_SECONDS:
        if redis_client.exists(redis_key):
            print("\n✅ SUCCESS: The complete user journey is verified.")
            print("    (Web Service -> PostgreSQL -> CDC -> Redis)")
            redis_client.delete(redis_key)
            sys.exit(0)
        time.sleep(POLL_INTERVAL_SECONDS)

    print(f"\n❌ FAILURE: Task {expected_hash} did not materialize in Redis within {MAX_WAIT_SECONDS} seconds.")
    sys.exit(1)

if __name__ == "__main__":
    main()