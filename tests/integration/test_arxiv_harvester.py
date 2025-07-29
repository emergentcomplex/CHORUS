# Filename: tests/integration/test_arxiv_harvester.py (Pytest Style)
import pytest


from chorus_engine.adapters.harvesters.arxiv_harvester import ArxivHarvester

pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def harvester():
    return ArxivHarvester()

def test_basic_search(harvester):
    results = list(harvester.search_articles(search_query='ti:"machine learning"'))
    assert results, "Search should return results for a known-good keyword."

def test_complex_boolean_search(harvester):
    query = 'au:Karpathy AND cat:cs.CV ANDNOT ti:transformer'
    results = list(harvester.search_articles(search_query=query))
    assert results, "Complex boolean search should return results."

def test_malformed_query(harvester):
    query = 'auth:"Yann LeCun"'
    results = list(harvester.search_articles(search_query=query))
    assert isinstance(results, list) and len(results) == 0

def test_pagination(harvester):
    limit = 105
    results = list(harvester.search_articles(search_query='cat:cs.AI', max_results=limit))
    assert len(results) == limit
