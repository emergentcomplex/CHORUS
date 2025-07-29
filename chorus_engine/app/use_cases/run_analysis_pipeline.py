# Filename: chorus_engine/app/use_cases/run_analysis_pipeline.py (Definitive)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This file contains the 'RunAnalysisPipeline' use case. It orchestrates the
# high-level business logic for performing a complete analysis, from planning
# to synthesis. It depends only on the abstract interfaces defined in the
# application layer, making it independent of any specific database, LLM,
# or other external tool.

import json
import logging
import re
from typing import Dict, List, Any

# CORRECT: Only import abstract interfaces from the app layer.
from chorus_engine.app.interfaces import (
    LLMInterface, 
    DatabaseInterface, 
    VectorDBInterface, 
    PersonaRepositoryInterface
)
from chorus_engine.core.entities import AnalysisTask, AnalysisReport, HarvesterTask, Persona


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
        persona_repo: PersonaRepositoryInterface, # CORRECT: Depend on the abstraction
    ):
        """
        Initializes the use case with its dependencies.
        """
        self.llm = llm_adapter
        self.db = db_adapter
        self.vector_db = vector_db_adapter
        self.persona_repo = persona_repo
        self.persona: Persona = self.persona_repo.get_persona_by_id("director_alpha")
        if not self.persona:
            raise ValueError("Default persona 'director_alpha' could not be loaded.")

    def execute(self, task: AnalysisTask):
        """
        Executes the entire analysis pipeline for a given task.
        """
        try:
            task_description = task.user_query.get('query', '')
            self.db.log_progress(task.query_hash, "Starting analysis pipeline...")

            plan_result = self._phase1_generate_collection_plan(task.query_hash, task_description)
            initial_darpa_docs = plan_result.get("initial_darpa_docs", [])
            collection_tasks = plan_result.get("collection_tasks", [])

            self.db.queue_and_monitor_harvester_tasks(task.query_hash, collection_tasks)

            final_report = self._phase3_final_synthesis(task.query_hash, initial_darpa_docs, task_description)

            self.db.update_analysis_task_completion(task.query_hash, final_report)
            self.db.log_progress(task.query_hash, "Analysis pipeline completed successfully.")

        except Exception as e:
            logging.error(f"Use case failed for task {task.query_hash}: {e}", exc_info=True)
            self.db.update_analysis_task_failure(task.query_hash, str(e))

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
            self.db.log_progress(query_hash, "No high-confidence DARPA documents found. Generating plan from user query alone.")

        self.db.log_progress(query_hash, "Phase 1: Generating dynamic collection plan...")

        planner_prompt = f"""
        You are an AI controller embodying the persona of a {self.persona.name}.
        Your task is to create a collection plan based on the user query and a large set of relevant DARPA documents.
        You must sift through the documents to find the most relevant signals of strategic threat, then generate harvesting tasks.

        [CONTEXT FOR PLANNING]:
        {context_for_planning}

        You have access to these harvesters: 'usajobs_live_search', 'usaspending_search', 'newsapi_search', 'arxiv_search'.
        Your output MUST be only the task blocks. DO NOT include any preamble. Each task must start with 'HARVESTER:'.
        """
        plan_text = self.llm.instruct(planner_prompt, self.CONFIG['planner_model'])
        collection_tasks = self._parse_collection_plan(plan_text)

        if not collection_tasks:
            self.db.log_progress(query_hash, "Warning: AI failed to generate a structured plan. Creating a default fallback plan.")
            collection_tasks = [
                HarvesterTask(task_id=0, script_name='usaspending_search', status='IDLE', parameters={'Keyword': task_description}),
                HarvesterTask(task_id=0, script_name='usajobs_live_search', status='IDLE', parameters={'Keyword': task_description}),
                HarvesterTask(task_id=0, script_name='newsapi_search', status='IDLE', parameters={'Keyword': task_description}),
                HarvesterTask(task_id=0, script_name='arxiv_search', status='IDLE', parameters={'Keyword': task_description}),
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
        **CRITICAL DIRECTIVE: YOU ARE NOT A GENERIC AI ASSISTANT. YOU ARE {self.persona.name.upper()}.**

        **PERSONA PROFILE:**
        - **Identity:** {self.persona.name}
        - **Worldview:** {self.persona.worldview}
        - **Core Axioms:** {'; '.join(self.persona.axioms)}

        **MISSION:**
        Analyze the provided [DOSSIER] to answer the [USER QUERY]. You must adhere strictly to your persona.
        Your entire analysis MUST be framed as an assessment of potential threats, capabilities, and strategic risks.

        [USER QUERY]: "{task_description}"
        
        [DOSSIER]:
        {json.dumps(combined_context, indent=2, default=str)}

        **OUTPUT FORMAT:**
        Generate a final report as a single block of text with these exact headers:
        [NARRATIVE ANALYSIS]
        (Your threat-focused, multi-paragraph narrative analysis goes here.)

        [ARGUMENT MAP]
        (Your structured argument map, using bullet points to highlight evidence.)

        [INTELLIGENCE GAPS]
        (A numbered list of 3-5 intelligence gaps.)
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
            logging.error(f"Failed to parse final report text: {e}")
            raise RuntimeError(f"Failed to parse the AI's final report text. Raw output was: {report_text[:500]}...")

    def _parse_collection_plan(self, plan_text: str) -> List[HarvesterTask]:
        """Parses the LLM's collection plan into a list of HarvesterTask entities."""
        tasks = []
        if not plan_text:
            return tasks
        
        harvester_blocks = re.findall(r'HARVESTER:.*?(?=HARVESTER:|$)', plan_text, re.DOTALL)
        for block in harvester_blocks:
            if not block.strip():
                continue
            
            script_name = ""
            params = {}
            for line in block.strip().split('\n'):
                if ':' not in line:
                    continue
                key, value = line.split(':', 1)
                key, value = key.strip().upper(), value.strip()
                if key == 'HARVESTER':
                    script_name = value
                elif key == 'KEYWORDS':
                    params['Keyword'] = value
            
            if script_name and params:
                tasks.append(HarvesterTask(task_id=0, script_name=script_name, status='IDLE', parameters=params))
        return tasks
