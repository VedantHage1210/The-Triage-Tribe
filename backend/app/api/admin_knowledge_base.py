from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_email
from app.db.session import get_db
from app.models.models import KnowledgeBase

router = APIRouter(
    prefix="/api/admin/knowledge-base",
    tags=["admin-knowledge-base"],
    dependencies=[Depends(get_current_admin_email)],
)


@router.get("")
def list_knowledge_base(category: str | None = None, db: Session = Depends(get_db)):
    """
    Read-only for v1 (Section 18, Day 8 note) — full CRUD + re-embedding on
    edit is a stretch goal (Section 20). Editing today means updating via
    scripts/seed_data.py and re-running scripts/embed_knowledge_base.py.
    """
    query = db.query(KnowledgeBase)
    if category:
        query = query.filter(KnowledgeBase.category == category)
    rows = query.all()

    return [
        {
            "id": str(r.id),
            "condition_name": r.condition_name,
            "icd_code": r.icd_code,
            "category": r.category,
            "associated_symptoms": r.associated_symptoms,
            "typical_severity": r.typical_severity,
            "guidance_text_en": r.guidance_text_en,
            "guidance_text_de": r.guidance_text_de,
            "source_dataset": r.source_dataset,
        }
        for r in rows
    ]
