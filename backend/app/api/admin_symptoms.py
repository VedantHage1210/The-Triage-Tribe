from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_email
from app.db.session import get_db
from app.models.models import Symptom
from app.schemas.admin_schema import SymptomIn, SymptomOut

router = APIRouter(
    prefix="/api/admin/symptoms",
    tags=["admin-symptoms"],
    dependencies=[Depends(get_current_admin_email)],
)


@router.get("", response_model=list[SymptomOut])
def list_symptoms(db: Session = Depends(get_db)):
    return db.query(Symptom).all()


@router.post("", response_model=SymptomOut)
def create_symptom(payload: SymptomIn, db: Session = Depends(get_db)):
    if db.query(Symptom).filter(Symptom.code == payload.code).first():
        raise HTTPException(status_code=400, detail="A symptom with this code already exists")

    symptom = Symptom(**payload.model_dump())
    db.add(symptom)
    db.commit()
    db.refresh(symptom)
    return symptom


@router.put("/{symptom_id}", response_model=SymptomOut)
def update_symptom(symptom_id: UUID, payload: SymptomIn, db: Session = Depends(get_db)):
    symptom = db.get(Symptom, symptom_id)
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")

    for field, value in payload.model_dump().items():
        setattr(symptom, field, value)
    db.commit()
    db.refresh(symptom)
    return symptom


@router.delete("/{symptom_id}")
def delete_symptom(symptom_id: UUID, db: Session = Depends(get_db)):
    symptom = db.get(Symptom, symptom_id)
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")

    db.delete(symptom)
    db.commit()
    return {"deleted": True}
