from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SymptomIn(BaseModel):
    code: str
    label_en: str
    label_de: Optional[str] = None
    category: str
    red_flag: bool = False


class SymptomOut(SymptomIn):
    id: UUID


class ContentUpdate(BaseModel):
    value_en: str
    value_de: Optional[str] = None


class ContentOut(BaseModel):
    key: str
    value_en: str
    value_de: Optional[str] = None


class SessionSummary(BaseModel):
    id: UUID
    category: Optional[str]
    language: str
    severity_result: Optional[str]
    confidence_score: Optional[float]
    triggered_by: Optional[str]
    patient_name: Optional[str]
    created_at: str
