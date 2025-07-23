# Filename: scripts/usaspending_harvester.py (v2.2)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# v2.2: Definitive & Performant. Implements the Axiom of Pragmatic Harvesting
#       by adding a max_results limit to all searches, preventing unbounded
#       collection and ensuring operational viability.

import requests
import logging
import time
from typing import List, Optional, Dict, Generator
from pydantic import BaseModel, Field, ValidationError

# --- Pydantic Models (Unchanged) ---
class USASpendingAwardResult(BaseModel):
    internal_id: int
    award_id: Optional[str] = Field(None, alias='Award ID')
    recipient_name: Optional[str] = Field(None, alias='Recipient Name')
    generated_internal_id: str
    recipient_id: Optional[str] = None

# --- Harvester Class (Upgraded) ---
class USASpendingHarvester:
    
    AWARD_TYPE_GROUPS = {
        "contracts": ["A", "B", "C", "D"], "idvs": ["IDV_A", "IDV_B", "IDV_C", "IDV_D", "IDV_E"],
        "grants": ["02", "03", "04", "05"], "loans": ["07", "08"], "other": ["06", "09", "10", "11", "-1"]
    }

    def __init__(self, user_agent: str = "CHORUS OSINT Engine"):
        self.api_host = "api.usaspending.gov"
        self.headers = {'Content-Type': 'application/json', 'User-Agent': user_agent}
        logging.info("USASpendingHarvester initialized.")

    def _make_request(self, payload: Dict) -> Optional[Dict]:
        url = f"https://{self.api_host}/api/v2/search/spending_by_award/"
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=45)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
        return None

    def search_awards(self, keyword: str, award_types: List[str] = ["contracts", "idvs"], max_results: int = 250) -> Generator[USASpendingAwardResult, None, None]:
        """
        A performant generator that queries the USAspending API with a hard limit on results.
        """
        logging.info(f"Initiating search for '{keyword}' across {award_types} with a limit of {max_results} results.")
        
        results_yielded = 0
        
        for group in award_types:
            if results_yielded >= max_results: break
            if group not in self.AWARD_TYPE_GROUPS: continue
            
            logging.info(f"--- Searching award group: {group} ---")
            page = 1
            while True:
                if results_yielded >= max_results: break
                
                payload = {
                    "filters": { "keywords": [keyword], "award_type_codes": self.AWARD_TYPE_GROUPS[group] },
                    "fields": ["Award ID", "Recipient Name", "recipient_id", "generated_internal_id"],
                    "page": page, "limit": 100
                }
                
                response_data = self._make_request(payload)

                if response_data is None: break
                results = response_data.get('results', [])
                if not results: break

                for award_data in results:
                    if results_yielded >= max_results: break
                    try:
                        yield USASpendingAwardResult.model_validate(award_data)
                        results_yielded += 1
                    except ValidationError as e:
                        logging.warning(f"Skipping award record due to validation error: {e}")
                
                if not response_data.get('page_metadata', {}).get('hasNext', False):
                    break
                
                page += 1
                time.sleep(1.5)