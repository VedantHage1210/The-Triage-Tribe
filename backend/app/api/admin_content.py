from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_email
from app.db.session import get_db
from app.models.models import UIContent
from app.schemas.admin_schema import ContentOut, ContentUpdate

router = APIRouter(
    prefix="/api/admin/content",
    tags=["admin-content"],
    dependencies=[Depends(get_current_admin_email)],
)


@router.get("", response_model=list[ContentOut])
def list_content(db: Session = Depends(get_db)):
    return db.query(UIContent).all()


@router.put("/{key}", response_model=ContentOut)
def update_content(key: str, payload: ContentUpdate, db: Session = Depends(get_db)):
    """
    Section 6.2 — a single save writes both languages atomically.
    Creates the key if it doesn't exist yet, so admins can add new
    UI strings without a developer touching the DB directly.
    """
    row = db.query(UIContent).filter(UIContent.key == key).first()
    if not row:
        row = UIContent(key=key, value_en=payload.value_en, value_de=payload.value_de)
        db.add(row)
    else:
        row.value_en = payload.value_en
        row.value_de = payload.value_de

    db.commit()
    db.refresh(row)
    return row
