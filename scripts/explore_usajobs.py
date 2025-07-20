# Filename: explore_usajobs_v5.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# Phase 1: USAJOBS API Exploration Script (V5 - "Response Profile" Logging)
#
# Purpose:
# This script provides a balanced "Goldilocks" logging level. It captures all
# essential structural and diagnostic information without creating an overly
# verbose log file. It logs concise "Response Profiles" for successes and full
# details for failures. This version also includes the resilient pagination logic.
#
# It will:
# 1. Load credentials securely from a ../.env file.
# 2. Probe all relevant endpoints.
# 3. Log a structured "Response Profile" for each successful request.
# 4. Log full error details for any failed request.
# 5. Handle pagination gracefully, whether a continuationToken is present or not.

import requests
import logging
import time
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# --- CONFIGURATION ---
try:
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except Exception as e:
    logging.error(f"Could not load .env file: {e}")

API_HOST = "data.usajobs.gov"
USER_AGENT_EMAIL = os.getenv("USAJOBS_EMAIL")
AUTH_KEY = os.getenv("USAJOBS_API_KEY")

# --- HEADERS ---
AUTH_HEADERS = {
    'Host': API_HOST,
    'User-Agent': USER_AGENT_EMAIL,
    'Authorization-Key': AUTH_KEY
}
PUBLIC_HEADERS = {
    'Host': API_HOST,
    'User-Agent': USER_AGENT_EMAIL,
}

# --- LOGGING SETUP ---
LOG_FILENAME = 'usajobs_api_log_v5.txt'
if os.path.exists(LOG_FILENAME):
    os.remove(LOG_FILENAME)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler()
    ]
)

def log_response_profile(response):
    """
    Logs a structured "Response Profile": a concise summary for successes,
    and a full error message for failures.
    """
    logging.info(f"  [ STATUS  ] {response.status_code}")
    logging.info(f"  [ SIZE    ] {len(response.content)} bytes")

    if response.status_code != 200:
        try:
            error_json = response.json()
            logging.warning(f"  [ ERROR-BODY ]\n{json.dumps(error_json, indent=2)}")
        except json.JSONDecodeError:
            logging.warning(f"  [ ERROR-BODY ] {response.text}")
        return

    try:
        data = response.json()
        logging.info(f"  [ PROFILE-KEYS ] Top-level keys: {list(data.keys())}")

        items = []
        if 'SearchResult' in data and 'SearchResultItems' in data['SearchResult']:
            items = data['SearchResult']['SearchResultItems']
            total_count = data['SearchResult'].get('SearchResultCountAll', 'N/A')
            logging.info(f"  [ PROFILE-LIST ] Type: SearchResultItems, Count: {len(items)}, Total Matches: {total_count}")
        elif 'CodeList' in data and data['CodeList']:
            items = data['CodeList'][0].get('ValidValue', [])
            logging.info(f"  [ PROFILE-LIST ] Type: CodeList, Count: {len(items)}")
        elif 'data' in data:
            items = data.get('data', [])
            logging.info(f"  [ PROFILE-LIST ] Type: HistoricJoa, Count: {len(items)}")

        if items:
            # Log the schema of the first item in the list
            logging.info(f"  [ PROFILE-SCHEMA ] Item keys: {list(items[0].keys())}")
        else:
            logging.info("  [ PROFILE-LIST ] List was empty.")

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logging.error(f"  [ PARSE-ERR ] Could not generate response profile: {e}")


def make_request(endpoint, headers, params=None):
    """Makes and logs a request to a specified endpoint."""
    url = f"https://{API_HOST}{endpoint}"
    logging.info(f"--> Requesting URL: {url} with params: {params}")
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        log_response_profile(response)
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"  [ REQUEST-ERR ] Request failed: {e}")
        return None

def probe_codelists():
    """Fetches a sample of codelists."""
    logging.info("\n" + "="*50)
    logging.info("PHASE 1.1: PROBING CODELIST ENDPOINTS")
    logging.info("="*50)
    codelist_endpoints = [
        '/api/codelist/agencysubelements', '/api/codelist/occupationalseries',
        '/api/codelist/securityclearances', '/api/codelist/hiringpaths'
    ]
    for endpoint in codelist_endpoints:
        make_request(endpoint, headers=PUBLIC_HEADERS)
        time.sleep(1)

def probe_search_endpoint():
    """Probes the /api/Search endpoint with safe and unsafe queries."""
    logging.info("\n" + "="*50)
    logging.info("PHASE 1.2: PROBING /api/Search ENDPOINT")
    logging.info("="*50)

    logging.info("\n--- Testing Safe Query ---")
    make_request('/api/Search', AUTH_HEADERS, params={'Keyword': 'physicist', 'ResultsPerPage': 2})

    logging.info("\n--- Testing Unsafe/Edge-Case Queries ---")
    logging.info("Testing invalid parameter value (JobCategoryCode=99999)...")
    make_request('/api/Search', AUTH_HEADERS, params={'JobCategoryCode': '99999'})

    logging.info("Testing pagination limits (ResultsPerPage=501, >500 max)...")
    make_request('/api/Search', AUTH_HEADERS, params={'Keyword': 'engineer', 'ResultsPerPage': 501})

def probe_historic_endpoints():
    """Probes the historical data endpoints with resilient pagination."""
    logging.info("\n" + "="*50)
    logging.info("PHASE 1.3: PROBING HISTORICAL ENDPOINTS")
    logging.info("="*50)

    logging.info("\n--- Testing /api/HistoricJoa Pagination ---")
    historic_params = {
        'StartPositionOpenDate': '2024-03-01',
        'EndPositionOpenDate': '2024-03-01',
        'HiringDepartmentCodes': 'DD'
    }
    initial_response = make_request('/api/historicjoa', PUBLIC_HEADERS, params=historic_params)

    continuation_token = None
    if initial_response and initial_response.status_code == 200:
        data = initial_response.json()
        # Safely get the continuationToken. .get() returns None if a key is not found.
        paging_data = data.get('paging', {})
        metadata = paging_data.get('metadata', {})
        continuation_token = metadata.get('continuationToken')

        if continuation_token:
            logging.info(f"  [ PAGINATION ] Found continuationToken for next step.")
        else:
            logging.info("  [ PAGINATION ] No continuationToken found. This is expected if all results fit on one page.")

    if continuation_token:
        logging.info("\n--- Making second request with continuationToken... ---")
        historic_params['continuationtoken'] = continuation_token
        make_request('/api/historicjoa', PUBLIC_HEADERS, params=historic_params)

def main():
    """Main execution function."""
    if not USER_AGENT_EMAIL or not AUTH_KEY:
        logging.error("FATAL: USAJOBS_EMAIL and/or USAJOBS_API_KEY not found in environment.")
        logging.error("Please ensure a .env file exists in the parent directory with the correct variables.")
        return

    logging.info("======== CHORUS :: USAJOBS API EXPLORATION SCRIPT (V5) START ========")
    
    probe_codelists()
    probe_search_endpoint()
    probe_historic_endpoints()

    logging.info("\n======== CHORUS :: USAJOBS API EXPLORATION SCRIPT (V5) COMPLETE ========")
    logging.info(f"See {LOG_FILENAME} for detailed results.")

if __name__ == "__main__":
    main()