# Filename: scripts/test_arxiv_harvester.py (v2.0)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# v2.0: An exhaustive test suite that validates the advanced query
#       capabilities and resilience of the upgraded ArxivHarvester.

import logging
import os
from arxiv_harvester import ArxivHarvester, ArxivArticle

# --- CONFIGURATION (Unchanged) ---
LOG_FILENAME = 'arxiv_harvester_test.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s', handlers=[logging.FileHandler(LOG_FILENAME), logging.StreamHandler()])

def run_test(test_name, func):
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

# --- TEST CASES (Now Exhaustive) ---

def test_initialization():
    try:
        ArxivHarvester()
        return True, "Harvester instantiated successfully."
    except Exception as e:
        return False, f"Instantiation failed: {e}"

def test_basic_search():
    harvester = ArxivHarvester()
    results = list(harvester.search_articles(search_query='ti:"machine learning"'))
    if not results: return False, "Search returned no results for a known-good keyword."
    return True, f"Found {len(results)} results."

def test_complex_boolean_search():
    """Tests a query with multiple fields and boolean operators."""
    harvester = ArxivHarvester()
    # Search for papers by a specific author (Karpathy) in a specific category (cs.CV)
    # that do NOT have "transformer" in the title.
    query = 'au:Karpathy AND cat:cs.CV ANDNOT ti:transformer'
    results = list(harvester.search_articles(search_query=query))
    if not results: return False, "Complex boolean search returned no results."
    return True, f"Found {len(results)} results for complex query."

def test_malformed_query():
    """Tests that a syntactically incorrect query is handled gracefully."""
    harvester = ArxivHarvester()
    # An incorrect field prefix 'auth:' instead of 'au:'
    query = 'auth:"Yann LeCun"'
    results = list(harvester.search_articles(search_query=query))
    # The correct behavior is to return an empty list, not crash.
    return isinstance(results, list) and len(results) == 0, "Correctly handled a malformed query and returned an empty list."

def test_pagination():
    harvester = ArxivHarvester()
    limit = 105
    results = list(harvester.search_articles(search_query='cat:cs.AI', max_results=limit))
    return len(results) == limit, f"Correctly fetched exactly {len(results)} results."

def main():
    print("\n" + "="*80)
    print("=      CHORUS - arXiv Harvester Module Test Suite (v2.0 - Exhaustive)      =")
    print("="*80)
    
    if os.path.exists(LOG_FILENAME): os.remove(LOG_FILENAME)

    test_suite = {
        "Harvester Initialization": test_initialization,
        "Basic Keyword Search": test_basic_search,
        "Advanced Boolean Search": test_complex_boolean_search,
        "Handles Malformed Query Gracefully": test_malformed_query,
        "Handles Pagination Correctly": test_pagination,
    }
    
    results = {name: run_test(name, func) for name, func in test_suite.items()}
    tests_passed = sum(1 for result in results.values() if result)
    total_tests = len(test_suite)

    print("\n" + "="*80)
    print("=                        TEST SUITE COMPLETE                       =")
    print("="*80)
    
    print(f"\nSUMMARY: {tests_passed} out of {total_tests} tests passed.")
    
    if tests_passed == total_tests:
        print("\n✅ All tests passed. The arXiv harvester is now a capable and resilient tool.")
    else:
        print("\n❌ One or more tests failed. Review the logs before proceeding.")
    
    print("="*80)

if __name__ == "__main__":
    main()