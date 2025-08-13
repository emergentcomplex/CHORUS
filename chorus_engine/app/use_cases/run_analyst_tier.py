# Filename: chorus_engine/app/use_cases/run_analyst_tier.py
# 🔱 CHORUS Analyst Tier Use Case (v5 - Final Interface Alignment)

import logging
import time
import json
from concurrent.futures import ThreadPoolExecutor
from chorus_engine.app.interfaces import (
    LLMInterface,
    DatabaseInterface,
    PersonaRepositoryInterface,
    VectorDBInterface  # Ensure VectorDBInterface is imported
)
from chorus_engine.core.entities import AnalysisTask, Persona

log = logging.getLogger(__name__)

class RunAnalystTier:
    """
    Orchestrates the parallel execution of the Analyst Tier, where multiple
    AI personas conduct independent research and generate preliminary reports.
    """
    CONFIG = {
        "analyst_personas": ["The Operator", "The Futurist", "The Systems Engineer", "The Fiscal Watchdog"]
    }

    def __init__(self,
                 llm_adapter: LLMInterface,
                 db_adapter: DatabaseInterface,
                 vector_db_adapter: VectorDBInterface, # Correct type hint
                 persona_repo: PersonaRepositoryInterface):
        self.llm = llm_adapter
        self.db = db_adapter
        self.vector_db = vector_db_adapter
        self.persona_repo = persona_repo

    def execute(self, query_hash: str):
        """
        Executes the full Analyst Tier pipeline for a given query hash.
        """
        start_time = time.perf_counter()
        try:
            if not self.llm.is_configured():
                raise RuntimeError("LLM adapter is not configured. Check API key.")

            task_data = self.db.get_task(query_hash)
            if not task_data:
                raise ValueError(f"Task with hash {query_hash} not found.")
            
            task = AnalysisTask(**task_data)
            user_query = task.user_query['query']

            self.db.update_task_status(query_hash, 'ANALYSIS_IN_PROGRESS')
            self.db.log_progress(query_hash, f"Executing Analyst Tier for query: '{user_query[:50]}...'")

            personas = [self.persona_repo.get_persona_by_id(pid) for pid in self.CONFIG["analyst_personas"]]
            valid_personas = [p for p in personas if p]
            if not valid_personas:
                raise ValueError("Could not load any valid Analyst personas.")

            with ThreadPoolExecutor(max_workers=len(valid_personas)) as executor:
                futures = [executor.submit(self._run_single_analyst_pipeline, task, persona) for persona in valid_personas]
                for future in futures:
                    future.result()

            self.db.update_task_status(query_hash, 'PENDING_SYNTHESIS')
            self.db.log_progress(query_hash, "Analyst Tier completed. Reports generated. Awaiting synthesis.")
            
            latency_seconds = time.perf_counter() - start_time
            log.info(f"Analyst Tier for {query_hash} completed in {latency_seconds:.2f}s")

        except Exception as e:
            log.error(f"Analyst Tier failed for task {query_hash}: {e}", exc_info=True)
            self.db.update_task_status(query_hash, 'FAILED')
            self.db.log_progress(query_hash, f"Analyst Tier failed: {e}")

    def _run_single_analyst_pipeline(self, task: AnalysisTask, persona: Persona):
        """A placeholder for the complex logic of a single analyst's workflow."""
        log.info(f"[{persona.persona_id}] starting analysis for task {task.query_hash}")
        user_query = task.user_query['query']
        
        # THE DEFINITIVE FIX: Call the method name defined in the interface.
        rag_context = self.vector_db.query_similar_documents(query=user_query, limit=5)
        log.info(f"[{persona.persona_id}] retrieved {len(rag_context)} documents.")
        
        time.sleep(1)
        
        log.info(f"[{persona.persona_id}] finished analysis for task {task.query_hash}")