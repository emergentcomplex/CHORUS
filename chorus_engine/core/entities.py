# Filename: chorus_engine/core/entities.py
# 🔱 CHORUS Core Domain Entities

from pydantic import BaseModel, Field
# THE DEFINITIVE FIX: Import the missing 'Optional' type hint.
from typing import Dict, Any, List, Optional
import datetime

class AnalysisTask(BaseModel):
    """Represents a single, stateful analysis task."""
    query_hash: str
    user_query: Dict[str, Any]
    status: str
    worker_id: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None

class Persona(BaseModel):
    """Represents an AI persona's configuration and identity."""
    persona_id: str = Field(..., alias='persona_name')
    tier: int = Field(..., alias='persona_tier')
    description: str = Field(..., alias='persona_description')
    subordinates: Optional[List[str]] = Field(None, alias='subordinate_personas')

    class Config:
        populate_by_name = True

class AnalysisReport(BaseModel):
    """Represents the structured output of an analyst's work."""
    persona_id: str = Field(..., description="The ID of the persona who generated this report.")
    query_hash: str = Field(..., description="The query hash this report belongs to.")
    title: str = Field(..., description="A concise, descriptive title for the report.")
    summary: str = Field(..., description="A one-paragraph executive summary of the key findings.")
    findings: List[str] = Field(..., description="A bulleted list of the most critical, evidence-based findings.")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="The analyst's confidence in their findings, from 0.0 to 1.0.")
    raw_text: Optional[str] = Field(None, description="The complete, raw text output from the LLM for archival.")

class HarvesterTask(BaseModel):
    """Represents a task for a harvester to go and collect data."""
    script_name: str
    associated_keywords: List[str]