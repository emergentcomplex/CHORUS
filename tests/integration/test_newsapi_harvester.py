# Filename: tests/integration/test_newsapi_harvester.py (Pytest Style)
import logging
import os
import pytest


from chorus_engine.adapters.harvesters.newsapi_harvester import NewsAPIHarvester

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def harvester():
    """Provides a NewsAPIHarvester instance for the test module."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        pytest.skip("NEWS_API_KEY not found in environment, skipping NewsAPI tests.")
    return NewsAPIHarvester(api_key=api_key)

def test_basic_search(harvester):
    """Tests a known-good search term returns valid, non-empty results."""
    results = list(harvester.search_articles({'q': 'DARPA'}))
    assert results, "Search should return results for a known-good keyword."

def test_domain_search(harvester):
    """Tests domain filtering."""
    params = {'q': 'international relations', 'domains': 'apnews.com'}
    results = list(harvester.search_articles(params))
    if results:
        for article in results:
            assert 'apnews.com' in article.url

def test_date_range_search(harvester):
    """Tests if the harvester can correctly search within a date range."""
    params = {'q': 'semiconductor', 'from': '2025-07-01', 'to': '2025-07-05'}
    results = list(harvester.search_articles(params))
    if results:
        for article in results:
            assert '2025-07-01' <= article.publishedAt[:10] <= '2025-07-05'

def test_max_results_limit(harvester):
    """Tests if the max_results parameter correctly limits the output."""
    params = {'q': 'technology', 'max_results': 5}
    results = list(harvester.search_articles(params))
    assert len(results) <= 5
