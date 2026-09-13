"""
Pydantic schemas — these are the contract between frontend and backend,
and also what the LLM's JSON output is validated against (Section 7.5).
"""
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Severity(str, Enum):
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    ROUTINE = "ROUTINE"
    SELF_CARE = "SELF_CARE"


class VitalSigns(BaseModel):
    """All optional — a patient/nurse may not have all of these on hand."""
    heart_rate_bpm: Optional[int] = Field(default=None, ge=0, le=300)
    bp_systolic: Optional[int] = Field(default=None, ge=0, le=300)
    bp_diastolic: Optional[int] = Field(default=None, ge=0, le=200)
    temperature_c: Optional[float] = Field(default=None, ge=25.0, le=45.0)
    spo2_percent: Optional[int] = Field(default=None, ge=0, le=100)


class TriageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    language: str = Field(default="en", pattern="^(en|de)$")
    category: Optional[str] = Field(default=None, max_length=64)
    session_id: Optional[UUID] = None  # present when answering a follow-up round
    patient_name: Optional[str] = Field(default=None, max_length=120)
    patient_age: Optional[int] = Field(default=None, ge=0, le=130)
    patient_blood_group: Optional[str] = Field(default=None, max_length=8)
    vitals: Optional[VitalSigns] = None


class ExtractedSymptoms(BaseModel):
    """Step A output — Section 7.2"""
    symptoms: list[str] = Field(default_factory=list)
    duration: Optional[str] = None
    severity_descriptors: list[str] = Field(default_factory=list)
    affected_area: Optional[str] = None


class TriageResult(BaseModel):
    """Step B output — Section 8.4 (RAG-grounded classification)"""
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    recommended_action: str
    cited_conditions: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    # Structured explainability — each entry names ONE input (a symptom or
    # a vital sign) and the direction it pushed the priority, e.g.
    # "SpO2 88% — below safe threshold" or "chest pain — high-risk symptom".
    # A nurse should be able to scan this in a few seconds without reading
    # the full reasoning paragraph.
    key_factors: list[str] = Field(default_factory=list)


class TriageResponse(BaseModel):
    session_id: UUID
    severity: Severity
    confidence: float
    reasoning: str
    recommended_action: str
    cited_conditions: list[str]
    follow_up_questions: list[str]
    key_factors: list[str] = Field(default_factory=list)
    needs_follow_up: bool
    triggered_by: str  # "guardrail" | "llm"
    language: str
    report_token: str


class VisualCheckResult(BaseModel):
    """Section 10.2 — deliberately no percentage/severity field, by design."""
    visible_features: list[str] = Field(default_factory=list)
    general_note: str
    recommend_professional_check: bool = True
    image_quality_sufficient: bool = True