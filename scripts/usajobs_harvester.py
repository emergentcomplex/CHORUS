# Filename: usajobs_harvester.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# Phase 2: USAJOBS Harvester Module Prototype (All core methods implemented)
#
# Purpose:
# This is the feature-complete prototype of the USAJobsHarvester class.
# It includes implementations for fetching historical jobs, all relevant
# codelists, and searching for live, currently-open jobs.

import requests
import logging
import os
import time
from typing import List, Optional, Dict, Generator
from pydantic import BaseModel, Field, ValidationError

# --- Pydantic Models for Data Structuring ---

# Models for /api/HistoricJoa
class JobLocation(BaseModel):
    PositionLocationCity: Optional[str] = None
    PositionLocationState: Optional[str] = None
    PositionLocationCountry: Optional[str] = None

class JobCategory(BaseModel):
    series: Optional[str] = Field(None, alias='Series')

class USAJobsAnnouncement(BaseModel):
    usajobs_control_number: int = Field(..., alias='usajobsControlNumber')
    position_title: str = Field(..., alias='positionTitle')
    agency_name: str = Field(..., alias='hiringAgencyName')
    department_name: str = Field(..., alias='hiringDepartmentName')
    open_date: str = Field(..., alias='positionOpenDate')
    close_date: str = Field(..., alias='positionCloseDate')
    security_clearance: Optional[str] = Field(None, alias='securityClearance')
    locations: List[JobLocation] = Field([], alias='PositionLocations')
    job_categories: List[JobCategory] = Field([], alias='JobCategories')
    minimum_grade: Optional[str] = Field(None, alias='minimumGrade')
    maximum_grade: Optional[str] = Field(None, alias='maximumGrade')

# Models for /api/Search
class LiveJobLocation(BaseModel):
    LocationName: str
    CountryCode: Optional[str] = None
    CityName: Optional[str] = None

class LiveJobDescriptor(BaseModel):
    PositionID: str
    PositionTitle: str
    PositionURI: str
    OrganizationName: str
    DepartmentName: str
    PositionLocation: List[LiveJobLocation]
    PublicationStartDate: str
    ApplicationCloseDate: str

class LiveJobSearchResult(BaseModel):
    MatchedObjectId: str
    MatchedObjectDescriptor: LiveJobDescriptor
    RelevanceRank: float


# --- Harvester Class ---

