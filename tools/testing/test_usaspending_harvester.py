# Filename: scripts/test_usaspending_harvester.py (v2.2)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# v2.2: Definitive test suite for the multi-query harvester. It now
#       correctly validates all core use cases and edge cases.

import logging
import os
from usaspending_harvester import USASpendingHarvester, USASpendingAwardResult

# --- CONFIGURATION ---
LOG_FILENAME = 'usaspending_harvester_test.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
    handlers=[logging.FileHandler(LOG_FILENAME), logging.StreamHandler()]
)

def run_test(test_name, func):
    """Helper function to run a test function and report its boolean result."""
    print(f"[*] Running Test: {test_name}...")
    try:
        result, msg = func()
        if result:
            logging.info(f"{test_name}: ✅ PASSED - {msg}")
            print(f"    -> ✅ PASSED: {msg}")
            return True
        else:
            logging.error(f"{test_name}: ❌ FAILED - {msg}")
            print(f"    -> ❌ FAILED: {msg}")
            return False
    except Exception as e:
        logging.critical(f"{test_name}: 💥 CRASHED with exception: {e}", exc_info=True)
        print(f"    -> 💥 CRASHED: {e}")
        return False

# --- TEST CASES ---

def test_initialization():
    """Tests if the harvester class can be instantiated."""
    try:
        USASpendingHarvester()
        return True, "Harvester instantiated successfully."
    except Exception as e:
        return False, f"Instantiation failed: {e}"

def test_successful_contract_search():
    """Tests a known-good search for contracts returns valid, non-empty results."""
    harvester = USASpendingHarvester()
    results = list(harvester.search_awards(keyword="hypersonic", award_types=["contracts"]))
    if not results: return False, "Search returned no results for a known-good keyword."
    if not isinstance(results[0], USASpendingAwardResult): return False, "Result is not a valid Pydantic model."
    return True, f"Found {len(results)} contract results."

def test_successful_multi_group_search():
    """Tests that the harvester can search across multiple valid groups."""
    harvester = USASpendingHarvester()
    # Search for both contracts and grants
    results = list(harvester.search_awards(keyword="research", award_types=["contracts", "grants"]))
    if not results: return False, "Multi-group search returned no results."
    return True, f"Found {len(results)} results across contracts and grants."

def test_no_results_keyword():
    """Tests that a nonsensical keyword returns an empty list across all groups."""
    harvester = USASpendingHarvester()
    results = list(harvester.search_awards(keyword="asdfqwertzxcv"))
    return isinstance(results, list) and len(results) == 0, "Correctly returned an empty list."

def test_handles_invalid_group():
    """Tests that the harvester skips an invalid award group name gracefully."""
    harvester = USASpendingHarvester()
    # This should not crash, it should just run the valid 'contracts' search
    results = list(harvester.search_awards(keyword="hypersonic", award_types=["contracts", "invalid_group"]))
    return len(results) > 0, "Correctly skipped the invalid group and returned results for the valid one."

def main():
    print("\n" + "="*80)
    print("=      CHORUS - USAspending.gov Harvester Module Test Suite (v2.2)      =")
    print("="*80)
    
    if os.path.exists(LOG_FILENAME): os.remove(LOG_FILENAME)

    test_suite = {
        "Harvester Initialization": test_initialization,
        "Successful Single-Group Search (Contracts)": test_successful_contract_search,
        "Successful Multi-Group Search (Contracts & Grants)": test_successful_multi_group_search,
        "Handles No-Results Keyword Gracefully": test_no_results_keyword,
        "Handles Invalid Award Group Gracefully": test_handles_invalid_group,
    }
    
    results = {name: run_test(name, func) for name, func in test_suite.items()}
    tests_passed = sum(1 for result in results.values() if result)
    total_tests = len(test_suite)

    print("\n" + "="*80)
    print("=                        TEST SUITE COMPLETE                       =")
    print("="*80)
    
    print(f"\nSUMMARY: {tests_passed} out of {total_tests} tests passed.")
    
    if tests_passed == total_tests:
        print("\n✅ All tests passed. The harvester module is now definitive and ready for integration.")
    else:
        print("\n❌ One or more tests failed. Review the logs before proceeding to Phase 3.")
        print(f"   Detailed logs are available in: {LOG_FILENAME}")
    
    print("="*80)

if __name__ == "__main__":
    main()  