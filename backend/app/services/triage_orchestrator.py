"""
Triage Orchestrator — wires together Section 7 (extraction, classification,
multi-turn) and Section 8 (RAG grounding). This is the single entry point
the /api/triage endpoint calls.
"""
from sqlalchemy.orm import Session

from app.schemas.triage_schema import ExtractedSymptoms, TriageResult
from app.services.llm_client import LLMClient
from app.services.rag_retriever import retrieve_relevant_conditions

llm = LLMClient()

CONFIDENCE_THRESHOLD = 0.6
MAX_FOLLOW_UP_ROUNDS = 2

# --- Step A: symptom extraction (Section 7.2) --------------------------

EXTRACTION_SYSTEM_PROMPT = """You are a medical symptom extraction engine. Do NOT diagnose or classify urgency.
From the patient's free-text description, extract:
{
  "symptoms": ["string", ...],
  "duration": "string|null",
  "severity_descriptors": ["string"],
  "affected_area": "string|null"
}
Output strict JSON only, no markdown fences, no commentary."""


def extract_symptoms(text: str, language: str) -> ExtractedSymptoms:
    user_message = f"Patient input ({language}): \"{text}\""
    raw = llm.get_json_completion(EXTRACTION_SYSTEM_PROMPT, user_message)
    return ExtractedSymptoms(**raw)


# --- Step B: RAG-grounded classification (Section 8.4) -----------------

CLASSIFICATION_SYSTEM_PROMPT = """You are a clinical triage support assistant. You do NOT diagnose.
Given the extracted symptom data AND the retrieved reference conditions below,
classify urgency into exactly one of:
EMERGENCY | URGENT | ROUTINE | SELF_CARE

Rules:
- Base your reasoning primarily on the retrieved reference data — do not
  contradict it without strong justification.
- If ANY life-threatening symptom is plausible, choose EMERGENCY.
- Cite which retrieved condition(s) most influenced your classification.
- The "reasoning" and "recommended_action" fields MUST be written entirely
  in {language_name}. Do not mix in English words or sentences, even if the
  retrieved reference data below is in English — translate any concepts you
  draw from it into {language_name}.
- Provide a "confidence" score 0.0-1.0.
- If confidence < 0.6, propose up to 2 targeted clarifying questions instead
  of finalizing, also written entirely in {language_name}.
- Never provide a diagnosis or medication dosage.

Output strict JSON only, matching this schema:
{{
  "severity": "EMERGENCY|URGENT|ROUTINE|SELF_CARE",
  "confidence": 0.0,
  "reasoning": "string",
  "recommended_action": "string",
  "cited_conditions": ["string", ...],
  "follow_up_questions": ["string", "string"]
}}"""

LANGUAGE_NAMES = {"en": "English", "de": "German"}


def classify_with_grounding(
    extracted: ExtractedSymptoms, retrieved_context: list[dict], language: str
) -> TriageResult:
    language_name = LANGUAGE_NAMES.get(language, "English")
    system_prompt = CLASSIFICATION_SYSTEM_PROMPT.format(language_name=language_name)
    user_message = (
        f"Extracted patient data: {extracted.model_dump_json()}\n"
        f"Retrieved reference conditions: {retrieved_context}"
    )
    raw = llm.get_json_completion(system_prompt, user_message)
    return TriageResult(**raw)


# --- Full pipeline (Steps A + B + C, Section 7.4) -----------------------

def run_triage_pipeline(
    text: str,
    language: str,
    category: str | None,
    db: Session,
    conversation_context: str = "",
    round_number: int = 0,
) -> tuple[TriageResult, ExtractedSymptoms, list[dict]]:
    """
    Runs extraction -> retrieval -> grounded classification.
    If confidence is low and we haven't hit the round cap, the caller
    (API layer) is responsible for surfacing follow_up_questions to the
    patient and re-invoking this with the appended context (Section 7.4).
    Returns (result, extracted_symptoms, retrieved_context) so the caller
    can persist everything for the audit trail (Section 8.6 / 5.3).
    """
    full_text = f"{conversation_context}\n{text}".strip() if conversation_context else text

    extracted = extract_symptoms(full_text, language)
    retrieved = retrieve_relevant_conditions(extracted.symptoms, category=category)
    result = classify_with_grounding(extracted, retrieved, language)

    return result, extracted, retrieved


def needs_follow_up(result: TriageResult, round_number: int) -> bool:
    return (
        result.confidence < CONFIDENCE_THRESHOLD
        and bool(result.follow_up_questions)
        and round_number < MAX_FOLLOW_UP_ROUNDS
    )
