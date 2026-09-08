from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import create_report_token, get_current_admin_email
from app.db.session import get_db
from app.models.models import TriageSession

router = APIRouter(
    prefix="/api/admin/sessions",
    tags=["admin-sessions"],
    dependencies=[Depends(get_current_admin_email)],
)


@router.get("")
def list_sessions(limit: int = 50, db: Session = Depends(get_db)):
    rows = (
        db.query(TriageSession)
        .order_by(TriageSession.created_at.desc())
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
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "report_token": create_report_token(r.id),
        }
        for r in rows
    ]
