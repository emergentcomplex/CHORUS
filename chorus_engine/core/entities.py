# Filename: chorus_engine/core/entities.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This file defines the core business objects (Entities) of the CHORUS system.
# These are pure data structures with no dependencies on external frameworks,
# databases, or UI components. They represent the highest-level concepts
# in the architecture.

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Persona(BaseModel):
    """
    Represents an AI persona's core identity, worldview, and guiding principles.
    This is a pure business object, independent of how it is stored.
    """
    id: str = Field(..., description="The unique identifier for the persona, e.g., 'analyst_hawk'.")
    name: str = Field(..., description="The human-readable name of the persona.")
    worldview: str = Field(..., description="A description of the persona's core beliefs and perspective.")
    axioms: List[str] = Field(..., description="A list of inviolable rules that guide the persona's analysis.")

class AnalysisTask(BaseModel):
    """
    Represents a single, top-level analysis request in the system.
    """
    query_hash: str = Field(..., description="The unique MD5 hash of the user query.")
    user_query: Dict[str, Any] = Field(..., description="The original query submitted by the user.")
    status: str = Field(..., description="The current status of the task (e.g., PENDING, IN_PROGRESS).")
    worker_id: Optional[str] = Field(None, description="The ID of the worker currently processing the task.")

class HarvesterTask(BaseModel):
    """
    Represents a data collection task to be executed by a harvester.
    """
    task_id: int = Field(..., description="The unique ID for the harvesting task.")
    script_name: str = Field(..., description="The name of the harvester script to execute.")
    status: str = Field(..., description="The current status of the task (e.g., IDLE, IN_PROGRESS).")
    parameters: Dict[str, Any] = Field(..., description="The parameters for the harvester, e.g., keywords.")

class AnalysisReport(BaseModel):
    """
    Represents the final, structured output of an analysis pipeline.
    """
    narrative_analysis: str = Field(..., description="The main, multi-paragraph narrative of the report.")
    argument_map: str = Field(..., description="A structured map of claims and supporting evidence.")
    intelligence_gaps: str = Field(..., description="A list of identified intelligence gaps.")
    raw_text: Optional[str] = Field(None, description="The complete, raw text output from the LLM for archival.")

