# Filename: chorus_engine/app/use_cases/run_judge_tier.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This file contains the 'RunJudgeTier' use case, the final stage of the
# adversarial council analysis pipeline.

import logging
import time
import json
import re
from typing import Dict, List, Any

from chorus_engine.app.interfaces import (
    LLMInterface,
    DatabaseInterface,
    PersonaRepositoryInterface
)
from chorus_engine.core.entities import AnalysisTask, Persona, AnalysisReport

log = logging.getLogger(__name__)
sli_logger = logging.getLogger('sli')

class RunJudgeTier:
    """
    A use case that orchestrates the final tier of analysis, where a Judge
    persona reviews the Director's briefing and issues the final, structured verdict.
    """
    CONFIG = {
        "synthesis_model": "gemini-1.5-pro",
        "judge_persona": "judge_prime"
    }

    def __init__(
        self,
        llm_adapter: LLMInterface,
        db_adapter: DatabaseInterface,
        persona_repo: PersonaRepositoryInterface,
    ):
        """Initializes the use case with its dependencies."""
        self.llm = llm_adapter
        self.db = db_adapter
        self.persona_repo = persona_repo

    def execute(self, task: AnalysisTask):
        """Executes the judge tier pipeline for a given task."""
        start_time = time.perf_counter()
        component_name = "J-SYNZ (Judge Tier)"

        try:
            if not self.llm.is_configured():
                raise RuntimeError("LLM adapter is not configured. Check API key.")

            self.db.log_progress(task.query_hash, "Executing Judge Tier...")

            judge_persona = self.persona_repo.get_persona_by_id(self.CONFIG["judge_persona"])
            if not judge_persona:
                raise ValueError(f"Could not load Judge persona '{self.CONFIG['judge_persona']}'.")

            briefing = self.db.get_director_briefing(task.query_hash)
            if not briefing:
                raise ValueError("No Director's Briefing found to render judgment on.")
            
            self.db.log_progress(task.query_hash, "Rendering final judgment...")
            task_description = task.user_query.get('query', '')

            verdict_prompt = f"""
            **CRITICAL DIRECTIVE: YOU ARE THE FINAL JUDGE OF THE CHORUS ENGINE.**
            **PERSONA PROFILE:**
            - **Identity:** {judge_persona.name}
            - **Worldview:** {judge_persona.worldview}
            - **Core Axioms:** {'; '.join(judge_persona.axioms)}
            **MISSION:**
            You have received the final synthesized briefing from your Director. Your task is to review this briefing and render the final, authoritative verdict. Your output must be a structured report that is clear, concise, and directly answers the user's original query.

            [USER QUERY]: "{task_description}"

            [DIRECTOR'S BRIEFING]:
            {briefing['briefing_text']}

            **OUTPUT FORMAT:**
            Generate the final verdict as a single block of text with these exact headers:
            [NARRATIVE ANALYSIS]
            (Your final, multi-paragraph narrative analysis here.)
            [ARGUMENT MAP]
            (Your final, structured argument map here as a markdown list.)
            [INTELLIGENCE GAPS]
            (Your final, enumerated list of intelligence gaps here.)
            """
            
            report_text = self.llm.instruct(verdict_prompt, self.CONFIG['synthesis_model'])
            if not report_text:
                raise RuntimeError("AI failed to generate final verdict.")

            final_report = self._parse_final_report(report_text)

            self.db.update_analysis_task_completion(task.query_hash, final_report)
            self.db.log_progress(task.query_hash, "Analysis pipeline completed successfully.")

            latency_seconds = time.perf_counter() - start_time
            sli_logger.info(
                'pipeline_success_rate',
                extra={'component': component_name, 'success': True, 'latency_seconds': round(latency_seconds, 2)}
            )

        except Exception as e:
            log.error(f"Judge Tier failed for task {task.query_hash}: {e}", exc_info=True)
            self.db.update_analysis_task_failure(task.query_hash, str(e))
            latency_seconds = time.perf_counter() - start_time
            sli_logger.error(
                'pipeline_success_rate',
                extra={'component': component_name, 'success': False, 'latency_seconds': round(latency_seconds, 2), 'error': str(e)}
            )

    def _parse_final_report(self, report_text: str) -> AnalysisReport:
        # THE DEFINITIVE FIX: Be stricter. If any part is missing, it's a failure.
        narrative_match = re.search(r'\[NARRATIVE ANALYSIS\](.*?)\[ARGUMENT MAP\]', report_text, re.DOTALL)
        arg_map_match = re.search(r'\[ARGUMENT MAP\](.*?)\[INTELLIGENCE GAPS\]', report_text, re.DOTALL)
        gaps_match = re.search(r'\[INTELLIGENCE GAPS\](.*)', report_text, re.DOTALL)

        if not all([narrative_match, arg_map_match, gaps_match]):
            raise RuntimeError(f"Failed to parse the AI's final report text. Raw output was: {report_text[:500]}...")

        return AnalysisReport(
            narrative_analysis=narrative_match.group(1).strip(),
            argument_map=arg_map_match.group(1).strip(),
            intelligence_gaps=gaps_match.group(1).strip(),
            raw_text=report_text
        )