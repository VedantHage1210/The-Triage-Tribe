from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    admin_auth,
    admin_content,
    admin_knowledge_base,
    admin_sessions,
    admin_symptoms,
    categories,
    content,
    symptoms,
    triage,
    visual_check,
)
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()

app = FastAPI(
    title="AI-Powered Clinical Triage Assistant",
    description="Bilingual (EN/DE), RAG-grounded triage API — see project roadmap for full spec.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(triage.router)
app.include_router(visual_check.router)
app.include_router(categories.router)
app.include_router(content.router)
app.include_router(symptoms.router)
app.include_router(admin_auth.router)
app.include_router(admin_symptoms.router)
app.include_router(admin_content.router)
app.include_router(admin_sessions.router)
app.include_router(admin_knowledge_base.router)


@app.on_event("startup")
def on_startup():
    # Day 1 simplicity: create tables directly. Swap to Alembic migrations
    # (Section 2 tech stack) once the schema stabilizes past the first
    # few days, so schema changes are tracked properly.
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
