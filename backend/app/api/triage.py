import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import create_report_token, verify_report_token
from app.core.limiter import limiter
from app.models.models import TriageSession, VisualAssessment
from app.schemas.triage_schema import Severity, TriageRequest, TriageResponse
from app.services.guardrail import check_red_flags, check_vital_red_flags
from app.services.pdf_report import generate_triage_report_pdf
from app.services.errors import TriagePipelineError
from app.services.triage_orchestrator import needs_follow_up, run_triage_pipeline

router = APIRouter(prefix="/api", tags=["triage"])
logger = logging.getLogger(__name__)

# Section 7.5 — safe fallback text shown if the LLM errors or returns
# something we can't validate. Never crash, never fail silently.
FALLBACK_MESSAGE = {
    "en": "We couldn't complete an AI assessment right now. Please consult a doctor "
          "if your symptoms concern you, or try again shortly.",
    "de": "Wir konnten die KI-Bewertung gerade nicht abschließen. Bitte wenden Sie sich "
          "an einen Arzt, wenn Ihre Symptome Sie beunruhigen, oder versuchen Sie es "
          "in Kürze erneut.",
}
FALLBACK_ACTION = {
    "en": "The AI assessment is unavailable. For concerning, worsening, or severe symptoms, seek urgent medical review now. Call emergency services for life-threatening symptoms.",
    "de": "Die KI-Bewertung ist nicht verfügbar. Bei beunruhigenden, zunehmenden oder starken Beschwerden suchen Sie bitte umgehend ärztliche Hilfe. Bei lebensbedrohlichen Symptomen rufen Sie den Notdienst.",
}


@router.post("/triage", response_model=TriageResponse)
@limiter.limit("10/minute")
def submit_triage(request: Request, payload: TriageRequest, db: Session = Depends(get_db)):
    # --- Existing session (answering a follow-up round) or a new one ---
    conversation_context = ""
    round_number = 0
    session_row: TriageSession | None = None

    if payload.session_id:
        session_row = db.get(TriageSession, payload.session_id)
        if session_row:
            conversation_context = session_row.input_text
            round_number = session_row.follow_up_rounds or 0

    # --- Step 0: deterministic guardrail (Section 7.1) — always first ---
    if check_red_flags(payload.text, payload.language, db):
        if session_row is None:
            session_row = TriageSession(
                category=payload.category,
                input_text=payload.text,
                language=payload.language,
                patient_name=payload.patient_name,
                patient_age=payload.patient_age,
                patient_blood_group=payload.patient_blood_group,
            )
            db.add(session_row)

        session_row.severity_result = Severity.EMERGENCY.value
        session_row.confidence_score = 1.0
        session_row.ai_reasoning = (
            "A described symptom matched a known emergency red-flag term."
        )
        session_row.recommended_action = (
            "Call emergency services immediately." if payload.language == "en"
            else "Rufen Sie sofort den Notdienst."
        )
        session_row.triggered_by = "guardrail"
        symptom_key_factor = (
            "Red-flag symptom detected" if payload.language == "en" else "Rotes Warnsignal-Symptom erkannt"
        )
        session_row.extracted_symptoms = {"key_factors": [symptom_key_factor]}
        db.commit()
        db.refresh(session_row)

        return TriageResponse(
            session_id=session_row.id,
            severity=Severity.EMERGENCY,
            confidence=1.0,
            reasoning=session_row.ai_reasoning,
            recommended_action=session_row.recommended_action,
            cited_conditions=[],
            follow_up_questions=[],
            key_factors=[symptom_key_factor],
            needs_follow_up=False,
            triggered_by="guardrail",
            language=payload.language,
            report_token=create_report_token(session_row.id),
        )

    # --- Step 0b: deterministic vital-sign thresholds — also before any
    #     LLM call. A dangerous number (e.g. SpO2 88%) should never wait
    #     on an LLM to notice it, and the reasons are ready-made key
    #     factors — no interpretation step that could get it wrong. ---
    vitals_emergency, vitals_reasons = check_vital_red_flags(payload.vitals, payload.language)
    if vitals_emergency:
        if session_row is None:
            session_row = TriageSession(
                category=payload.category,
                input_text=payload.text,
                language=payload.language,
                patient_name=payload.patient_name,
                patient_age=payload.patient_age,
                patient_blood_group=payload.patient_blood_group,
            )
            db.add(session_row)

        session_row.severity_result = Severity.EMERGENCY.value
        session_row.confidence_score = 1.0
        session_row.ai_reasoning = (
            "One or more reported vital signs are outside a safe range."
            if payload.language == "en"
            else "Ein oder mehrere gemeldete Vitalwerte liegen außerhalb eines sicheren Bereichs."
        )
        session_row.recommended_action = (
            "Call emergency services immediately." if payload.language == "en"
            else "Rufen Sie sofort den Notdienst."
        )
        session_row.triggered_by = "guardrail"
        session_row.extracted_symptoms = {
            "key_factors": vitals_reasons,
            "vitals": payload.vitals.model_dump(exclude_none=True) if payload.vitals else {},
        }
        db.commit()
        db.refresh(session_row)

        return TriageResponse(
            session_id=session_row.id,
            severity=Severity.EMERGENCY,
            confidence=1.0,
            reasoning=session_row.ai_reasoning,
            recommended_action=session_row.recommended_action,
            cited_conditions=[],
            follow_up_questions=[],
            key_factors=vitals_reasons,
            needs_follow_up=False,
            triggered_by="guardrail",
            language=payload.language,
            report_token=create_report_token(session_row.id),
        )

    # --- Steps A + B (+ C loop is driven by the frontend re-calling this
    #     endpoint with the same session_id when needs_follow_up is true) ---
    try:
        result, extracted, retrieved = run_triage_pipeline(
            text=payload.text,
            language=payload.language,
            category=payload.category,
            db=db,
            conversation_context=conversation_context,
            round_number=round_number,
            vitals=payload.vitals,
        )
        follow_up_needed = needs_follow_up(result, round_number)

        if session_row is None:
            session_row = TriageSession(
                category=payload.category,
                input_text=payload.text,
                language=payload.language,
                patient_name=payload.patient_name,
                patient_age=payload.patient_age,
                patient_blood_group=payload.patient_blood_group,
            )
            db.add(session_row)
        else:
            session_row.input_text = conversation_context + "\n" + payload.text

        extracted_dict = extracted.model_dump()
        extracted_dict["key_factors"] = result.key_factors
        if payload.vitals:
            # No dedicated vitals columns exist on TriageSession (avoids a
            # schema migration under a tight deadline) — the extracted_symptoms
            # JSONB column already exists and accepts arbitrary keys, so vitals
            # ride along in there for the PDF/audit trail without any ALTER TABLE.
            extracted_dict["vitals"] = payload.vitals.model_dump(exclude_none=True)
        session_row.extracted_symptoms = extracted_dict
        session_row.severity_result = result.severity.value
        session_row.confidence_score = result.confidence
        session_row.ai_reasoning = result.reasoning
        session_row.recommended_action = result.recommended_action
        session_row.cited_conditions = result.cited_conditions
        session_row.follow_up_rounds = round_number + (1 if follow_up_needed else 0)
        session_row.triggered_by = "llm"
        db.commit()
        db.refresh(session_row)

        return TriageResponse(
            session_id=session_row.id,
            severity=result.severity,
            confidence=result.confidence,
            reasoning=result.reasoning,
            recommended_action=result.recommended_action,
            cited_conditions=result.cited_conditions,
            follow_up_questions=result.follow_up_questions if follow_up_needed else [],
            key_factors=result.key_factors,
            needs_follow_up=follow_up_needed,
            triggered_by="llm",
            language=payload.language,
            report_token=create_report_token(session_row.id),
        )

    except TriagePipelineError as e:
        # Expected failure mode: the LLM provider errored or returned
        # something unparseable. Normal operating condition for a system
        # that depends on a third-party API — not a code defect.
        logger.warning("Triage pipeline failure (LLM/provider): %s", e)
        return _fallback_response(db, payload, session_row)

    except Exception:
        # Anything else here is a genuine code defect (AttributeError,
        # TypeError, KeyError, ...) — two of these shipped to prod hidden
        # behind a bare `except Exception` before this split existed.
        # Still shows the patient-facing safe fallback (never crash), but
        # logged loudly and distinctly so it doesn't get lost among
        # ordinary LLM hiccups. Grep logs for "BUG:" to find these.
        logger.critical("BUG: unexpected exception in triage pipeline", exc_info=True)
        return _fallback_response(db, payload, session_row)


