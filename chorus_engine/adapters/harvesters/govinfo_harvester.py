# Filename: chorus_engine/adapters/harvesters/govinfo_harvester.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# Harvester for the GovInfo.gov API, providing access to official
# U.S. Government publications.

import requests
import logging
from typing import List, Optional, Dict, Generator
from pydantic import BaseModel, Field, ValidationError

# --- Pydantic Models for Data Structuring ---
class GovInfoPackage(BaseModel):
    packageId: str
    lastModified: str
    packageLink: str
    docClass: str
    title: str
    congress: Optional[str] = None

class GovInfoHarvester:
    """
    A client for interacting with the GovInfo.gov API.
    """
    def __init__(self, api_key: str):
        self.api_host = "https://api.govinfo.gov"
        if not api_key:
            raise ValueError("GovInfo API Key cannot be empty.")
        self.headers = {'X-Api-Key': api_key}
        logging.info("GovInfoHarvester initialized.")

    def _make_request(self, params: Dict) -> Optional[Dict]:
        url = f"{self.api_host}/packages/search"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error for {url}: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
        return None

    def search_publications(self, query: str, max_results: int = 100) -> Generator[GovInfoPackage, None, None]:
        """
        A generator that searches for publications and yields results.

        Args:
            query: The search query string (e.g., "hypersonic defense").
            max_results: The maximum number of results to return.

        Yields:
            GovInfoPackage: A validated Pydantic model of a single publication package.
        """
        logging.info(f"Searching GovInfo for query: '{query}'")
        
        page_size = 100 # API default
        offset = 0
        results_yielded = 0

        while results_yielded < max_results:
            params = {
                'query': query,
                'pageSize': min(page_size, max_results - results_yielded),
                'offset': offset
            }
            
            response_data = self._make_request(params)

            if not response_data or not response_data.get('packages'):
                break

            packages = response_data['packages']
            for package_data in packages:
                try:
                    package = GovInfoPackage.model_validate(package_data)
                    yield package
                    results_yielded += 1
                except ValidationError as e:
                    logging.warning(f"Skipping GovInfo package due to validation error: {e}")
            
            if not response_data.get('nextPage'):
                break
            
            offset += page_size
