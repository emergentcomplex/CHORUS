# Filename: tools/testing/stress_test_usaspending.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# A diagnostic tool to empirically discover the stable parallel request limit
# for the USAspending.gov API. The result of this test should be used to
# configure the SENTINEL_WORKERS environment variable.

import requests
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# --- CONFIGURATION ---
API_ENDPOINT = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
TEST_KEYWORD = "logistics" # A common keyword guaranteed to have many pages
HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'CHORUS-Stress-Test-Client'
}

# Define the scenarios to test, from conservative to extreme.
# Each scenario is (number_of_parallel_workers, requests_per_worker)
TEST_SCENARIOS = [
    (1, 20, "Baseline (1 Worker)"),
    (2, 20, "Conservative (2 Workers)"),
    (4, 20, "Moderate (4 Workers)"),
    (8, 20, "Aggressive (8 Workers)"),
    (16, 20, "Extreme (16 Workers)"),
]

# --- Worker Function ---
def run_worker(session, worker_id, num_requests):
    """The function executed by each thread. It simulates one harvester worker."""
    success_count = 0
    failure_count = 0
    for i in range(num_requests):
        try:
            # Each request needs a slightly different payload to avoid caching
            payload = {
                "filters": {
                    "keywords": [TEST_KEYWORD],
                    "award_type_codes": ["A", "B", "C", "D"]
                },
                "fields": ["Award ID"],
                "page": i + 1, # Each request fetches a different page
                "limit": 1
            }
            response = session.post(API_ENDPOINT, headers=HEADERS, json=payload, timeout=45)
            if response.status_code == 200:
                success_count += 1
            else:
                failure_count += 1
        except requests.exceptions.RequestException:
            failure_count += 1
        # A small, realistic delay within a worker's own logic
        time.sleep(0.1)
    return success_count, failure_count

# --- Main Orchestrator ---
def main():
    """Main execution function for the stress test."""
    print("="*80)
    print("=      CHORUS - USAspending.gov Parallel Stress Test      =")
    print("=  This will determine the safe concurrency limit for the Sentinel.  =")
    print("="*80)

    results = {}
    with requests.Session() as session:
        for workers, reqs_per_worker, name in TEST_SCENARIOS:
            print(f"\n--- Testing Scenario: '{name}' ({workers} parallel workers) ---")
            
            total_requests = workers * reqs_per_worker
            total_success = 0
            total_failure = 0

            with ThreadPoolExecutor(max_workers=workers) as executor:
                # Create a future for each worker
                futures = [executor.submit(run_worker, session, i, reqs_per_worker) for i in range(workers)]
                
                # Use tqdm to show progress as workers complete
                with tqdm(total=total_requests, desc="  -> Progress") as pbar:
                    for future in as_completed(futures):
                        success, failure = future.result()
                        total_success += success
                        total_failure += failure
                        pbar.update(success + failure)

            success_rate = (total_success / total_requests) * 100 if total_requests > 0 else 0
            results[workers] = success_rate
            
            print(f"  -> Scenario Complete. Success Rate: {total_success}/{total_requests} ({success_rate:.1f}%)")

            if success_rate < 95.0:
                print("  -> Stability compromised. Halting further tests.")
                break

    print("\n\n" + "="*80)
    print("=                        STRESS TEST COMPLETE                        =")
    print("="*80)
    
    print("\n--- FINAL RESULTS ---")
    for workers, rate in results.items():
        print(f"  - {workers} Parallel Workers:\tSuccess Rate: {rate:.1f}%")

    # Automated Analysis and Recommendation
    safe_worker_limit = 0
    for workers, rate in results.items():
        if rate >= 95.0:
            safe_worker_limit = workers
        else:
            break

    print("\n--- DEFINITIVE RECOMMENDATION ---")
    if safe_worker_limit > 0:
        print(f"The API is stable with up to {safe_worker_limit} parallel workers.")
        print(f"✅ To ensure stability, the 'SENTINEL_WORKERS' environment variable should be set to {safe_worker_limit}.")
    else:
        print("❌ CRITICAL FAILURE: Even a single worker failed the baseline test.")
        print("   This indicates a potential IP block or that the API is currently unstable.")
    print("="*80)

if __name__ == "__main__":
    main()
