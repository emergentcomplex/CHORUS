# Filename: scripts/explore_newsapi.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# Phase 1: NewsAPI Exploration Script
#
# Purpose:
# This script is a standalone tool for probing the NewsAPI to understand its
# endpoints, authentication, response schemas, and pagination before building
# the production harvester for Analyst Tempo.

import requests
import logging
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# --- CONFIGURATION ---
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

API_HOST = "newsapi.org"
API_KEY = os.getenv("NEWS_API_KEY")

# --- LOGGING SETUP ---
LOG_FILENAME = 'newsapi_api_log.txt'
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
    """Logs a structured 'Response Profile' of an HTTP response."""
    logging.info(f"  [ STATUS  ] {response.status_code}")
    logging.info(f"  [ SIZE    ] {len(response.content)} bytes")
    try:
        data = response.json()
        if response.status_code != 200:
            logging.warning(f"  [ ERROR-BODY ]\n{json.dumps(data, indent=2)}")
            return

        logging.info(f"  [ PROFILE-KEYS ] Top-level keys: {list(data.keys())}")
        
        results = data.get('articles', [])
        logging.info(f"  [ PROFILE-LIST ] Article Count: {len(results)}")
        logging.info(f"  [ PROFILE-TOTAL ] Total Results Available: {data.get('totalResults')}")

        if results:
            logging.info(f"  [ PROFILE-SCHEMA ] Article keys: {list(results[0].keys())}")
        else:
            logging.info("  [ PROFILE-LIST ] List was empty.")

    except json.JSONDecodeError:
        logging.error(f"  [ PARSE-ERR ] Could not parse response as JSON. Body:\n{response.text[:500]}...")

def make_request(endpoint, params=None):
    """Makes and logs a GET request to a specified endpoint."""
    url = f"https://{API_HOST}{endpoint}"
    headers = {'X-Api-Key': API_KEY}
    
    logging.info(f"--> GET Requesting URL: {url}")
    logging.info(f"    Params: {params}")
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        log_response_profile(response)
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"  [ REQUEST-ERR ] Request failed: {e}")
        return None

def probe_newsapi():
    """Executes a series of probes against the NewsAPI."""
    logging.info("\n" + "="*50 + "\nPROBE 1: Safe Query - Basic Keyword Search\n" + "="*50)
    make_request('/v2/everything', params={'q': 'DARPA', 'pageSize': 2})

    logging.info("\n" + "="*50 + "\nPROBE 2: Complex Query - Targeted Search\n" + "="*50)
    make_request('/v2/everything', params={
        'q': '"hypersonic glide vehicle"',
        'searchIn': 'title,content',
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 2
    })

    logging.info("\n" + "="*50 + "\nPROBE 3: Edge Case - Pagination Test\n" + "="*50)
    make_request('/v2/everything', params={'q': 'defense contractor', 'pageSize': 2, 'page': 2})
    
    logging.info("\n" + "="*50 + "\nPROBE 4: Edge Case - No Results\n" + "="*50)
    make_request('/v2/everything', params={'q': 'asdfqwertzxcv', 'pageSize': 2})

def main():
    """Main execution function."""
    if not API_KEY:
        logging.error("FATAL: NEWS_API_KEY not found in environment.")
        logging.error("Please ensure a .env file exists in the project root with the correct variable.")
        return

    logging.info("======== CHORUS :: NewsAPI EXPLORATION SCRIPT START ========")
    probe_newsapi()
    logging.info("\n======== CHORUS :: NewsAPI EXPLORATION SCRIPT COMPLETE ========")
    logging.info(f"See {LOG_FILENAME} for detailed results.")

if __name__ == "__main__":
    main()