def _fallback_response(db: Session, payload: TriageRequest, session_row: TriageSession | None) -> TriageResponse:
    if session_row is None:
        session_row = TriageSession(
            category=payload.category,
            input_text=payload.text,
            language=payload.language,
        )
        db.add(session_row)

    session_row.severity_result = Severity.URGENT.value
    session_row.ai_reasoning = "AI assessment unavailable; showing a safe default."
    session_row.recommended_action = FALLBACK_ACTION.get(payload.language, FALLBACK_ACTION["en"])
    session_row.triggered_by = "fallback"
    db.commit()
    db.refresh(session_row)

    return TriageResponse(
        session_id=session_row.id,
        severity=Severity.URGENT,
        confidence=0.0,
        reasoning=session_row.ai_reasoning,
        recommended_action=session_row.recommended_action,
        cited_conditions=[],
        follow_up_questions=[],
        needs_follow_up=False,
        triggered_by="fallback",
        language=payload.language,
        report_token=create_report_token(session_row.id),
    )


@router.get("/triage/{session_id}/report.pdf")
def download_report(
    session_id: UUID,
    lang: str = "en",
    token: str = Query(..., min_length=20),
    db: Session = Depends(get_db),
):
    """
    Section 11.3 — generates the PDF on demand from stored session data.
    Includes the visual observation (Section 10) if one exists for this
    session, so eyes/skin sessions get a fuller report.
    """
    if not verify_report_token(token, session_id):
        raise HTTPException(status_code=403, detail="Invalid or expired report access token")

    session = db.get(TriageSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    visual = (
        db.query(VisualAssessment)
        .filter(VisualAssessment.session_id == session_id)
        .order_by(VisualAssessment.created_at.desc())
        .first()
    )
    visual_dict = (
        {"general_note": visual.general_note, "visible_features": visual.visible_features}
        if visual
        else None
    )

    pdf_bytes = generate_triage_report_pdf(session, lang=lang, visual_observation=visual_dict)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="triage-report-{str(session_id)[:8]}.pdf"'
        },
    )