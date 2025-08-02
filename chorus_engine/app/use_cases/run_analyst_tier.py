# Filename: chorus_engine/app/use_cases/run_analyst_tier.py
import logging
import time
import json
import re
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor

from chorus_engine.app.interfaces import (
    LLMInterface,
    DatabaseInterface,
    VectorDBInterface,
    PersonaRepositoryInterface
)
from chorus_engine.core.entities import AnalysisTask, HarvesterTask, Persona

log = logging.getLogger(__name__)
sli_logger = logging.getLogger('sli')

class RunAnalystTier:
    CONFIG = {
        "planner_model": "gemini-1.5-pro",
        "synthesis_model": "gemini-1.5-pro",
        "analyst_personas": ["analyst_hawk", "analyst_dove", "analyst_skeptic", "analyst_futurist"]
    }

    def __init__(
        self,
        llm_adapter: LLMInterface,
        db_adapter: DatabaseInterface,
        vector_db_adapter: VectorDBInterface,
        persona_repo: PersonaRepositoryInterface,
    ):
        self.llm = llm_adapter
        self.db = db_adapter
        self.vector_db = vector_db_adapter
        self.persona_repo = persona_repo

    def execute(self, task: AnalysisTask):
        start_time = time.perf_counter()
        component_name = "J-ANLZ (Analyst Tier)"
        try:
            if not self.llm.is_configured():
                raise RuntimeError("LLM adapter is not configured. Check API key.")
            self.db.log_progress(task.query_hash, "Executing Analyst Tier...")
            personas = [self.persona_repo.get_persona_by_id(pid) for pid in self.CONFIG["analyst_personas"]]
            valid_personas = [p for p in personas if p]
            if not valid_personas:
                raise ValueError("Could not load any valid Analyst personas.")
            with ThreadPoolExecutor(max_workers=len(valid_personas)) as executor:
                futures = [executor.submit(self._run_single_analyst_pipeline, task, persona) for persona in valid_personas]
                for future in futures:
                    future.result()
            self.db.update_task_status(task.query_hash, 'PENDING_SYNTHESIS')
            self.db.log_progress(task.query_hash, "Analyst Tier completed. Reports generated. Awaiting synthesis.")
            latency_seconds = time.perf_counter() - start_time
            sli_logger.info('pipeline_success_rate', extra={'component': component_name, 'success': True, 'latency_seconds': round(latency_seconds, 2)})
        except Exception as e:
            log.error(f"Analyst Tier failed for task {task.query_hash}: {e}", exc_info=True)
            self.db.update_analysis_task_failure(task.query_hash, str(e)) # CORRECTED
            latency_seconds = time.perf_counter() - start_time
            sli_logger.error('pipeline_success_rate', extra={'component': component_name, 'success': False, 'latency_seconds': round(latency_seconds, 2), 'error': str(e)})

    def _run_single_analyst_pipeline(self, task: AnalysisTask, persona: Persona):
        self.db.log_progress(task.query_hash, f"[{persona.name}] Beginning analysis...")
        task_description = task.user_query.get('query', '')
        collection_tasks = self._generate_collection_plan(task.query_hash, task_description, persona)
        self.db.queue_and_monitor_harvester_tasks(task.query_hash, collection_tasks)
        datalake_context = self.db.load_data_from_datalake()
        synthesis_prompt = f"""
        **CRITICAL DIRECTIVE: YOU ARE {persona.name.upper()}.**
        **PERSONA PROFILE:**
        - **Identity:** {persona.name}
        - **Worldview:** {persona.worldview}
        - **Core Axioms:** {'; '.join(persona.axioms)}
        **MISSION:**
        Analyze the provided [DOSSIER] to answer the [USER QUERY]. Your analysis MUST be from your persona's unique perspective.
        [USER QUERY]: "{task_description}"
        [DOSSIER]:
        {json.dumps(datalake_context, indent=2, default=str)}
        **OUTPUT FORMAT:**
        Generate a preliminary analysis report as a single block of text.
        """
        report_text = self.llm.instruct(synthesis_prompt, self.CONFIG['synthesis_model'])
        if not report_text:
            raise RuntimeError(f"AI failed to generate report for persona {persona.name}.")
        self.db.save_analyst_report(task.query_hash, persona.id, report_text)
        self.db.log_progress(task.query_hash, f"[{persona.name}] Preliminary report saved.")

    def _generate_collection_plan(self, query_hash: str, task_description: str, persona: Persona) -> List[HarvesterTask]:
        self.db.log_progress(query_hash, f"[{persona.name}] Generating dynamic collection plan...")
        available_harvesters = self.db.get_available_harvesters()
        harvester_list_str = ", ".join([f"'{h}'" for h in available_harvesters])
        planner_prompt = f"""
        You are an AI controller embodying the persona of a {persona.name}.
        Your worldview is: "{persona.worldview}"
        Your core axioms are: {'; '.join(persona.axioms)}
        Based on this persona and the user query, create a collection plan.
        [USER QUERY]: {task_description}
        You have access to these harvesters: {harvester_list_str}.
        Your output MUST be only the task blocks. Each task must start with 'HARVESTER:'.
        Focus on keywords and sources that align with your persona's unique perspective.
        """
        plan_text = self.llm.instruct(planner_prompt, self.CONFIG['planner_model'])
        tasks = []
        if not plan_text: return tasks
        harvester_blocks = re.findall(r'HARVESTER:.*?(?=HARVESTER:|$)', plan_text, re.DOTALL)
        for block in harvester_blocks:
            if not block.strip(): continue
            script_name, params = "", {}
            for line in block.strip().split('\n'):
                if ':' not in line: continue
                key, value = line.split(':', 1)
                key, value = key.strip().upper(), value.strip()
                if key == 'HARVESTER': script_name = value
                elif key == 'KEYWORDS': params['Keyword'] = value
            if script_name and params:
                tasks.append(HarvesterTask(task_id=0, script_name=script_name, status='IDLE', parameters=params))
        if not tasks:
            self.db.log_progress(query_hash, f"Warning: [{persona.name}] failed to generate a structured plan. Creating a default fallback plan.")
            tasks = [HarvesterTask(task_id=0, script_name=h_name, status='IDLE', parameters={'Keyword': task_description}) for h_name in available_harvesters]
        return tasks