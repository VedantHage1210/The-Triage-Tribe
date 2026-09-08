from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy import text

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
settings.validate()

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


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    if settings.ENVIRONMENT.lower() in {"production", "prod"}:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

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

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend_dist"
if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.on_event("startup")
def on_startup():
    # Day 1 simplicity: create tables directly. Swap to Alembic migrations
    # (Section 2 tech stack) once the schema stabilizes past the first
    # few days, so schema changes are tracked properly.
    if settings.AUTO_CREATE_TABLES:
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as exc:
            # Keep the health endpoint available so deployment diagnostics can
            # report a missing database configuration instead of timing out.
            print(f"Database initialization skipped: {exc}")


@app.get("/api/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        return {"status": "degraded", "database": "unavailable"}


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    """Serve the built patient app when running as a single Docker Space."""
    requested_file = FRONTEND_DIST / full_path
    if full_path and requested_file.is_file():
        return FileResponse(requested_file)
    return FileResponse(FRONTEND_DIST / "index.html")
