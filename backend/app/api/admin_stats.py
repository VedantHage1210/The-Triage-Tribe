from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_email
from app.db.session import get_db
from app.models.models import TriageSession

router = APIRouter(
    prefix="/api/admin/stats",
    tags=["admin-stats"],
    dependencies=[Depends(get_current_admin_email)],
)


@router.get("")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(TriageSession.id)).scalar() or 0

    by_severity = dict(
        db.query(TriageSession.severity_result, func.count(TriageSession.id))
        .filter(TriageSession.severity_result.isnot(None))
        .group_by(TriageSession.severity_result)
        .all()
    )

    by_source = dict(
        db.query(TriageSession.triggered_by, func.count(TriageSession.id))
        .filter(TriageSession.triggered_by.isnot(None))
        .group_by(TriageSession.triggered_by)
        .all()
    )

    by_category = [
        {"category": category, "count": count}
        for category, count in (
            db.query(TriageSession.category, func.count(TriageSession.id))
            .filter(TriageSession.category.isnot(None))
            .group_by(TriageSession.category)
            .order_by(func.count(TriageSession.id).desc())
            .limit(8)
            .all()
        )
    ]

    return {
        "total_sessions": total,
        "by_severity": {
            "EMERGENCY": by_severity.get("EMERGENCY", 0),
            "URGENT": by_severity.get("URGENT", 0),
            "ROUTINE": by_severity.get("ROUTINE", 0),
            "SELF_CARE": by_severity.get("SELF_CARE", 0),
        },
        "by_source": {
            "guardrail": by_source.get("guardrail", 0),
            "llm": by_source.get("llm", 0),
            "fallback": by_source.get("fallback", 0),
        },
        "by_category": by_category,
    }
