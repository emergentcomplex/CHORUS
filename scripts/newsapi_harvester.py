# Filename: scripts/newsapi_harvester.py (v2.0)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# v2.0: Definitive & Capable. The harvester is upgraded to support advanced
#       filtering (domains, sources, date ranges), making it a truly
#       intelligent tool for Analyst Tempo.

import requests
import logging
import time
from typing import List, Optional, Dict, Generator
from pydantic import BaseModel, Field, ValidationError

# --- Pydantic Models (Unchanged) ---
class NewsArticleSource(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None

class NewsArticle(BaseModel):
    source: NewsArticleSource
    author: Optional[str] = None
    title: str
    description: Optional[str] = None
    url: str
    urlToImage: Optional[str] = None
    publishedAt: str
    content: Optional[str] = None

# --- Harvester Class (Upgraded) ---
class NewsAPIHarvester:
    """
    A client for interacting with the NewsAPI, supporting advanced queries.
    """
    def __init__(self, api_key: str):
        self.api_host = "newsapi.org"
        if not api_key:
            raise ValueError("NewsAPI API Key cannot be empty.")
        self.headers = {'X-Api-Key': api_key}
        logging.info("NewsAPIHarvester initialized.")

    def _make_request(self, params: Dict) -> Optional[Dict]:
        url = f"https://{self.api_host}/v2/everything"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error for {url}: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
        return None

    def search_articles(self, search_parameters: Dict) -> Generator[NewsArticle, None, None]:
        """
        A generator that queries the /v2/everything endpoint using a flexible set of parameters.

        Args:
            search_parameters: A dictionary of API parameters like 'q', 'domains',
                               'from', 'to', 'pageSize', etc.

        Yields:
            NewsArticle: A validated Pydantic model of a single news article.
        """
        logging.info(f"Searching for news articles with params: {search_parameters}")
        
        # Set defaults if not provided
        search_parameters.setdefault('language', 'en')
        search_parameters.setdefault('sortBy', 'relevancy')
        search_parameters.setdefault('pageSize', 100)
        
        page = 1
        results_yielded = 0
        max_results = search_parameters.pop('max_results', 100) # Allow caller to set a limit

        while True:
            if results_yielded >= max_results:
                break

            params = search_parameters.copy()
            params['page'] = page
            
            response_data = self._make_request(params)

            if not response_data or response_data.get('status') != 'ok':
                break

            articles = response_data.get('articles', [])
            if not articles:
                break

            for article_data in articles:
                if results_yielded >= max_results:
                    break
                try:
                    article = NewsArticle.model_validate(article_data)
                    yield article
                    results_yielded += 1
                except ValidationError as e:
                    logging.warning(f"Skipping article due to validation error: {e}")
            
            # The free API is limited to 100 total results, so we stop if we've seen them all
            total_api_results = response_data.get('totalResults', 0)
            if results_yielded >= total_api_results or results_yielded >= 100:
                break
            
            page += 1
            time.sleep(1)