# Filename: chorus_engine/app/use_cases/run_analysis_pipeline.py (With Pre-flight Check)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This file contains the 'RunAnalysisPipeline' use case.

import json
import logging
import re
import time
from typing import Dict, List, Any

from chorus_engine.app.interfaces import (
    LLMInterface, 
    DatabaseInterface, 
    VectorDBInterface, 
    PersonaRepositoryInterface
)
from chorus_engine.core.entities import AnalysisTask, AnalysisReport, HarvesterTask, Persona

sli_logger = logging.getLogger('sli')

class RunAnalysisPipeline:
    """
    A use case class that encapsulates the logic for running a full analysis pipeline.
    """
    CONFIG = {
        "synthesis_model": "gemini-1.5-pro",
        "planner_model": "gemini-1.5-pro",
    }

    def __init__(
        self,
        llm_adapter: LLMInterface,
        db_adapter: DatabaseInterface,
        vector_db_adapter: VectorDBInterface,
        persona_repo: PersonaRepositoryInterface,
    ):
        """Initializes the use case with its dependencies."""
        self.llm = llm_adapter
        self.db = db_adapter
        self.vector_db = vector_db_adapter
        self.persona_repo = persona_repo
        self.persona: Persona = self.persona_repo.get_persona_by_id("director_alpha")
        if not self.persona:
            raise ValueError("Default persona 'director_alpha' could not be loaded.")

    def execute(self, task: AnalysisTask):
        """Executes the entire analysis pipeline for a given task."""
        start_time = time.perf_counter()
        task_mode = task.user_query.get('mode', 'deep_dive')
        component_name = f"J-ANLZ ({task_mode.title()} Mode)"

        try:
            # THE DEFINITIVE FIX: Perform a pre-flight check before any work begins.
            if not self.llm.is_configured():
                raise RuntimeError("LLM adapter is not configured. Check API key.")

            task_description = task.user_query.get('query', '')
            self.db.log_progress(task.query_hash, "Starting analysis pipeline...")

            plan_result = self._phase1_generate_collection_plan(task.query_hash, task_description)
            initial_darpa_docs = plan_result.get("initial_darpa_docs", [])
            collection_tasks = plan_result.get("collection_tasks", [])

            self.db.queue_and_monitor_harvester_tasks(task.query_hash, collection_tasks)

            final_report = self._phase3_final_synthesis(task.query_hash, initial_darpa_docs, task_description)

            self.db.update_analysis_task_completion(task.query_hash, final_report)
            self.db.log_progress(task.query_hash, "Analysis pipeline completed successfully.")

            latency_seconds = time.perf_counter() - start_time
            sli_logger.info(
                'pipeline_success_rate',
                extra={'component': component_name, 'success': True, 'latency_seconds': round(latency_seconds, 2)}
            )

        except Exception as e:
            logging.error(f"Use case failed for task {task.query_hash}: {e}", exc_info=True)
            self.db.update_analysis_task_failure(task.query_hash, str(e))

            latency_seconds = time.perf_counter() - start_time
            sli_logger.error(
                'pipeline_success_rate',
                extra={'component': component_name, 'success': False, 'latency_seconds': round(latency_seconds, 2), 'error': str(e)}
            )

    def _phase1_generate_collection_plan(self, query_hash: str, task_description: str) -> Dict[str, Any]:
        """Generates a data collection plan based on an initial RAG query."""
        self.db.log_progress(query_hash, "Phase 1: Performing initial analysis on DARPA data...")
        rag_query = "Quantum Computing"
        darpa_docs = self.vector_db.query_similar_documents(rag_query, limit=200)
        context_for_planning = task_description
        if darpa_docs:
            self.db.log_progress(query_hash, f"Found {len(darpa_docs)} relevant DARPA documents to inform planning.")
            context_for_planning += "\n\n[RELEVANT DARPA DOCUMENTS]:\n" + json.dumps(darpa_docs, indent=2)
        else:
            self.db.log_progress(query_hash, "No high-confidence DARPA documents found.")

        self.db.log_progress(query_hash, "Phase 1: Generating dynamic collection plan...")
        available_harvesters = self.db.get_available_harvesters()
        harvester_list_str = ", ".join([f"'{h}'" for h in available_harvesters])
        planner_prompt = f"""
        You are an AI controller embodying the persona of a {self.persona.name}.
        Your task is to create a collection plan based on the user query and relevant documents.
        [CONTEXT FOR PLANNING]:
        {context_for_planning}
        You have access to these harvesters: {harvester_list_str}.
        Your output MUST be only the task blocks. Each task must start with 'HARVESTER:'.
        """
        plan_text = self.llm.instruct(planner_prompt, self.CONFIG['planner_model'])
        collection_tasks = self._parse_collection_plan(plan_text)
        if not collection_tasks:
            self.db.log_progress(query_hash, "Warning: AI failed to generate a structured plan. Creating a default fallback plan.")
            collection_tasks = [
                HarvesterTask(task_id=0, script_name=h_name, status='IDLE', parameters={'Keyword': task_description})
                for h_name in available_harvesters
            ]
        return {"collection_tasks": collection_tasks, "initial_darpa_docs": darpa_docs}

    def _phase3_final_synthesis(self, query_hash: str, initial_darpa_docs: list, task_description: str) -> AnalysisReport:
        """Fuses all data sources into a final, structured report."""
        self.db.log_progress(query_hash, "Phase 3: Fusing all data sources for final synthesis...")
        datalake_context = self.db.load_data_from_datalake()
        combined_context = {
            "initial_darpa_rag_documents": initial_darpa_docs,
            "harvested_data": datalake_context
        }
        synthesis_prompt = f"""
        **CRITICAL DIRECTIVE: YOU ARE {self.persona.name.upper()}.**
        **PERSONA PROFILE:**
        - **Identity:** {self.persona.name}
        - **Worldview:** {self.persona.worldview}
        - **Core Axioms:** {'; '.join(self.persona.axioms)}
        **MISSION:**
        Analyze the provided [DOSSIER] to answer the [USER QUERY].
        [USER QUERY]: "{task_description}"
        [DOSSIER]:
        {json.dumps(combined_context, indent=2, default=str)}
        **OUTPUT FORMAT:**
        Generate a final report as a single block of text with these exact headers:
        [NARRATIVE ANALYSIS]
        (Your analysis here.)
        [ARGUMENT MAP]
        (Your argument map here.)
        [INTELLIGENCE GAPS]
        (Your intelligence gaps here.)
        """
        report_text = self.llm.instruct(synthesis_prompt, self.CONFIG['synthesis_model'])
        if not report_text:
            raise RuntimeError("AI failed to generate a final report text.")
        try:
            narrative = re.search(r'\[NARRATIVE ANALYSIS\](.*?)\[ARGUMENT MAP\]', report_text, re.DOTALL)
            arg_map = re.search(r'\[ARGUMENT MAP\](.*?)\[INTELLIGENCE GAPS\]', report_text, re.DOTALL)
            gaps = re.search(r'\[INTELLIGENCE GAPS\](.*)', report_text, re.DOTALL)
            return AnalysisReport(
                narrative_analysis=narrative.group(1).strip() if narrative else "N/A",
                argument_map=arg_map.group(1).strip() if arg_map else "N/A",
                intelligence_gaps=gaps.group(1).strip() if gaps else "N/A",
                raw_text=report_text
            )
        except Exception as e:
            raise RuntimeError(f"Failed to parse the AI's final report text. Raw output was: {report_text[:500]}...")

    def _parse_collection_plan(self, plan_text: str) -> List[HarvesterTask]:
        """Parses the LLM's collection plan into a list of HarvesterTask entities."""
        tasks = []
        if not plan_text: return tasks
        harvester_blocks = re.findall(r'HARVESTER:.*?(?=HARVESTER:|$)', plan_text, re.DOTALL)
        for block in harvester_blocks:
            if not block.strip(): continue
            script_name = ""
            params = {}
            for line in block.strip().split('\n'):
                if ':' not in line: continue
                key, value = line.split(':', 1)
                key, value = key.strip().upper(), value.strip()
                if key == 'HARVESTER':
                    script_name = value
                elif key == 'KEYWORDS':
                    params['Keyword'] = value
            if script_name and params:
                tasks.append(HarvesterTask(task_id=0, script_name=script_name, status='IDLE', parameters=params))
        return tasks
