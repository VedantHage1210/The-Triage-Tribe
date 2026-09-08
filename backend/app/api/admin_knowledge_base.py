from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_email
from app.db.session import get_db
from app.models.models import KnowledgeBase

router = APIRouter(
    prefix="/api/admin/knowledge-base",
    tags=["admin-knowledge-base"],
    dependencies=[Depends(get_current_admin_email)],
)


class KnowledgeBasePayload(BaseModel):
    condition_name: str = Field(min_length=1, max_length=160)
    icd_code: str | None = Field(default=None, max_length=32)
    category: str = Field(min_length=1, max_length=64)
    associated_symptoms: list[str] = Field(default_factory=list, max_length=50)
    typical_severity: str | None = Field(default=None, max_length=32)
    guidance_text_en: str = Field(min_length=1, max_length=5000)
    guidance_text_de: str | None = Field(default=None, max_length=5000)
    source_dataset: str | None = Field(default=None, max_length=160)


def _to_row(row: KnowledgeBase) -> dict:
    return {
        "id": str(row.id),
        "condition_name": row.condition_name,
        "icd_code": row.icd_code,
        "category": row.category,
        "associated_symptoms": row.associated_symptoms,
        "typical_severity": row.typical_severity,
        "guidance_text_en": row.guidance_text_en,
        "guidance_text_de": row.guidance_text_de,
        "source_dataset": row.source_dataset,
    }


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

    return [_to_row(r) for r in rows]


@router.post("", status_code=201)
def create_knowledge_base(payload: KnowledgeBasePayload, db: Session = Depends(get_db)):
    row = KnowledgeBase(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_row(row)


@router.put("/{knowledge_id}")
def update_knowledge_base(knowledge_id: UUID, payload: KnowledgeBasePayload, db: Session = Depends(get_db)):
    row = db.get(KnowledgeBase, knowledge_id)
    if not row:
        raise HTTPException(status_code=404, detail="Knowledge base entry not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return _to_row(row)


@router.delete("/{knowledge_id}", status_code=204)
def delete_knowledge_base(knowledge_id: UUID, db: Session = Depends(get_db)):
    row = db.get(KnowledgeBase, knowledge_id)
    if not row:
        raise HTTPException(status_code=404, detail="Knowledge base entry not found")
    db.delete(row)
    db.commit()
