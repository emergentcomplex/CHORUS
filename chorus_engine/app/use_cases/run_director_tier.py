# Filename: chorus_engine/app/use_cases/run_director_tier.py
import logging
import time
import json
from typing import Dict, List, Any

from chorus_engine.app.interfaces import (
    LLMInterface,
    DatabaseInterface,
    PersonaRepositoryInterface
)
from chorus_engine.core.entities import AnalysisTask, Persona

log = logging.getLogger(__name__)
sli_logger = logging.getLogger('sli')

class RunDirectorTier:
    CONFIG = {
        "synthesis_model": "gemini-1.5-pro",
        "director_persona": "director_alpha"
    }

    def __init__(
        self,
        llm_adapter: LLMInterface,
        db_adapter: DatabaseInterface,
        persona_repo: PersonaRepositoryInterface,
    ):
        self.llm = llm_adapter
        self.db = db_adapter
        self.persona_repo = persona_repo

    def execute(self, task: AnalysisTask):
        start_time = time.perf_counter()
        component_name = "J-SYNZ (Director Tier)"
        try:
            if not self.llm.is_configured():
                raise RuntimeError("LLM adapter is not configured. Check API key.")
            self.db.log_progress(task.query_hash, "Executing Director Tier...")
            director_persona = self.persona_repo.get_persona_by_id(self.CONFIG["director_persona"])
            if not director_persona:
                raise ValueError(f"Could not load Director persona '{self.CONFIG['director_persona']}'.")
            analyst_reports = self.db.get_analyst_reports(task.query_hash)
            if not analyst_reports:
                raise ValueError("No analyst reports found to synthesize.")
            self.db.log_progress(task.query_hash, f"Synthesizing {len(analyst_reports)} competing analyst reports.")
            dossier = "\n\n---\n\n".join([f"ANALYST: {r['persona_id']}\n\n{r['report_text']}" for r in analyst_reports])
            task_description = task.user_query.get('query', '')
            synthesis_prompt = f"""
            **CRITICAL DIRECTIVE: YOU ARE {director_persona.name.upper()}.**
            **PERSONA PROFILE:**
            - **Identity:** {director_persona.name}
            - **Worldview:** {director_persona.worldview}
            - **Core Axioms:** {'; '.join(director_persona.axioms)}
            **MISSION:**
            You have received the following preliminary reports from your team of analysts. They have approached the user's query from their unique perspectives. Your task is to synthesize these competing views into a single, focused Director's Briefing. Identify areas of consensus and dissent, and highlight the most critical findings.
            [USER QUERY]: "{task_description}"
            [ANALYST DOSSIER]:
            {dossier}
            **OUTPUT FORMAT:**
            Generate the Director's Briefing as a single, concise block of text.
            """
            briefing_text = self.llm.instruct(synthesis_prompt, self.CONFIG['synthesis_model'])
            if not briefing_text:
                raise RuntimeError("AI failed to generate Director's Briefing.")
            self.db.save_director_briefing(task.query_hash, briefing_text)
            self.db.log_progress(task.query_hash, "Director's Briefing saved.")
            self.db.update_task_status(task.query_hash, 'PENDING_JUDGMENT')
            self.db.log_progress(task.query_hash, "Director Tier completed. Awaiting final judgment.")
            latency_seconds = time.perf_counter() - start_time
            sli_logger.info('pipeline_success_rate', extra={'component': component_name, 'success': True, 'latency_seconds': round(latency_seconds, 2)})
        except Exception as e:
            log.error(f"Director Tier failed for task {task.query_hash}: {e}", exc_info=True)
            self.db.update_analysis_task_failure(task.query_hash, str(e)) # CORRECTED
            latency_seconds = time.perf_counter() - start_time
            sli_logger.error('pipeline_success_rate', extra={'component': component_name, 'success': False, 'latency_seconds': round(latency_seconds, 2), 'error': str(e)})