# Filename: scripts/arxiv_harvester.py (v2.0)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# v2.0: Definitive & Resilient. The Pydantic model is upgraded to handle
#       optional fields like 'comment', and the class is hardened.

import requests
import logging
import time
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Generator
from pydantic import BaseModel, Field, ValidationError

# --- Pydantic Models (Upgraded) ---
class ArxivAuthor(BaseModel):
    name: str

class ArxivArticle(BaseModel):
    id: str
    title: str
    summary: str
    published: str
    updated: str
    authors: List[ArxivAuthor]
    pdf_url: Optional[str] = None
    # THE RESILIENCE FIX: The comment field is optional.
    comment: Optional[str] = None

# --- Harvester Class (Hardened) ---
class ArxivHarvester:
    """
    A client for interacting with the arXiv.org API.
    """
    def __init__(self):
        self.api_host = "http://export.arxiv.org"
        self.headers = {'User-Agent': 'CHORUS-OSINT-Engine/1.0'}
        self.ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom' # arXiv-specific namespace
        }
        logging.info("ArxivHarvester initialized.")

    def _make_request(self, params: Dict) -> Optional[ET.Element]:
        url = f"{self.api_host}/api/query"
        try:
            time.sleep(3) # Respect the rate limit
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return ET.fromstring(response.content)
        except requests.exceptions.HTTPError as e:
            # The API returns a 400 for bad queries, which is a valid failure mode
            if e.response.status_code == 400:
                logging.warning(f"API returned 400 Bad Request (likely a malformed query): {e.response.text}")
            else:
                logging.error(f"HTTP Error for {url}: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
        except ET.ParseError as e:
            logging.error(f"Failed to parse XML response: {e}")
        return None

    def search_articles(self, search_query: str, max_results: int = 100) -> Generator[ArxivArticle, None, None]:
        logging.info(f"Searching arXiv for query: '{search_query}'")
        
        start = 0
        results_yielded = 0
        page_size = 100

        while results_yielded < max_results:
            params = {
                'search_query': search_query,
                'start': start,
                'max_results': min(page_size, max_results - results_yielded)
            }
            
            root = self._make_request(params)

            if root is None: break

            entries = root.findall('atom:entry', self.ns)
            if not entries: break

            for entry in entries:
                try:
                    authors = [ArxivAuthor(name=author.find('atom:name', self.ns).text) for author in entry.findall('atom:author', self.ns)]
                    pdf_link = entry.find("atom:link[@title='pdf']", self.ns)
                    comment_tag = entry.find('arxiv:comment', self.ns)
                    
                    article_data = {
                        "id": entry.find('atom:id', self.ns).text,
                        "title": entry.find('atom:title', self.ns).text.strip(),
                        "summary": entry.find('atom:summary', self.ns).text.strip(),
                        "published": entry.find('atom:published', self.ns).text,
                        "updated": entry.find('atom:updated', self.ns).text,
                        "authors": authors,
                        "pdf_url": pdf_link.get('href') if pdf_link is not None else None,
                        "comment": comment_tag.text if comment_tag is not None else None
                    }
                    article = ArxivArticle.model_validate(article_data)
                    yield article
                    results_yielded += 1
                except (ValidationError, AttributeError) as e:
                    entry_id = entry.find('atom:id', self.ns).text if entry.find('atom:id', self.ns) is not None else 'N/A'
                    logging.warning(f"Skipping article {entry_id} due to parsing/validation error: {e}")
            
            start += page_size