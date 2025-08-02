# Filename: chorus_engine/app/interfaces.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This file defines the abstract interfaces (ports) that the application layer
# uses to communicate with external services (adapters).

import abc
from typing import List, Optional, Dict, Any

from chorus_engine.core.entities import AnalysisTask, AnalysisReport, HarvesterTask, Persona


class LLMInterface(abc.ABC):
    """An abstract interface for interacting with a Large Language Model."""

    @abc.abstractmethod
    def is_configured(self) -> bool:
        """
        A fast, local check to see if the adapter has the necessary
        credentials/configuration to perform its function.
        """
        pass

    @abc.abstractmethod
    def instruct(self, prompt: str, model_name: str) -> Optional[str]:
        """Sends a prompt to the specified LLM and returns the text response."""
        pass


class VectorDBInterface(abc.ABC):
    """An abstract interface for a vector database."""

    @abc.abstractmethod
    def query_similar_documents(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Finds documents with content semantically similar to the query."""
        pass


class PersonaRepositoryInterface(abc.ABC):
    """An abstract interface for a repository that provides Persona entities."""

    @abc.abstractmethod
    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """Retrieves a single persona by its unique ID."""
        pass

    @abc.abstractmethod
    def get_all_personas(self) -> List[Persona]:
        """Retrieves all available personas."""
        pass


class DatabaseInterface(abc.ABC):
    """
    An abstract interface for the primary application database, handling
    task management and state persistence.
    """

    @abc.abstractmethod
    def get_available_harvesters(self) -> List[str]:
        """Retrieves a list of unique harvester script names from the tasks table."""
        pass

    @abc.abstractmethod
    def claim_analysis_task(self, worker_id: str) -> Optional[AnalysisTask]:
        """Atomically claims a task ready for the Analyst Tier."""
        pass

    @abc.abstractmethod
    def claim_synthesis_task(self, worker_id: str) -> Optional[AnalysisTask]:
        """Atomically claims a task ready for the Director or Judge Tiers."""
        pass

    @abc.abstractmethod
    def get_analyst_reports(self, query_hash: str) -> List[Dict[str, Any]]:
        """Retrieves all analyst reports for a given mission."""
        pass

    @abc.abstractmethod
    def get_director_briefing(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieves the director's briefing for a given mission."""
        pass

    @abc.abstractmethod
    def save_director_briefing(self, query_hash: str, briefing_text: str) -> None:
        """Saves the director's synthesized briefing to the database."""
        pass

    @abc.abstractmethod
    def update_task_status(self, query_hash: str, new_status: str) -> None:
        """Updates the status of a task in the task_queue."""
        pass

    @abc.abstractmethod
    def save_analyst_report(self, query_hash: str, persona_id: str, report_text: str) -> None:
        """Saves a single analyst's report to the database."""
        pass

    @abc.abstractmethod
    def update_analysis_task_completion(self, query_hash: str, report: AnalysisReport) -> None:
        """Marks an analysis task as completed and saves the final report."""
        pass

    @abc.abstractmethod
    def update_analysis_task_failure(self, query_hash: str, error_message: str) -> None:
        """Marks an analysis task as failed and logs the error."""
        pass

    @abc.abstractmethod
    def log_progress(self, query_hash: str, message: str) -> None:
        """Logs a user-facing progress update for a given task."""
        pass

    @abc.abstractmethod
    def queue_and_monitor_harvester_tasks(self, query_hash: str, tasks: List[HarvesterTask]) -> bool:
        """Queues a list of harvester tasks and waits for their completion."""
        pass

    @abc.abstractmethod
    def load_data_from_datalake(self) -> Dict[str, Any]:
        """Loads the most recent data from all sources in the datalake."""
        pass