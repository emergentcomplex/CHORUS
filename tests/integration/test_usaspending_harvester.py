# Filename: tests/integration/test_usaspending_harvester.py (Pytest Style)
import pytest


from chorus_engine.adapters.harvesters.usaspending_harvester import USASpendingHarvester, USASpendingAwardResult

pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def harvester():
    return USASpendingHarvester()

def test_successful_contract_search(harvester):
    results = list(harvester.search_awards(keyword="hypersonic", award_types=["contracts"]))
    assert results, "Search should return results for a known-good keyword."
    assert isinstance(results[0], USASpendingAwardResult)

def test_successful_multi_group_search(harvester):
    results = list(harvester.search_awards(keyword="research", award_types=["contracts", "grants"]))
    assert results, "Multi-group search should return results."

def test_no_results_keyword(harvester):
    results = list(harvester.search_awards(keyword="asdfqwertzxcv"))
    assert isinstance(results, list) and len(results) == 0

def test_handles_invalid_group(harvester):
    results = list(harvester.search_awards(keyword="hypersonic", award_types=["contracts", "invalid_group"]))
    assert len(results) > 0
