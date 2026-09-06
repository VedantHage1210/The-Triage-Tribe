from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import UIContent

router = APIRouter(prefix="/api", tags=["content"])


@router.get("/content/{key}")
def get_content(key: str, lang: str = "en", db: Session = Depends(get_db)):
    row = db.query(UIContent).filter(UIContent.key == key).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"No content for key '{key}'")

    value = row.value_de if lang == "de" and row.value_de else row.value_en
    return {"key": key, "value": value, "language": lang if (lang == "de" and row.value_de) else "en"}


@router.get("/content")
def list_content(db: Session = Depends(get_db)):
    rows = db.query(UIContent).all()
    return [{"key": r.key, "value_en": r.value_en, "value_de": r.value_de} for r in rows]
