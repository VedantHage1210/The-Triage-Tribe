from fastapi import APIRouter, Depends
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.core.security import create_report_token, get_current_admin_email
from app.db.session import get_db
from app.models.models import TriageSession

router = APIRouter(
    prefix="/api/admin/sessions",
    tags=["admin-sessions"],
    dependencies=[Depends(get_current_admin_email)],
)

# Nurse queue order: most urgent first. Within the same severity, oldest
# first — the patient who has been waiting longest gets seen next, same
# logic as a real ED queue.
SEVERITY_PRIORITY = case(
    (TriageSession.severity_result == "EMERGENCY", 0),
    (TriageSession.severity_result == "URGENT", 1),
    (TriageSession.severity_result == "ROUTINE", 2),
    (TriageSession.severity_result == "SELF_CARE", 3),
    else_=4,
)


@router.get("")
def list_sessions(limit: int = 50, db: Session = Depends(get_db)):
    rows = (
        db.query(TriageSession)
        .order_by(SEVERITY_PRIORITY, TriageSession.created_at.asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "category": r.category,
            "language": r.language,
            "severity_result": r.severity_result,
            "confidence_score": r.confidence_score,
            "triggered_by": r.triggered_by,
            "patient_name": r.patient_name,
            "patient_age": r.patient_age,
            "patient_blood_group": r.patient_blood_group,
            "input_text": r.input_text,
            "ai_reasoning": r.ai_reasoning,
            "recommended_action": r.recommended_action,
            "cited_conditions": r.cited_conditions or [],
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "report_token": create_report_token(r.id),
            "key_factors": (r.extracted_symptoms or {}).get("key_factors", []),
            "vitals": (r.extracted_symptoms or {}).get("vitals", {}),
        }
        for r in rows
    ]