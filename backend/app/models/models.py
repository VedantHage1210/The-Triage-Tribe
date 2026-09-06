"""
All database models in one module for simplicity in a 10-day build.
Matches the schema in the project roadmap, Section 5 + additions from
Section 8 (knowledge_base), Section 10 (visual_assessments), and
Section 11 (patient info columns on triage_sessions).
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def gen_uuid() -> uuid.UUID:
    return uuid.uuid4()


class Symptom(Base):
    """symptoms_i18n — Section 5.1"""
    __tablename__ = "symptoms_i18n"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    label_en: Mapped[str] = mapped_column(Text, nullable=False)
    label_de: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    red_flag: Mapped[bool] = mapped_column(Boolean, default=False)


class TriageRule(Base):
    """triage_rules — Section 5.2"""
    __tablename__ = "triage_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    symptom_code: Mapped[str] = mapped_column(String, ForeignKey("symptoms_i18n.code"), nullable=False)
    severity_level: Mapped[str] = mapped_column(String, nullable=False)  # emergency|urgent|routine|self_care
    advice_en: Mapped[str] = mapped_column(Text, nullable=False)
    advice_de: Mapped[str] = mapped_column(Text, nullable=True)


class TriageSession(Base):
    """triage_sessions — Section 5.3 + Section 11.2 patient info columns"""
    __tablename__ = "triage_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    category: Mapped[str] = mapped_column(String, nullable=True, index=True)
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(2), nullable=False, default="en")

    extracted_symptoms: Mapped[dict] = mapped_column(JSONB, nullable=True)
    severity_result: Mapped[str] = mapped_column(String, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    ai_reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=True)
    cited_conditions: Mapped[dict] = mapped_column(JSONB, nullable=True)
    follow_up_rounds: Mapped[int] = mapped_column(Integer, default=0)
    triggered_by: Mapped[str] = mapped_column(String, nullable=True)  # "guardrail" | "llm"

    # Patient info (Section 11.2) — all optional, never blocks the flow
    patient_name: Mapped[str] = mapped_column(String, nullable=True)
    patient_age: Mapped[int] = mapped_column(Integer, nullable=True)
    patient_blood_group: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    visual_assessments = relationship("VisualAssessment", back_populates="session")


class UIContent(Base):
    """ui_content_i18n — Section 5.4"""
    __tablename__ = "ui_content_i18n"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    key: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    value_en: Mapped[str] = mapped_column(Text, nullable=False)
    value_de: Mapped[str] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminUser(Base):
    """admin_users — Section 5.5"""
    __tablename__ = "admin_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class KnowledgeBase(Base):
    """knowledge_base — Section 8.5 (RAG source rows; embeddings live in the vector store, keyed by id)"""
    __tablename__ = "knowledge_base"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    condition_name: Mapped[str] = mapped_column(String, nullable=False)
    icd_code: Mapped[str] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    associated_symptoms: Mapped[dict] = mapped_column(JSONB, nullable=False)
    typical_severity: Mapped[str] = mapped_column(String, nullable=True)
    guidance_text_en: Mapped[str] = mapped_column(Text, nullable=False)
    guidance_text_de: Mapped[str] = mapped_column(Text, nullable=True)
    source_dataset: Mapped[str] = mapped_column(String, nullable=True)


class VisualAssessment(Base):
    """visual_assessments — Section 10.3"""
    __tablename__ = "visual_assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("triage_sessions.id"))
    category: Mapped[str] = mapped_column(String, nullable=False)  # "eyes" | "skin"
    visible_features: Mapped[dict] = mapped_column(JSONB, nullable=True)
    general_note: Mapped[str] = mapped_column(Text, nullable=True)
    image_quality_sufficient: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session = relationship("TriageSession", back_populates="visual_assessments")