class USAJobsHarvester:
    """
    A client for interacting with the USAJOBS API.
    """
    def __init__(self, user_agent: str, auth_key: str):
        self.api_host = "data.usajobs.gov"
        if not user_agent or not auth_key:
            raise ValueError("USAJOBS User-Agent and Auth-Key cannot be empty.")

        self.auth_headers = {
            'Host': self.api_host,
            'User-Agent': user_agent,
            'Authorization-Key': auth_key
        }
        self.public_headers = {
            'Host': self.api_host,
            'User-Agent': user_agent
        }
        logging.info("USAJobsHarvester initialized.")

    def _make_request(self, endpoint, headers, params=None):
        """Internal helper for making requests and handling basic errors."""
        url = f"https://{self.api_host}{endpoint}"
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error for {url}: {e}")
            logging.error(f"Response body: {e.response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
        return None

    def get_all_codelists(self) -> Dict[str, List[Dict]]:
        """Fetches a curated list of important codelists from the API."""
        logging.info("Fetching all relevant codelists...")
        codelist_endpoints = [
            'agencysubelements', 'occupationalseries', 'securityclearances',
            'hiringpaths', 'positionofferingtypes', 'positionscheduletypes',
            'payplans', 'servicetypes'
        ]
        all_lists = {}
        for endpoint_name in codelist_endpoints:
            endpoint_path = f"/api/codelist/{endpoint_name}"
            response_data = self._make_request(endpoint_path, self.public_headers)
            if response_data and 'CodeList' in response_data and response_data['CodeList']:
                codelist_data = response_data['CodeList'][0].get('ValidValue', [])
                all_lists[endpoint_name] = codelist_data
            else:
                logging.warning(f"Failed to fetch or parse codelist: {endpoint_name}")
            time.sleep(1)
        return all_lists

    def get_live_jobs(self, search_params: Dict) -> Generator[LiveJobSearchResult, None, None]:
        """
        A generator that queries the /api/Search endpoint for currently open jobs.
        Handles page-based pagination.

        Args:
            search_params: A dictionary of search parameters (e.g., {'Keyword': 'analyst'}).

        Yields:
            LiveJobSearchResult: A Pydantic model of a live job search result.
        """
        logging.info(f"Searching for live jobs with params: {search_params}")
        
        page = 1
        results_per_page = 250 # A reasonable page size
        
        while True:
            params = search_params.copy()
            params['Page'] = page
            params['ResultsPerPage'] = results_per_page
            
            response_data = self._make_request('/api/Search', self.auth_headers, params)

            if not response_data or 'SearchResult' not in response_data:
                break

            search_result_items = response_data['SearchResult'].get('SearchResultItems', [])
            if not search_result_items:
                logging.info("No more live jobs found. Search complete.")
                break

            for job_data in search_result_items:
                try:
                    live_job = LiveJobSearchResult.model_validate(job_data)
                    yield live_job
                except ValidationError as e:
                    job_id = job_data.get('MatchedObjectId', 'N/A')
                    logging.warning(f"Skipping live job {job_id} due to validation error: {e}")
            
            page += 1
            time.sleep(1) # Be polite

    def get_historical_jobs(self, start_date: str, end_date: str, department_codes: List[str] = None) -> Generator[USAJobsAnnouncement, None, None]:
        """A generator that fetches historical job announcements within a date range."""
        logging.info(f"Fetching historical jobs from {start_date} to {end_date}")
        params = {'StartPositionOpenDate': start_date, 'EndPositionOpenDate': end_date}
        if department_codes:
            params['HiringDepartmentCodes'] = ','.join(department_codes)

        while True:
            response_data = self._make_request('/api/historicjoa', self.public_headers, params)
            if not response_data or 'data' not in response_data:
                break
            job_list = response_data.get('data', [])
            if not job_list:
                break
            for job_data in job_list:
                try:
                    announcement = USAJobsAnnouncement.model_validate(job_data)
                    yield announcement
                except ValidationError as e:
                    control_num = job_data.get('usajobsControlNumber', 'N/A')
                    logging.warning(f"Skipping job record {control_num} due to validation error: {e}")
            paging_data = response_data.get('paging', {})
            metadata = paging_data.get('metadata', {})
            continuation_token = metadata.get('continuationToken')
            if continuation_token:
                params['continuationtoken'] = continuation_token
                time.sleep(1)
            else:
                break

# --- Example Usage (for testing during development) ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    try:
        from dotenv import load_dotenv
        from pathlib import Path
        env_path = Path(__file__).resolve().parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)
        USAJOBS_EMAIL = os.getenv("USAJOBS_EMAIL")
        USAJOBS_API_KEY = os.getenv("USAJOBS_API_KEY")
    except ImportError:
        logging.warning("python-dotenv not found. Please set environment variables manually for testing.")
        USAJOBS_EMAIL = None
        USAJOBS_API_KEY = None

    if USAJOBS_EMAIL and USAJOBS_API_KEY:
        harvester = USAJobsHarvester(user_agent=USAJOBS_EMAIL, auth_key=USAJOBS_API_KEY)
        
        print("\n--- Testing get_live_jobs (IMPLEMENTED) ---")
        live_jobs_generator = harvester.get_live_jobs(search_params={'Keyword': 'Cybersecurity'})
        
        print("Fetching first 5 live jobs for 'Cybersecurity'...")
        for i, job in enumerate(live_jobs_generator):
            if i >= 5:
                break
            print(f"\n--- Live Job {i+1} ---")
            print(job.model_dump_json(indent=2))
            
    else:
        logging.error("Could not run test. USAJOBS_EMAIL and USAJOBS_API_KEY not found in environment.")