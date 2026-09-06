from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Symptom

router = APIRouter(prefix="/api", tags=["symptoms"])


@router.get("/symptoms")
def list_symptoms(category: str | None = None, lang: str = "en", db: Session = Depends(get_db)):
    query = db.query(Symptom)
    if category:
        query = query.filter(Symptom.category == category)
    rows = query.all()

    return [
        {
            "code": r.code,
            "label": (r.label_de if lang == "de" and r.label_de else r.label_en),
            "category": r.category,
        }
        for r in rows
    ]
